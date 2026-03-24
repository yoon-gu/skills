# Claude API — Java

> **참고:** Java SDK는 Claude API와 어노테이션 클래스를 사용한 베타 도구 사용을 지원합니다. Agent SDK는 아직 Java에서 사용할 수 없습니다.

## 설치

Maven:

```xml
<dependency>
    <groupId>com.anthropic</groupId>
    <artifactId>anthropic-java</artifactId>
    <version>2.16.1</version>
</dependency>
```

Gradle:

```groovy
implementation("com.anthropic:anthropic-java:2.16.1")
```

## 클라이언트 초기화

```java
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;

// Default (reads ANTHROPIC_API_KEY from environment)
AnthropicClient client = AnthropicOkHttpClient.fromEnv();

// Explicit API key
AnthropicClient client = AnthropicOkHttpClient.builder()
    .apiKey("your-api-key")
    .build();
```

---

## 기본 메시지 요청

```java
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.Message;
import com.anthropic.models.messages.Model;

MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_4_6)
    .maxTokens(16000L)
    .addUserMessage("What is the capital of France?")
    .build();

Message response = client.messages().create(params);
response.content().stream()
    .flatMap(block -> block.text().stream())
    .forEach(textBlock -> System.out.println(textBlock.text()));
```

---

## 스트리밍

```java
import com.anthropic.core.http.StreamResponse;
import com.anthropic.models.messages.RawMessageStreamEvent;

MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_4_6)
    .maxTokens(64000L)
    .addUserMessage("Write a haiku")
    .build();

try (StreamResponse<RawMessageStreamEvent> streamResponse = client.messages().createStreaming(params)) {
    streamResponse.stream()
        .flatMap(event -> event.contentBlockDelta().stream())
        .flatMap(deltaEvent -> deltaEvent.delta().text().stream())
        .forEach(textDelta -> System.out.print(textDelta.text()));
}
```

---

## 사고(Thinking)

**적응형 사고(Adaptive thinking)는 Claude 4.6+ 모델에 권장되는 모드입니다.** Claude가 언제, 얼마나 사고할지를 동적으로 결정합니다. 빌더에는 직접적인 `.thinking(ThinkingConfigAdaptive)` 오버로드가 있어 수동 유니온 래핑이 필요 없습니다.

```java
import com.anthropic.models.messages.ContentBlock;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.Model;
import com.anthropic.models.messages.ThinkingConfigAdaptive;

MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_SONNET_4_6)
    .maxTokens(16000L)
    .thinking(ThinkingConfigAdaptive.builder().build())
    .addUserMessage("Solve this step by step: 27 * 453")
    .build();

for (ContentBlock block : client.messages().create(params).content()) {
    block.thinking().ifPresent(t -> System.out.println("[thinking] " + t.thinking()));
    block.text().ifPresent(t -> System.out.println(t.text()));
}
```

> **지원 중단(Deprecated):** `ThinkingConfigEnabled.builder().budgetTokens(N)` (및 `.enabledThinking(N)` 단축 메서드)은 Claude 4.6에서 여전히 작동하지만 지원 중단되었습니다. 위의 적응형 사고를 사용하세요.

`ContentBlock` 타입 축소: `.thinking()` / `.text()`는 `Optional<T>`를 반환합니다 — `.ifPresent(...)` 또는 `.stream().flatMap(...)`을 사용하세요. 대안: `isThinking()` / `asThinking()` boolean+unwrap 쌍 (잘못된 변형에서 예외 발생).

---

## 도구 사용 (베타)

Java SDK는 어노테이션 클래스를 사용한 베타 도구 사용을 지원합니다. 도구 클래스는 `BetaToolRunner`를 통한 자동 실행을 위해 `Supplier<String>`을 구현합니다.

### 도구 실행기 (자동 루프)

