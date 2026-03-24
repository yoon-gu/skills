# Claude API — TypeScript

## 설치

```bash
npm install @anthropic-ai/sdk
```

## 클라이언트 초기화

```typescript
import Anthropic from "@anthropic-ai/sdk";

// Default (uses ANTHROPIC_API_KEY env var)
const client = new Anthropic();

// Explicit API key
const client = new Anthropic({ apiKey: "your-api-key" });
```

---

## 기본 메시지 요청

```typescript
const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 16000,
  messages: [{ role: "user", content: "What is the capital of France?" }],
});
// response.content is ContentBlock[] — a discriminated union. Narrow by .type
// before accessing .text (TypeScript will error on content[0].text without this).
for (const block of response.content) {
  if (block.type === "text") {
    console.log(block.text);
  }
}
```

---

## 시스템 프롬프트

```typescript
const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 16000,
  system:
    "You are a helpful coding assistant. Always provide examples in Python.",
  messages: [{ role: "user", content: "How do I read a JSON file?" }],
});
```

---

## 비전 (이미지)

### URL

```typescript
const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 16000,
  messages: [
    {
      role: "user",
      content: [
        {
          type: "image",
          source: { type: "url", url: "https://example.com/image.png" },
        },
        { type: "text", text: "Describe this image" },
      ],
    },
  ],
});
```

### Base64

```typescript
import fs from "fs";

const imageData = fs.readFileSync("image.png").toString("base64");

const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 16000,
  messages: [
    {
      role: "user",
      content: [
        {
          type: "image",
          source: { type: "base64", media_type: "image/png", data: imageData },
        },
        { type: "text", text: "What's in this image?" },
      ],
    },
  ],
});
```

---

## 프롬프트 캐싱

### 자동 캐싱 (권장)

최상위 `cache_control`을 사용하여 요청의 마지막 캐시 가능한 블록을 자동으로 캐싱합니다:

```typescript
const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 16000,
  cache_control: { type: "ephemeral" }, // auto-caches the last cacheable block
  system: "You are an expert on this large document...",
  messages: [{ role: "user", content: "Summarize the key points" }],
});
```

### 수동 캐시 제어

세밀한 제어가 필요한 경우, 특정 콘텐츠 블록에 `cache_control`을 추가합니다:

```typescript
const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 16000,
  system: [
    {
      type: "text",
      text: "You are an expert on this large document...",
      cache_control: { type: "ephemeral" }, // default TTL is 5 minutes
    },
  ],
  messages: [{ role: "user", content: "Summarize the key points" }],
});

// With explicit TTL (time-to-live)
const response2 = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 16000,
  system: [
    {
      type: "text",
      text: "You are an expert on this large document...",
      cache_control: { type: "ephemeral", ttl: "1h" }, // 1 hour TTL
    },
  ],
  messages: [{ role: "user", content: "Summarize the key points" }],
});
```

---

## 확장 사고

> **Opus 4.6 및 Sonnet 4.6:** 적응형 사고를 사용합니다. `budget_tokens`는 Opus 4.6과 Sonnet 4.6 모두에서 더 이상 사용되지 않습니다.
> **이전 모델:** `thinking: {type: "enabled", budget_tokens: N}`을 사용합니다 (`max_tokens`보다 작아야 하며, 최소 1024).

```typescript
// Opus 4.6: adaptive thinking (recommended)
const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 16000,
  thinking: { type: "adaptive" },
  output_config: { effort: "high" }, // low | medium | high | max
  messages: [
    { role: "user", content: "Solve this math problem step by step..." },
  ],
});

for (const block of response.content) {
  if (block.type === "thinking") {
    console.log("Thinking:", block.thinking);
  } else if (block.type === "text") {
    console.log("Response:", block.text);
  }
}
```

---

## 오류 처리

SDK의 타입이 지정된 예외 클래스를 사용하세요 -- 문자열 매칭으로 오류 메시지를 확인하지 마세요:

```typescript
import Anthropic from "@anthropic-ai/sdk";

try {
  const response = await client.messages.create({...});
} catch (error) {
  if (error instanceof Anthropic.BadRequestError) {
    console.error("Bad request:", error.message);
  } else if (error instanceof Anthropic.AuthenticationError) {
    console.error("Invalid API key");
  } else if (error instanceof Anthropic.RateLimitError) {
    console.error("Rate limited - retry later");
  } else if (error instanceof Anthropic.APIError) {
    console.error(`API error ${error.status}:`, error.message);
  }
}
```

