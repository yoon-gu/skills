# Message Batches API — TypeScript

Batches API (`POST /v1/messages/batches`)는 Messages API 요청을 표준 가격의 50%로 비동기적으로 처리합니다.

## 주요 사항

- 배치당 최대 100,000개의 요청 또는 256 MB
- 대부분의 배치는 1시간 이내에 완료되며, 최대 24시간 소요
- 결과는 생성 후 29일간 조회 가능
- 모든 토큰 사용에 대해 50% 비용 절감
- 모든 Messages API 기능 지원 (비전, 도구, 캐싱 등)

---

## 배치 생성

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const messageBatch = await client.messages.batches.create({
  requests: [
    {
      custom_id: "request-1",
      params: {
        model: "claude-opus-4-6",
        max_tokens: 16000,
        messages: [
          { role: "user", content: "Summarize climate change impacts" },
        ],
      },
    },
    {
      custom_id: "request-2",
      params: {
        model: "claude-opus-4-6",
        max_tokens: 16000,
        messages: [
          { role: "user", content: "Explain quantum computing basics" },
        ],
      },
    },
  ],
});

console.log(`Batch ID: ${messageBatch.id}`);
console.log(`Status: ${messageBatch.processing_status}`);
```

---

## 완료 폴링

```typescript
let batch;
while (true) {
  batch = await client.messages.batches.retrieve(messageBatch.id);
  if (batch.processing_status === "ended") break;
  console.log(
    `Status: ${batch.processing_status}, processing: ${batch.request_counts.processing}`,
  );
  await new Promise((resolve) => setTimeout(resolve, 60_000));
}

console.log("Batch complete!");
console.log(`Succeeded: ${batch.request_counts.succeeded}`);
console.log(`Errored: ${batch.request_counts.errored}`);
```

---

## 결과 조회

```typescript
for await (const result of await client.messages.batches.results(
  messageBatch.id,
)) {
  switch (result.result.type) {
    case "succeeded":
      console.log(
        `[${result.custom_id}] ${result.result.message.content[0].text.slice(0, 100)}`,
      );
      break;
    case "errored":
      if (result.result.error.type === "invalid_request") {
        console.log(`[${result.custom_id}] Validation error - fix and retry`);
      } else {
        console.log(`[${result.custom_id}] Server error - safe to retry`);
      }
      break;
    case "expired":
      console.log(`[${result.custom_id}] Expired - resubmit`);
      break;
  }
}
```

---

## 배치 취소

```typescript
const cancelled = await client.messages.batches.cancel(messageBatch.id);
console.log(`Status: ${cancelled.processing_status}`); // "canceling"
```
