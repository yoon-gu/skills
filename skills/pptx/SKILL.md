---
name: pptx
description: "Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions \"deck,\" \"slides,\" \"presentation,\" or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill."
license: Proprietary. LICENSE.txt has complete terms
---

# PPTX 스킬

## 빠른 참조

| 작업 | 가이드 |
|------|--------|
| 콘텐츠 읽기/분석 | `python -m markitdown presentation.pptx` |
| 템플릿에서 편집 또는 생성 | [editing.md](editing.md) 읽기 |
| 처음부터 생성 | [pptxgenjs.md](pptxgenjs.md) 읽기 |

---

## 콘텐츠 읽기

```bash
# Text extraction
python -m markitdown presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## 편집 워크플로우

**자세한 내용은 [editing.md](editing.md)를 참조하세요.**

1. `thumbnail.py`로 템플릿 분석
2. 언팩 → 슬라이드 조작 → 콘텐츠 편집 → 정리 → 팩

---

## 처음부터 생성

**자세한 내용은 [pptxgenjs.md](pptxgenjs.md)를 참조하세요.**

템플릿이나 참조 프레젠테이션이 없을 때 사용합니다.

---

## 디자인 아이디어

**지루한 슬라이드를 만들지 마세요.** 흰색 배경에 단순한 글머리 기호는 누구에게도 감명을 주지 못합니다. 각 슬라이드에 이 목록의 아이디어를 고려하세요.

### 시작하기 전에

- **대담하고 콘텐츠에 맞는 색상 팔레트 선택**: 팔레트는 이 주제를 위해 디자인된 느낌이어야 합니다. 색상을 완전히 다른 프레젠테이션에 넣어도 "잘 어울린다"면, 충분히 구체적인 선택을 하지 않은 것입니다.
- **균등함보다 지배적 색상**: 하나의 색상이 지배적이어야 하며(시각적 비중 60-70%), 1-2개의 보조 톤과 하나의 강렬한 강조색을 사용하세요. 모든 색상에 동일한 비중을 부여하지 마세요.
- **명암 대비**: 타이틀 + 결론 슬라이드에는 어두운 배경, 콘텐츠에는 밝은 배경("샌드위치" 구조). 또는 전체적으로 어두운 배경을 사용하여 프리미엄 느낌을 줍니다.
- **시각적 모티프에 전념**: 하나의 독특한 요소를 선택하고 반복하세요 — 둥근 이미지 프레임, 색상 원 안의 아이콘, 두꺼운 단면 테두리. 모든 슬라이드에 적용하세요.

### 색상 팔레트

주제에 맞는 색상을 선택하세요 — 기본 파란색을 사용하지 마세요. 다음 팔레트를 영감으로 활용하세요:

| 테마 | 기본색 | 보조색 | 강조색 |
|------|--------|--------|--------|
| **Midnight Executive** | `1E2761` (네이비) | `CADCFC` (아이스 블루) | `FFFFFF` (화이트) |
| **Forest & Moss** | `2C5F2D` (포레스트) | `97BC62` (모스) | `F5F5F5` (크림) |
| **Coral Energy** | `F96167` (코랄) | `F9E795` (골드) | `2F3C7E` (네이비) |
| **Warm Terracotta** | `B85042` (테라코타) | `E7E8D1` (샌드) | `A7BEAE` (세이지) |
| **Ocean Gradient** | `065A82` (딥 블루) | `1C7293` (틸) | `21295C` (미드나이트) |
| **Charcoal Minimal** | `36454F` (차콜) | `F2F2F2` (오프화이트) | `212121` (블랙) |
| **Teal Trust** | `028090` (틸) | `00A896` (시폼) | `02C39A` (민트) |
| **Berry & Cream** | `6D2E46` (베리) | `A26769` (더스티 로즈) | `ECE2D0` (크림) |
| **Sage Calm** | `84B59F` (세이지) | `69A297` (유칼립투스) | `50808E` (슬레이트) |
| **Cherry Bold** | `990011` (체리) | `FCF6F5` (오프화이트) | `2F3C7E` (네이비) |

### 각 슬라이드에 대해

**모든 슬라이드에는 시각적 요소가 필요합니다** — 이미지, 차트, 아이콘 또는 도형. 텍스트만 있는 슬라이드는 기억에 남지 않습니다.

**레이아웃 옵션:**
- 2단 구성 (왼쪽 텍스트, 오른쪽 일러스트레이션)
- 아이콘 + 텍스트 행 (색상 원 안의 아이콘, 굵은 헤더, 아래 설명)
- 2x2 또는 2x3 그리드 (한쪽은 이미지, 다른 쪽은 콘텐츠 블록 그리드)
- 하프 블리드 이미지 (왼쪽 또는 오른쪽 전체) 위에 콘텐츠 오버레이

**데이터 표시:**
- 큰 통계 콜아웃 (큰 숫자 60-72pt, 아래 작은 라벨)
- 비교 열 (전/후, 장단점, 나란히 옵션)
- 타임라인 또는 프로세스 흐름 (번호 매긴 단계, 화살표)

**시각적 완성도:**
- 섹션 헤더 옆에 작은 색상 원 안의 아이콘
- 핵심 통계나 태그라인을 위한 이탤릭 강조 텍스트

### 타이포그래피

**흥미로운 폰트 조합을 선택하세요** — Arial을 기본으로 사용하지 마세요. 개성 있는 헤더 폰트를 선택하고 깔끔한 본문 폰트와 조합하세요.

| 헤더 폰트 | 본문 폰트 |
|-----------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |
| Palatino | Garamond |
| Consolas | Calibri |

| 요소 | 크기 |
|------|------|
| 슬라이드 제목 | 36-44pt 굵게 |
| 섹션 헤더 | 20-24pt 굵게 |
| 본문 텍스트 | 14-16pt |
| 캡션 | 10-12pt 연하게 |

### 간격

- 최소 0.5" 여백
- 콘텐츠 블록 사이 0.3-0.5"
- 여유 공간을 남기세요—모든 공간을 채우지 마세요

### 피해야 할 것 (흔한 실수)

- **같은 레이아웃을 반복하지 마세요** — 슬라이드마다 열, 카드, 콜아웃을 다양하게 하세요
- **본문 텍스트를 가운데 정렬하지 마세요** — 단락과 목록은 왼쪽 정렬; 제목만 가운데 정렬
- **크기 대비를 줄이지 마세요** — 제목은 14-16pt 본문과 구별되려면 36pt 이상이어야 합니다
- **기본 파란색을 사용하지 마세요** — 특정 주제를 반영하는 색상을 선택하세요
- **간격을 무작위로 섞지 마세요** — 0.3" 또는 0.5" 간격을 선택하고 일관되게 사용하세요
- **한 슬라이드만 스타일링하고 나머지를 방치하지 마세요** — 완전히 적용하거나 전체적으로 심플하게 유지하세요
- **텍스트만 있는 슬라이드를 만들지 마세요** — 이미지, 아이콘, 차트 또는 시각적 요소를 추가하세요; 단순한 제목 + 글머리 기호를 피하세요
- **텍스트 박스 패딩을 잊지 마세요** — 선이나 도형을 텍스트 가장자리에 맞출 때, 텍스트 박스에 `margin: 0`을 설정하거나 패딩을 감안하여 도형을 오프셋하세요
- **낮은 대비 요소를 사용하지 마세요** — 아이콘과 텍스트 모두 배경과 강한 대비가 필요합니다; 밝은 배경에 밝은 텍스트나 어두운 배경에 어두운 텍스트를 피하세요
- **절대로 제목 아래에 강조선을 사용하지 마세요** — 이것은 AI가 생성한 슬라이드의 특징입니다; 대신 여백이나 배경색을 사용하세요

---

## QA (필수)

**문제가 있다고 가정하세요. 당신의 임무는 그것을 찾는 것입니다.**

첫 번째 렌더링은 거의 정확하지 않습니다. QA를 확인 단계가 아닌 버그 사냥으로 접근하세요. 첫 번째 검사에서 문제를 하나도 발견하지 못했다면, 충분히 꼼꼼하게 보지 않은 것입니다.

### 콘텐츠 QA

```bash
python -m markitdown output.pptx
```

누락된 콘텐츠, 오타, 잘못된 순서를 확인하세요.

**템플릿 사용 시 남은 플레이스홀더 텍스트를 확인하세요:**

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

grep이 결과를 반환하면, 성공을 선언하기 전에 수정하세요.

### 시각적 QA

**서브에이전트를 사용하세요** — 2-3개 슬라이드라도. 코드를 계속 보았기 때문에 실제로 있는 것이 아니라 기대하는 것을 보게 됩니다. 서브에이전트는 새로운 시각을 가지고 있습니다.

슬라이드를 이미지로 변환한 다음([이미지로 변환](#이미지로-변환) 참조), 이 프롬프트를 사용하세요:

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images:
1. /path/to/slide-01.jpg (Expected: [brief description])
2. /path/to/slide-02.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.
```

### 검증 루프

1. 슬라이드 생성 → 이미지로 변환 → 검사
2. **발견된 문제 목록** (문제를 발견하지 못했다면, 더 비판적으로 다시 살펴보세요)
3. 문제 수정
4. **영향받은 슬라이드 재검증** — 하나의 수정이 종종 다른 문제를 만듭니다
5. 전체 점검에서 새로운 문제가 없을 때까지 반복

**최소한 한 번의 수정-검증 사이클을 완료할 때까지 성공을 선언하지 마세요.**

---

## 이미지로 변환

시각적 검사를 위해 프레젠테이션을 개별 슬라이드 이미지로 변환합니다:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

이렇게 하면 `slide-01.jpg`, `slide-02.jpg` 등이 생성됩니다.

수정 후 특정 슬라이드를 다시 렌더링하려면:

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## 의존성

- `pip install "markitdown[pptx]"` - 텍스트 추출
- `pip install Pillow` - 썸네일 그리드
- `npm install -g pptxgenjs` - 처음부터 생성
- LibreOffice (`soffice`) - PDF 변환 (샌드박스 환경에서 `scripts/office/soffice.py`를 통해 자동 구성)
- Poppler (`pdftoppm`) - PDF를 이미지로 변환