모든 클래스는 타입이 지정된 `status` 필드를 가진 `Anthropic.APIError`를 확장합니다. 가장 구체적인 것부터 가장 일반적인 것 순서로 확인하세요. 전체 오류 코드 참조는 [shared/error-codes.md](../../shared/error-codes.md)를 참조하세요.

---

## 다중 턴 대화

API는 상태를 유지하지 않으므로 매번 전체 대화 기록을 전송해야 합니다. 메시지 배열의 타입을 지정하려면 `Anthropic.MessageParam[]`을 사용하세요:

```typescript
const messages: Anthropic.MessageParam[] = [
  { role: "user", content: "My name is Alice." },
  { role: "assistant", content: "Hello Alice! Nice to meet you." },
  { role: "user", content: "What's my name?" },
];

const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 16000,
  messages: messages,
});
```

**규칙:**

- 동일한 역할의 연속 메시지가 허용됩니다 -- API가 이를 하나의 턴으로 결합합니다
- 첫 번째 메시지는 `user`여야 합니다
- 모든 API 데이터 구조에 SDK 타입(`Anthropic.MessageParam`, `Anthropic.Message`, `Anthropic.Tool` 등)을 사용하세요 -- 동일한 인터페이스를 다시 정의하지 마세요

---

### 압축 (긴 대화)

> **베타, Opus 4.6 및 Sonnet 4.6.** 대화가 200K 컨텍스트 윈도우에 가까워지면, 압축이 서버 측에서 이전 컨텍스트를 자동으로 요약합니다. API는 `compaction` 블록을 반환합니다. 이후 요청에서 이를 다시 전달해야 합니다 -- 텍스트만이 아닌 `response.content`를 추가하세요.

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();
const messages: Anthropic.Beta.BetaMessageParam[] = [];

async function chat(userMessage: string): Promise<string> {
  messages.push({ role: "user", content: userMessage });

  const response = await client.beta.messages.create({
    betas: ["compact-2026-01-12"],
    model: "claude-opus-4-6",
    max_tokens: 16000,
    messages,
    context_management: {
      edits: [{ type: "compact_20260112" }],
    },
  });

  // Append full content — compaction blocks must be preserved
  messages.push({ role: "assistant", content: response.content });

  const textBlock = response.content.find(
    (b): b is Anthropic.Beta.BetaTextBlock => b.type === "text",
  );
  return textBlock?.text ?? "";
}

// Compaction triggers automatically when context grows large
console.log(await chat("Help me build a Python web scraper"));
console.log(await chat("Add support for JavaScript-rendered pages"));
console.log(await chat("Now add rate limiting and error handling"));
```

---

## 중단 이유

응답의 `stop_reason` 필드는 모델이 생성을 중단한 이유를 나타냅니다:

| 값              | 의미                                                            |
| --------------- | --------------------------------------------------------------- |
| `end_turn`      | Claude가 자연스럽게 응답을 완료함                                  |
| `max_tokens`    | `max_tokens` 제한에 도달함 -- 값을 늘리거나 스트리밍을 사용하세요     |
| `stop_sequence` | 사용자 정의 중단 시퀀스에 도달함                                    |
| `tool_use`      | Claude가 도구를 호출하려 함 -- 실행 후 계속 진행하세요               |
| `pause_turn`    | 모델이 일시 중지되었으며 재개 가능 (에이전트 플로우)                  |
| `refusal`       | Claude가 안전상의 이유로 거부함 -- 출력이 스키마와 일치하지 않을 수 있음 |

---

## 비용 최적화 전략

### 1. 반복되는 컨텍스트에 프롬프트 캐싱 사용

```typescript
// Automatic caching (simplest — caches the last cacheable block)
const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 16000,
  cache_control: { type: "ephemeral" },
  system: largeDocumentText, // e.g., 50KB of context
  messages: [{ role: "user", content: "Summarize the key points" }],
});

// First request: full cost
// Subsequent requests: ~90% cheaper for cached portion
```

### 2. 요청 전 토큰 수 카운팅 사용

```typescript
const countResponse = await client.messages.countTokens({
  model: "claude-opus-4-6",
  messages: messages,
  system: system,
});

const estimatedInputCost = countResponse.input_tokens * 0.000005; // $5/1M tokens
console.log(`Estimated input cost: $${estimatedInputCost.toFixed(4)}`);
```
