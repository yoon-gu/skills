# 도구 사용 개념

이 파일은 Claude API를 사용한 도구 사용의 개념적 기초를 다룹니다. 언어별 코드 예제는 `python/`, `typescript/` 또는 기타 언어 폴더를 참조하세요.

## 사용자 정의 도구

### 도구 정의 구조

> **참고:** Tool Runner(베타)를 사용할 때, 도구 스키마는 함수 시그니처(Python), Zod 스키마(TypeScript), 어노테이션된 클래스(Java), `jsonschema` 구조체 태그(Go), 또는 `BaseTool` 하위 클래스(Ruby)로부터 자동으로 생성됩니다. 아래의 원시 JSON 스키마 형식은 수동 접근 방식이나 Tool Runner를 지원하지 않는 SDK를 위한 것입니다.

각 도구에는 이름, 설명 및 입력을 위한 JSON Schema가 필요합니다:

```json
{
  "name": "get_weather",
  "description": "Get current weather for a location",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City and state, e.g., San Francisco, CA"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "Temperature unit"
      }
    },
    "required": ["location"]
  }
}
```

**도구 정의 모범 사례:**

- 명확하고 설명적인 이름을 사용하세요 (예: `get_weather`, `search_database`, `send_email`)
- 상세한 설명을 작성하세요 — Claude는 이를 사용하여 도구 사용 여부를 결정합니다
- 각 속성에 대한 설명을 포함하세요
- 고정된 값 집합이 있는 매개변수에는 `enum`을 사용하세요
- 반드시 필요한 매개변수는 `required`에 표시하고, 나머지는 기본값이 있는 선택적 매개변수로 만드세요

---

### 도구 선택 옵션

Claude가 도구를 사용하는 시점을 제어합니다:

| 값                                | 동작                                           |
| --------------------------------- | --------------------------------------------- |
| `{"type": "auto"}`                | Claude가 도구 사용 여부를 결정합니다 (기본값)     |
| `{"type": "any"}`                 | Claude가 최소 하나의 도구를 사용해야 합니다       |
| `{"type": "tool", "name": "..."}` | Claude가 지정된 도구를 사용해야 합니다            |
| `{"type": "none"}`                | Claude가 도구를 사용할 수 없습니다               |

모든 `tool_choice` 값에는 `"disable_parallel_tool_use": true`를 포함하여 Claude가 응답당 최대 하나의 도구만 사용하도록 강제할 수 있습니다. 기본적으로 Claude는 단일 응답에서 여러 도구 호출을 요청할 수 있습니다.

---

### Tool Runner vs 수동 루프

**Tool Runner (권장):** SDK의 Tool Runner는 에이전트 루프를 자동으로 처리합니다 — API를 호출하고, 도구 사용 요청을 감지하고, 도구 함수를 실행하고, 결과를 Claude에 다시 전달하며, Claude가 도구 호출을 멈출 때까지 반복합니다. Python, TypeScript, Java, Go, Ruby SDK(베타)에서 사용 가능합니다. Python SDK는 MCP 변환 헬퍼(`anthropic.lib.tools.mcp`)도 제공하여 MCP 도구, 프롬프트, 리소스를 Tool Runner와 함께 사용할 수 있도록 변환합니다 — 자세한 내용은 `python/claude-api/tool-use.md`를 참조하세요.

**수동 에이전트 루프:** 루프에 대한 세밀한 제어가 필요할 때 사용합니다 (예: 커스텀 로깅, 조건부 도구 실행, 사람 개입 승인). `stop_reason == "end_turn"`이 될 때까지 루프를 실행하고, tool_use 블록을 보존하기 위해 항상 전체 `response.content`를 추가하며, 각 `tool_result`에 일치하는 `tool_use_id`가 포함되도록 하세요.

**서버 측 도구의 중지 사유:** 서버 측 도구(코드 실행, 웹 검색 등)를 사용할 때 API는 서버 측 샘플링 루프를 실행합니다. 이 루프가 기본 제한인 10회 반복에 도달하면 응답의 `stop_reason`이 `"pause_turn"`이 됩니다. 계속하려면 사용자 메시지와 어시스턴트 응답을 다시 보내고 또 다른 API 요청을 하세요 — 서버가 중단된 곳에서 재개합니다. "Continue."와 같은 추가 사용자 메시지를 추가하지 마세요 — API가 후행 `server_tool_use` 블록을 감지하고 자동으로 재개해야 함을 인식합니다.

