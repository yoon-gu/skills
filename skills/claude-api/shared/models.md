# Claude 모델 카탈로그

**이 파일에 나열된 정확한 모델 ID만 사용하세요.** 모델 ID를 추측하거나 임의로 만들지 마세요 — 잘못된 ID는 API 오류를 유발합니다. 가능한 경우 별칭을 사용하세요. 최신 정보는 `shared/live-sources.md`의 모델 개요 URL을 WebFetch하거나, 아래 프로그래밍 방식 모델 탐색을 참조하여 Models API를 직접 쿼리하세요.

## 프로그래밍 방식 모델 탐색

**실시간** 기능 데이터 — 컨텍스트 윈도우, 최대 출력 토큰, 기능 지원 (thinking, vision, effort, structured outputs 등) — 는 아래 캐시된 테이블에 의존하지 말고 Models API를 쿼리하세요. 사용자가 "X의 컨텍스트 윈도우는 얼마인가요", "모델 X가 vision/thinking/effort를 지원하나요", "어떤 모델이 기능 Y를 지원하나요"라고 묻거나, 런타임에 기능별로 모델을 선택하려는 경우 이 방법을 사용하세요.

```python
m = client.models.retrieve("claude-opus-4-6")
m.id                 # "claude-opus-4-6"
m.display_name       # "Claude Opus 4.6"
m.max_input_tokens   # context window (int)
m.max_tokens         # max output tokens (int)

# capabilities is an untyped nested dict — bracket access, check ["supported"] at the leaf
caps = m.capabilities
caps["image_input"]["supported"]                       # vision
caps["thinking"]["types"]["adaptive"]["supported"]     # adaptive thinking
caps["effort"]["max"]["supported"]                     # effort: max (also low/medium/high)
caps["structured_outputs"]["supported"]
caps["context_management"]["compact_20260112"]["supported"]

# filter across all models — iterate the page object directly (auto-paginates); do NOT use .data
[m for m in client.models.list()
 if m.capabilities["thinking"]["types"]["adaptive"]["supported"]
 and m.max_input_tokens >= 200_000]
```

최상위 필드 (`id`, `display_name`, `max_input_tokens`, `max_tokens`)는 타입이 지정된 속성입니다. `capabilities`는 dict이므로 속성 접근이 아닌 대괄호 접근을 사용하세요. API는 모든 모델에 대해 각 리프에 `supported: true/false`가 있는 전체 기능 트리를 반환하므로, `.get()` 가드 없이 대괄호 체인을 안전하게 사용할 수 있습니다. TypeScript SDK: 동일한 메서드 이름이며, 반복 시 자동 페이지네이션됩니다.

### Raw HTTP

