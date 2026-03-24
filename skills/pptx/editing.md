# 프레젠테이션 편집

## 템플릿 기반 워크플로우

기존 프레젠테이션을 템플릿으로 사용하는 경우:

1. **기존 슬라이드 분석**:
   ```bash
   python scripts/thumbnail.py template.pptx
   python -m markitdown template.pptx
   ```
   `thumbnails.jpg`를 검토하여 레이아웃을 확인하고, markitdown 출력을 검토하여 플레이스홀더 텍스트를 확인하세요.

2. **슬라이드 매핑 계획**: 각 콘텐츠 섹션에 대해 템플릿 슬라이드를 선택하세요.

   **다양한 레이아웃을 사용하세요** — 단조로운 프레젠테이션은 일반적인 실패 유형입니다. 기본적인 제목 + 글머리 기호 슬라이드만 사용하지 마세요. 다음을 적극적으로 찾으세요:
   - 다단 레이아웃 (2단, 3단)
   - 이미지 + 텍스트 조합
   - 텍스트 오버레이가 있는 전체 블리드 이미지
   - 인용문 또는 콜아웃 슬라이드
   - 섹션 구분 슬라이드
   - 통계/숫자 강조 슬라이드
   - 아이콘 그리드 또는 아이콘 + 텍스트 행

   **피하세요:** 모든 슬라이드에 동일한 텍스트 중심 레이아웃 반복.

   콘텐츠 유형을 레이아웃 스타일에 맞추세요(예: 핵심 포인트 -> 글머리 기호 슬라이드, 팀 정보 -> 다단, 추천사 -> 인용문 슬라이드).

3. **압축 해제**: `python scripts/office/unpack.py template.pptx unpacked/`

4. **프레젠테이션 구성** (서브에이전트가 아닌 직접 수행):
   - 불필요한 슬라이드 삭제 (`<p:sldIdLst>`에서 제거)
   - 재사용할 슬라이드 복제 (`add_slide.py`)
   - `<p:sldIdLst>`에서 슬라이드 재정렬
   - **5단계 전에 모든 구조적 변경을 완료하세요**

5. **콘텐츠 편집**: 각 `slide{N}.xml`의 텍스트를 업데이트하세요.
   **가능한 경우 여기서 서브에이전트를 사용하세요** — 슬라이드는 별도의 XML 파일이므로 서브에이전트가 병렬로 편집할 수 있습니다.

6. **정리**: `python scripts/clean.py unpacked/`

7. **패킹**: `python scripts/office/pack.py unpacked/ output.pptx --original template.pptx`

---

## 스크립트

| 스크립트 | 용도 |
|----------|------|
| `unpack.py` | PPTX 추출 및 정렬 출력 |
| `add_slide.py` | 슬라이드 복제 또는 레이아웃에서 생성 |
| `clean.py` | 고아 파일 제거 |
| `pack.py` | 검증과 함께 재패킹 |
| `thumbnail.py` | 슬라이드 시각적 그리드 생성 |

### unpack.py

```bash
python scripts/office/unpack.py input.pptx unpacked/
```

PPTX를 추출하고, XML을 정렬 출력하며, 스마트 따옴표를 이스케이프합니다.

### add_slide.py

```bash
python scripts/add_slide.py unpacked/ slide2.xml      # Duplicate slide
python scripts/add_slide.py unpacked/ slideLayout2.xml # From layout
```

원하는 위치의 `<p:sldIdLst>`에 추가할 `<p:sldId>`를 출력합니다.

### clean.py

```bash
python scripts/clean.py unpacked/
```

`<p:sldIdLst>`에 없는 슬라이드, 참조되지 않는 미디어, 고아 관계를 제거합니다.

### pack.py

```bash
python scripts/office/pack.py unpacked/ output.pptx --original input.pptx
```

검증, 복구, XML 압축, 스마트 따옴표 재인코딩을 수행합니다.

### thumbnail.py

```bash
python scripts/thumbnail.py input.pptx [output_prefix] [--cols N]
```

슬라이드 파일명을 레이블로 한 `thumbnails.jpg`를 생성합니다. 기본 3열, 그리드당 최대 12개.

**템플릿 분석에만 사용하세요** (레이아웃 선택). 시각적 QA의 경우, `soffice` + `pdftoppm`을 사용하여 전체 해상도 개별 슬라이드 이미지를 만드세요—SKILL.md 참조.

---

## 슬라이드 작업

슬라이드 순서는 `ppt/presentation.xml` -> `<p:sldIdLst>`에 있습니다.

**재정렬**: `<p:sldId>` 요소를 재배치하세요.

**삭제**: `<p:sldId>`를 제거한 후 `clean.py`를 실행하세요.

**추가**: `add_slide.py`를 사용하세요. 슬라이드 파일을 수동으로 복사하지 마세요—스크립트가 노트 참조, Content_Types.xml, 관계 ID 등 수동 복사에서 누락되는 항목을 처리합니다.

