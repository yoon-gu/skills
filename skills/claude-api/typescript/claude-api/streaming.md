# 스트리밍 — TypeScript

## 빠른 시작

```typescript
const stream = client.messages.stream({
  model: "claude-opus-4-6",
  max_tokens: 64000,
  messages: [{ role: "user", content: "Write a story" }],
});

for await (const event of stream) {
  if (
    event.type === "content_block_delta" &&
    event.delta.type === "text_delta"
  ) {
    process.stdout.write(event.delta.text);
  }
}
```

---

## 다양한 콘텐츠 타입 처리

> **Opus 4.6:** `thinking: {type: "adaptive"}`를 사용합니다. 이전 모델에서는 `thinking: {type: "enabled", budget_tokens: N}`을 대신 사용하세요.

```typescript
const stream = client.messages.stream({
  model: "claude-opus-4-6",
  max_tokens: 64000,
  thinking: { type: "adaptive" },
  messages: [{ role: "user", content: "Analyze this problem" }],
});

for await (const event of stream) {
  switch (event.type) {
    case "content_block_start":
      switch (event.content_block.type) {
        case "thinking":
          console.log("\n[Thinking...]");
          break;
        case "text":
          console.log("\n[Response:]");
          break;
      }
      break;
    case "content_block_delta":
      switch (event.delta.type) {
        case "thinking_delta":
          process.stdout.write(event.delta.thinking);
          break;
        case "text_delta":
          process.stdout.write(event.delta.text);
          break;
      }
      break;
  }
}
```

---

## 도구 사용과 스트리밍 (Tool Runner)

`stream: true`와 함께 Tool Runner를 사용합니다. 외부 루프는 Tool Runner 반복(메시지)을 순회하고, 내부 루프는 스트림 이벤트를 처리합니다:

```typescript
import Anthropic from "@anthropic-ai/sdk";
import { betaZodTool } from "@anthropic-ai/sdk/helpers/beta/zod";
import { z } from "zod";

const client = new Anthropic();

const getWeather = betaZodTool({
  name: "get_weather",
  description: "Get current weather for a location",
  inputSchema: z.object({
    location: z.string().describe("City and state, e.g., San Francisco, CA"),
  }),
  run: async ({ location }) => `72°F and sunny in ${location}`,
});

const runner = client.beta.messages.toolRunner({
  model: "claude-opus-4-6",
  max_tokens: 64000,
  tools: [getWeather],
  messages: [
    { role: "user", content: "What's the weather in Paris and London?" },
  ],
  stream: true,
});

// Outer loop: each tool runner iteration
for await (const messageStream of runner) {
  // Inner loop: stream events for this iteration
  for await (const event of messageStream) {
    switch (event.type) {
      case "content_block_delta":
        switch (event.delta.type) {
          case "text_delta":
            process.stdout.write(event.delta.text);
            break;
          case "input_json_delta":
            // Tool input being streamed
            break;
        }
        break;
    }
  }
}
```

---

## 최종 메시지 가져오기

```typescript
const stream = client.messages.stream({
  model: "claude-opus-4-6",
  max_tokens: 64000,
  messages: [{ role: "user", content: "Hello" }],
});

for await (const event of stream) {
  // Process events...
}

const finalMessage = await stream.finalMessage();
console.log(`Tokens used: ${finalMessage.usage.output_tokens}`);
```

---

## 스트림 이벤트 타입

| 이벤트 타입           | 설명                        | 발생 시점                          |
| --------------------- | --------------------------- | --------------------------------- |
| `message_start`       | 메시지 메타데이터 포함        | 시작 시 한 번                      |
| `content_block_start` | 새 콘텐츠 블록 시작           | text/tool_use 블록이 시작될 때      |
| `content_block_delta` | 증분 콘텐츠 업데이트          | 각 토큰/청크마다                    |
| `content_block_stop`  | 콘텐츠 블록 완료              | 블록이 완료될 때                    |
| `message_delta`       | 메시지 수준 업데이트          | `stop_reason`, 사용량 정보 포함     |
| `message_stop`        | 메시지 완료                  | 끝에서 한 번                       |

## 모범 사례

1. **항상 출력을 플러시하세요** -- 즉시 표시하려면 `process.stdout.write()`를 사용하세요
2. **부분 응답을 처리하세요** -- 스트림이 중단되면 불완전한 콘텐츠가 있을 수 있습니다
3. **토큰 사용량을 추적하세요** -- `message_delta` 이벤트에 사용량 정보가 포함됩니다
4. **`finalMessage()`를 사용하세요** -- 스트리밍 중에도 완전한 `Anthropic.Message` 객체를 가져옵니다. `.on()` 이벤트를 `new Promise()`로 감싸지 마세요 -- `finalMessage()`가 모든 완료/오류/중단 상태를 내부적으로 처리합니다
5. **웹 UI에서는 버퍼링하세요** -- 과도한 DOM 업데이트를 피하기 위해 렌더링 전에 몇 개의 토큰을 버퍼링하는 것을 고려하세요
6. **델타에는 `stream.on("text", ...)`를 사용하세요** -- `text` 이벤트는 델타 문자열만 제공하므로 `content_block_delta` 이벤트를 수동으로 필터링하는 것보다 간단합니다
7. **스트리밍이 있는 에이전트 루프의 경우** -- 도구 사용 루프와 `stream()` + `finalMessage()`를 결합하는 방법은 tool-use.md의 [스트리밍 수동 루프](./tool-use.md#streaming-manual-loop) 섹션을 참조하세요

## Raw SSE 형식

SDK가 아닌 Raw HTTP를 사용하는 경우, 스트림은 Server-Sent Events를 반환합니다:

```
event: message_start
data: {"type":"message_start","message":{"id":"msg_...","type":"message",...}}

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Hello"}}

event: content_block_stop
data: {"type":"content_block_stop","index":0}

event: message_delta
data: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":12}}

event: message_stop
data: {"type":"message_stop"}
```
