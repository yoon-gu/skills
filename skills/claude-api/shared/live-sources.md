# 실시간 문서 소스

이 파일은 platform.claude.com 및 Agent SDK 저장소에서 최신 정보를 가져오기 위한 WebFetch URL을 포함합니다. 캐시된 콘텐츠가 마지막으로 업데이트된 이후 변경되었을 수 있는 최신 데이터가 필요할 때 이 URL을 사용하세요.

## WebFetch 사용 시점

- 사용자가 "최신" 또는 "현재" 정보를 명시적으로 요청할 때
- 캐시된 데이터가 잘못된 것으로 보일 때
- 사용자가 캐시된 콘텐츠에 포함되지 않은 기능에 대해 질문할 때
- 사용자가 특정 API 세부 정보나 예제가 필요할 때

## Claude API 문서 URL

### 모델 및 가격

| 주제            | URL                                                                   | 추출 프롬프트                                                                   |
| --------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| 모델 개요       | `https://platform.claude.com/docs/en/about-claude/models/overview.md` | "Extract current model IDs, context windows, and pricing for all Claude models" |
| 가격            | `https://platform.claude.com/docs/en/pricing.md`                      | "Extract current pricing per million tokens for input and output"               |

### 핵심 기능

| 주제              | URL                                                                          | 추출 프롬프트                                                                          |
| ----------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| 확장된 사고       | `https://platform.claude.com/docs/en/build-with-claude/extended-thinking.md` | "Extract extended thinking parameters, budget_tokens requirements, and usage examples" |
| 적응형 사고       | `https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking.md` | "Extract adaptive thinking setup, effort levels, and Claude Opus 4.6 usage examples"         |
| Effort 매개변수   | `https://platform.claude.com/docs/en/build-with-claude/effort.md`            | "Extract effort levels, cost-quality tradeoffs, and interaction with thinking"        |
| 도구 사용         | `https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview.md`  | "Extract tool definition schema, tool_choice options, and handling tool results"       |
| 스트리밍          | `https://platform.claude.com/docs/en/build-with-claude/streaming.md`         | "Extract streaming event types, SDK examples, and best practices"                      |
| 프롬프트 캐싱     | `https://platform.claude.com/docs/en/build-with-claude/prompt-caching.md`    | "Extract cache_control usage, pricing benefits, and implementation examples"           |

### 미디어 및 파일

| 주제        | URL                                                                    | 추출 프롬프트                                                     |
| ----------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------- |
| 비전        | `https://platform.claude.com/docs/en/build-with-claude/vision.md`      | "Extract supported image formats, size limits, and code examples" |
| PDF 지원    | `https://platform.claude.com/docs/en/build-with-claude/pdf-support.md` | "Extract PDF handling capabilities, limits, and examples"         |

### API 작업

| 주제             | URL                                                                         | 추출 프롬프트                                                                                           |
| ---------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| 배치 처리        | `https://platform.claude.com/docs/en/build-with-claude/batch-processing.md` | "Extract batch API endpoints, request format, and polling for results"                                  |
| Files API        | `https://platform.claude.com/docs/en/build-with-claude/files.md`            | "Extract file upload, download, and referencing in messages, including supported types and beta header" |
| 토큰 카운팅      | `https://platform.claude.com/docs/en/build-with-claude/token-counting.md`   | "Extract token counting API usage and examples"                                                         |
| 속도 제한        | `https://platform.claude.com/docs/en/api/rate-limits.md`                    | "Extract current rate limits by tier and model"                                                         |
| 오류             | `https://platform.claude.com/docs/en/api/errors.md`                         | "Extract HTTP error codes, meanings, and retry guidance"                                                |

### 도구

| 주제           | URL                                                                                    | 추출 프롬프트                                                                            |
| -------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 코드 실행      | `https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool.md` | "Extract code execution tool setup, file upload, container reuse, and response handling" |
| 컴퓨터 사용    | `https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use.md`        | "Extract computer use tool setup, capabilities, and implementation examples"             |

### 고급 기능

