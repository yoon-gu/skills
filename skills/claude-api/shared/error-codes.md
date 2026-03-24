# HTTP 오류 코드 참조

이 파일은 Claude API가 반환하는 HTTP 오류 코드, 일반적인 원인, 그리고 처리 방법을 문서화합니다. 언어별 오류 처리 예제는 `python/` 또는 `typescript/` 폴더를 참조하세요.

## 오류 코드 요약

| 코드 | 오류 유형                | 재시도 가능 | 일반적인 원인                        |
| ---- | ----------------------- | ---------- | ------------------------------------ |
| 400  | `invalid_request_error` | 아니오      | 잘못된 요청 형식 또는 매개변수        |
| 401  | `authentication_error`  | 아니오      | 유효하지 않거나 누락된 API 키         |
| 403  | `permission_error`      | 아니오      | API 키에 권한 없음                   |
| 404  | `not_found_error`       | 아니오      | 잘못된 엔드포인트 또는 모델 ID        |
| 413  | `request_too_large`     | 아니오      | 요청이 크기 제한 초과                 |
| 429  | `rate_limit_error`      | 예          | 너무 많은 요청                       |
| 500  | `api_error`             | 예          | Anthropic 서비스 문제                |
| 529  | `overloaded_error`      | 예          | API가 일시적으로 과부하 상태          |

## 상세 오류 정보

### 400 Bad Request

**원인:**

- 요청 본문의 잘못된 JSON 형식
- 필수 매개변수 누락 (`model`, `max_tokens`, `messages`)
- 잘못된 매개변수 타입 (예: 정수가 필요한 곳에 문자열)
- 빈 messages 배열
- user/assistant가 번갈아 나오지 않는 messages

**오류 예시:**

```json
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "messages: roles must alternate between \"user\" and \"assistant\""
  },
  "request_id": "req_011CSHoEeqs5C35K2UUqR7Fy"
}
```

**해결 방법:** 전송 전에 요청 구조를 검증하세요. 다음을 확인하세요:

- `model`이 유효한 모델 ID인지
- `max_tokens`가 양의 정수인지
- `messages` 배열이 비어 있지 않고 올바르게 번갈아 나오는지

---

### 401 Unauthorized

**원인:**

- `x-api-key` 헤더 또는 `Authorization` 헤더 누락
- 잘못된 API 키 형식
- 취소되었거나 삭제된 API 키

**해결 방법:** `ANTHROPIC_API_KEY` 환경 변수가 올바르게 설정되어 있는지 확인하세요.

---

### 403 Forbidden

**원인:**

- API 키가 요청한 모델에 대한 접근 권한이 없음
- 조직 수준의 제한
- 베타 접근 권한 없이 베타 기능에 접근 시도

**해결 방법:** Console에서 API 키 권한을 확인하세요. 다른 API 키가 필요하거나 특정 기능에 대한 접근 권한을 요청해야 할 수 있습니다.

---

### 404 Not Found

**원인:**

- 모델 ID 오타 (예: `claude-sonnet-4.6` 대신 `claude-sonnet-4-6`)
- 더 이상 사용되지 않는 모델 ID 사용
- 잘못된 API 엔드포인트

**해결 방법:** 모델 문서에서 정확한 모델 ID를 사용하세요. 별칭을 사용할 수 있습니다 (예: `claude-opus-4-6`).

---

### 413 Request Too Large

**원인:**

- 요청 본문이 최대 크기 초과
- 입력 토큰이 너무 많음
- 이미지 데이터가 너무 큼

**해결 방법:** 입력 크기를 줄이세요 — 대화 기록을 잘라내거나, 이미지를 압축/리사이즈하거나, 큰 문서를 청크로 분할하세요.

---

### 400 유효성 검사 오류

일부 400 오류는 매개변수 유효성 검사와 관련이 있습니다:

- `max_tokens`가 모델의 제한을 초과
- 잘못된 `temperature` 값 (0.0-1.0이어야 함)
- 확장된 사고에서 `budget_tokens` >= `max_tokens`
- 잘못된 도구 정의 스키마

**확장된 사고에서 흔한 실수:**

