---
name: webapp-testing
description: Playwright를 사용하여 로컬 웹 애플리케이션과 상호작용하고 테스트하기 위한 도구 모음. 프론트엔드 기능 검증, UI 동작 디버깅, 브라우저 스크린샷 캡처, 브라우저 로그 확인을 지원합니다.
license: Complete terms in LICENSE.txt
---

# 웹 애플리케이션 테스트

로컬 웹 애플리케이션을 테스트하려면 네이티브 Python Playwright 스크립트를 작성하세요.

**사용 가능한 헬퍼 스크립트**:
- `scripts/with_server.py` - 서버 생명주기 관리 (다중 서버 지원)

**항상 스크립트를 `--help`와 함께 먼저 실행하세요** - 사용법을 확인할 수 있습니다. 스크립트를 먼저 실행해보고 맞춤형 솔루션이 절대적으로 필요하다고 판단될 때까지 소스 코드를 읽지 마세요. 이 스크립트들은 매우 클 수 있어 컨텍스트 윈도우를 오염시킬 수 있습니다. 이 스크립트들은 컨텍스트 윈도우에 읽어들이는 것이 아니라 블랙박스 스크립트로 직접 호출하기 위해 존재합니다.

## 의사결정 트리: 접근 방식 선택

```
사용자 작업 → 정적 HTML인가?
    ├─ 예 → HTML 파일을 직접 읽어 셀렉터 식별
    │         ├─ 성공 → 셀렉터를 사용하여 Playwright 스크립트 작성
    │         └─ 실패/불완전 → 동적으로 처리 (아래 참조)
    │
    └─ 아니오 (동적 웹앱) → 서버가 이미 실행 중인가?
        ├─ 아니오 → 실행: python scripts/with_server.py --help
        │        그런 다음 헬퍼를 사용하고 간소화된 Playwright 스크립트 작성
        │
        └─ 예 → 정찰 후 행동:
            1. 탐색 후 networkidle 대기
            2. 스크린샷 촬영 또는 DOM 검사
            3. 렌더링된 상태에서 셀렉터 식별
            4. 발견된 셀렉터로 작업 실행
```

## 예시: with_server.py 사용

서버를 시작하려면 먼저 `--help`를 실행한 다음 헬퍼를 사용하세요:

**단일 서버:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**다중 서버 (예: 백엔드 + 프론트엔드):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

자동화 스크립트를 생성하려면 Playwright 로직만 포함하세요 (서버는 자동으로 관리됩니다):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## 정찰 후 행동 패턴

1. **렌더링된 DOM 검사**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. 검사 결과에서 **셀렉터 식별**

3. 발견된 셀렉터를 사용하여 **작업 실행**

## 일반적인 실수

❌ 동적 앱에서 `networkidle` 대기 전에 DOM을 검사**하지 마세요**
✅ 검사 전에 `page.wait_for_load_state('networkidle')`을 **기다리세요**

## 모범 사례

- **번들 스크립트를 블랙박스로 사용하세요** - 작업을 수행하려면 `scripts/`에 있는 스크립트 중 도움이 될 수 있는 것이 있는지 고려하세요. 이 스크립트들은 컨텍스트 윈도우를 어지럽히지 않으면서 일반적이고 복잡한 워크플로우를 안정적으로 처리합니다. `--help`로 사용법을 확인한 후 직접 호출하세요.
- 동기 스크립트에는 `sync_playwright()`를 사용하세요
- 완료 시 항상 브라우저를 닫으세요
- 설명적인 셀렉터를 사용하세요: `text=`, `role=`, CSS 셀렉터 또는 ID
- 적절한 대기를 추가하세요: `page.wait_for_selector()` 또는 `page.wait_for_timeout()`

## 참고 파일

- **examples/** - 일반적인 패턴을 보여주는 예시:
  - `element_discovery.py` - 페이지에서 버튼, 링크 및 입력 요소 발견
  - `static_html_automation.py` - 로컬 HTML에 file:// URL 사용
  - `console_logging.py` - 자동화 중 콘솔 로그 캡처
