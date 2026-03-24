---
name: claude-api
description: "Build apps with the Claude API or Anthropic SDK. TRIGGER when: code imports `anthropic`/`@anthropic-ai/sdk`/`claude_agent_sdk`, or user asks to use Claude API, Anthropic SDKs, or Agent SDK. DO NOT TRIGGER when: code imports `openai`/other AI SDK, general programming, or ML/data-science tasks."
license: Complete terms in LICENSE.txt
---

# Claude로 LLM 기반 애플리케이션 구축하기

이 스킬은 Claude를 사용하여 LLM 기반 애플리케이션을 구축하는 데 도움을 줍니다. 필요에 따라 적절한 Surface를 선택하고, 프로젝트 언어를 감지한 다음, 해당 언어별 문서를 읽으세요.

## 기본값

사용자가 별도로 요청하지 않는 한:

Claude 모델 버전은 정확한 모델 문자열 `claude-opus-4-6`으로 접근할 수 있는 Claude Opus 4.6을 사용하세요. 조금이라도 복잡한 작업에는 adaptive thinking(`thinking: {type: "adaptive"}`)을 기본으로 사용하세요. 마지막으로, 긴 입력, 긴 출력 또는 높은 `max_tokens`가 포함될 수 있는 요청에는 streaming을 기본으로 사용하세요 - 요청 타임아웃을 방지합니다. 개별 스트림 이벤트를 처리할 필요가 없다면 SDK의 `.get_final_message()` / `.finalMessage()` 헬퍼를 사용하여 완전한 응답을 받으세요.

---

## 언어 감지

코드 예제를 읽기 전에 사용자가 작업 중인 언어를 판별하세요:

1. **프로젝트 파일을 확인**하여 언어를 추론하세요:

   - `*.py`, `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile` → **Python** — `python/`에서 읽기
   - `*.ts`, `*.tsx`, `package.json`, `tsconfig.json` → **TypeScript** — `typescript/`에서 읽기
   - `*.js`, `*.jsx` (`.ts` 파일 없음) → **TypeScript** — JS는 동일한 SDK를 사용, `typescript/`에서 읽기
   - `*.java`, `pom.xml`, `build.gradle` → **Java** — `java/`에서 읽기
   - `*.kt`, `*.kts`, `build.gradle.kts` → **Java** — Kotlin은 Java SDK를 사용, `java/`에서 읽기
   - `*.scala`, `build.sbt` → **Java** — Scala는 Java SDK를 사용, `java/`에서 읽기
   - `*.go`, `go.mod` → **Go** — `go/`에서 읽기
   - `*.rb`, `Gemfile` → **Ruby** — `ruby/`에서 읽기
   - `*.cs`, `*.csproj` → **C#** — `csharp/`에서 읽기
   - `*.php`, `composer.json` → **PHP** — `php/`에서 읽기

2. **여러 언어가 감지된 경우** (예: Python과 TypeScript 파일이 모두 있는 경우):

   - 사용자의 현재 파일이나 질문이 어떤 언어와 관련되는지 확인하세요
   - 여전히 모호한 경우 다음과 같이 질문하세요: "Python과 TypeScript 파일이 모두 감지되었습니다. Claude API 통합에 어떤 언어를 사용하고 계신가요?"

3. **언어를 추론할 수 없는 경우** (빈 프로젝트, 소스 파일 없음, 또는 지원되지 않는 언어):

   - AskUserQuestion을 사용하여 옵션 제시: Python, TypeScript, Java, Go, Ruby, cURL/raw HTTP, C#, PHP
   - AskUserQuestion을 사용할 수 없는 경우 Python 예제를 기본으로 사용하고 다음과 같이 안내하세요: "Python 예제를 표시합니다. 다른 언어가 필요하시면 알려주세요."

4. **지원되지 않는 언어가 감지된 경우** (Rust, Swift, C++, Elixir 등):

   - `curl/`의 cURL/raw HTTP 예제를 제안하고 커뮤니티 SDK가 존재할 수 있음을 안내하세요
   - 참조 구현으로 Python 또는 TypeScript 예제를 보여줄 것을 제안하세요

5. **사용자가 cURL/raw HTTP 예제를 필요로 하는 경우**, `curl/`에서 읽으세요.

