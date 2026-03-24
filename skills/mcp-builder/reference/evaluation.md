# MCP 서버 평가 가이드

## 개요

이 문서는 MCP 서버에 대한 포괄적인 평가를 작성하는 방법에 대한 지침을 제공합니다. 평가는 LLM이 제공된 도구만을 사용하여 현실적이고 복잡한 질문에 효과적으로 답할 수 있는지를 테스트합니다.

---

## 빠른 참조

### 평가 요구사항
- 사람이 읽을 수 있는 질문 10개 작성
- 질문은 반드시 읽기 전용(READ-ONLY), 독립적(INDEPENDENT), 비파괴적(NON-DESTRUCTIVE)이어야 함
- 각 질문은 여러 도구 호출이 필요 (수십 개가 될 수도 있음)
- 답변은 단일하고 검증 가능한 값이어야 함
- 답변은 안정적(STABLE)이어야 함 (시간이 지나도 변하지 않아야 함)

### 출력 형식
```xml
<evaluation>
   <qa_pair>
      <question>여기에 질문을 작성</question>
      <answer>단일 검증 가능한 답변</answer>
   </qa_pair>
</evaluation>
```

---

## 평가의 목적

MCP 서버의 품질 측정 기준은 서버가 도구를 얼마나 잘 또는 포괄적으로 구현했는지가 아니라, 이러한 구현(입출력 스키마, 독스트링/설명, 기능)이 다른 컨텍스트 없이 MCP 서버에만 접근할 수 있는 LLM이 현실적이고 어려운 질문에 답하는 것을 얼마나 잘 가능하게 하는지입니다.

## 평가 개요

읽기 전용(READ-ONLY), 독립적(INDEPENDENT), 비파괴적(NON-DESTRUCTIVE), 멱등(IDEMPOTENT) 연산만 사용하여 답할 수 있는 사람이 읽을 수 있는 질문 10개를 작성합니다. 각 질문은 다음과 같아야 합니다:
- 현실적
- 명확하고 간결
- 모호하지 않음
- 복잡하며, 잠재적으로 수십 개의 도구 호출이나 단계가 필요
- 사전에 식별한 단일하고 검증 가능한 값으로 답변 가능

## 질문 가이드라인

### 핵심 요구사항

1. **질문은 반드시 독립적이어야 합니다**
   - 각 질문은 다른 질문의 답변에 의존해서는 안 됩니다
   - 다른 질문 처리로 인한 사전 쓰기 작업을 가정해서는 안 됩니다

2. **질문은 반드시 비파괴적이고 멱등적인 도구 사용만 요구해야 합니다**
   - 정답에 도달하기 위해 상태를 수정하도록 지시하거나 요구해서는 안 됩니다

3. **질문은 현실적이고, 명확하고, 간결하며, 복잡해야 합니다**
   - 다른 LLM이 답변하기 위해 여러 (잠재적으로 수십 개의) 도구나 단계를 사용해야 합니다

### 복잡성과 깊이

4. **질문은 깊은 탐색을 요구해야 합니다**
   - 여러 하위 질문과 순차적 도구 호출이 필요한 다중 홉(multi-hop) 질문을 고려하세요
   - 각 단계는 이전 질문에서 찾은 정보를 활용해야 합니다

5. **질문은 광범위한 페이지네이션을 요구할 수 있습니다**
   - 여러 페이지의 결과를 넘겨야 할 수 있습니다
   - 틈새 정보를 찾기 위해 오래된 데이터(1-2년 전)를 조회해야 할 수 있습니다
   - 질문은 반드시 어려워야 합니다

6. **질문은 깊은 이해를 요구해야 합니다**
   - 표면적인 지식이 아닌 깊은 이해가 필요합니다
   - 증거가 필요한 참/거짓 질문으로 복잡한 아이디어를 제시할 수 있습니다
   - LLM이 다양한 가설을 탐색해야 하는 객관식 형식을 사용할 수 있습니다

7. **질문은 단순한 키워드 검색으로 풀 수 없어야 합니다**
   - 대상 콘텐츠의 특정 키워드를 포함하지 마세요
   - 동의어, 관련 개념 또는 바꿔 표현을 사용하세요
   - 여러 번의 검색, 여러 관련 항목 분석, 컨텍스트 추출 후 답변 도출이 필요해야 합니다

### 도구 테스트

