# Files API — TypeScript

Files API는 Messages API 요청에서 사용할 파일을 업로드합니다. 콘텐츠 블록에서 `file_id`를 참조하여 여러 API 호출에 걸쳐 파일을 다시 업로드하지 않아도 됩니다.

**베타:** API 호출 시 `betas: ["files-api-2025-04-14"]`를 전달하세요 (SDK가 필요한 헤더를 자동으로 설정합니다).

## 주요 사항

- 최대 파일 크기: 500 MB
- 총 저장 용량: 조직당 100 GB
- 파일은 삭제할 때까지 유지됨
- 파일 작업(업로드, 목록 조회, 삭제)은 무료이며, 메시지에서 사용된 콘텐츠는 입력 토큰으로 과금
- Amazon Bedrock 또는 Google Vertex AI에서는 사용 불가

---

## 파일 업로드

```typescript
import Anthropic, { toFile } from "@anthropic-ai/sdk";
import fs from "fs";

const client = new Anthropic();

const uploaded = await client.beta.files.upload({
  file: await toFile(fs.createReadStream("report.pdf"), undefined, {
    type: "application/pdf",
  }),
  betas: ["files-api-2025-04-14"],
});

console.log(`File ID: ${uploaded.id}`);
console.log(`Size: ${uploaded.size_bytes} bytes`);
```

---

## 메시지에서 파일 사용

### PDF / 텍스트 문서

```typescript
const response = await client.beta.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 16000,
  messages: [
    {
      role: "user",
      content: [
        { type: "text", text: "Summarize the key findings in this report." },
        {
          type: "document",
          source: { type: "file", file_id: uploaded.id },
          title: "Q4 Report",
          citations: { enabled: true },
        },
      ],
    },
  ],
  betas: ["files-api-2025-04-14"],
});

console.log(response.content[0].text);
```

---

## 파일 관리

### 파일 목록 조회

```typescript
const files = await client.beta.files.list({
  betas: ["files-api-2025-04-14"],
});
for (const f of files.data) {
  console.log(`${f.id}: ${f.filename} (${f.size_bytes} bytes)`);
}
```

### 파일 삭제

```typescript
await client.beta.files.delete("file_011CNha8iCJcU1wXNR6q4V8w", {
  betas: ["files-api-2025-04-14"],
});
```

### 파일 다운로드

```typescript
const response = await client.beta.files.download(
  "file_011CNha8iCJcU1wXNR6q4V8w",
  { betas: ["files-api-2025-04-14"] },
);
const content = Buffer.from(await response.arrayBuffer());
await fs.promises.writeFile("output.txt", content);
```