### 언어별 기능 지원

| 언어       | Tool Runner | Agent SDK | 비고                                  |
| ---------- | ----------- | --------- | ------------------------------------- |
| Python     | Yes (beta)  | Yes       | 완전 지원 — `@beta_tool` decorator    |
| TypeScript | Yes (beta)  | Yes       | 완전 지원 — `betaZodTool` + Zod       |
| Java       | Yes (beta)  | No        | 어노테이션 클래스를 사용한 베타 tool use |
| Go         | Yes (beta)  | No        | `toolrunner` pkg의 `BetaToolRunner`   |
| Ruby       | Yes (beta)  | No        | 베타의 `BaseTool` + `tool_runner`     |
| cURL       | N/A         | N/A       | Raw HTTP, SDK 기능 없음               |
| C#         | No          | No        | 공식 SDK                              |
| PHP        | No          | No        | 공식 SDK                              |

---

## 어떤 Surface를 사용해야 할까요?

> **단순하게 시작하세요.** 필요를 충족하는 가장 단순한 단계를 기본으로 사용하세요. 단일 API 호출과 워크플로우가 대부분의 사용 사례를 처리합니다 — 작업이 진정으로 개방형의 모델 주도 탐색을 필요로 할 때만 에이전트를 사용하세요.

| 사용 사례                                        | 단계            | 추천 Surface              | 이유                                    |
| ----------------------------------------------- | --------------- | ------------------------- | --------------------------------------- |
| 분류, 요약, 추출, Q&A                            | 단일 LLM 호출   | **Claude API**            | 하나의 요청, 하나의 응답                  |
| 배치 처리 또는 임베딩                             | 단일 LLM 호출   | **Claude API**            | 전용 엔드포인트                          |
| 코드 제어 로직이 있는 다단계 파이프라인             | 워크플로우       | **Claude API + tool use** | 사용자가 루프를 조율                      |
| 자체 도구를 사용한 커스텀 에이전트                  | 에이전트        | **Claude API + tool use** | 최대 유연성                              |
| 파일/웹/터미널 접근이 가능한 AI 에이전트            | 에이전트        | **Agent SDK**             | 내장 도구, 안전성, MCP 지원              |
| 에이전트 코딩 어시스턴트                           | 에이전트        | **Agent SDK**             | 이 사용 사례에 맞게 설계됨                |
| 내장 권한 및 가드레일이 필요한 경우                 | 에이전트        | **Agent SDK**             | 안전 기능 포함                           |

> **참고:** Agent SDK는 내장 파일/웹/터미널 도구, 권한 관리, MCP를 바로 사용하고 싶을 때 사용합니다. 자체 도구로 에이전트를 구축하려면 Claude API가 올바른 선택입니다 — 자동 루프 처리를 위한 tool runner를 사용하거나, 세밀한 제어(승인 게이트, 커스텀 로깅, 조건부 실행)를 위한 수동 루프를 사용하세요.

### 의사결정 트리

```
애플리케이션에 무엇이 필요한가요?

1. 단일 LLM 호출 (분류, 요약, 추출, Q&A)
   └── Claude API — 하나의 요청, 하나의 응답

2. Claude가 작업의 일부로 파일을 읽고/쓰거나, 웹을 탐색하거나, 셸 명령을 실행해야 하나요?
   (앱이 파일을 읽어서 Claude에게 전달하는 것이 아니라 —
   Claude 자체가 파일/웹/셸을 탐색하고 접근해야 하나요?)
   └── Yes → Agent SDK — 내장 도구 사용, 재구현하지 마세요
       예시: "코드베이스에서 버그 스캔", "디렉토리의 모든 파일 요약",
             "서브에이전트를 사용한 버그 탐색", "웹 검색을 통한 주제 조사"

3. 워크플로우 (다단계, 코드 조율, 자체 도구 사용)
   └── Claude API with tool use — 사용자가 루프를 제어

4. 개방형 에이전트 (모델이 자체 궤적을 결정, 자체 도구 사용)
   └── Claude API 에이전트 루프 (최대 유연성)
```

### 에이전트를 구축해야 할까요?