8. **질문은 도구 반환 값을 스트레스 테스트해야 합니다**
   - 큰 JSON 객체나 목록을 반환하여 LLM에 부하를 줄 수 있습니다
   - 다양한 유형의 데이터 이해가 필요해야 합니다:
     - ID와 이름
     - 타임스탬프와 날짜/시간 (월, 일, 년, 초)
     - 파일 ID, 이름, 확장자, MIME 타입
     - URL, GID 등
   - 도구가 모든 유용한 형태의 데이터를 반환하는 능력을 검증해야 합니다

9. **질문은 대부분 실제 사용 사례를 반영해야 합니다**
   - LLM의 도움을 받는 사람이 실제로 관심을 가질 정보 검색 작업이어야 합니다

10. **질문은 수십 번의 도구 호출을 요구할 수 있습니다**
    - 이는 제한된 컨텍스트를 가진 LLM에게 도전이 됩니다
    - MCP 서버 도구가 반환하는 정보를 줄이도록 유도합니다

11. **모호한 질문을 포함하세요**
    - 모호하거나 어떤 도구를 호출할지 어려운 결정이 필요할 수 있습니다
    - LLM이 실수하거나 잘못 해석할 가능성을 만드세요
    - 모호성에도 불구하고 여전히 단일한 검증 가능한 답변이 있어야 합니다

### 안정성

12. **질문은 답변이 변하지 않도록 설계해야 합니다**
    - 동적인 "현재 상태"에 의존하는 질문을 하지 마세요
    - 예를 들어, 다음을 세지 마세요:
      - 게시물의 반응 수
      - 스레드의 답글 수
      - 채널의 멤버 수

13. **MCP 서버가 생성하는 질문의 종류를 제한하도록 두지 마세요**
    - 도전적이고 복잡한 질문을 만드세요
    - 일부는 사용 가능한 MCP 서버 도구로 풀 수 없을 수도 있습니다
    - 질문은 특정 출력 형식을 요구할 수 있습니다 (datetime vs. epoch time, JSON vs. MARKDOWN)
    - 질문은 완료하기 위해 수십 번의 도구 호출을 요구할 수 있습니다

## 답변 가이드라인

### 검증

1. **답변은 직접 문자열 비교로 검증 가능해야 합니다**
   - 답변이 여러 형식으로 다시 작성될 수 있는 경우, 질문에서 출력 형식을 명확히 지정하세요
   - 예시: "YYYY/MM/DD 형식을 사용하세요.", "True 또는 False로 답하세요.", "A, B, C, 또는 D로만 답하세요."
   - 답변은 다음과 같은 단일 검증 가능한 값이어야 합니다:
     - 사용자 ID, 사용자 이름, 표시 이름, 이름, 성
     - 채널 ID, 채널 이름
     - 메시지 ID, 문자열
     - URL, 제목
     - 수량
     - 타임스탬프, 날짜/시간
     - 불리언 (참/거짓 질문용)
     - 이메일 주소, 전화번호
     - 파일 ID, 파일 이름, 파일 확장자
     - 객관식 답변
   - 답변에 특별한 서식이나 복잡하고 구조화된 출력이 필요해서는 안 됩니다
   - 답변은 직접 문자열 비교를 사용하여 검증됩니다

### 가독성

2. **답변은 일반적으로 사람이 읽기 쉬운 형식을 선호해야 합니다**
   - 예시: 이름, 성, 날짜/시간, 파일 이름, 메시지 문자열, URL, yes/no, true/false, a/b/c/d
   - 불투명한 ID보다는 (ID도 허용 가능하지만)
   - 대다수의 답변은 사람이 읽기 쉬워야 합니다

### 안정성

3. **답변은 안정적/고정적이어야 합니다**
   - 오래된 콘텐츠를 살펴보세요 (예: 끝난 대화, 출시된 프로젝트, 답변된 질문)
   - 항상 같은 답변을 반환하는 "완료된" 개념을 기반으로 질문을 만드세요
   - 비고정적 답변으로부터 격리하기 위해 고정된 시간 범위를 고려하도록 질문할 수 있습니다
   - 변경될 가능성이 낮은 컨텍스트에 의존하세요
   - 예: 논문 이름을 찾는 경우, 나중에 출판된 논문과 혼동되지 않도록 충분히 구체적이어야 합니다

4. **답변은 명확하고 모호하지 않아야 합니다**
   - 질문은 단일하고 명확한 답변이 있도록 설계해야 합니다
   - 답변은 MCP 서버 도구를 사용하여 도출할 수 있어야 합니다