```java
import com.anthropic.models.beta.messages.MessageCreateParams;
import com.anthropic.models.beta.messages.BetaMessage;
import com.anthropic.helpers.BetaToolRunner;
import com.fasterxml.jackson.annotation.JsonClassDescription;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import java.util.function.Supplier;

@JsonClassDescription("Get the weather in a given location")
static class GetWeather implements Supplier<String> {
    @JsonPropertyDescription("The city and state, e.g. San Francisco, CA")
    public String location;

    @Override
    public String get() {
        return "The weather in " + location + " is sunny and 72°F";
    }
}

BetaToolRunner toolRunner = client.beta().messages().toolRunner(
    MessageCreateParams.builder()
        .model("claude-opus-4-6")
        .maxTokens(16000L)
        .putAdditionalHeader("anthropic-beta", "structured-outputs-2025-11-13")
        .addTool(GetWeather.class)
        .addUserMessage("What's the weather in San Francisco?")
        .build());

for (BetaMessage message : toolRunner) {
    System.out.println(message);
}
```

### 메모리 도구

Java SDK는 메모리 도구 백엔드를 구현하기 위한 `BetaMemoryToolHandler`를 제공합니다. 파일 저장소를 관리하는 핸들러를 제공하면 `BetaToolRunner`가 메모리 도구 호출을 자동으로 처리합니다.

```java
import com.anthropic.helpers.BetaMemoryToolHandler;
import com.anthropic.helpers.BetaToolRunner;
import com.anthropic.models.beta.messages.BetaMemoryTool20250818;
import com.anthropic.models.beta.messages.BetaMessage;
import com.anthropic.models.beta.messages.MessageCreateParams;
import com.anthropic.models.beta.messages.ToolRunnerCreateParams;

// Implement BetaMemoryToolHandler with your storage backend (e.g., filesystem)
BetaMemoryToolHandler memoryHandler = new FileSystemMemoryToolHandler(sandboxRoot);

MessageCreateParams createParams = MessageCreateParams.builder()
    .model("claude-opus-4-6")
    .maxTokens(4096L)
    .addTool(BetaMemoryTool20250818.builder().build())
    .addUserMessage("Remember that my favorite color is blue")
    .build();

BetaToolRunner toolRunner = client.beta().messages().toolRunner(
    ToolRunnerCreateParams.builder()
        .betaMemoryToolHandler(memoryHandler)
        .initialMessageParams(createParams)
        .build());

for (BetaMessage message : toolRunner) {
    System.out.println(message);
}
```

메모리 도구에 대한 자세한 내용은 [공유 메모리 도구 개념](../shared/tool-use-concepts.md)을 참조하세요.

### 비베타 도구 선언 (수동 JSON 스키마)

`Tool.InputSchema.Properties`는 자유 형식 `Map<String, JsonValue>` 래퍼입니다 — `putAdditionalProperty`를 통해 속성 스키마를 구성합니다. `type: "object"`가 기본값입니다. 빌더에는 `ToolUnion`으로 자동 래핑하는 직접적인 `.addTool(Tool)` 오버로드가 있습니다.

```java
import com.anthropic.core.JsonValue;
import com.anthropic.models.messages.Tool;

Tool tool = Tool.builder()
    .name("get_weather")
    .description("Get the current weather in a given location")
    .inputSchema(Tool.InputSchema.builder()
        .properties(Tool.InputSchema.Properties.builder()
            .putAdditionalProperty("location", JsonValue.from(Map.of("type", "string")))
            .build())
        .required(List.of("location"))
        .build())
    .build();

MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_SONNET_4_6)
    .maxTokens(16000L)
    .addTool(tool)
    .addUserMessage("Weather in Paris?")
    .build();
```

수동 도구 루프의 경우, 응답에서 `tool_use` 블록을 처리하고, `tool_result`를 다시 전송하며, `stop_reason`이 `"end_turn"`이 될 때까지 반복합니다. [공유 도구 사용 개념](../shared/tool-use-concepts.md)을 참조하세요.

### 콘텐츠 블록으로 `MessageParam` 구성 (도구 결과 왕복)

`MessageParam.Content`는 내부 유니온 클래스(string | list)입니다. 빌더의 `.contentOfBlockParams(List<ContentBlockParam>)` 별칭을 사용하세요 — 정적 `ofBlockParams`를 가진 별도의 `MessageParamContent` 클래스는 없습니다:

