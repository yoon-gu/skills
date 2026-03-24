# 스트리밍 — Python

## 빠른 시작

```python
with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=64000,
    messages=[{"role": "user", "content": "Write a story"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### 비동기

```python
async with async_client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=64000,
    messages=[{"role": "user", "content": "Write a story"}]
) as stream:
    async for text in stream.text_stream:
        print(text, end="", flush=True)
```

---

## 다양한 콘텐츠 유형 처리

Claude는 텍스트, 사고 블록 또는 도구 사용을 반환할 수 있습니다. 각각을 적절하게 처리하세요:

> **Opus 4.6:** `thinking: {type: "adaptive"}`를 사용하세요. 이전 모델에서는 `thinking: {type: "enabled", budget_tokens: N}`을 대신 사용하세요.

```python
with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=64000,
    thinking={"type": "adaptive"},
    messages=[{"role": "user", "content": "Analyze this problem"}]
) as stream:
    for event in stream:
        if event.type == "content_block_start":
            if event.content_block.type == "thinking":
                print("\n[Thinking...]")
            elif event.content_block.type == "text":
                print("\n[Response:]")

        elif event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                print(event.delta.thinking, end="", flush=True)
            elif event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)
```

---

## 도구 사용과 함께 스트리밍

Python 도구 러너는 현재 완전한 메시지를 반환합니다. 도구와 함께 토큰 단위 스트리밍이 필요한 경우, 수동 루프 내에서 개별 API 호출에 스트리밍을 사용하세요:

```python
with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=64000,
    tools=tools,
    messages=messages
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    response = stream.get_final_message()
    # Continue with tool execution if response.stop_reason == "tool_use"
```

---

## 최종 메시지 가져오기

```python
with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=64000,
    messages=[{"role": "user", "content": "Hello"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    # Get full message after streaming
    final_message = stream.get_final_message()
    print(f"\n\nTokens used: {final_message.usage.output_tokens}")
```

---

## 진행 상태 업데이트와 함께 스트리밍

```python
def stream_with_progress(client, **kwargs):
    """Stream a response with progress updates."""
    total_tokens = 0
    content_parts = []

    with client.messages.stream(**kwargs) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    text = event.delta.text
                    content_parts.append(text)
                    print(text, end="", flush=True)

            elif event.type == "message_delta":
                if event.usage and event.usage.output_tokens is not None:
                    total_tokens = event.usage.output_tokens

        final_message = stream.get_final_message()

    print(f"\n\n[Tokens used: {total_tokens}]")
    return "".join(content_parts)
```

---

## 스트림에서의 오류 처리

```python
try:
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=64000,
        messages=[{"role": "user", "content": "Write a story"}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
except anthropic.APIConnectionError:
    print("\nConnection lost. Please retry.")
except anthropic.RateLimitError:
    print("\nRate limited. Please wait and retry.")
except anthropic.APIStatusError as e:
    print(f"\nAPI error: {e.status_code}")
```

---

## 스트림 이벤트 유형

| 이벤트 유형            | 설명                        | 발생 시점                          |
| --------------------- | --------------------------- | --------------------------------- |
| `message_start`       | 메시지 메타데이터 포함        | 시작 시 한 번                      |
| `content_block_start` | 새 콘텐츠 블록 시작           | 텍스트/도구 사용 블록이 시작될 때    |
| `content_block_delta` | 증분 콘텐츠 업데이트          | 각 토큰/청크마다                    |
| `content_block_stop`  | 콘텐츠 블록 완료              | 블록이 완료될 때                    |
| `message_delta`       | 메시지 수준 업데이트          | `stop_reason`, 사용량 정보 포함     |
| `message_stop`        | 메시지 완료                   | 끝에서 한 번                       |

## 모범 사례

1. **항상 출력을 플러시하세요** — 토큰을 즉시 표시하려면 `flush=True`를 사용하세요
2. **부분 응답을 처리하세요** — 스트림이 중단되면 불완전한 콘텐츠가 있을 수 있습니다
3. **토큰 사용량을 추적하세요** — `message_delta` 이벤트에 사용량 정보가 포함됩니다
4. **타임아웃을 설정하세요** — 애플리케이션에 적절한 타임아웃을 설정하세요
5. **스트리밍을 기본으로 사용하세요** — `.get_final_message()`를 사용하면 개별 이벤트를 처리하지 않아도 타임아웃 보호와 함께 완전한 응답을 받을 수 있습니다