```python
# Handle pause_turn in your agentic loop
if response.stop_reason == "pause_turn":
    messages = [
        {"role": "user", "content": user_query},
        {"role": "assistant", "content": response.content},
    ]
    # Make another API request — server resumes automatically
    response = client.messages.create(
        model="claude-opus-4-6", messages=messages, tools=tools
    )
```

무한 루프를 방지하기 위해 `max_continuations` 제한(예: 5)을 설정하세요. 전체 가이드는 다음을 참조하세요: `https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons`

> **보안:** Tool Runner는 Claude가 요청할 때마다 도구 함수를 자동으로 실행합니다. 부작용이 있는 도구(이메일 전송, 데이터베이스 수정, 금융 거래)의 경우, 도구 함수 내에서 입력을 검증하고 파괴적 작업에 대해서는 확인을 요구하는 것을 고려하세요. 각 도구 실행 전에 사람의 승인이 필요한 경우 수동 에이전트 루프를 사용하세요.

---

### 도구 결과 처리

Claude가 도구를 사용하면 응답에 `tool_use` 블록이 포함됩니다. 다음을 수행해야 합니다:

1. 제공된 입력으로 도구를 실행합니다
2. `tool_result` 메시지로 결과를 다시 보냅니다
3. 대화를 계속합니다

**도구 결과의 오류 처리:** 도구 실행이 실패하면 `"is_error": true`를 설정하고 유용한 오류 메시지를 제공하세요. Claude는 일반적으로 오류를 인식하고 다른 접근 방식을 시도하거나 추가 설명을 요청합니다.

**다중 도구 호출:** Claude는 단일 응답에서 여러 도구를 요청할 수 있습니다. 계속하기 전에 모두 처리하세요 — 모든 결과를 단일 `user` 메시지로 다시 보내세요.

---

## 서버 측 도구: 코드 실행

코드 실행 도구는 Claude가 안전하고 격리된 컨테이너에서 코드를 실행할 수 있게 합니다. 사용자 정의 도구와 달리 서버 측 도구는 Anthropic 인프라에서 실행됩니다 — 클라이언트 측에서 아무것도 실행할 필요가 없습니다. 도구 정의만 포함하면 Claude가 나머지를 처리합니다.

### 주요 사항

- 격리된 컨테이너에서 실행됩니다 (1 CPU, 5 GiB RAM, 5 GiB 디스크)
- 인터넷 접근 불가 (완전 격리)
- 데이터 과학 라이브러리가 사전 설치된 Python 3.11
- 컨테이너는 30일간 유지되며 요청 간에 재사용 가능
- 웹 검색/웹 가져오기 도구와 함께 사용 시 무료; 그 외에는 조직당 월 1,550시간 무료 후 시간당 $0.05

### 도구 정의

이 도구는 스키마가 필요 없습니다 — `tools` 배열에 선언하기만 하면 됩니다:

```json
{
  "type": "code_execution_20260120",
  "name": "code_execution"
}
```

Claude는 자동으로 `bash_code_execution`(셸 명령 실행)과 `text_editor_code_execution`(파일 생성/보기/편집)에 접근할 수 있게 됩니다.

### 사전 설치된 Python 라이브러리

- **데이터 과학**: pandas, numpy, scipy, scikit-learn, statsmodels
- **시각화**: matplotlib, seaborn
- **파일 처리**: openpyxl, xlsxwriter, pillow, pypdf, pdfplumber, python-docx, python-pptx
- **수학**: sympy, mpmath
- **유틸리티**: tqdm, python-dateutil, pytz, sqlite3

추가 패키지는 `pip install`을 통해 런타임에 설치할 수 있습니다.

### 업로드 지원 파일 형식

| 유형   | 확장자                              |
| ------ | ---------------------------------- |
| 데이터 | CSV, Excel (.xlsx/.xls), JSON, XML |
| 이미지 | JPEG, PNG, GIF, WebP               |
| 텍스트 | .txt, .md, .py, .js 등             |

### 컨테이너 재사용

요청 간에 상태(파일, 설치된 패키지, 변수)를 유지하기 위해 컨테이너를 재사용합니다. 첫 번째 응답에서 `container_id`를 추출하여 후속 요청에 전달하세요.

### 응답 구조

응답에는 텍스트와 도구 결과 블록이 번갈아 포함됩니다:

- `text` — Claude의 설명
- `server_tool_use` — Claude가 수행하는 작업
- `bash_code_execution_tool_result` — 코드 실행 출력 (성공/실패 확인을 위해 `return_code`를 확인하세요)
- `text_editor_code_execution_tool_result` — 파일 작업 결과