### 다양성

5. **답변은 다양해야 합니다**
   - 답변은 다양한 형태와 형식의 단일 검증 가능한 값이어야 합니다
   - 사용자 관련: 사용자 ID, 사용자 이름, 표시 이름, 이름, 성, 이메일 주소, 전화번호
   - 채널 관련: 채널 ID, 채널 이름, 채널 주제
   - 메시지 관련: 메시지 ID, 메시지 문자열, 타임스탬프, 월, 일, 년

6. **답변은 복잡한 구조여서는 안 됩니다**
   - 값의 목록이 아닌
   - 복잡한 객체가 아닌
   - ID나 문자열의 목록이 아닌
   - 자연어 텍스트가 아닌
   - 단, 직접 문자열 비교를 사용하여 간단하게 검증할 수 있고
   - 현실적으로 재현할 수 있는 경우는 제외
   - LLM이 같은 목록을 다른 순서나 형식으로 반환할 가능성이 낮아야 합니다

## 평가 프로세스

### 1단계: 문서 검토

대상 API의 문서를 읽고 다음을 이해합니다:
- 사용 가능한 엔드포인트와 기능
- 모호한 부분이 있으면 웹에서 추가 정보를 가져오기
- 이 단계를 가능한 한 많이 병렬화하기
- 각 하위 에이전트가 파일 시스템이나 웹의 문서만 검토하도록 보장

### 2단계: 도구 검토

MCP 서버에서 사용 가능한 도구를 나열합니다:
- MCP 서버를 직접 검사
- 입출력 스키마, 독스트링, 설명 이해
- 이 단계에서는 도구 자체를 호출하지 않음

### 3단계: 이해도 심화

충분한 이해를 얻을 때까지 1단계와 2단계를 반복합니다:
- 여러 번 반복
- 만들고 싶은 작업의 종류에 대해 생각
- 이해도를 정제
- 어떤 단계에서도 MCP 서버 구현의 코드 자체를 읽어서는 안 됩니다
- 직관과 이해를 사용하여 합리적이고 현실적이지만 매우 도전적인 작업을 만드세요

### 4단계: 읽기 전용 콘텐츠 검사

API와 도구를 이해한 후, MCP 서버 도구를 사용합니다:
- 읽기 전용(READ-ONLY) 및 비파괴적(NON-DESTRUCTIVE) 작업만으로 콘텐츠 검사
- 목표: 현실적인 질문을 만들기 위한 특정 콘텐츠(예: 사용자, 채널, 메시지, 프로젝트, 작업) 식별
- 상태를 수정하는 도구를 호출해서는 안 됩니다
- MCP 서버 구현의 코드 자체를 읽지 않습니다
- 개별 하위 에이전트가 독립적인 탐색을 수행하도록 이 단계를 병렬화
- 각 하위 에이전트가 읽기 전용, 비파괴적, 멱등 작업만 수행하도록 보장
- 주의: 일부 도구는 많은 데이터를 반환하여 컨텍스트가 부족해질 수 있습니다
- 증분적이고, 작고, 대상이 명확한 도구 호출로 탐색하세요
- 모든 도구 호출 요청에서 `limit` 파라미터를 사용하여 결과를 제한하세요 (10개 미만)
- 페이지네이션을 사용하세요

### 5단계: 작업 생성

콘텐츠를 검사한 후, 사람이 읽을 수 있는 질문 10개를 작성합니다:
- LLM이 MCP 서버로 이 질문들에 답할 수 있어야 합니다
- 위의 모든 질문 및 답변 가이드라인을 따르세요

## 출력 형식

각 QA 쌍은 질문과 답변으로 구성됩니다. 출력은 다음 구조의 XML 파일이어야 합니다:

```xml
<evaluation>
   <qa_pair>
      <question>Find the project created in Q2 2024 with the highest number of completed tasks. What is the project name?</question>
      <answer>Website Redesign</answer>
   </qa_pair>
   <qa_pair>
      <question>Search for issues labeled as "bug" that were closed in March 2024. Which user closed the most issues? Provide their username.</question>
      <answer>sarah_dev</answer>
   </qa_pair>
   <qa_pair>
      <question>Look for pull requests that modified files in the /api directory and were merged between January 1 and January 31, 2024. How many different contributors worked on these PRs?</question>
      <answer>7</answer>
   </qa_pair>
   <qa_pair>
      <question>Find the repository with the most stars that was created before 2023. What is the repository name?</question>
      <answer>data-pipeline</answer>
   </qa_pair>
</evaluation>
```

