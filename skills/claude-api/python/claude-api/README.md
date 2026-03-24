# Claude API — Python

## 설치

```bash
pip install anthropic
```

## 클라이언트 초기화

```python
import anthropic

# Default (uses ANTHROPIC_API_KEY env var)
client = anthropic.Anthropic()

# Explicit API key
client = anthropic.Anthropic(api_key="your-api-key")

# Async client
async_client = anthropic.AsyncAnthropic()
```

---

## 기본 메시지 요청

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)
# response.content is a list of content block objects (TextBlock, ThinkingBlock,
# ToolUseBlock, ...). Check .type before accessing .text.
for block in response.content:
    if block.type == "text":
        print(block.text)
```

---

## 시스템 프롬프트

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    system="You are a helpful coding assistant. Always provide examples in Python.",
    messages=[{"role": "user", "content": "How do I read a JSON file?"}]
)
```

---

## 비전 (이미지)

### Base64

```python
import base64

with open("image.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_data
                }
            },
            {"type": "text", "text": "What's in this image?"}
        ]
    }]
)
```

### URL

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "url",
                    "url": "https://example.com/image.png"
                }
            },
            {"type": "text", "text": "Describe this image"}
        ]
    }]
)
```

---

## 프롬프트 캐싱

대규모 컨텍스트를 캐싱하여 비용을 절감합니다 (최대 90% 절감).

### 자동 캐싱 (권장)

최상위 `cache_control`을 사용하여 요청에서 마지막 캐싱 가능한 블록을 자동으로 캐싱합니다 — 개별 콘텐츠 블록에 주석을 달 필요가 없습니다:

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    cache_control={"type": "ephemeral"},  # auto-caches the last cacheable block
    system="You are an expert on this large document...",
    messages=[{"role": "user", "content": "Summarize the key points"}]
)
```

### 수동 캐시 제어

세밀한 제어를 위해 특정 콘텐츠 블록에 `cache_control`을 추가합니다:

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    system=[{
        "type": "text",
        "text": "You are an expert on this large document...",
        "cache_control": {"type": "ephemeral"}  # default TTL is 5 minutes
    }],
    messages=[{"role": "user", "content": "Summarize the key points"}]
)

# With explicit TTL (time-to-live)
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    system=[{
        "type": "text",
        "text": "You are an expert on this large document...",
        "cache_control": {"type": "ephemeral", "ttl": "1h"}  # 1 hour TTL
    }],
    messages=[{"role": "user", "content": "Summarize the key points"}]
)
```

---

## 확장 사고

> **Opus 4.6 및 Sonnet 4.6:** 적응형 사고를 사용합니다. `budget_tokens`는 Opus 4.6과 Sonnet 4.6 모두에서 더 이상 사용되지 않습니다.
> **이전 모델:** `thinking: {type: "enabled", budget_tokens: N}`을 사용합니다 (`max_tokens`보다 작아야 하며, 최소 1024).

```python
# Opus 4.6: adaptive thinking (recommended)
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},  # low | medium | high | max
    messages=[{"role": "user", "content": "Solve this step by step..."}]
)

# Access thinking and response
for block in response.content:
    if block.type == "thinking":
        print(f"Thinking: {block.thinking}")
    elif block.type == "text":
        print(f"Response: {block.text}")
```

---

## 오류 처리

```python
import anthropic

try:
    response = client.messages.create(...)
except anthropic.BadRequestError as e:
    print(f"Bad request: {e.message}")
except anthropic.AuthenticationError:
    print("Invalid API key")
except anthropic.PermissionDeniedError:
    print("API key lacks required permissions")
except anthropic.NotFoundError:
    print("Invalid model or endpoint")
except anthropic.RateLimitError as e:
    retry_after = int(e.response.headers.get("retry-after", "60"))
    print(f"Rate limited. Retry after {retry_after}s.")
except anthropic.APIStatusError as e:
    if e.status_code >= 500:
        print(f"Server error ({e.status_code}). Retry later.")
    else:
        print(f"API error: {e.message}")
except anthropic.APIConnectionError:
    print("Network error. Check internet connection.")
```

---

## 멀티턴 대화

API는 상태를 유지하지 않습니다 — 매번 전체 대화 기록을 전송해야 합니다.

```python
class ConversationManager:
    """Manage multi-turn conversations with the Claude API."""

    def __init__(self, client: anthropic.Anthropic, model: str, system: str = None):
        self.client = client
        self.model = model
        self.system = system
        self.messages = []

    def send(self, user_message: str, **kwargs) -> str:
        """Send a message and get a response."""
        self.messages.append({"role": "user", "content": user_message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 16000),
            system=self.system,
            messages=self.messages,
            **kwargs
        )

        assistant_message = next(
            (b.text for b in response.content if b.type == "text"), ""
        )
        self.messages.append({"role": "assistant", "content": assistant_message})

        return assistant_message