| 주제               | URL                                                                           | 추출 프롬프트                                                |
| ------------------ | ----------------------------------------------------------------------------- | --------------------------------------------------- |
| 구조화된 출력      | `https://platform.claude.com/docs/en/build-with-claude/structured-outputs.md` | "Extract output_config.format usage and schema enforcement"                           |
| 압축               | `https://platform.claude.com/docs/en/build-with-claude/compaction.md`         | "Extract compaction setup, trigger config, and streaming with compaction"             |
| 인용               | `https://platform.claude.com/docs/en/build-with-claude/citations.md`          | "Extract citation format and implementation"        |
| 컨텍스트 윈도우    | `https://platform.claude.com/docs/en/build-with-claude/context-windows.md`    | "Extract context window sizes and token management" |

---

## Claude API SDK 저장소

| SDK        | URL                                                       | 설명                           |
| ---------- | --------------------------------------------------------- | ------------------------------ |
| Python     | `https://github.com/anthropics/anthropic-sdk-python`     | `anthropic` pip 패키지 소스    |
| TypeScript | `https://github.com/anthropics/anthropic-sdk-typescript` | `@anthropic-ai/sdk` npm 소스  |
| Java       | `https://github.com/anthropics/anthropic-sdk-java`       | `anthropic-java` Maven 소스   |
| Go         | `https://github.com/anthropics/anthropic-sdk-go`         | Go 모듈 소스                   |
| Ruby       | `https://github.com/anthropics/anthropic-sdk-ruby`       | `anthropic` gem 소스           |
| C#         | `https://github.com/anthropics/anthropic-sdk-csharp`     | NuGet 패키지 소스              |
| PHP        | `https://github.com/anthropics/anthropic-sdk-php`        | Composer 패키지 소스           |

---

## Agent SDK 문서 URL

### 핵심 문서

| 주제                 | URL                                                         | 추출 프롬프트                                                   |
| -------------------- | ----------------------------------------------------------- | --------------------------------------------------------------- |
| Agent SDK 개요       | `https://platform.claude.com/docs/en/agent-sdk.md`          | "Extract the Agent SDK overview, key features, and use cases"   |
| Agent SDK Python     | `https://github.com/anthropics/claude-agent-sdk-python`     | "Extract Python SDK installation, imports, and basic usage"     |
| Agent SDK TypeScript | `https://github.com/anthropics/claude-agent-sdk-typescript` | "Extract TypeScript SDK installation, imports, and basic usage" |

### SDK 참조 (GitHub README)

| 주제           | URL                                                                                       | 추출 프롬프트                                                |
| -------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Python SDK     | `https://raw.githubusercontent.com/anthropics/claude-agent-sdk-python/main/README.md`     | "Extract Python SDK API reference, classes, and methods"     |
| TypeScript SDK | `https://raw.githubusercontent.com/anthropics/claude-agent-sdk-typescript/main/README.md` | "Extract TypeScript SDK API reference, types, and functions" |

### npm/PyPI 패키지

| 패키지                              | URL                                                            | 설명                      |
| ----------------------------------- | -------------------------------------------------------------- | ------------------------- |
| claude-agent-sdk (Python)           | `https://pypi.org/project/claude-agent-sdk/`                   | PyPI의 Python 패키지      |
| @anthropic-ai/claude-agent-sdk (TS) | `https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk` | npm의 TypeScript 패키지   |

### GitHub 저장소

| 리소스         | URL                                                         | 설명                                |
| -------------- | ----------------------------------------------------------- | ----------------------------------- |
| Python SDK     | `https://github.com/anthropics/claude-agent-sdk-python`     | Python 패키지 소스                  |
| TypeScript SDK | `https://github.com/anthropics/claude-agent-sdk-typescript` | TypeScript/Node.js 패키지 소스      |
| MCP Servers    | `https://github.com/modelcontextprotocol`                   | 공식 MCP 서버 구현                  |

---

## 대체 전략

WebFetch가 실패할 경우 (네트워크 문제, URL 변경):

1. 언어별 파일의 캐시된 콘텐츠를 사용하세요 (캐시 날짜에 주의)
2. 사용자에게 데이터가 오래되었을 수 있음을 알리세요
3. platform.claude.com 또는 GitHub 저장소를 직접 확인하도록 안내하세요
