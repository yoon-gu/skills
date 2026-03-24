# Claude API — Go

> **참고:** Go SDK는 Claude API와 `BetaToolRunner`를 통한 베타 도구 사용을 지원합니다. Agent SDK는 아직 Go에서 사용할 수 없습니다.

## 설치

```bash
go get github.com/anthropics/anthropic-sdk-go
```

## 클라이언트 초기화

```go
import (
    "github.com/anthropics/anthropic-sdk-go"
    "github.com/anthropics/anthropic-sdk-go/option"
)

// Default (uses ANTHROPIC_API_KEY env var)
client := anthropic.NewClient()

// Explicit API key
client := anthropic.NewClient(
    option.WithAPIKey("your-api-key"),
)
```

---

## 기본 메시지 요청

```go
response, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
    Model:     anthropic.ModelClaudeOpus4_6,
    MaxTokens: 16000,
    Messages: []anthropic.MessageParam{
        anthropic.NewUserMessage(anthropic.NewTextBlock("What is the capital of France?")),
    },
})
if err != nil {
    log.Fatal(err)
}
for _, block := range response.Content {
    switch variant := block.AsAny().(type) {
    case anthropic.TextBlock:
        fmt.Println(variant.Text)
    }
}
```

---

## 스트리밍

```go
stream := client.Messages.NewStreaming(context.Background(), anthropic.MessageNewParams{
    Model:     anthropic.ModelClaudeOpus4_6,
    MaxTokens: 64000,
    Messages: []anthropic.MessageParam{
        anthropic.NewUserMessage(anthropic.NewTextBlock("Write a haiku")),
    },
})

for stream.Next() {
    event := stream.Current()
    switch eventVariant := event.AsAny().(type) {
    case anthropic.ContentBlockDeltaEvent:
        switch deltaVariant := eventVariant.Delta.AsAny().(type) {
        case anthropic.TextDelta:
            fmt.Print(deltaVariant.Text)
        }
    }
}
if err := stream.Err(); err != nil {
    log.Fatal(err)
}
```

**최종 메시지 누적** (스트림에는 `GetFinalMessage()`가 없습니다):

```go
stream := client.Messages.NewStreaming(ctx, params)
message := anthropic.Message{}
for stream.Next() {
    message.Accumulate(stream.Current())
}
if err := stream.Err(); err != nil { log.Fatal(err) }
// message.Content now has the complete response
```


---

## 도구 사용

### Tool Runner (Beta — 권장)

**Beta:** Go SDK는 `toolrunner` 패키지를 통해 자동 도구 사용 루프를 위한 `BetaToolRunner`를 제공합니다.

```go
import (
    "context"
    "fmt"
    "log"

    "github.com/anthropics/anthropic-sdk-go"
    "github.com/anthropics/anthropic-sdk-go/toolrunner"
)

// Define tool input with jsonschema tags for automatic schema generation
type GetWeatherInput struct {
    City string `json:"city" jsonschema:"required,description=The city name"`
}

// Create a tool with automatic schema generation from struct tags
weatherTool, err := toolrunner.NewBetaToolFromJSONSchema(
    "get_weather",
    "Get current weather for a city",
    func(ctx context.Context, input GetWeatherInput) (anthropic.BetaToolResultBlockParamContentUnion, error) {
        return anthropic.BetaToolResultBlockParamContentUnion{
            OfText: &anthropic.BetaTextBlockParam{
                Text: fmt.Sprintf("The weather in %s is sunny, 72°F", input.City),
            },
        }, nil
    },
)
if err != nil {
    log.Fatal(err)
}

// Create a tool runner that handles the conversation loop automatically
runner := client.Beta.Messages.NewToolRunner(
    []anthropic.BetaTool{weatherTool},
    anthropic.BetaToolRunnerParams{
        BetaMessageNewParams: anthropic.BetaMessageNewParams{
            Model:     anthropic.ModelClaudeOpus4_6,
            MaxTokens: 16000,
            Messages: []anthropic.BetaMessageParam{
                anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("What's the weather in Paris?")),
            },
        },
        MaxIterations: 5,
    },
)

// Run until Claude produces a final response
message, err := runner.RunToCompletion(context.Background())
if err != nil {
    log.Fatal(err)
}

// RunToCompletion returns *BetaMessage; content is []BetaContentBlockUnion.
// Narrow via AsAny() switch — note the Beta-namespace types (BetaTextBlock,
// not TextBlock):
for _, block := range message.Content {
    switch block := block.AsAny().(type) {
    case anthropic.BetaTextBlock:
        fmt.Println(block.Text)
    }
}
```

**Go tool runner의 주요 기능:**

- Go 구조체의 `jsonschema` 태그를 통한 자동 스키마 생성
- 간단한 일회성 사용을 위한 `RunToCompletion()`
- 대화의 각 메시지를 처리하기 위한 `All()` 이터레이터
- 단계별 반복을 위한 `NextMessage()`
- `NewToolRunnerStreaming()`과 `AllStreaming()`을 통한 스트리밍 변형

