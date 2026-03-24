# Claude API — C#

> **참고:** C# SDK는 C#용 공식 Anthropic SDK입니다. 도구 사용은 Messages API를 통해 지원됩니다. 클래스 어노테이션 기반 도구 실행기는 사용할 수 없습니다. JSON 스키마를 사용한 원시 도구 정의를 사용하세요. SDK는 함수 호출을 포함한 Microsoft.Extensions.AI IChatClient 통합도 지원합니다.

## 설치

```bash
dotnet add package Anthropic
```

## 클라이언트 초기화

```csharp
using Anthropic;

// Default (uses ANTHROPIC_API_KEY env var)
AnthropicClient client = new();

// Explicit API key (use environment variables — never hardcode keys)
AnthropicClient client = new() {
    ApiKey = Environment.GetEnvironmentVariable("ANTHROPIC_API_KEY")
};
```

---

## 기본 메시지 요청

```csharp
using Anthropic.Models.Messages;

var parameters = new MessageCreateParams
{
    Model = Model.ClaudeOpus4_6,
    MaxTokens = 16000,
    Messages = [new() { Role = Role.User, Content = "What is the capital of France?" }]
};
var response = await client.Messages.Create(parameters);

// ContentBlock is a union wrapper. .Value unwraps to the variant object,
// then OfType<T> filters to the type you want. Or use the TryPick* idiom
// shown in the Thinking section below.
foreach (var text in response.Content.Select(b => b.Value).OfType<TextBlock>())
{
    Console.WriteLine(text.Text);
}
```

---

## 스트리밍

```csharp
using Anthropic.Models.Messages;

var parameters = new MessageCreateParams
{
    Model = Model.ClaudeOpus4_6,
    MaxTokens = 64000,
    Messages = [new() { Role = Role.User, Content = "Write a haiku" }]
};

await foreach (RawMessageStreamEvent streamEvent in client.Messages.CreateStreaming(parameters))
{
    if (streamEvent.TryPickContentBlockDelta(out var delta) &&
        delta.Delta.TryPickText(out var text))
    {
        Console.Write(text.Text);
    }
}
```

**`RawMessageStreamEvent` TryPick 메서드** (이름에서 `Message`/`Raw` 접두사가 제거됨): `TryPickStart`, `TryPickDelta`, `TryPickStop`, `TryPickContentBlockStart`, `TryPickContentBlockDelta`, `TryPickContentBlockStop`. `TryPickMessageStop`은 없습니다 — `TryPickStop`을 사용하세요.

---

## 사고

**적응형 사고는 Claude 4.6+ 모델에 권장되는 모드입니다.** Claude가 언제, 얼마나 사고할지 동적으로 결정합니다.

```csharp
using Anthropic.Models.Messages;

var response = await client.Messages.Create(new MessageCreateParams
{
    Model = Model.ClaudeOpus4_6,
    MaxTokens = 16000,
    // ThinkingConfigParam? implicitly converts from the concrete variant classes —
    // no wrapper needed.
    Thinking = new ThinkingConfigAdaptive(),
    Messages =
    [
        new() { Role = Role.User, Content = "Solve: 27 * 453" },
    ],
});

// ThinkingBlock(s) precede TextBlock in Content. TryPick* narrows the union.
foreach (var block in response.Content)
{
    if (block.TryPickThinking(out ThinkingBlock? t))
    {
        Console.WriteLine($"[thinking] {t.Thinking}");
    }
    else if (block.TryPickText(out TextBlock? text))
    {
        Console.WriteLine(text.Text);
    }
}
```

> **지원 중단:** `new ThinkingConfigEnabled { BudgetTokens = N }` (고정 예산 확장 사고)는 Claude 4.6에서 여전히 작동하지만 지원 중단되었습니다. 위의 적응형 사고를 사용하세요.

`TryPick*`의 대안: `.Select(b => b.Value).OfType<ThinkingBlock>()` (기본 메시지 예제와 동일한 LINQ 패턴).

---

## 도구 사용

### 도구 정의

`Tool` (`ToolParam`이 아님)과 `InputSchema` 레코드를 사용합니다. `InputSchema.Type`은 생성자에 의해 자동으로 `"object"`로 설정됩니다 — 직접 설정하지 마세요. `ToolUnion`은 `Tool`로부터 암시적 변환이 가능하며, 컬렉션 표현식 `[...]`에 의해 트리거됩니다.