## 평가 예시

### 좋은 질문

**예시 1: 깊은 탐색이 필요한 다중 홉 질문 (GitHub MCP)**
```xml
<qa_pair>
   <question>Find the repository that was archived in Q3 2023 and had previously been the most forked project in the organization. What was the primary programming language used in that repository?</question>
   <answer>Python</answer>
</qa_pair>
```

이 질문이 좋은 이유:
- 아카이브된 저장소를 찾기 위해 여러 번의 검색이 필요
- 아카이브 전에 가장 많이 포크된 저장소를 식별해야 함
- 프로그래밍 언어를 확인하기 위해 저장소 세부 정보를 검토해야 함
- 답변이 단순하고 검증 가능한 값
- 변하지 않는 과거(완료된) 데이터 기반

**예시 2: 키워드 매칭 없이 컨텍스트 이해가 필요한 질문 (프로젝트 관리 MCP)**
```xml
<qa_pair>
   <question>Locate the initiative focused on improving customer onboarding that was completed in late 2023. The project lead created a retrospective document after completion. What was the lead's role title at that time?</question>
   <answer>Product Manager</answer>
</qa_pair>
```

이 질문이 좋은 이유:
- 특정 프로젝트 이름을 사용하지 않음 ("고객 온보딩 개선에 초점을 맞춘 이니셔티브")
- 특정 기간의 완료된 프로젝트를 찾아야 함
- 프로젝트 리더와 그들의 역할을 식별해야 함
- 회고 문서에서 컨텍스트를 이해해야 함
- 답변이 사람이 읽기 쉽고 안정적
- 완료된 작업 기반 (변하지 않음)

**예시 3: 여러 단계가 필요한 복잡한 집계 (이슈 트래커 MCP)**
```xml
<qa_pair>
   <question>Among all bugs reported in January 2024 that were marked as critical priority, which assignee resolved the highest percentage of their assigned bugs within 48 hours? Provide the assignee's username.</question>
   <answer>alex_eng</answer>
</qa_pair>
```

이 질문이 좋은 이유:
- 날짜, 우선순위, 상태별로 버그를 필터링해야 함
- 담당자별로 그룹화하고 해결률을 계산해야 함
- 48시간 이내를 판단하기 위해 타임스탬프를 이해해야 함
- 페이지네이션을 테스트 (처리할 버그가 잠재적으로 많음)
- 답변이 단일 사용자 이름
- 특정 기간의 과거 데이터 기반

**예시 4: 여러 데이터 유형 간의 종합이 필요한 질문 (CRM MCP)**
```xml
<qa_pair>
   <question>Find the account that upgraded from the Starter to Enterprise plan in Q4 2023 and had the highest annual contract value. What industry does this account operate in?</question>
   <answer>Healthcare</answer>
</qa_pair>
```

이 질문이 좋은 이유:
- 구독 등급 변경을 이해해야 함
- 특정 기간의 업그레이드 이벤트를 식별해야 함
- 계약 금액을 비교해야 함
- 계정 산업 정보에 접근해야 함
- 답변이 단순하고 검증 가능
- 완료된 과거 거래 기반

### 나쁜 질문

**예시 1: 시간이 지나면 답변이 변함**
```xml
<qa_pair>
   <question>How many open issues are currently assigned to the engineering team?</question>
   <answer>47</answer>
</qa_pair>
```

이 질문이 나쁜 이유:
- 이슈가 생성, 닫히거나 재할당됨에 따라 답변이 변함
- 안정적/고정적 데이터를 기반으로 하지 않음
- 동적인 "현재 상태"에 의존

**예시 2: 키워드 검색으로 너무 쉽게 풀림**
```xml
<qa_pair>
   <question>Find the pull request with title "Add authentication feature" and tell me who created it.</question>
   <answer>developer123</answer>
</qa_pair>
```

이 질문이 나쁜 이유:
- 정확한 제목으로 단순 키워드 검색하면 풀림
- 깊은 탐색이나 이해가 필요하지 않음
- 종합이나 분석이 필요하지 않음

**예시 3: 모호한 답변 형식**
```xml
<qa_pair>
   <question>List all the repositories that have Python as their primary language.</question>
   <answer>repo1, repo2, repo3, data-pipeline, ml-tools</answer>
</qa_pair>
```