> **보안:** 경로 탐색 공격을 방지하기 위해 다운로드한 파일을 디스크에 쓰기 전에 항상 `os.path.basename()` / `path.basename()`으로 파일 이름을 정리하세요. 전용 출력 디렉토리에 파일을 작성하세요.

---

## 서버 측 도구: 웹 검색 및 웹 가져오기

웹 검색과 웹 가져오기를 통해 Claude가 웹을 검색하고 페이지 콘텐츠를 가져올 수 있습니다. 서버 측에서 실행됩니다 — 도구 정의만 포함하면 Claude가 쿼리, 가져오기, 결과 처리를 자동으로 수행합니다.

### 도구 정의

```json
[
  { "type": "web_search_20260209", "name": "web_search" },
  { "type": "web_fetch_20260209", "name": "web_fetch" }
]
```

### 동적 필터링 (Opus 4.6 / Sonnet 4.6)

`web_search_20260209` 및 `web_fetch_20260209` 버전은 **동적 필터링**을 지원합니다 — Claude가 검색 결과가 컨텍스트 윈도우에 도달하기 전에 코드를 작성하고 실행하여 필터링함으로써 정확도와 토큰 효율성을 향상시킵니다. 동적 필터링은 이 도구 버전에 내장되어 자동으로 활성화됩니다; `code_execution` 도구를 별도로 선언하거나 베타 헤더를 전달할 필요가 없습니다.

```json
{
  "tools": [
    { "type": "web_search_20260209", "name": "web_search" },
    { "type": "web_fetch_20260209", "name": "web_fetch" }
  ]
}
```

동적 필터링 없이 이전 버전인 `web_search_20250305`도 사용 가능합니다.

> **참고:** 웹 검색과 독립적으로 코드 실행이 필요한 경우(데이터 분석, 파일 처리, 시각화)에만 독립 `code_execution` 도구를 포함하세요. `_20260209` 웹 도구와 함께 포함하면 모델을 혼란시킬 수 있는 두 번째 실행 환경이 생성됩니다.

---

## 서버 측 도구: 프로그래밍 방식 도구 호출

프로그래밍 방식 도구 호출을 통해 Claude가 코드로 복잡한 다중 도구 워크플로를 실행하여 중간 결과를 컨텍스트 윈도우 밖에 유지합니다. Claude가 도구를 직접 호출하는 코드를 작성하여 다단계 작업의 토큰 사용량을 줄입니다.

전체 문서는 WebFetch를 사용하세요:

- URL: `https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling`

---

## 서버 측 도구: 도구 검색

도구 검색 도구를 통해 Claude가 모든 정의를 컨텍스트 윈도우에 로드하지 않고도 대규모 라이브러리에서 동적으로 도구를 발견할 수 있습니다. 많은 도구가 있지만 주어진 쿼리에 소수만 관련이 있을 때 유용합니다.

전체 문서는 WebFetch를 사용하세요:

- URL: `https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool`

---

## 도구 사용 예제

도구 정의에 직접 샘플 도구 호출을 제공하여 사용 패턴을 시연하고 매개변수 오류를 줄일 수 있습니다. 이를 통해 Claude가 도구 입력을 올바르게 포맷하는 방법을 이해할 수 있으며, 특히 복잡한 스키마를 가진 도구에 유용합니다.

전체 문서는 WebFetch를 사용하세요:

- URL: `https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use`

---

## 서버 측 도구: 컴퓨터 사용

컴퓨터 사용을 통해 Claude가 데스크톱 환경과 상호작용할 수 있습니다 (스크린샷, 마우스, 키보드). Anthropic에서 호스팅(코드 실행처럼 서버 측)하거나 자체 호스팅(사용자가 환경을 제공하고 클라이언트 측에서 작업 실행)할 수 있습니다.

전체 문서는 WebFetch를 사용하세요:

- URL: `https://platform.claude.com/docs/en/agents-and-tools/computer-use/overview`

---

## 클라이언트 측 도구: 메모리

메모리 도구를 통해 Claude가 메모리 파일 디렉토리를 통해 대화 간에 정보를 저장하고 검색할 수 있습니다. Claude는 세션 간에 유지되는 파일을 생성, 읽기, 업데이트, 삭제할 수 있습니다.

### 주요 사항

- 클라이언트 측 도구 — 구현을 통해 저장소를 제어합니다
- 지원 명령: `view`, `create`, `str_replace`, `insert`, `delete`, `rename`
- `/memories` 디렉토리의 파일에서 작동합니다
- Python, TypeScript, Java SDK는 메모리 백엔드 구현을 위한 헬퍼 클래스/함수를 제공합니다