# Usage
conversation = ConversationManager(
    client=anthropic.Anthropic(),
    model="claude-opus-4-6",
    system="You are a helpful assistant."
)

response1 = conversation.send("My name is Alice.")
response2 = conversation.send("What's my name?")  # Claude remembers "Alice"
```

**규칙:**

- 메시지는 `user`와 `assistant` 사이에서 교대로 전송되어야 합니다
- 첫 번째 메시지는 반드시 `user`여야 합니다

---

### 압축 (긴 대화)

> **베타, Opus 4.6 및 Sonnet 4.6.** 대화가 200K 컨텍스트 윈도우에 가까워지면, 압축이 이전 컨텍스트를 서버 측에서 자동으로 요약합니다. API는 `compaction` 블록을 반환합니다. 이후 요청에서 이를 다시 전달해야 합니다 — 텍스트만이 아닌 `response.content`를 추가하세요.

```python
import anthropic

client = anthropic.Anthropic()
messages = []

def chat(user_message: str) -> str:
    messages.append({"role": "user", "content": user_message})

    response = client.beta.messages.create(
        betas=["compact-2026-01-12"],
        model="claude-opus-4-6",
        max_tokens=16000,
        messages=messages,
        context_management={
            "edits": [{"type": "compact_20260112"}]
        }
    )

    # Append full content — compaction blocks must be preserved
    messages.append({"role": "assistant", "content": response.content})

    return next(block.text for block in response.content if block.type == "text")

# Compaction triggers automatically when context grows large
print(chat("Help me build a Python web scraper"))
print(chat("Add support for JavaScript-rendered pages"))
print(chat("Now add rate limiting and error handling"))
```

---

## 중단 이유

응답의 `stop_reason` 필드는 모델이 생성을 중단한 이유를 나타냅니다:

| 값 | 의미 |
|-------|---------|
| `end_turn` | Claude가 자연스럽게 응답을 완료했습니다 |
| `max_tokens` | `max_tokens` 제한에 도달했습니다 — 값을 늘리거나 스트리밍을 사용하세요 |
| `stop_sequence` | 사용자 지정 중단 시퀀스에 도달했습니다 |
| `tool_use` | Claude가 도구를 호출하려 합니다 — 실행 후 계속하세요 |
| `pause_turn` | 모델이 일시 중지되었으며 재개할 수 있습니다 (에이전트 흐름) |
| `refusal` | Claude가 안전상의 이유로 거부했습니다 — 출력이 스키마와 일치하지 않을 수 있습니다 |

---

## 비용 최적화 전략

### 1. 반복되는 컨텍스트에 프롬프트 캐싱 사용

```python
# Automatic caching (simplest — caches the last cacheable block)
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    cache_control={"type": "ephemeral"},
    system=large_document_text,  # e.g., 50KB of context
    messages=[{"role": "user", "content": "Summarize the key points"}]
)

# First request: full cost
# Subsequent requests: ~90% cheaper for cached portion
```

### 2. 적절한 모델 선택

```python
# Default to Opus for most tasks
response = client.messages.create(
    model="claude-opus-4-6",  # $5.00/$25.00 per 1M tokens
    max_tokens=16000,
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)

# Use Sonnet for high-volume production workloads
standard_response = client.messages.create(
    model="claude-sonnet-4-6",  # $3.00/$15.00 per 1M tokens
    max_tokens=16000,
    messages=[{"role": "user", "content": "Summarize this document"}]
)

# Use Haiku only for simple, speed-critical tasks
simple_response = client.messages.create(
    model="claude-haiku-4-5",  # $1.00/$5.00 per 1M tokens
    max_tokens=256,
    messages=[{"role": "user", "content": "Classify this as positive or negative"}]
)
```

### 3. 요청 전 토큰 수 계산

```python
count_response = client.messages.count_tokens(
    model="claude-opus-4-6",
    messages=messages,
    system=system
)

estimated_input_cost = count_response.input_tokens * 0.000005  # $5/1M tokens
print(f"Estimated input cost: ${estimated_input_cost:.4f}")
```

---

## 지수 백오프를 사용한 재시도

> **참고:** Anthropic SDK는 속도 제한(429) 및 서버 오류(5xx)에 대해 자동으로 지수 백오프로 재시도합니다. `max_retries`(기본값: 2)로 설정할 수 있습니다. SDK가 제공하는 것 이상의 동작이 필요한 경우에만 사용자 지정 재시도 로직을 구현하세요.

```python
import time
import random
import anthropic

def call_with_retry(
    client: anthropic.Anthropic,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    **kwargs
):
    """Call the API with exponential backoff retry."""
    last_exception = None

    for attempt in range(max_retries):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError as e:
            last_exception = e
        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                last_exception = e
            else:
                raise  # Client errors (4xx except 429) should not be retried

        delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
        print(f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s")
        time.sleep(delay)

    raise last_exception
```