이 질문이 나쁜 이유:
- 답변이 어떤 순서로든 반환될 수 있는 목록
- 직접 문자열 비교로 검증하기 어려움
- LLM이 다르게 형식화할 수 있음 (JSON 배열, 쉼표 구분, 줄바꿈 구분)
- 특정 집계(개수)나 최상급(가장 많은 별)을 물어보는 것이 더 좋음

## 검증 프로세스

평가를 작성한 후:

1. **XML 파일을 검토**하여 스키마를 이해합니다
2. **각 작업 지시를 로드**하고 MCP 서버와 도구를 사용하여 병렬로 작업을 직접 풀어서 정답을 식별합니다
3. **쓰기(WRITE) 또는 파괴적(DESTRUCTIVE) 작업**이 필요한 것을 표시합니다
4. **모든 정답을 모아** 문서에서 잘못된 답변을 교체합니다
5. **쓰기 또는 파괴적 작업이 필요한 `<qa_pair>`를 제거**합니다

컨텍스트가 부족해지지 않도록 작업 풀기를 병렬화하고, 모든 답변을 모은 후 마지막에 파일을 수정하세요.

## 양질의 평가를 만들기 위한 팁

1. **작업 생성 전에 깊이 생각하고 계획하세요**
2. **기회가 있는 곳에서 병렬화하여** 프로세스 속도를 높이고 컨텍스트를 관리하세요
3. **사람이 실제로 달성하고 싶어하는 현실적인 사용 사례에 집중하세요**
4. **MCP 서버 기능의 한계를 테스트하는 도전적인 질문을 만드세요**
5. **과거 데이터와 완료된 개념을 사용하여 안정성을 보장하세요**
6. **MCP 서버 도구를 사용하여 직접 질문을 풀어 답변을 검증하세요**
7. **프로세스에서 배운 것을 바탕으로 반복하고 개선하세요**

---

# 평가 실행

평가 파일을 작성한 후, 제공된 평가 하네스를 사용하여 MCP 서버를 테스트할 수 있습니다.

## 설정

1. **의존성 설치**

   ```bash
   pip install -r scripts/requirements.txt
   ```

   또는 수동으로 설치:
   ```bash
   pip install anthropic mcp
   ```

2. **API 키 설정**

   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## 평가 파일 형식

평가 파일은 `<qa_pair>` 요소가 포함된 XML 형식을 사용합니다:

```xml
<evaluation>
   <qa_pair>
      <question>Find the project created in Q2 2024 with the highest number of completed tasks. What is the project name?</question>
      <answer>Website Redesign</answer>
   </qa_pair>
   <qa_pair>
      <question>Search for issues labeled as "bug" that were closed in March 2024. Which user closed the most issues? Provide their username.</question>
      <answer>sarah_dev</answer>
   </qa_pair>
</evaluation>
```

## 평가 실행

평가 스크립트(`scripts/evaluation.py`)는 세 가지 전송 유형을 지원합니다:

**중요:**
- **stdio 전송**: 평가 스크립트가 자동으로 MCP 서버 프로세스를 실행하고 관리합니다. 서버를 수동으로 실행하지 마세요.
- **sse/http 전송**: 평가를 실행하기 전에 MCP 서버를 별도로 시작해야 합니다. 스크립트는 지정된 URL에서 이미 실행 중인 서버에 연결합니다.

### 1. 로컬 STDIO 서버

로컬에서 실행하는 MCP 서버용 (스크립트가 서버를 자동으로 실행):

```bash
python scripts/evaluation.py \
  -t stdio \
  -c python \
  -a my_mcp_server.py \
  evaluation.xml
```

환경 변수 포함:
```bash
python scripts/evaluation.py \
  -t stdio \
  -c python \
  -a my_mcp_server.py \
  -e API_KEY=abc123 \
  -e DEBUG=true \
  evaluation.xml
```

### 2. Server-Sent Events (SSE)

SSE 기반 MCP 서버용 (먼저 서버를 시작해야 함):

```bash
python scripts/evaluation.py \
  -t sse \
  -u https://example.com/mcp \
  -H "Authorization: Bearer token123" \
  -H "X-Custom-Header: value" \
  evaluation.xml
```

### 3. HTTP (Streamable HTTP)

HTTP 기반 MCP 서버용 (먼저 서버를 시작해야 함):

```bash
python scripts/evaluation.py \
  -t http \
  -u https://example.com/mcp \
  -H "Authorization: Bearer token123" \
  evaluation.xml
```