```csharp
using System.Text.Json;
using Anthropic.Models.Messages;

var parameters = new MessageCreateParams
{
    Model = Model.ClaudeSonnet4_6,
    MaxTokens = 16000,
    Tools = [
        new Tool {
            Name = "get_weather",
            Description = "Get the current weather in a given location",
            InputSchema = new() {
                Properties = new Dictionary<string, JsonElement> {
                    ["location"] = JsonSerializer.SerializeToElement(
                        new { type = "string", description = "City name" }),
                },
                Required = ["location"],
            },
        },
    ],
    Messages = [new() { Role = Role.User, Content = "Weather in Paris?" }],
};
```

`anthropic-sdk-csharp/src/Anthropic/Models/Messages/Tool.cs` 및 `ToolUnion.cs:799` (암시적 변환)에서 파생되었습니다.

루프 패턴에 대해서는 [공유 도구 사용 개념](../shared/tool-use-concepts.md)을 참조하세요.
### 응답 콘텐츠를 후속 어시스턴트 메시지로 변환

Claude의 응답을 어시스턴트 턴에서 다시 전달할 때, **`.ToParam()` 헬퍼가 없습니다** — 각 `ContentBlock` 변형을 해당하는 `*Param` 대응물로 수동 재구성하세요. `new ContentBlockParam(block.Json)`을 사용하지 마세요: 컴파일되고 직렬화되지만, `.Value`가 `null`로 유지되어 `TryPick*`/`Validate()`가 실패합니다 (타입이 지정된 경로가 아닌 저하된 JSON 패스스루).

```csharp
using Anthropic.Models.Messages;

Message response = await client.Messages.Create(parameters);

// No .ToParam() — reconstruct per variant. Implicit conversions from each
// *Param type to ContentBlockParam mean no explicit wrapper.
List<ContentBlockParam> assistantContent = [];
List<ContentBlockParam> toolResults = [];
foreach (ContentBlock block in response.Content)
{
    if (block.TryPickText(out TextBlock? text))
    {
        assistantContent.Add(new TextBlockParam { Text = text.Text });
    }
    else if (block.TryPickThinking(out ThinkingBlock? thinking))
    {
        // Signature MUST be preserved — the API rejects tampering
        assistantContent.Add(new ThinkingBlockParam
        {
            Thinking = thinking.Thinking,
            Signature = thinking.Signature,
        });
    }
    else if (block.TryPickRedactedThinking(out RedactedThinkingBlock? redacted))
    {
        assistantContent.Add(new RedactedThinkingBlockParam { Data = redacted.Data });
    }
    else if (block.TryPickToolUse(out ToolUseBlock? toolUse))
    {
        // ToolUseBlock has required Caller; ToolUseBlockParam.Caller is optional — don't copy it
        assistantContent.Add(new ToolUseBlockParam
        {
            ID = toolUse.ID,
            Name = toolUse.Name,
            Input = toolUse.Input,
        });
        // Execute the tool; collect ONE result per tool_use block — the API
        // rejects the follow-up if any tool_use ID lacks a matching tool_result.
        string result = ExecuteYourTool(toolUse.Name, toolUse.Input);
        toolResults.Add(new ToolResultBlockParam
        {
            ToolUseID = toolUse.ID,
            Content = result,
        });
    }
}

// Follow-up: prior messages + assistant echo + user tool_result(s)
List<MessageParam> followUpMessages =
[
    .. parameters.Messages,
    new() { Role = Role.Assistant, Content = assistantContent },
    new() { Role = Role.User, Content = toolResults },
];
```

`ToolResultBlockParam`에는 튜플 생성자가 없습니다 — 객체 이니셜라이저를 사용하세요. `Content`는 문자열 또는 리스트 유니온이며, 일반 `string`이 암시적으로 변환됩니다.

---

## 컨텍스트 편집 / 압축 (베타)

