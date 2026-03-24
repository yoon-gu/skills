---
name: mcp-builder
description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
license: Complete terms in LICENSE.txt
---

# MCP 서버 개발 가이드

## 개요

잘 설계된 도구를 통해 LLM이 외부 서비스와 상호작용할 수 있도록 하는 MCP (Model Context Protocol) 서버를 만듭니다. MCP 서버의 품질은 LLM이 실제 작업을 얼마나 잘 수행할 수 있게 하는지로 측정됩니다.

---

# 프로세스

## 🚀 상위 수준 워크플로우

고품질 MCP 서버를 만들려면 네 가지 주요 단계를 거칩니다:

### 1단계: 심층 조사 및 계획

#### 1.1 현대적 MCP 설계 이해

**API 커버리지 vs. 워크플로우 도구:**
포괄적인 API 엔드포인트 커버리지와 전문화된 워크플로우 도구 사이의 균형을 맞추세요. 워크플로우 도구는 특정 작업에 더 편리할 수 있지만, 포괄적인 커버리지는 에이전트에게 작업을 조합할 수 있는 유연성을 제공합니다. 성능은 클라이언트에 따라 다릅니다 — 일부 클라이언트는 기본 도구를 결합하는 코드 실행의 이점을 얻고, 다른 클라이언트는 상위 수준 워크플로우에서 더 잘 작동합니다. 불확실할 때는 포괄적인 API 커버리지를 우선시하세요.

**도구 이름 지정과 검색 가능성:**
명확하고 설명적인 도구 이름은 에이전트가 적절한 도구를 빠르게 찾는 데 도움이 됩니다. 일관된 접두사(예: `github_create_issue`, `github_list_repos`)와 동작 중심 이름 지정을 사용하세요.

**컨텍스트 관리:**
에이전트는 간결한 도구 설명과 결과를 필터링/페이지네이션하는 기능의 이점을 얻습니다. 집중적이고 관련성 높은 데이터를 반환하는 도구를 설계하세요. 일부 클라이언트는 에이전트가 데이터를 효율적으로 필터링하고 처리하는 데 도움이 되는 코드 실행을 지원합니다.

**실행 가능한 오류 메시지:**
오류 메시지는 구체적인 제안과 다음 단계를 통해 에이전트를 해결책으로 안내해야 합니다.

#### 1.2 MCP 프로토콜 문서 학습

**MCP 명세 탐색:**

사이트맵에서 관련 페이지를 찾는 것부터 시작하세요: `https://modelcontextprotocol.io/sitemap.xml`

그런 다음 마크다운 형식을 위해 `.md` 접미사가 붙은 특정 페이지를 가져오세요 (예: `https://modelcontextprotocol.io/specification/draft.md`).

검토해야 할 주요 페이지:
- 명세 개요 및 아키텍처
- 전송 메커니즘 (streamable HTTP, stdio)
- Tool, resource, prompt 정의

#### 1.3 프레임워크 문서 학습

**권장 스택:**
- **언어**: TypeScript (고품질 SDK 지원과 많은 실행 환경에서의 좋은 호환성, 예: MCPB. 또한 AI 모델은 폭넓은 사용, 정적 타이핑, 우수한 린팅 도구의 이점을 받아 TypeScript 코드를 잘 생성합니다)
- **전송**: 원격 서버에는 Streamable HTTP, 상태 비저장 JSON 사용 (상태 유지 세션과 스트리밍 응답에 비해 확장 및 유지보수가 더 간편함). 로컬 서버에는 stdio.

**프레임워크 문서 로드:**

- **MCP 모범 사례**: [📋 모범 사례 보기](./reference/mcp_best_practices.md) - 핵심 가이드라인

**TypeScript (권장):**
- **TypeScript SDK**: WebFetch를 사용하여 `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` 로드
- [⚡ TypeScript 가이드](./reference/node_mcp_server.md) - TypeScript 패턴 및 예제

**Python:**
- **Python SDK**: WebFetch를 사용하여 `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md` 로드
- [🐍 Python 가이드](./reference/python_mcp_server.md) - Python 패턴 및 예제

#### 1.4 구현 계획

**API 이해:**
서비스의 API 문서를 검토하여 주요 엔드포인트, 인증 요구사항, 데이터 모델을 파악하세요. 필요에 따라 웹 검색과 WebFetch를 사용하세요.

**도구 선택:**
포괄적인 API 커버리지를 우선시하세요. 가장 일반적인 작업부터 시작하여 구현할 엔드포인트 목록을 작성하세요.

---

### 2단계: 구현

#### 2.1 프로젝트 구조 설정

프로젝트 설정에 대해서는 언어별 가이드를 참조하세요:
- [⚡ TypeScript 가이드](./reference/node_mcp_server.md) - 프로젝트 구조, package.json, tsconfig.json
- [🐍 Python 가이드](./reference/python_mcp_server.md) - 모듈 구성, 의존성

#### 2.2 핵심 인프라 구현

공유 유틸리티 생성:
- 인증이 포함된 API 클라이언트
- 오류 처리 헬퍼
- 응답 포맷팅 (JSON/Markdown)
- 페이지네이션 지원

#### 2.3 도구 구현

각 도구에 대해:

**입력 스키마:**
- Zod (TypeScript) 또는 Pydantic (Python) 사용
- 제약 조건과 명확한 설명 포함
- 필드 설명에 예제 추가