```java
import com.anthropic.models.messages.MessageParam;
import com.anthropic.models.messages.ContentBlockParam;
import com.anthropic.models.messages.ToolResultBlockParam;

List<ContentBlockParam> results = List.of(
    ContentBlockParam.ofToolResult(ToolResultBlockParam.builder()
        .toolUseId(toolUseBlock.id())
        .content(yourResultString)
        .build())
);

MessageParam toolResultMsg = MessageParam.builder()
    .role(MessageParam.Role.USER)
    .contentOfBlockParams(results)   // builder alias for Content.ofBlockParams(...)
    .build();
```

---

## 노력(Effort) 매개변수

Effort는 `OutputConfig` 내부에 중첩되어 있습니다 — `MessageCreateParams.Builder`에 직접적인 `.effort()`는 없습니다.

```java
import com.anthropic.models.messages.OutputConfig;

.outputConfig(OutputConfig.builder()
    .effort(OutputConfig.Effort.HIGH)  // or LOW, MEDIUM, MAX
    .build())
```

비용-품질 제어를 위해 `Thinking = ThinkingConfigAdaptive`와 함께 사용합니다.

---

## 프롬프트 캐싱

시스템 메시지를 `CacheControlEphemeral`이 포함된 `TextBlockParam` 목록으로 작성합니다. `.systemOfTextBlockParams(...)`를 사용하세요 — 일반 `.system(String)` 오버로드는 캐시 제어를 전달할 수 없습니다.

```java
import com.anthropic.models.messages.TextBlockParam;
import com.anthropic.models.messages.CacheControlEphemeral;

.systemOfTextBlockParams(List.of(
    TextBlockParam.builder()
        .text(longSystemPrompt)
        .cacheControl(CacheControlEphemeral.builder()
            .ttl(CacheControlEphemeral.Ttl.TTL_1H)  // optional; also TTL_5M
            .build())
        .build()))
```

`MessageCreateParams.Builder`와 `Tool.builder()`에도 최상위 `.cacheControl(CacheControlEphemeral)`이 있습니다.

---

## 토큰 카운팅

```java
import com.anthropic.models.messages.MessageCountTokensParams;

long tokens = client.messages().countTokens(
    MessageCountTokensParams.builder()
        .model(Model.CLAUDE_SONNET_4_6)
        .addUserMessage("Hello")
        .build()
).inputTokens();
```

---

## 구조화된 출력

클래스 기반 오버로드는 POJO에서 JSON 스키마를 자동으로 도출하고 타입이 지정된 `.text()` 반환값을 제공합니다 — 수동 스키마나 수동 파싱이 필요 없습니다.

```java
import com.anthropic.models.messages.StructuredMessageCreateParams;

record Book(String title, String author) {}
record BookList(List<Book> books) {}

StructuredMessageCreateParams<BookList> params = MessageCreateParams.builder()
    .model(Model.CLAUDE_SONNET_4_6)
    .maxTokens(16000L)
    .outputConfig(BookList.class)  // returns a typed builder
    .addUserMessage("List 3 classic novels")
    .build();

client.messages().create(params).content().stream()
    .flatMap(cb -> cb.text().stream())
    .forEach(typed -> {
        // typed.text() returns BookList, not String
        for (Book b : typed.text().books()) System.out.println(b.title());
    });
```

Jackson 어노테이션 지원: `@JsonPropertyDescription`, `@JsonIgnore`, `@ArraySchema(minItems=...)`. 수동 스키마 경로: `OutputConfig.builder().format(JsonOutputFormat.builder().schema(...).build())`.

---

## PDF / 문서 입력

`DocumentBlockParam` 빌더에는 소스 단축 메서드가 있습니다. `ContentBlockParam.ofDocument()`로 래핑하고 `.addUserMessageOfBlockParams()`를 통해 전달합니다.

```java
import com.anthropic.models.messages.DocumentBlockParam;
import com.anthropic.models.messages.ContentBlockParam;
import com.anthropic.models.messages.TextBlockParam;

DocumentBlockParam doc = DocumentBlockParam.builder()
    .base64Source(base64String)  // or .urlSource("https://...") or .textSource("...")
    .title("My Document")        // optional
    .build();

.addUserMessageOfBlockParams(List.of(
    ContentBlockParam.ofDocument(doc),
    ContentBlockParam.ofText(TextBlockParam.builder().text("Summarize this").build())))
```