---

## 콘텐츠 편집

**서브에이전트:** 가능한 경우 여기서 사용하세요(4단계 완료 후). 각 슬라이드는 별도의 XML 파일이므로 서브에이전트가 병렬로 편집할 수 있습니다. 서브에이전트에 보내는 프롬프트에 다음을 포함하세요:
- 편집할 슬라이드 파일 경로
- **"모든 변경에 Edit 도구를 사용하세요"**
- 아래의 서식 규칙 및 일반적인 실수

각 슬라이드에 대해:
1. 슬라이드의 XML을 읽으세요
2. 모든 플레이스홀더 콘텐츠를 식별하세요—텍스트, 이미지, 차트, 아이콘, 캡션
3. 각 플레이스홀더를 최종 콘텐츠로 교체하세요

**sed나 Python 스크립트가 아닌 Edit 도구를 사용하세요.** Edit 도구는 무엇을 어디에서 교체할지 구체적으로 지정하도록 강제하여 더 나은 신뢰성을 제공합니다.

### 서식 규칙

- **모든 헤더, 소제목, 인라인 레이블을 굵게 처리**: `<a:rPr>`에 `b="1"`을 사용하세요. 여기에는 다음이 포함됩니다:
  - 슬라이드 제목
  - 슬라이드 내 섹션 헤더
  - 줄 시작 부분의 인라인 레이블 (예: "상태:", "설명:")
- **유니코드 글머리 기호(•)를 절대 사용하지 마세요**: `<a:buChar>` 또는 `<a:buAutoNum>`으로 적절한 목록 서식을 사용하세요
- **글머리 기호 일관성**: 레이아웃에서 글머리 기호를 상속받으세요. `<a:buChar>` 또는 `<a:buNone>`만 지정하세요.

---

## 일반적인 실수

### 템플릿 적용

소스 콘텐츠의 항목이 템플릿보다 적은 경우:
- 텍스트만 지우지 말고 **초과 요소를 완전히 제거하세요** (이미지, 도형, 텍스트 박스)
- 텍스트 콘텐츠 지운 후 고아 비주얼 확인
- 불일치하는 개수를 잡기 위해 시각적 QA 실행

다른 길이의 콘텐츠로 텍스트를 교체하는 경우:
- **짧은 교체**: 보통 안전합니다
- **긴 교체**: 오버플로우 또는 예기치 않은 줄바꿈이 발생할 수 있습니다
- 텍스트 변경 후 시각적 QA로 테스트하세요
- 템플릿의 디자인 제약에 맞게 콘텐츠를 자르거나 분할하는 것을 고려하세요

**템플릿 슬롯 != 소스 항목**: 템플릿에 팀원 4명이 있지만 소스에 사용자 3명이 있는 경우, 텍스트만이 아니라 4번째 멤버의 전체 그룹(이미지 + 텍스트 박스)을 삭제하세요.

### 다중 항목 콘텐츠

소스에 여러 항목(번호 매김 목록, 여러 섹션)이 있는 경우, 각각에 대해 별도의 `<a:p>` 요소를 만드세요 — **절대 하나의 문자열로 연결하지 마세요**.

**잘못된 예** — 모든 항목이 하나의 단락:
```xml
<a:p>
  <a:r><a:rPr .../><a:t>Step 1: Do the first thing. Step 2: Do the second thing.</a:t></a:r>
</a:p>
```

**올바른 예** — 굵은 헤더가 있는 별도의 단락:
```xml
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 1</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" .../><a:t>Do the first thing.</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 2</a:t></a:r>
</a:p>
<!-- continue pattern -->
```

줄 간격을 유지하기 위해 원본 단락에서 `<a:pPr>`을 복사하세요. 헤더에는 `b="1"`을 사용하세요.

### 스마트 따옴표

unpack/pack에서 자동으로 처리됩니다. 하지만 Edit 도구는 스마트 따옴표를 ASCII로 변환합니다.

**따옴표가 포함된 새 텍스트를 추가할 때는 XML 엔티티를 사용하세요:**

```xml
<a:t>the &#x201C;Agreement&#x201D;</a:t>
```

| 문자 | 이름 | 유니코드 | XML 엔티티 |
|------|------|----------|------------|
| `\u201c` | 왼쪽 큰따옴표 | U+201C | `&#x201C;` |
| `\u201d` | 오른쪽 큰따옴표 | U+201D | `&#x201D;` |
| `\u2018` | 왼쪽 작은따옴표 | U+2018 | `&#x2018;` |
| `\u2019` | 오른쪽 작은따옴표 | U+2019 | `&#x2019;` |

### 기타

- **공백**: 앞뒤 공백이 있는 `<a:t>`에 `xml:space="preserve"`를 사용하세요
- **XML 파싱**: `xml.etree.ElementTree`가 아닌 `defusedxml.minidom`을 사용하세요 (네임스페이스 손상)
