# Files API — Python

Files API는 Messages API 요청에서 사용할 파일을 업로드합니다. 여러 API 호출에서 재업로드를 피하고 콘텐츠 블록에서 `file_id`로 파일을 참조합니다.

**베타:** API 호출에 `betas=["files-api-2025-04-14"]`를 전달하세요 (SDK가 필요한 헤더를 자동으로 설정합니다).

## 주요 사항

- 최대 파일 크기: 500 MB
- 총 저장 용량: 조직당 100 GB
- 파일은 삭제할 때까지 유지됩니다
- 파일 작업(업로드, 목록, 삭제)은 무료이며, 메시지에서 사용된 콘텐츠는 입력 토큰으로 과금됩니다
- Amazon Bedrock 또는 Google Vertex AI에서는 사용할 수 없습니다

---

## 파일 업로드

```python
import anthropic

client = anthropic.Anthropic()

uploaded = client.beta.files.upload(
    file=("report.pdf", open("report.pdf", "rb"), "application/pdf"),
)
print(f"File ID: {uploaded.id}")
print(f"Size: {uploaded.size_bytes} bytes")
```

---

## 메시지에서 파일 사용

### PDF / 텍스트 문서

```python
response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Summarize the key findings in this report."},
            {
                "type": "document",
                "source": {"type": "file", "file_id": uploaded.id},
                "title": "Q4 Report",           # optional
                "citations": {"enabled": True}   # optional, enables citations
            }
        ]
    }],
    betas=["files-api-2025-04-14"],
)
for block in response.content:
    if block.type == "text":
        print(block.text)
```

### 이미지

```python
image_file = client.beta.files.upload(
    file=("photo.png", open("photo.png", "rb"), "image/png"),
)

response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {
                "type": "image",
                "source": {"type": "file", "file_id": image_file.id}
            }
        ]
    }],
    betas=["files-api-2025-04-14"],
)
```

---

## 파일 관리

### 파일 목록 조회

```python
files = client.beta.files.list()
for f in files.data:
    print(f"{f.id}: {f.filename} ({f.size_bytes} bytes)")
```

### 파일 메타데이터 조회

```python
file_info = client.beta.files.retrieve_metadata("file_011CNha8iCJcU1wXNR6q4V8w")
print(f"Filename: {file_info.filename}")
print(f"MIME type: {file_info.mime_type}")
```

### 파일 삭제

```python
client.beta.files.delete("file_011CNha8iCJcU1wXNR6q4V8w")
```

### 파일 다운로드

코드 실행 도구나 스킬이 생성한 파일만 다운로드할 수 있습니다 (사용자가 업로드한 파일은 불가).

```python
file_content = client.beta.files.download("file_011CNha8iCJcU1wXNR6q4V8w")
file_content.write_to_file("output.txt")
```

---

## 전체 엔드투엔드 예제

문서를 한 번 업로드한 후 여러 질문을 합니다:

```python
import anthropic

client = anthropic.Anthropic()

# 1. Upload once
uploaded = client.beta.files.upload(
    file=("contract.pdf", open("contract.pdf", "rb"), "application/pdf"),
)
print(f"Uploaded: {uploaded.id}")

# 2. Ask multiple questions using the same file_id
questions = [
    "What are the key terms and conditions?",
    "What is the termination clause?",
    "Summarize the payment schedule.",
]

for question in questions:
    response = client.beta.messages.create(
        model="claude-opus-4-6",
        max_tokens=16000,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {
                    "type": "document",
                    "source": {"type": "file", "file_id": uploaded.id}
                }
            ]
        }],
        betas=["files-api-2025-04-14"],
    )
    print(f"\nQ: {question}")
    text = next((b.text for b in response.content if b.type == "text"), "")
    print(f"A: {text[:200]}")

# 3. Clean up when done
client.beta.files.delete(uploaded.id)
```