---

## 서버 측 도구

버전 접미사가 붙은 타입; `name`/`type`은 빌더에 의해 자동 설정됩니다. 모든 타입에 대해 직접적인 `.addTool()` 오버로드가 있어 수동 `ToolUnion` 래핑이 필요 없습니다.

```java
import com.anthropic.models.messages.WebSearchTool20260209;
import com.anthropic.models.messages.ToolBash20250124;
import com.anthropic.models.messages.ToolTextEditor20250728;
import com.anthropic.models.messages.CodeExecutionTool20260120;

.addTool(WebSearchTool20260209.builder()
    .maxUses(5L)                              // optional
    .allowedDomains(List.of("example.com"))   // optional
    .build())
.addTool(ToolBash20250124.builder().build())
.addTool(ToolTextEditor20250728.builder().build())
.addTool(CodeExecutionTool20260120.builder().build())
```

다음도 사용 가능: `WebFetchTool20260209`, `MemoryTool20250818`, `ToolSearchToolBm25_20251119`.

### 베타 네임스페이스 (MCP, 압축)

베타 전용 기능에는 `com.anthropic.models.beta.messages.*`를 사용합니다 — 클래스 이름에 `Beta` 접두사가 있으며 beta 패키지에 위치합니다. 베타 `MessageCreateParams.Builder`에는 직접적인 `.addTool(BetaToolBash20250124)` 오버로드와 `.addMcpServer()`가 있습니다:

```java
import com.anthropic.models.beta.messages.MessageCreateParams;
import com.anthropic.models.beta.messages.BetaToolBash20250124;
import com.anthropic.models.beta.messages.BetaCodeExecutionTool20260120;
import com.anthropic.models.beta.messages.BetaRequestMcpServerUrlDefinition;

MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_4_6)
    .maxTokens(16000L)
    .addBeta("mcp-client-2025-11-20")
    .addTool(BetaToolBash20250124.builder().build())
    .addTool(BetaCodeExecutionTool20260120.builder().build())
    .addMcpServer(BetaRequestMcpServerUrlDefinition.builder()
        .name("my-server")
        .url("https://example.com/mcp")
        .build())
    .addUserMessage("...")
    .build();

client.beta().messages().create(params);
```

`BetaTool*` 타입은 비베타 `Tool*`과 호환되지 않습니다 — 요청당 하나의 네임스페이스를 선택하세요.

**응답에서 서버 도구 블록 읽기:** `ServerToolUseBlock`에는 `.id()`, `.name()` (enum), 그리고 원시 `JsonValue`를 반환하는 `._input()`이 있습니다 — 타입이 지정된 `.input()`은 없습니다. 코드 실행 결과의 경우 두 단계를 언래핑합니다:

```java
for (ContentBlock block : response.content()) {
    block.serverToolUse().ifPresent(stu -> {
        System.out.println("tool: " + stu.name() + " input: " + stu._input());
    });
    block.codeExecutionToolResult().ifPresent(r -> {
        r.content().resultBlock().ifPresent(result -> {
            System.out.println("stdout: " + result.stdout());
            System.out.println("stderr: " + result.stderr());
            System.out.println("exit: " + result.returnCode());
        });
    });
}
```

---

## Files API (베타)

`client.beta().files()` 아래에 있습니다. 메시지에서 파일 참조는 베타 메시지 타입이 필요합니다 (비베타 `DocumentBlockParam.Source`에는 파일 ID 변형이 없습니다).

```java
import com.anthropic.models.beta.files.FileUploadParams;
import com.anthropic.models.beta.files.FileMetadata;
import com.anthropic.models.beta.messages.BetaRequestDocumentBlock;
import java.nio.file.Paths;

FileMetadata meta = client.beta().files().upload(
    FileUploadParams.builder()
        .file(Paths.get("/path/to/doc.pdf"))  // or .file(InputStream) or .file(byte[])
        .build());

// Reference in a beta message:
BetaRequestDocumentBlock doc = BetaRequestDocumentBlock.builder()
    .fileSource(meta.id())
    .build();
```

기타 메서드: `.list()`, `.delete(String fileId)`, `.download(String fileId)`, `.retrieveMetadata(String fileId)`.