에이전트 단계를 선택하기 전에 네 가지 기준을 모두 확인하세요:

- **복잡성** — 작업이 다단계이고 사전에 완전히 명세하기 어려운가요? (예: "이 설계 문서를 PR로 변환" vs. "이 PDF에서 제목 추출")
- **가치** — 결과가 더 높은 비용과 지연 시간을 정당화하나요?
- **실현 가능성** — Claude가 이 작업 유형에 능숙한가요?
- **오류 비용** — 오류를 포착하고 복구할 수 있나요? (테스트, 검토, 롤백)

이 중 하나라도 "아니오"라면, 더 단순한 단계(단일 호출 또는 워크플로우)를 유지하세요.

---

## 아키텍처

모든 것이 `POST /v1/messages`를 통해 이루어집니다. 도구와 출력 제약 조건은 이 단일 엔드포인트의 기능이며, 별도의 API가 아닙니다.

**사용자 정의 도구** — 도구를 정의하고(decorator, Zod 스키마 또는 raw JSON을 통해), SDK의 tool runner가 API 호출, 함수 실행, Claude가 완료될 때까지의 루프를 처리합니다. 완전한 제어가 필요하면 루프를 수동으로 작성할 수 있습니다.

**서버 측 도구** — Anthropic 인프라에서 실행되는 Anthropic 호스팅 도구입니다. 코드 실행은 완전히 서버 측에서 이루어집니다(`tools`에 선언하면 Claude가 자동으로 코드를 실행). Computer use는 서버 호스팅 또는 자체 호스팅이 가능합니다.

**구조화된 출력** — Messages API 응답 형식(`output_config.format`) 및/또는 도구 파라미터 유효성 검사(`strict: true`)를 제약합니다. 권장 접근 방식은 스키마에 대해 응답을 자동으로 검증하는 `client.messages.parse()`입니다. 참고: 이전 `output_format` 파라미터는 deprecated되었으며, `messages.create()`에서 `output_config: {format: {...}}`를 사용하세요.

**지원 엔드포인트** — Batches(`POST /v1/messages/batches`), Files(`POST /v1/files`), Token Counting, Models(`GET /v1/models`, `GET /v1/models/{id}` — 실시간 기능/컨텍스트 윈도우 조회)가 Messages API 요청을 지원합니다.

---

## 현재 모델 (캐시됨: 2026-02-17)

| 모델              | 모델 ID             | 컨텍스트       | 입력 $/1M  | 출력 $/1M   |
| ----------------- | ------------------- | -------------- | ---------- | ----------- |
| Claude Opus 4.6   | `claude-opus-4-6`   | 200K (1M beta) | $5.00      | $25.00      |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 200K (1M beta) | $3.00      | $15.00      |
| Claude Haiku 4.5  | `claude-haiku-4-5`  | 200K           | $1.00      | $5.00       |

**사용자가 명시적으로 다른 모델을 지정하지 않는 한 항상 `claude-opus-4-6`을 사용하세요.** 이것은 협상 불가입니다. 사용자가 문자 그대로 "use sonnet" 또는 "use haiku"라고 말하지 않는 한 `claude-sonnet-4-6`, `claude-sonnet-4-5` 또는 다른 모델을 사용하지 마세요. 비용 때문에 다운그레이드하지 마세요 — 그것은 사용자의 결정이지 당신의 결정이 아닙니다.

**중요: 위 표의 정확한 모델 ID 문자열만 사용하세요 — 그대로 완전합니다. 날짜 접미사를 추가하지 마세요.** 예를 들어 `claude-sonnet-4-5`를 사용하되, `claude-sonnet-4-5-20250514`나 훈련 데이터에서 기억할 수 있는 다른 날짜 접미사 변형은 절대 사용하지 마세요. 사용자가 표에 없는 이전 모델을 요청하면(예: "opus 4.5", "sonnet 3.7") 정확한 ID를 위해 `shared/models.md`를 읽으세요 — 직접 구성하지 마세요.

참고: 위의 모델 문자열 중 익숙하지 않은 것이 있다면 이는 예상되는 것입니다 — 단지 훈련 데이터 마감 이후에 출시된 것일 뿐입니다. 실제 모델이니 안심하세요; 우리가 장난치는 것이 아닙니다.