**베타 네임스페이스 접두사가 일관적이지 않습니다** (`src/Anthropic/Models/Beta/Messages/*.cs` @ 12.8.0에서 소스 검증됨). 접두사 없음: `MessageCreateParams`, `MessageCountTokensParams`, `Role`. **나머지는 모두 `Beta` 접두사를 가집니다**: `BetaMessageParam`, `BetaMessage`, `BetaContentBlock`, `BetaToolUseBlock`, 모든 블록 매개변수 타입. 접두사가 없는 `Role`은 두 네임스페이스를 모두 임포트하면 `Anthropic.Models.Messages.Role`과 충돌합니다 (CS0104). 가장 안전한 방법: Beta만 임포트하세요. 혼합 사용 시 베타 `Role`에 별칭을 지정하세요:

```csharp
using Anthropic.Models.Beta.Messages;
using NonBeta = Anthropic.Models.Messages;  // only if you also need non-beta types
// Now: MessageCreateParams, BetaMessageParam, Role (beta's), NonBeta.Role (if needed)
```


`BetaMessage.Content`는 `IReadOnlyList<BetaContentBlock>`입니다 — 15개 변형의 구분된 유니온입니다. `TryPick*`으로 좁히세요. **응답 `BetaContentBlock`은 매개변수 `BetaContentBlockParam`에 할당할 수 없습니다** — C#에는 `.ToParam()`이 없습니다. 각 블록을 변환하여 왕복하세요:

```csharp
using Anthropic.Models.Beta.Messages;

var betaParams = new MessageCreateParams   // no Beta prefix — one of only 2 unprefixed
{
    Model = Model.ClaudeOpus4_6,
    MaxTokens = 16000,
    Betas = ["compact-2026-01-12"],
    ContextManagement = new BetaContextManagementConfig
    {
        Edits = [new BetaCompact20260112Edit()],
    },
    Messages = messages,
};
BetaMessage resp = await client.Beta.Messages.Create(betaParams);

foreach (BetaContentBlock block in resp.Content)
{
    if (block.TryPickCompaction(out BetaCompactionBlock? compaction))
    {
        // Content is nullable — compaction can fail server-side
        Console.WriteLine($"compaction summary: {compaction.Content}");
    }
}

// Context-edit metadata lives on a separate nullable field
if (resp.ContextManagement is { } ctx)
{
    foreach (var edit in ctx.AppliedEdits)
        Console.WriteLine($"cleared {edit.ClearedInputTokens} tokens");
}

// ROUND-TRIP: BetaMessageParam.Content is BetaMessageParamContent (a string|list
// union). It implicit-converts from List<BetaContentBlockParam>, NOT from the
// response's IReadOnlyList<BetaContentBlock>. Convert each block:
List<BetaContentBlockParam> paramBlocks = [];
foreach (var b in resp.Content)
{
    if (b.TryPickText(out var t)) paramBlocks.Add(new BetaTextBlockParam { Text = t.Text });
    else if (b.TryPickCompaction(out var c)) paramBlocks.Add(new BetaCompactionBlockParam { Content = c.Content });
    // ... other variants as needed
}
messages.Add(new BetaMessageParam { Role = Role.Assistant, Content = paramBlocks });
```

15개의 `BetaContentBlock.TryPick*` 변형 전체: `Text`, `Thinking`, `RedactedThinking`, `ToolUse`, `ServerToolUse`, `WebSearchToolResult`, `WebFetchToolResult`, `CodeExecutionToolResult`, `BashCodeExecutionToolResult`, `TextEditorCodeExecutionToolResult`, `ToolSearchToolResult`, `McpToolUse`, `McpToolResult`, `ContainerUpload`, `Compaction`.

**`BetaToolUseBlock.Input`은 `IReadOnlyDictionary<string, JsonElement>`입니다** — 키로 인덱싱한 다음 `JsonElement` 추출기를 호출하세요:

```csharp
if (block.TryPickToolUse(out BetaToolUseBlock? tu))
{
    int a = tu.Input["a"].GetInt32();
    string s = tu.Input["name"].GetString()!;
}
```

---

## 노력 매개변수

노력은 `OutputConfig` 아래에 중첩되며, 최상위 속성이 아닙니다. `ApiEnum<string, Effort>`는 열거형으로부터 암시적 변환이 가능하므로 `Effort.High`를 직접 할당하세요.

```csharp
OutputConfig = new OutputConfig { Effort = Effort.High },
```

값: `Effort.Low`, `Effort.Medium`, `Effort.High`, `Effort.Max`. 비용-품질 제어를 위해 `Thinking = new ThinkingConfigAdaptive()`와 결합하세요.

---

## 프롬프트 캐싱