```bash
curl https://api.anthropic.com/v1/models/claude-opus-4-6 \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

```json
{
  "id": "claude-opus-4-6",
  "display_name": "Claude Opus 4.6",
  "max_input_tokens": 1000000,
  "max_tokens": 128000,
  "capabilities": {
    "image_input": {"supported": true},
    "structured_outputs": {"supported": true},
    "thinking": {"supported": true, "types": {"enabled": {"supported": true}, "adaptive": {"supported": true}}},
    "effort": {"supported": true, "low": {"supported": true}, …, "max": {"supported": true}},
    …
  }
}
```

## 현재 모델 (권장)

| 모델명            | 별칭 (이것을 사용)  | 전체 ID                         | 컨텍스트        | 최대 출력  | 상태   |
|-------------------|---------------------|-------------------------------|----------------|------------|--------|
| Claude Opus 4.6   | `claude-opus-4-6`   | —                             | 200K (1M beta) | 128K       | Active |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | -                             | 200K (1M beta) | 64K        | Active |
| Claude Haiku 4.5  | `claude-haiku-4-5`  | `claude-haiku-4-5-20251001`   | 200K           | 64K        | Active |

### 모델 설명

- **Claude Opus 4.6** — 에이전트 구축과 코딩을 위한 가장 지능적인 모델입니다. 적응형 사고(권장)를 지원하며, 128K 최대 출력 토큰(대용량 출력 시 스트리밍 필요). `context-1m-2025-08-07` 헤더를 통해 1M 컨텍스트 윈도우를 베타로 사용 가능합니다.
- **Claude Sonnet 4.6** — 속도와 지능의 최적 조합 모델입니다. 적응형 사고(권장)를 지원합니다. `context-1m-2025-08-07` 헤더를 통해 1M 컨텍스트 윈도우를 베타로 사용 가능합니다. 64K 최대 출력 토큰.
- **Claude Haiku 4.5** — 간단한 작업을 위한 가장 빠르고 비용 효율적인 모델입니다.

## 레거시 모델 (여전히 활성)

| 모델명            | 별칭 (이것을 사용)  | 전체 ID                         | 상태   |
|-------------------|---------------------|-------------------------------|--------|
| Claude Opus 4.5   | `claude-opus-4-5`   | `claude-opus-4-5-20251101`    | Active |
| Claude Opus 4.1   | `claude-opus-4-1`   | `claude-opus-4-1-20250805`    | Active |
| Claude Sonnet 4.5 | `claude-sonnet-4-5` | `claude-sonnet-4-5-20250929`  | Active |
| Claude Sonnet 4   | `claude-sonnet-4-0` | `claude-sonnet-4-20250514`    | Active |
| Claude Opus 4     | `claude-opus-4-0`   | `claude-opus-4-20250514`      | Active |

## 지원 종료 예정 모델 (곧 폐지)

| 모델명            | 별칭 (이것을 사용)  | 전체 ID                         | 상태       | 폐지 예정    |
|-------------------|---------------------|-------------------------------|------------|--------------|
| Claude Haiku 3    | —                   | `claude-3-haiku-20240307`     | Deprecated | Apr 19, 2026 |

## 폐지된 모델 (더 이상 사용 불가)

| 모델명            | 전체 ID                         | 폐지일      |
|-------------------|-------------------------------|-------------|
| Claude Sonnet 3.7 | `claude-3-7-sonnet-20250219`  | Feb 19, 2026 |
| Claude Haiku 3.5  | `claude-3-5-haiku-20241022`   | Feb 19, 2026 |
| Claude Opus 3     | `claude-3-opus-20240229`      | Jan 5, 2026 |
| Claude Sonnet 3.5 | `claude-3-5-sonnet-20241022`  | Oct 28, 2025 |
| Claude Sonnet 3.5 | `claude-3-5-sonnet-20240620`  | Oct 28, 2025 |
| Claude Sonnet 3   | `claude-3-sonnet-20240229`    | Jul 21, 2025 |
| Claude 2.1        | `claude-2.1`                  | Jul 21, 2025 |
| Claude 2.0        | `claude-2.0`                  | Jul 21, 2025 |

## 사용자 요청 해석

사용자가 이름으로 모델을 요청할 때, 이 테이블을 사용하여 올바른 모델 ID를 찾으세요:

| 사용자 요청...                            | 사용할 모델 ID                 |
|-------------------------------------------|--------------------------------|
| "opus", "most powerful"                   | `claude-opus-4-6`              |
| "opus 4.6"                                | `claude-opus-4-6`              |
| "opus 4.5"                                | `claude-opus-4-5`              |
| "opus 4.1"                                | `claude-opus-4-1`              |
| "opus 4", "opus 4.0"                      | `claude-opus-4-0`              |
| "sonnet", "balanced"                      | `claude-sonnet-4-6`            |
| "sonnet 4.6"                              | `claude-sonnet-4-6`            |
| "sonnet 4.5"                              | `claude-sonnet-4-5`            |
| "sonnet 4", "sonnet 4.0"                  | `claude-sonnet-4-0`            |
| "sonnet 3.7"                              | 폐지됨 — `claude-sonnet-4-5` 권장 |
| "sonnet 3.5"                              | 폐지됨 — `claude-sonnet-4-5` 권장 |
| "haiku", "fast", "cheap"                  | `claude-haiku-4-5`             |
| "haiku 4.5"                               | `claude-haiku-4-5`             |
| "haiku 3.5"                               | 폐지됨 — `claude-haiku-4-5` 권장 |
| "haiku 3"                                 | 지원 종료 예정 — `claude-haiku-4-5` 권장 |