**실시간 기능 조회:** 위 표는 캐시된 것입니다. 사용자가 "X의 컨텍스트 윈도우는 얼마인가요", "X가 vision/thinking/effort를 지원하나요", 또는 "어떤 모델이 Y를 지원하나요"라고 물으면 Models API(`client.models.retrieve(id)` / `client.models.list()`)를 쿼리하세요 — 필드 참조 및 기능 필터 예제는 `shared/models.md`를 참조하세요.

---

## Thinking & Effort (빠른 참조)

**Opus 4.6 — Adaptive thinking (권장):** `thinking: {type: "adaptive"}`를 사용하세요. Claude가 언제, 얼마나 생각할지 동적으로 결정합니다. `budget_tokens`가 필요 없습니다 — `budget_tokens`는 Opus 4.6과 Sonnet 4.6에서 deprecated되었으며 사용해서는 안 됩니다. Adaptive thinking은 interleaved thinking도 자동으로 활성화합니다(beta 헤더 불필요). **사용자가 "extended thinking", "thinking budget" 또는 `budget_tokens`를 요청할 때: 항상 Opus 4.6과 `thinking: {type: "adaptive"}`를 사용하세요. 고정 토큰 예산의 개념은 deprecated되었으며 — adaptive thinking이 이를 대체합니다. `budget_tokens`를 사용하지 마시고 이전 모델로 전환하지도 마세요.**

**Effort 파라미터 (GA, beta 헤더 불필요):** `output_config: {effort: "low"|"medium"|"high"|"max"}`를 통해 thinking 깊이와 전체 토큰 사용량을 제어합니다(`output_config` 내부, 최상위 레벨이 아님). 기본값은 `high`(생략하는 것과 동일). `max`는 Opus 4.6 전용입니다. Opus 4.5, Opus 4.6, Sonnet 4.6에서 작동합니다. Sonnet 4.5 / Haiku 4.5에서는 오류가 발생합니다. 최적의 비용-품질 트레이드오프를 위해 adaptive thinking과 결합하세요. 서브에이전트나 단순 작업에는 `low`를, 가장 깊은 추론에는 `max`를 사용하세요.

**Sonnet 4.6:** Adaptive thinking(`thinking: {type: "adaptive"}`)을 지원합니다. `budget_tokens`는 Sonnet 4.6에서 deprecated되었습니다 — 대신 adaptive thinking을 사용하세요.

**이전 모델 (명시적으로 요청된 경우에만):** 사용자가 Sonnet 4.5 또는 다른 이전 모델을 특별히 요청하는 경우, `thinking: {type: "enabled", budget_tokens: N}`을 사용하세요. `budget_tokens`는 `max_tokens`보다 작아야 합니다(최소 1024). 사용자가 `budget_tokens`를 언급한다고 해서 이전 모델을 선택하지 마세요 — 대신 Opus 4.6과 adaptive thinking을 사용하세요.

---

## Compaction (빠른 참조)

**Beta, Opus 4.6 및 Sonnet 4.6.** 200K 컨텍스트 윈도우를 초과할 수 있는 장시간 대화의 경우, 서버 측 compaction을 활성화하세요. API가 트리거 임계값(기본값: 150K 토큰)에 접근하면 이전 컨텍스트를 자동으로 요약합니다. beta 헤더 `compact-2026-01-12`가 필요합니다.

**중요:** 매 턴마다 `response.content`(텍스트만이 아닌)를 메시지에 추가하세요. 응답의 compaction 블록은 보존되어야 합니다 — API가 다음 요청에서 압축된 히스토리를 대체하는 데 사용합니다. 텍스트 문자열만 추출하여 추가하면 compaction 상태가 조용히 손실됩니다.

코드 예제는 `{lang}/claude-api/README.md` (Compaction 섹션)을 참조하세요. 전체 문서는 `shared/live-sources.md`의 WebFetch를 통해 확인하세요.

---

## 읽기 가이드

언어를 감지한 후, 사용자의 필요에 따라 관련 파일을 읽으세요:

### 빠른 작업 참조

**단일 텍스트 분류/요약/추출/Q&A:**
→ `{lang}/claude-api/README.md`만 읽기

