---
name: web-artifacts-builder
description: 최신 프론트엔드 웹 기술(React, Tailwind CSS, shadcn/ui)을 사용하여 정교한 다중 컴포넌트 claude.ai HTML 아티팩트를 생성하기 위한 도구 모음. 상태 관리, 라우팅 또는 shadcn/ui 컴포넌트가 필요한 복잡한 아티팩트에 사용 - 단순한 단일 파일 HTML/JSX 아티팩트에는 사용하지 않음.
license: Complete terms in LICENSE.txt
---

# Web Artifacts Builder

강력한 프론트엔드 claude.ai 아티팩트를 빌드하려면 다음 단계를 따르세요:
1. `scripts/init-artifact.sh`를 사용하여 프론트엔드 저장소를 초기화합니다
2. 생성된 코드를 편집하여 아티팩트를 개발합니다
3. `scripts/bundle-artifact.sh`를 사용하여 모든 코드를 단일 HTML 파일로 번들링합니다
4. 사용자에게 아티팩트를 표시합니다
5. (선택 사항) 아티팩트를 테스트합니다

**스택**: React 18 + TypeScript + Vite + Parcel (번들링) + Tailwind CSS + shadcn/ui

## 디자인 및 스타일 가이드라인

매우 중요: 흔히 "AI 슬롭"이라고 불리는 것을 피하기 위해, 과도한 중앙 정렬 레이아웃, 보라색 그라데이션, 균일한 둥근 모서리, Inter 폰트의 사용을 피하세요.

## 빠른 시작

### 1단계: 프로젝트 초기화

초기화 스크립트를 실행하여 새 React 프로젝트를 생성합니다:
```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

이 스크립트는 다음이 완전히 구성된 프로젝트를 생성합니다:
- ✅ React + TypeScript (Vite 사용)
- ✅ Tailwind CSS 3.4.1 및 shadcn/ui 테마 시스템
- ✅ 경로 별칭 (`@/`) 구성됨
- ✅ 40개 이상의 shadcn/ui 컴포넌트 사전 설치됨
- ✅ 모든 Radix UI 의존성 포함됨
- ✅ 번들링을 위한 Parcel 구성됨 (.parcelrc 사용)
- ✅ Node 18+ 호환성 (자동 감지 및 Vite 버전 고정)

### 2단계: 아티팩트 개발

아티팩트를 빌드하려면 생성된 파일을 편집하세요. 안내는 아래 **일반적인 개발 작업**을 참조하세요.

### 3단계: 단일 HTML 파일로 번들링

React 앱을 단일 HTML 아티팩트로 번들링하려면:
```bash
bash scripts/bundle-artifact.sh
```

이 스크립트는 `bundle.html`을 생성합니다 - 모든 JavaScript, CSS 및 의존성이 인라인된 자체 완결형 아티팩트입니다. 이 파일은 Claude 대화에서 아티팩트로 직접 공유할 수 있습니다.

**요구 사항**: 프로젝트 루트 디렉토리에 `index.html`이 있어야 합니다.

**스크립트가 수행하는 작업**:
- 번들링 의존성 설치 (parcel, @parcel/config-default, parcel-resolver-tspaths, html-inline)
- 경로 별칭 지원이 포함된 `.parcelrc` 설정 생성
- Parcel로 빌드 (소스 맵 없음)
- html-inline을 사용하여 모든 에셋을 단일 HTML로 인라인

### 4단계: 사용자와 아티팩트 공유

마지막으로, 번들링된 HTML 파일을 사용자와 대화에서 공유하여 아티팩트로 볼 수 있게 합니다.

### 5단계: 아티팩트 테스트/시각화 (선택 사항)

참고: 이것은 완전히 선택적인 단계입니다. 필요하거나 요청된 경우에만 수행하세요.

아티팩트를 테스트/시각화하려면 사용 가능한 도구(다른 Skills 또는 Playwright나 Puppeteer 같은 내장 도구 포함)를 사용하세요. 일반적으로 아티팩트를 사전에 테스트하는 것은 요청과 완성된 아티팩트를 볼 수 있는 시점 사이에 지연을 추가하므로 피하세요. 아티팩트를 제시한 후, 요청이 있거나 문제가 발생하면 나중에 테스트하세요.

## 참고 자료

- **shadcn/ui 컴포넌트**: https://ui.shadcn.com/docs/components