### 수동 루프

에이전트 루프를 세밀하게 제어하려면 `ToolParam`으로 도구를 정의하고, `StopReason`을 확인하고, 직접 도구를 실행한 후 `tool_result` 블록을 다시 전달합니다. 도구 호출을 가로채거나 검증하거나 로깅해야 할 때 사용하는 패턴입니다.

`anthropic-sdk-go/examples/tools/main.go`에서 파생되었습니다.

```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"

    "github.com/anthropics/anthropic-sdk-go"
)

func main() {
    client := anthropic.NewClient()

    // 1. Define tools. ToolParam.InputSchema uses a map, no struct tags needed.
    addTool := anthropic.ToolParam{
        Name:        "add",
        Description: anthropic.String("Add two integers"),
        InputSchema: anthropic.ToolInputSchemaParam{
            Properties: map[string]any{
                "a": map[string]any{"type": "integer"},
                "b": map[string]any{"type": "integer"},
            },
        },
    }
    // ToolParam must be wrapped in ToolUnionParam for the Tools slice
    tools := []anthropic.ToolUnionParam{{OfTool: &addTool}}

    messages := []anthropic.MessageParam{
        anthropic.NewUserMessage(anthropic.NewTextBlock("What is 2 + 3?")),
    }

    for {
        resp, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
            Model:     anthropic.ModelClaudeSonnet4_6,
            MaxTokens: 16000,
            Messages:  messages,
            Tools:     tools,
        })
        if err != nil {
            log.Fatal(err)
        }

        // 2. Append the assistant response to history BEFORE processing tool calls.
        //    resp.ToParam() converts Message → MessageParam in one call.
        messages = append(messages, resp.ToParam())

        // 3. Walk content blocks. ContentBlockUnion is a flattened struct;
        //    use block.AsAny().(type) to switch on the actual variant.
        toolResults := []anthropic.ContentBlockParamUnion{}
        for _, block := range resp.Content {
            switch variant := block.AsAny().(type) {
            case anthropic.TextBlock:
                fmt.Println(variant.Text)
            case anthropic.ToolUseBlock:
                // 4. Parse the tool input. Use variant.JSON.Input.Raw() to get the
                //    raw JSON — block.Input is json.RawMessage, not the parsed value.
                var in struct {
                    A int `json:"a"`
                    B int `json:"b"`
                }
                if err := json.Unmarshal([]byte(variant.JSON.Input.Raw()), &in); err != nil {
                    log.Fatal(err)
                }
                result := fmt.Sprintf("%d", in.A+in.B)
                // 5. NewToolResultBlock(toolUseID, content, isError) builds the
                //    ContentBlockParamUnion for you. block.ID is the tool_use_id.
                toolResults = append(toolResults,
                    anthropic.NewToolResultBlock(block.ID, result, false))
            }
        }

        // 6. Exit when Claude stops asking for tools
        if resp.StopReason != anthropic.StopReasonToolUse {
            break
        }

        // 7. Tool results go in a user message (variadic: all results in one turn)
        messages = append(messages, anthropic.NewUserMessage(toolResults...))
    }
}
```

**주요 API 표면:**

| 심볼 | 용도 |
|---|---|
| `resp.ToParam()` | `Message` 응답을 기록용 `MessageParam`으로 변환 |
| `block.AsAny().(type)` | `ContentBlockUnion` 변형에 대한 타입 스위치 |
| `variant.JSON.Input.Raw()` | 도구 입력의 원시 JSON 문자열 (`json.Unmarshal`용) |
| `anthropic.NewToolResultBlock(id, content, isError)` | `tool_result` 블록 생성 |
| `anthropic.NewUserMessage(blocks...)` | 도구 결과를 사용자 턴으로 래핑 |
| `anthropic.StopReasonToolUse` | 루프 종료를 확인하기 위한 `StopReason` 상수 |
| `anthropic.ToolUnionParam{OfTool: &t}` | `ToolParam`을 `Tools:` 유니온으로 래핑 |

---

## 사고

`MessageNewParams`에서 `Thinking`을 설정하여 Claude의 내부 추론을 활성화합니다. 응답에는 최종 `TextBlock` 앞에 `ThinkingBlock` 콘텐츠가 포함됩니다.

**적응형 사고는 Claude 4.6+ 모델에서 권장되는 모드입니다.** Claude가 언제, 얼마나 사고할지 동적으로 결정합니다. 비용-품질 제어를 위해 `effort` 매개변수와 함께 사용하세요.

`anthropic-sdk-go/message.go` (`ThinkingConfigParamUnion`, `NewThinkingConfigAdaptiveParam`)에서 파생되었습니다.