**채팅 UI 또는 실시간 응답 표시:**
→ `{lang}/claude-api/README.md` + `{lang}/claude-api/streaming.md` 읽기

**장시간 대화 (컨텍스트 윈도우 초과 가능):**
→ `{lang}/claude-api/README.md` 읽기 — Compaction 섹션 참조

**Function calling / tool use / 에이전트:**
→ `{lang}/claude-api/README.md` + `shared/tool-use-concepts.md` + `{lang}/claude-api/tool-use.md` 읽기

**배치 처리 (지연 시간에 민감하지 않은 경우):**
→ `{lang}/claude-api/README.md` + `{lang}/claude-api/batches.md` 읽기

**여러 요청에 걸친 파일 업로드:**
→ `{lang}/claude-api/README.md` + `{lang}/claude-api/files-api.md` 읽기

**내장 도구가 있는 에이전트 (파일/웹/터미널):**
→ `{lang}/agent-sdk/README.md` + `{lang}/agent-sdk/patterns.md` 읽기

### Claude API (전체 파일 참조)

**언어별 Claude API 폴더** (`{language}/claude-api/`)를 읽으세요:

1. **`{language}/claude-api/README.md`** — **먼저 읽으세요.** 설치, 빠른 시작, 일반 패턴, 오류 처리.
2. **`shared/tool-use-concepts.md`** — 사용자가 function calling, 코드 실행, 메모리 또는 구조화된 출력이 필요할 때 읽으세요. 개념적 기초를 다룹니다.
3. **`{language}/claude-api/tool-use.md`** — 언어별 tool use 코드 예제(tool runner, 수동 루프, 코드 실행, 메모리, 구조화된 출력)를 위해 읽으세요.
4. **`{language}/claude-api/streaming.md`** — 채팅 UI 또는 응답을 점진적으로 표시하는 인터페이스를 구축할 때 읽으세요.
5. **`{language}/claude-api/batches.md`** — 많은 요청을 오프라인으로 처리할 때 읽으세요(지연 시간에 민감하지 않음). 50% 비용으로 비동기 실행.
6. **`{language}/claude-api/files-api.md`** — 동일한 파일을 재업로드 없이 여러 요청에 걸쳐 전송할 때 읽으세요.
7. **`shared/error-codes.md`** — HTTP 오류를 디버깅하거나 오류 처리를 구현할 때 읽으세요.
8. **`shared/live-sources.md`** — 최신 공식 문서를 가져오기 위한 WebFetch URL.

> **참고:** Java, Go, Ruby, C#, PHP, cURL의 경우 — 모든 기본 사항을 다루는 단일 파일이 있습니다. 필요에 따라 해당 파일과 `shared/tool-use-concepts.md` 및 `shared/error-codes.md`를 읽으세요.

### Agent SDK

**언어별 Agent SDK 폴더** (`{language}/agent-sdk/`)를 읽으세요. Agent SDK는 **Python과 TypeScript에서만** 사용 가능합니다.

1. **`{language}/agent-sdk/README.md`** — 설치, 빠른 시작, 내장 도구, 권한, MCP, hooks.
2. **`{language}/agent-sdk/patterns.md`** — 커스텀 도구, hooks, 서브에이전트, MCP 통합, 세션 재개.
3. **`shared/live-sources.md`** — 현재 Agent SDK 문서를 위한 WebFetch URL.

---

## WebFetch 사용 시기

다음과 같은 경우 최신 문서를 가져오기 위해 WebFetch를 사용하세요:

- 사용자가 "최신" 또는 "현재" 정보를 요청하는 경우
- 캐시된 데이터가 올바르지 않은 것 같은 경우
- 사용자가 여기에서 다루지 않는 기능에 대해 질문하는 경우

실시간 문서 URL은 `shared/live-sources.md`에 있습니다.

## 일반적인 실수