```
# Wrong: budget_tokens must be < max_tokens
thinking: budget_tokens=10000, max_tokens=1000  → Error!

# Correct
thinking: budget_tokens=10000, max_tokens=16000
```

---

### 429 속도 제한

**원인:**

- 분당 요청 수(RPM) 초과
- 분당 토큰 수(TPM) 초과
- 일당 토큰 수(TPD) 초과

**확인할 헤더:**

- `retry-after`: 재시도 전 대기할 초
- `x-ratelimit-limit-*`: 제한량
- `x-ratelimit-remaining-*`: 남은 할당량

**해결 방법:** Anthropic SDK는 429 및 5xx 오류를 지수 백오프로 자동 재시도합니다 (기본값: `max_retries=2`). 사용자 정의 재시도 동작은 언어별 오류 처리 예제를 참조하세요.

---

### 500 Internal Server Error

**원인:**

- 일시적인 Anthropic 서비스 문제
- API 처리 버그

**해결 방법:** 지수 백오프로 재시도하세요. 지속되면 [status.anthropic.com](https://status.anthropic.com)을 확인하세요.

---

### 529 Overloaded

**원인:**

- 높은 API 수요
- 서비스 용량 도달

**해결 방법:** 지수 백오프로 재시도하세요. 다른 모델 사용 (Haiku는 일반적으로 부하가 적음), 요청을 시간에 걸쳐 분산, 또는 요청 큐잉 구현을 고려하세요.

---

## 흔한 실수와 해결 방법

| 실수                            | 오류             | 해결 방법                                                    |
| ------------------------------- | ---------------- | ----------------------------------------------------------- |
| `budget_tokens` >= `max_tokens` | 400              | `budget_tokens` < `max_tokens`인지 확인                      |
| 모델 ID 오타                     | 404              | `claude-opus-4-6` 같은 유효한 모델 ID 사용                    |
| 첫 번째 메시지가 `assistant`     | 400              | 첫 번째 메시지는 `user`여야 함                                |
| 같은 역할의 연속 메시지           | 400              | `user`와 `assistant`를 번갈아 사용                            |
| 코드에 API 키 하드코딩           | 401 (키 유출)     | 환경 변수 사용                                               |
| 사용자 정의 재시도 필요           | 429/5xx          | SDK가 자동 재시도; `max_retries`로 사용자 정의                 |

## SDK의 타입 지정 예외

HTTP 오류 코드를 문자열 매칭으로 오류 메시지를 확인하는 대신 **항상 SDK의 타입 지정 예외 클래스를 사용하세요**. 각 HTTP 오류 코드는 특정 예외 클래스에 매핑됩니다:

| HTTP 코드 | TypeScript 클래스               | Python 클래스                     |
| --------- | --------------------------------- | --------------------------------- |
| 400       | `Anthropic.BadRequestError`       | `anthropic.BadRequestError`       |
| 401       | `Anthropic.AuthenticationError`   | `anthropic.AuthenticationError`   |
| 403       | `Anthropic.PermissionDeniedError` | `anthropic.PermissionDeniedError` |
| 404       | `Anthropic.NotFoundError`         | `anthropic.NotFoundError`         |
| 429       | `Anthropic.RateLimitError`        | `anthropic.RateLimitError`        |
| 500+      | `Anthropic.InternalServerError`   | `anthropic.InternalServerError`   |
| Any       | `Anthropic.APIError`              | `anthropic.APIError`              |

```typescript
// ✅ Correct: use typed exceptions
try {
  const response = await client.messages.create({...});
} catch (error) {
  if (error instanceof Anthropic.RateLimitError) {
    // Handle rate limiting
  } else if (error instanceof Anthropic.APIError) {
    console.error(`API error ${error.status}:`, error.message);
  }
}

// ❌ Wrong: don't check error messages with string matching
try {
  const response = await client.messages.create({...});
} catch (error) {
  const msg = error instanceof Error ? error.message : String(error);
  if (msg.includes("429") || msg.includes("rate_limit")) { ... }
}
```

모든 예외 클래스는 `status` 속성을 가진 `Anthropic.APIError`를 확장합니다. `instanceof` 검사를 가장 구체적인 것에서 가장 일반적인 것 순으로 사용하세요 (예: `APIError` 전에 `RateLimitError`를 확인).