> **보안:** API 키, 비밀번호, 토큰 또는 기타 비밀 정보를 메모리 파일에 저장하지 마세요. 개인 식별 정보(PII)에 주의하세요 — 사용자 데이터를 영구 저장하기 전에 데이터 개인정보 보호 규정(GDPR, CCPA)을 확인하세요. 참조 구현에는 내장된 접근 제어가 없습니다; 다중 사용자 시스템에서는 도구 핸들러에 사용자별 메모리 디렉토리와 인증을 구현하세요.

전체 구현 예제는 WebFetch를 사용하세요:

- 문서: `https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool.md`

---

## 구조화된 출력

구조화된 출력은 Claude의 응답을 특정 JSON 스키마를 따르도록 제한하여 유효하고 파싱 가능한 출력을 보장합니다. 이는 별도의 도구가 아니라 Messages API 응답 형식 및/또는 도구 매개변수 검증을 향상시킵니다.

두 가지 기능을 사용할 수 있습니다:

- **JSON 출력** (`output_config.format`): Claude의 응답 형식을 제어합니다
- **엄격한 도구 사용** (`strict: true`): 유효한 도구 매개변수 스키마를 보장합니다

**지원 모델:** Claude Opus 4.6, Claude Sonnet 4.6, Claude Haiku 4.5. 레거시 모델(Claude Opus 4.5, Claude Opus 4.1)도 구조화된 출력을 지원합니다.

> **권장:** 스키마에 대해 응답을 자동으로 검증하는 `client.messages.parse()`를 사용하세요. `messages.create()`를 직접 사용할 때는 `output_config: {format: {...}}`를 사용하세요. `output_format` 편의 매개변수도 일부 SDK 메서드(예: `.parse()`)에서 허용되지만, `output_config.format`이 정식 API 수준 매개변수입니다.

### JSON Schema 제한사항

**지원됨:**

- 기본 타입: object, array, string, integer, number, boolean, null
- `enum`, `const`, `anyOf`, `allOf`, `$ref`/`$def`
- 문자열 형식: `date-time`, `time`, `date`, `duration`, `email`, `hostname`, `uri`, `ipv4`, `ipv6`, `uuid`
- `additionalProperties: false` (모든 객체에 필수)

**지원되지 않음:**

- 재귀 스키마
- 숫자 제약 조건 (`minimum`, `maximum`, `multipleOf`)
- 문자열 제약 조건 (`minLength`, `maxLength`)
- 복잡한 배열 제약 조건
- `false` 이외의 값으로 설정된 `additionalProperties`

Python 및 TypeScript SDK는 지원되지 않는 제약 조건을 API로 보내는 스키마에서 자동으로 제거하고 클라이언트 측에서 검증합니다.

### 중요 참고사항

- **첫 번째 요청 지연**: 새 스키마는 일회성 컴파일 비용이 발생합니다. 동일한 스키마를 사용하는 후속 요청은 24시간 캐시를 사용합니다.
- **거부**: Claude가 안전상의 이유로 거부하면 (`stop_reason: "refusal"`), 출력이 스키마와 일치하지 않을 수 있습니다.
- **토큰 제한**: `stop_reason: "max_tokens"`인 경우 출력이 불완전할 수 있습니다. `max_tokens`를 늘리세요.
- **호환되지 않음**: 인용(400 오류 반환), 메시지 프리필링.
- **호환됨**: Batches API, 스트리밍, 토큰 카운팅, 확장 사고.

---

## 효과적인 도구 사용을 위한 팁

1. **상세한 설명을 제공하세요**: Claude는 도구를 언제, 어떻게 사용할지 이해하기 위해 설명에 크게 의존합니다
2. **구체적인 도구 이름을 사용하세요**: `get_current_weather`가 `weather`보다 낫습니다
3. **입력을 검증하세요**: 실행 전에 항상 도구 입력을 검증하세요
4. **오류를 우아하게 처리하세요**: Claude가 적응할 수 있도록 유용한 오류 메시지를 반환하세요
5. **도구 수를 제한하세요**: 너무 많은 도구는 모델을 혼란시킬 수 있습니다 — 집중된 세트를 유지하세요
6. **도구 상호작용을 테스트하세요**: 다양한 시나리오에서 Claude가 도구를 올바르게 사용하는지 확인하세요

상세한 도구 사용 문서는 WebFetch를 사용하세요:

- URL: `https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview`