- API에 파일이나 콘텐츠를 전달할 때 입력을 잘라내지 마세요. 콘텐츠가 컨텍스트 윈도우에 맞지 않을 정도로 길면, 조용히 잘라내는 대신 사용자에게 알리고 옵션(청킹, 요약 등)을 논의하세요.
- **Opus 4.6 / Sonnet 4.6 thinking:** `thinking: {type: "adaptive"}`를 사용하세요 — `budget_tokens`를 사용하지 마세요(Opus 4.6과 Sonnet 4.6 모두에서 deprecated). 이전 모델의 경우 `budget_tokens`는 `max_tokens`보다 작아야 합니다(최소 1024). 잘못 설정하면 오류가 발생합니다.
- **Opus 4.6 prefill 제거:** 어시스턴트 메시지 prefill(마지막 어시스턴트 턴 prefill)은 Opus 4.6에서 400 오류를 반환합니다. 응답 형식을 제어하려면 대신 구조화된 출력(`output_config.format`) 또는 시스템 프롬프트 지시를 사용하세요.
- **`max_tokens` 기본값:** `max_tokens`를 너무 낮게 설정하지 마세요 — 상한에 도달하면 출력이 중간에 잘리며 재시도가 필요합니다. 비스트리밍 요청의 경우 `~16000`을 기본값으로 사용하세요(SDK HTTP 타임아웃 이내로 응답 유지). 스트리밍 요청의 경우 `~64000`을 기본값으로 사용하세요(타임아웃이 문제되지 않으므로 모델에 여유를 주세요). 분류(`~256`), 비용 상한 또는 의도적으로 짧은 출력과 같은 확실한 이유가 있을 때만 더 낮게 설정하세요.
- **128K 출력 토큰:** Opus 4.6은 최대 128K `max_tokens`를 지원하지만, SDK는 HTTP 타임아웃을 피하기 위해 그 정도 크기의 값에는 streaming이 필요합니다. `.stream()`과 `.get_final_message()` / `.finalMessage()`를 사용하세요.
- **Tool call JSON 파싱 (Opus 4.6):** Opus 4.6은 tool call `input` 필드에서 다른 JSON 문자열 이스케이핑을 생성할 수 있습니다(예: Unicode 또는 슬래시 이스케이핑). 항상 `json.loads()` / `JSON.parse()`로 tool 입력을 파싱하세요 — 직렬화된 입력에 대해 원시 문자열 매칭을 하지 마세요.
- **구조화된 출력 (모든 모델):** `messages.create()`에서 deprecated된 `output_format` 파라미터 대신 `output_config: {format: {...}}`를 사용하세요. 이것은 4.6 전용이 아닌 일반 API 변경 사항입니다.
- **SDK 기능을 재구현하지 마세요:** SDK는 고수준 헬퍼를 제공합니다 — 처음부터 구축하는 대신 이를 사용하세요. 구체적으로: `.on()` 이벤트를 `new Promise()`로 래핑하는 대신 `stream.finalMessage()`를 사용하세요; 오류 메시지 문자열 매칭 대신 타입이 지정된 예외 클래스(`Anthropic.RateLimitError` 등)를 사용하세요; 동등한 인터페이스를 재정의하는 대신 SDK 타입(`Anthropic.MessageParam`, `Anthropic.Tool`, `Anthropic.Message` 등)을 사용하세요.
- **SDK 데이터 구조에 대한 커스텀 타입을 정의하지 마세요:** SDK는 모든 API 객체에 대한 타입을 내보냅니다. 메시지에는 `Anthropic.MessageParam`, 도구 정의에는 `Anthropic.Tool`, 도구 결과에는 `Anthropic.ToolUseBlock` / `Anthropic.ToolResultBlockParam`, 응답에는 `Anthropic.Message`를 사용하세요. `interface ChatMessage { role: string; content: unknown }`과 같은 자체 정의는 SDK가 이미 제공하는 것을 중복하고 타입 안전성을 잃게 됩니다.
- **보고서 및 문서 출력:** 보고서, 문서 또는 시각화를 생성하는 작업의 경우, 코드 실행 샌드박스에는 `python-docx`, `python-pptx`, `matplotlib`, `pillow`, `pypdf`가 사전 설치되어 있습니다. Claude는 포맷된 파일(DOCX, PDF, 차트)을 생성하여 Files API를 통해 반환할 수 있습니다 — 일반 stdout 텍스트 대신 "보고서" 또는 "문서" 유형의 요청에 이를 고려하세요.