`System`은 `MessageCreateParamsSystem?`을 받습니다 — `string` 또는 `List<TextBlockParam>`의 유니온입니다. `SystemTextBlockParam`은 없으며, 일반 `TextBlockParam`을 사용하세요. 암시적 변환에는 구체적인 `List<TextBlockParam>` 타입이 필요합니다 (배열 리터럴은 변환되지 않습니다).

```csharp
System = new List<TextBlockParam> {
    new() {
        Text = longSystemPrompt,
        CacheControl = new CacheControlEphemeral(),  // auto-sets Type = "ephemeral"
    },
},
```

`CacheControlEphemeral`의 선택적 `Ttl`: `new() { Ttl = Ttl.Ttl1h }` 또는 `Ttl.Ttl5m`. `CacheControl`은 `Tool.CacheControl` 및 최상위 `MessageCreateParams.CacheControl`에도 존재합니다.

---

## 토큰 카운팅

```csharp
MessageTokensCount result = await client.Messages.CountTokens(new MessageCountTokensParams {
    Model = Model.ClaudeOpus4_6,
    Messages = [new() { Role = Role.User, Content = "Hello" }],
});
long tokens = result.InputTokens;
```

`MessageCountTokensParams.Tools`는 `MessageCreateParams.Tools` (`ToolUnion`)와 다른 유니온 타입 (`MessageCountTokensTool`)을 사용합니다 — 도구를 전달할 때 중요한 경우 컴파일러가 알려줄 것입니다.

---

## 구조화된 출력

```csharp
OutputConfig = new OutputConfig {
    Format = new JsonOutputFormat {
        Schema = new Dictionary<string, JsonElement> {
            ["type"] = JsonSerializer.SerializeToElement("object"),
            ["properties"] = JsonSerializer.SerializeToElement(
                new { name = new { type = "string" } }),
            ["required"] = JsonSerializer.SerializeToElement(new[] { "name" }),
        },
    },
},
```

`JsonOutputFormat.Type`은 생성자에 의해 자동으로 `"json_schema"`로 설정됩니다. `Schema`는 필수입니다.

---

## PDF / 문서 입력

`DocumentBlockParam`은 `DocumentBlockParamSource` 유니온을 받습니다: `Base64PdfSource` / `UrlPdfSource` / `PlainTextSource` / `ContentBlockSource`. `Base64PdfSource`는 자동으로 `MediaType = "application/pdf"` 및 `Type = "base64"`를 설정합니다.

```csharp
new MessageParam {
    Role = Role.User,
    Content = new List<ContentBlockParam> {
        new DocumentBlockParam { Source = new Base64PdfSource { Data = base64String } },
        new TextBlockParam { Text = "Summarize this PDF" },
    },
}
```

---

## 서버 측 도구

웹 검색, bash, 텍스트 편집기, 코드 실행은 내장 서버 도구입니다. 타입 이름에는 버전 접미사가 붙으며, 생성자가 자동으로 `name`/`type`을 설정합니다. 모두 `ToolUnion`으로 암시적 변환됩니다.

```csharp
Tools = [
    new WebSearchTool20260209(),
    new ToolBash20250124(),
    new ToolTextEditor20250728(),
    new CodeExecutionTool20260120(),
],
```

추가 사용 가능: `WebFetchTool20260209`, `MemoryTool20250818`. `WebSearchTool20260209` 선택 옵션: `AllowedDomains`, `BlockedDomains`, `MaxUses`, `UserLocation`.

---

## 파일 API (베타)

파일은 `client.Beta.Files` (네임스페이스 `Anthropic.Models.Beta.Files`) 아래에 있습니다. `BinaryContent`는 `Stream` 및 `byte[]`로부터 암시적 변환됩니다.

```csharp
using Anthropic.Models.Beta.Files;
using Anthropic.Models.Beta.Messages;

FileMetadata meta = await client.Beta.Files.Upload(
    new FileUploadParams { File = File.OpenRead("doc.pdf") });

// Referencing the uploaded file requires Beta message types:
new BetaRequestDocumentBlock {
    Source = new BetaFileDocumentSource { FileID = meta.ID },
}
```

비베타 `DocumentBlockParamSource` 유니온에는 파일 ID 변형이 없습니다 — 파일 참조에는 `client.Beta.Messages.Create()`가 필요합니다.