**출력 스키마:**
- 구조화된 데이터에 대해 가능한 한 `outputSchema` 정의
- 도구 응답에서 `structuredContent` 사용 (TypeScript SDK 기능)
- 클라이언트가 도구 출력을 이해하고 처리하는 데 도움

**도구 설명:**
- 기능에 대한 간결한 요약
- 매개변수 설명
- 반환 타입 스키마

**구현:**
- I/O 작업에 async/await 사용
- 실행 가능한 메시지를 포함한 적절한 오류 처리
- 해당되는 경우 페이지네이션 지원
- 최신 SDK 사용 시 텍스트 콘텐츠와 구조화된 데이터 모두 반환

**어노테이션:**
- `readOnlyHint`: true/false
- `destructiveHint`: true/false
- `idempotentHint`: true/false
- `openWorldHint`: true/false

---

### 3단계: 검토 및 테스트

#### 3.1 코드 품질

검토 항목:
- 중복 코드 없음 (DRY 원칙)
- 일관된 오류 처리
- 완전한 타입 커버리지
- 명확한 도구 설명

#### 3.2 빌드 및 테스트

**TypeScript:**
- `npm run build`를 실행하여 컴파일 확인
- MCP Inspector로 테스트: `npx @modelcontextprotocol/inspector`

**Python:**
- 구문 확인: `python -m py_compile your_server.py`
- MCP Inspector로 테스트

자세한 테스트 방법과 품질 체크리스트는 언어별 가이드를 참조하세요.

---

### 4단계: 평가 생성

MCP 서버를 구현한 후, 효과를 테스트하기 위한 포괄적인 평가를 생성하세요.

**완전한 평가 가이드라인은 [✅ 평가 가이드](./reference/evaluation.md)를 로드하세요.**

#### 4.1 평가 목적 이해

평가를 사용하여 LLM이 현실적이고 복잡한 질문에 답하기 위해 MCP 서버를 효과적으로 사용할 수 있는지 테스트하세요.

#### 4.2 10개의 평가 질문 작성

효과적인 평가를 만들려면 평가 가이드에 설명된 프로세스를 따르세요:

1. **도구 검사**: 사용 가능한 도구를 나열하고 기능을 이해
2. **콘텐츠 탐색**: READ-ONLY 작업을 사용하여 사용 가능한 데이터 탐색
3. **질문 생성**: 복잡하고 현실적인 질문 10개 작성
4. **답변 검증**: 각 질문을 직접 풀어서 답변 확인

#### 4.3 평가 요구사항

각 질문이 다음을 충족하는지 확인하세요:
- **독립적**: 다른 질문에 의존하지 않음
- **읽기 전용**: 비파괴적 작업만 필요
- **복잡성**: 여러 도구 호출과 심층 탐색 필요
- **현실적**: 사람들이 관심을 가질 실제 사용 사례 기반
- **검증 가능**: 문자열 비교로 확인할 수 있는 단일하고 명확한 답변
- **안정적**: 시간이 지나도 답변이 변하지 않음

#### 4.4 출력 형식

다음 구조로 XML 파일을 생성하세요:

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
    <answer>3</answer>
  </qa_pair>
<!-- More qa_pairs... -->
</evaluation>
```

---

# 참조 파일

## 📚 문서 라이브러리

개발 중 필요에 따라 이 리소스들을 로드하세요:

### 핵심 MCP 문서 (먼저 로드)
- **MCP 프로토콜**: `https://modelcontextprotocol.io/sitemap.xml`의 사이트맵에서 시작한 후 `.md` 접미사가 붙은 특정 페이지를 가져오세요
- [📋 MCP 모범 사례](./reference/mcp_best_practices.md) - 다음을 포함하는 범용 MCP 가이드라인:
  - 서버 및 도구 이름 지정 규칙
  - 응답 형식 가이드라인 (JSON vs Markdown)
  - 페이지네이션 모범 사례
  - 전송 선택 (streamable HTTP vs stdio)
  - 보안 및 오류 처리 표준

### SDK 문서 (1/2단계에서 로드)
- **Python SDK**: `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`에서 가져오기
- **TypeScript SDK**: `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`에서 가져오기

### 언어별 구현 가이드 (2단계에서 로드)
- [🐍 Python 구현 가이드](./reference/python_mcp_server.md) - 다음을 포함하는 완전한 Python/FastMCP 가이드:
  - 서버 초기화 패턴
  - Pydantic 모델 예제
  - `@mcp.tool`을 사용한 도구 등록
  - 완전한 동작 예제
  - 품질 체크리스트

- [⚡ TypeScript 구현 가이드](./reference/node_mcp_server.md) - 다음을 포함하는 완전한 TypeScript 가이드:
  - 프로젝트 구조
  - Zod 스키마 패턴
  - `server.registerTool`을 사용한 도구 등록
  - 완전한 동작 예제
  - 품질 체크리스트

### 평가 가이드 (4단계에서 로드)
- [✅ 평가 가이드](./reference/evaluation.md) - 다음을 포함하는 완전한 평가 생성 가이드:
  - 질문 작성 가이드라인
  - 답변 검증 전략
  - XML 형식 명세
  - 예제 질문 및 답변
  - 제공된 스크립트를 사용한 평가 실행