```go
// There is no ThinkingConfigParamOfAdaptive helper — construct the union
// struct-literal directly and take the address of the variant.
adaptive := anthropic.NewThinkingConfigAdaptiveParam()
params := anthropic.MessageNewParams{
    Model:     anthropic.ModelClaudeSonnet4_6,
    MaxTokens: 16000,
    Thinking:  anthropic.ThinkingConfigParamUnion{OfAdaptive: &adaptive},
    Messages: []anthropic.MessageParam{
        anthropic.NewUserMessage(anthropic.NewTextBlock("How many r's in strawberry?")),
    },
}

resp, err := client.Messages.New(context.Background(), params)
if err != nil {
    log.Fatal(err)
}

// ThinkingBlock(s) precede TextBlock in content
for _, block := range resp.Content {
    switch b := block.AsAny().(type) {
    case anthropic.ThinkingBlock:
        fmt.Println("[thinking]", b.Thinking)
    case anthropic.TextBlock:
        fmt.Println(b.Text)
    }
}
```

> **지원 중단:** `ThinkingConfigParamOfEnabled(budgetTokens)` (고정 예산 확장 사고)는 Claude 4.6에서 여전히 작동하지만 지원 중단되었습니다. 위의 적응형 사고를 사용하세요.

비활성화하려면: `anthropic.ThinkingConfigParamUnion{OfDisabled: &anthropic.ThinkingConfigDisabledParam{}}`.

---

## 서버 측 도구

버전 접미사가 붙은 구조체 이름에 `Param` 접미사를 사용합니다. `Name`/`Type`은 `constant.*` 타입으로, 제로 값이 올바르게 마셜링되므로 `{}`가 작동합니다. 해당하는 `Of*` 필드와 함께 `ToolUnionParam`으로 래핑합니다.

```go
Tools: []anthropic.ToolUnionParam{
    {OfWebSearchTool20260209: &anthropic.WebSearchTool20260209Param{}},
    {OfBashTool20250124: &anthropic.ToolBash20250124Param{}},
    {OfTextEditor20250728: &anthropic.ToolTextEditor20250728Param{}},
    {OfCodeExecutionTool20260120: &anthropic.CodeExecutionTool20260120Param{}},
},
```

다음도 사용 가능: `WebFetchTool20260209Param`, `MemoryTool20250818Param`, `ToolSearchToolBm25_20251119Param`, `ToolSearchToolRegex20251119Param`.

---

## PDF / 문서 입력

`NewDocumentBlock` 범용 헬퍼는 모든 소스 타입을 허용합니다. `MediaType`/`Type`은 자동으로 설정됩니다.

```go
b64 := base64.StdEncoding.EncodeToString(pdfBytes)

msg := anthropic.NewUserMessage(
    anthropic.NewDocumentBlock(anthropic.Base64PDFSourceParam{Data: b64}),
    anthropic.NewTextBlock("Summarize this document"),
)
```

기타 소스: `URLPDFSourceParam{URL: "https://..."}`, `PlainTextSourceParam{Data: "..."}`.

---

## Files API (Beta)

`client.Beta.Files` 아래에 있습니다. 메서드는 **`Upload`**입니다 (`New`/`Create`가 아님). 매개변수 구조체는 `BetaFileUploadParams`입니다. `File` 필드는 `io.Reader`를 받습니다. 멀티파트 인코딩을 위해 파일명과 콘텐츠 타입을 첨부하려면 `anthropic.File()`을 사용하세요.

```go
f, _ := os.Open("./upload_me.txt")
defer f.Close()

meta, err := client.Beta.Files.Upload(ctx, anthropic.BetaFileUploadParams{
    File:  anthropic.File(f, "upload_me.txt", "text/plain"),
    Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaFilesAPI2025_04_14},
})
// meta.ID is the file_id to reference in subsequent message requests
```

기타 `Beta.Files` 메서드: `List`, `Delete`, `Download`, `GetMetadata`.

---

## 컨텍스트 편집 / 압축 (Beta)

`BetaMessageNewParams`에서 `ContextManagement`와 함께 `Beta.Messages.New`를 사용합니다. `NewBetaAssistantMessage`는 없습니다. 왕복 변환에는 `.ToParam()`을 사용하세요.

```go
params := anthropic.BetaMessageNewParams{
    Model:     anthropic.ModelClaudeOpus4_6,  // also supported: ModelClaudeSonnet4_6
    MaxTokens: 16000,
    Betas:     []anthropic.AnthropicBeta{"compact-2026-01-12"},
    ContextManagement: anthropic.BetaContextManagementConfigParam{
        Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
            {OfCompact20260112: &anthropic.BetaCompact20260112EditParam{}},
        },
    },
    Messages: []anthropic.BetaMessageParam{ /* ... */ },
}

resp, err := client.Beta.Messages.New(ctx, params)
if err != nil {
    log.Fatal(err)
}

// Round-trip: append response to history via .ToParam()
params.Messages = append(params.Messages, resp.ToParam())

// Read compaction blocks from the response
for _, block := range resp.Content {
    if c, ok := block.AsAny().(anthropic.BetaCompactionBlock); ok {
        fmt.Println("compaction summary:", c.Content)
    }
}
```

기타 편집 타입: `BetaClearToolUses20250919EditParam`, `BetaClearThinking20251015EditParam`.