## 명령줄 옵션

```
usage: evaluation.py [-h] [-t {stdio,sse,http}] [-m MODEL] [-c COMMAND]
                     [-a ARGS [ARGS ...]] [-e ENV [ENV ...]] [-u URL]
                     [-H HEADERS [HEADERS ...]] [-o OUTPUT]
                     eval_file

위치 인수:
  eval_file             평가 XML 파일 경로

선택적 인수:
  -h, --help            도움말 메시지 표시
  -t, --transport       전송 유형: stdio, sse, 또는 http (기본값: stdio)
  -m, --model           사용할 Claude 모델 (기본값: claude-3-7-sonnet-20250219)
  -o, --output          보고서 출력 파일 (기본값: stdout에 출력)

stdio 옵션:
  -c, --command         MCP 서버를 실행할 명령 (예: python, node)
  -a, --args            명령의 인수 (예: server.py)
  -e, --env             KEY=VALUE 형식의 환경 변수

sse/http 옵션:
  -u, --url             MCP 서버 URL
  -H, --header          'Key: Value' 형식의 HTTP 헤더
```

## 출력

평가 스크립트는 다음을 포함하는 상세 보고서를 생성합니다:

- **요약 통계**:
  - 정확도 (정답/전체)
  - 평균 작업 소요 시간
  - 작업당 평균 도구 호출 수
  - 총 도구 호출 수

- **작업별 결과**:
  - 프롬프트 및 예상 응답
  - 에이전트의 실제 응답
  - 답변 정답 여부 (✅/❌)
  - 소요 시간 및 도구 호출 세부 정보
  - 에이전트의 접근 방식 요약
  - 에이전트의 도구에 대한 피드백

### 보고서를 파일로 저장

```bash
python scripts/evaluation.py \
  -t stdio \
  -c python \
  -a my_server.py \
  -o evaluation_report.md \
  evaluation.xml
```

## 전체 예시 워크플로우

평가를 작성하고 실행하는 전체 예시입니다:

1. **평가 파일 작성** (`my_evaluation.xml`):

```xml
<evaluation>
   <qa_pair>
      <question>Find the user who created the most issues in January 2024. What is their username?</question>
      <answer>alice_developer</answer>
   </qa_pair>
   <qa_pair>
      <question>Among all pull requests merged in Q1 2024, which repository had the highest number? Provide the repository name.</question>
      <answer>backend-api</answer>
   </qa_pair>
   <qa_pair>
      <question>Find the project that was completed in December 2023 and had the longest duration from start to finish. How many days did it take?</question>
      <answer>127</answer>
   </qa_pair>
</evaluation>
```

2. **의존성 설치**:

```bash
pip install -r scripts/requirements.txt
export ANTHROPIC_API_KEY=your_api_key
```

3. **평가 실행**:

```bash
python scripts/evaluation.py \
  -t stdio \
  -c python \
  -a github_mcp_server.py \
  -e GITHUB_TOKEN=ghp_xxx \
  -o github_eval_report.md \
  my_evaluation.xml
```

4. **보고서 검토** (`github_eval_report.md`):
   - 어떤 질문이 통과/실패했는지 확인
   - 도구에 대한 에이전트의 피드백 읽기
   - 개선할 영역 식별
   - MCP 서버 설계 반복 개선

## 문제 해결

### 연결 오류

연결 오류가 발생하는 경우:
- **STDIO**: 명령과 인수가 올바른지 확인
- **SSE/HTTP**: URL에 접근 가능하고 헤더가 올바른지 확인
- 필요한 API 키가 환경 변수나 헤더에 설정되어 있는지 확인

### 낮은 정확도

많은 평가가 실패하는 경우:
- 각 작업에 대한 에이전트의 피드백 검토
- 도구 설명이 명확하고 포괄적인지 확인
- 입력 파라미터가 잘 문서화되어 있는지 확인
- 도구가 너무 많거나 너무 적은 데이터를 반환하는지 고려
- 오류 메시지가 실행 가능한지 확인

### 시간 초과 문제

작업이 시간 초과되는 경우:
- 더 강력한 모델을 사용 (예: `claude-3-7-sonnet-20250219`)
- 도구가 너무 많은 데이터를 반환하는지 확인
- 페이지네이션이 올바르게 작동하는지 확인
- 복잡한 질문을 단순화하는 것을 고려
