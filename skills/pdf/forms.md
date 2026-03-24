**중요: 반드시 다음 단계를 순서대로 완료해야 합니다. 코드 작성으로 건너뛰지 마세요.**

PDF 양식을 작성해야 하는 경우, 먼저 PDF에 작성 가능한 양식 필드가 있는지 확인하세요. 이 파일의 디렉토리에서 다음 스크립트를 실행하세요:
 `python scripts/check_fillable_fields <file.pdf>`, 결과에 따라 "작성 가능한 필드" 또는 "작성 불가능한 필드" 섹션으로 이동하여 해당 지침을 따르세요.

# 작성 가능한 필드
PDF에 작성 가능한 양식 필드가 있는 경우:
- 이 파일의 디렉토리에서 다음 스크립트를 실행하세요: `python scripts/extract_form_field_info.py <input.pdf> <field_info.json>`. 다음 형식의 필드 목록이 포함된 JSON 파일이 생성됩니다:
```
[
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "rect": ([left, bottom, right, top] bounding box in PDF coordinates, y=0 is the bottom of the page),
    "type": ("text", "checkbox", "radio_group", or "choice"),
  },
  // Checkboxes have "checked_value" and "unchecked_value" properties:
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "type": "checkbox",
    "checked_value": (Set the field to this value to check the checkbox),
    "unchecked_value": (Set the field to this value to uncheck the checkbox),
  },
  // Radio groups have a "radio_options" list with the possible choices.
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "type": "radio_group",
    "radio_options": [
      {
        "value": (set the field to this value to select this radio option),
        "rect": (bounding box for the radio button for this option)
      },
      // Other radio options
    ]
  },
  // Multiple choice fields have a "choice_options" list with the possible choices:
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "type": "choice",
    "choice_options": [
      {
        "value": (set the field to this value to select this option),
        "text": (display text of the option)
      },
      // Other choice options
    ],
  }
]
```
- PDF를 PNG로 변환합니다(각 페이지당 하나의 이미지). 이 파일의 디렉토리에서 다음 스크립트를 실행하세요:
`python scripts/convert_pdf_to_images.py <file.pdf> <output_directory>`
그런 다음 이미지를 분석하여 각 양식 필드의 용도를 파악하세요(바운딩 박스 PDF 좌표를 이미지 좌표로 변환해야 합니다).
- 각 필드에 입력할 값이 포함된 `field_values.json` 파일을 다음 형식으로 생성하세요:
```
[
  {
    "field_id": "last_name", // Must match the field_id from `extract_form_field_info.py`
    "description": "The user's last name",
    "page": 1, // Must match the "page" value in field_info.json
    "value": "Simpson"
  },
  {
    "field_id": "Checkbox12",
    "description": "Checkbox to be checked if the user is 18 or over",
    "page": 1,
    "value": "/On" // If this is a checkbox, use its "checked_value" value to check it. If it's a radio button group, use one of the "value" values in "radio_options".
  },
  // more fields
]
```
- 이 파일의 디렉토리에서 `fill_fillable_fields.py` 스크립트를 실행하여 작성된 PDF를 생성하세요:
`python scripts/fill_fillable_fields.py <input pdf> <field_values.json> <output pdf>`
이 스크립트는 제공한 필드 ID와 값이 유효한지 검증합니다. 오류 메시지가 출력되면 해당 필드를 수정하고 다시 시도하세요.

# 작성 불가능한 필드
PDF에 작성 가능한 양식 필드가 없는 경우, 텍스트 주석을 추가합니다. 먼저 PDF 구조에서 좌표를 추출하고(더 정확함), 필요한 경우 시각적 추정으로 대체합니다.

## 1단계: 먼저 구조 추출 시도

다음 스크립트를 실행하여 텍스트 레이블, 선, 체크박스와 정확한 PDF 좌표를 추출하세요:
`python scripts/extract_form_structure.py <input.pdf> form_structure.json`

다음 내용이 포함된 JSON 파일이 생성됩니다:
- **레이블**: 정확한 좌표가 포함된 모든 텍스트 요소 (PDF 포인트 단위의 x0, top, x1, bottom)
- **선**: 행 경계를 정의하는 수평선
- **체크박스**: 체크박스인 작은 사각형 (중심 좌표 포함)
- **행 경계**: 수평선에서 계산된 행의 상단/하단 위치

**결과 확인**: `form_structure.json`에 의미 있는 레이블(양식 필드에 해당하는 텍스트 요소)이 있으면 **방법 A: 구조 기반 좌표**를 사용하세요. PDF가 스캔/이미지 기반이고 레이블이 거의 없거나 전혀 없으면 **방법 B: 시각적 추정**을 사용하세요.

---

## 방법 A: 구조 기반 좌표 (권장)

`extract_form_structure.py`가 PDF에서 텍스트 레이블을 찾은 경우 사용하세요.

### A.1: 구조 분석

form_structure.json을 읽고 다음을 식별하세요:

1. **레이블 그룹**: 하나의 레이블을 구성하는 인접 텍스트 요소 (예: "Last" + "Name")
2. **행 구조**: 유사한 `top` 값을 가진 레이블은 같은 행에 있습니다
3. **필드 열**: 입력 영역은 레이블 끝 이후에 시작됩니다 (x0 = label.x1 + gap)
4. **체크박스**: 구조에서 직접 체크박스 좌표를 사용하세요

**좌표계**: y=0이 페이지 상단에 있고 y가 아래로 증가하는 PDF 좌표.

### A.2: 누락된 요소 확인

구조 추출이 모든 양식 요소를 감지하지 못할 수 있습니다. 일반적인 경우:
- **원형 체크박스**: 사각형 직사각형만 체크박스로 감지됩니다
- **복잡한 그래픽**: 장식 요소 또는 비표준 양식 컨트롤
- **흐릿하거나 밝은 색상의 요소**: 추출되지 않을 수 있습니다

PDF 이미지에서 form_structure.json에 없는 양식 필드가 보이면, 해당 특정 필드에 대해 **시각적 분석**을 사용해야 합니다(아래 "하이브리드 방법" 참조).

### A.3: PDF 좌표로 fields.json 생성

각 필드에 대해 추출된 구조에서 입력 좌표를 계산하세요:

**텍스트 필드:**
- 입력 x0 = 레이블 x1 + 5 (레이블 뒤 작은 간격)
- 입력 x1 = 다음 레이블의 x0, 또는 행 경계
- 입력 top = 레이블 top과 동일
- 입력 bottom = 아래쪽 행 경계선, 또는 레이블 bottom + row_height

**체크박스:**
- form_structure.json에서 직접 체크박스 사각형 좌표를 사용하세요
- entry_bounding_box = [checkbox.x0, checkbox.top, checkbox.x1, checkbox.bottom]

`pdf_width`와 `pdf_height`를 사용하여 fields.json을 생성하세요(PDF 좌표를 나타냄):
```json
{
  "pages": [
    {"page_number": 1, "pdf_width": 612, "pdf_height": 792}
  ],
  "form_fields": [
    {
      "page_number": 1,
      "description": "Last name entry field",
      "field_label": "Last Name",
      "label_bounding_box": [43, 63, 87, 73],
      "entry_bounding_box": [92, 63, 260, 79],
      "entry_text": {"text": "Smith", "font_size": 10}
    },
    {
      "page_number": 1,
      "description": "US Citizen Yes checkbox",
      "field_label": "Yes",
      "label_bounding_box": [260, 200, 280, 210],
      "entry_bounding_box": [285, 197, 292, 205],
      "entry_text": {"text": "X"}
    }
  ]
}
```

**중요**: `pdf_width`/`pdf_height`와 form_structure.json에서 직접 가져온 좌표를 사용하세요.

### A.4: 바운딩 박스 검증

작성하기 전에 바운딩 박스에 오류가 없는지 확인하세요:
`python scripts/check_bounding_boxes.py fields.json`

교차하는 바운딩 박스와 글꼴 크기에 비해 너무 작은 입력 박스를 확인합니다. 보고된 오류를 모두 수정한 후 작성하세요.

---

## 방법 B: 시각적 추정 (대체)

PDF가 스캔/이미지 기반이고 구조 추출에서 사용 가능한 텍스트 레이블을 찾지 못한 경우 사용하세요(예: 모든 텍스트가 "(cid:X)" 패턴으로 표시되는 경우).

### B.1: PDF를 이미지로 변환

`python scripts/convert_pdf_to_images.py <input.pdf> <images_dir/>`

### B.2: 초기 필드 식별

각 페이지 이미지를 검사하여 양식 섹션을 식별하고 필드 위치의 **대략적인 추정치**를 얻으세요:
- 양식 필드 레이블과 대략적인 위치
- 입력 영역(텍스트 입력을 위한 선, 박스 또는 빈 공간)
- 체크박스와 대략적인 위치

각 필드에 대해 대략적인 픽셀 좌표를 기록하세요(아직 정확할 필요는 없습니다).

### B.3: 확대 정밀화 (정확도를 위해 필수)

각 필드에 대해 추정된 위치 주변 영역을 잘라내어 좌표를 정밀하게 조정하세요.

**ImageMagick을 사용하여 확대 잘라내기 생성:**
```bash
magick <page_image> -crop <width>x<height>+<x>+<y> +repage <crop_output.png>
```

설명:
- `<x>, <y>` = 잘라내기 영역의 왼쪽 상단 모서리 (대략적인 추정치에서 패딩을 뺀 값 사용)
- `<width>, <height>` = 잘라내기 영역 크기 (필드 영역 + 각 측면 ~50px 패딩)

**예시:** (100, 150) 근처로 추정된 "Name" 필드를 정밀화하려면:
```bash
magick images_dir/page_1.png -crop 300x80+50+120 +repage crops/name_field.png
```

(참고: `magick` 명령을 사용할 수 없는 경우, 동일한 인수로 `convert`를 사용해 보세요).

**잘라낸 이미지를 검사**하여 정확한 좌표를 결정하세요:
1. 입력 영역이 시작되는 정확한 픽셀 식별 (레이블 뒤)
2. 입력 영역이 끝나는 위치 식별 (다음 필드 또는 가장자리 전)
3. 입력 선/박스의 상단과 하단 식별

**잘라내기 좌표를 전체 이미지 좌표로 변환:**
- full_x = crop_x + crop_offset_x
- full_y = crop_y + crop_offset_y

예시: 잘라내기가 (50, 120)에서 시작되고 잘라낸 이미지 내에서 입력 박스가 (52, 18)에서 시작되는 경우:
- entry_x0 = 52 + 50 = 102
- entry_top = 18 + 120 = 138

**각 필드에 대해 반복**하고, 가능한 경우 인접한 필드를 하나의 잘라내기로 그룹화하세요.

### B.4: 정밀화된 좌표로 fields.json 생성

`image_width`와 `image_height`를 사용하여 fields.json을 생성하세요(이미지 좌표를 나타냄):
```json
{
  "pages": [
    {"page_number": 1, "image_width": 1700, "image_height": 2200}
  ],
  "form_fields": [
    {
      "page_number": 1,
      "description": "Last name entry field",
      "field_label": "Last Name",
      "label_bounding_box": [120, 175, 242, 198],
      "entry_bounding_box": [255, 175, 720, 218],
      "entry_text": {"text": "Smith", "font_size": 10}
    }
  ]
}
```

**중요**: `image_width`/`image_height`와 확대 분석에서 얻은 정밀화된 픽셀 좌표를 사용하세요.

### B.5: 바운딩 박스 검증

작성하기 전에 바운딩 박스에 오류가 없는지 확인하세요:
`python scripts/check_bounding_boxes.py fields.json`

교차하는 바운딩 박스와 글꼴 크기에 비해 너무 작은 입력 박스를 확인합니다. 보고된 오류를 모두 수정한 후 작성하세요.

---

## 하이브리드 방법: 구조 + 시각적

구조 추출이 대부분의 필드에서 작동하지만 일부 요소를 놓치는 경우 사용하세요(예: 원형 체크박스, 비정상적인 양식 컨트롤).

1. form_structure.json에서 감지된 필드에는 **방법 A**를 사용하세요
2. 누락된 필드의 시각적 분석을 위해 **PDF를 이미지로 변환**하세요
3. 누락된 필드에 대해 **확대 정밀화**(방법 B에서)를 사용하세요
4. **좌표 결합**: 구조 추출의 필드에는 `pdf_width`/`pdf_height`를 사용하세요. 시각적으로 추정된 필드의 경우 이미지 좌표를 PDF 좌표로 변환해야 합니다:
   - pdf_x = image_x * (pdf_width / image_width)
   - pdf_y = image_y * (pdf_height / image_height)
5. fields.json에서 **단일 좌표계를 사용**하세요 - 모두 `pdf_width`/`pdf_height`를 사용한 PDF 좌표로 변환하세요

---

## 2단계: 작성 전 검증

**항상 작성하기 전에 바운딩 박스를 검증하세요:**
`python scripts/check_bounding_boxes.py fields.json`

다음을 확인합니다:
- 교차하는 바운딩 박스 (텍스트 겹침을 유발)
- 지정된 글꼴 크기에 비해 너무 작은 입력 박스

진행하기 전에 fields.json에서 보고된 오류를 수정하세요.

## 3단계: 양식 작성

작성 스크립트가 좌표계를 자동 감지하고 변환을 처리합니다:
`python scripts/fill_pdf_form_with_annotations.py <input.pdf> fields.json <output.pdf>`

## 4단계: 출력 확인

작성된 PDF를 이미지로 변환하고 텍스트 배치를 확인하세요:
`python scripts/convert_pdf_to_images.py <output.pdf> <verify_images/>`

텍스트가 잘못 배치된 경우:
- **방법 A**: `pdf_width`/`pdf_height`와 함께 form_structure.json의 PDF 좌표를 사용하고 있는지 확인하세요
- **방법 B**: 이미지 치수가 일치하고 좌표가 정확한 픽셀인지 확인하세요
- **하이브리드**: 시각적으로 추정된 필드의 좌표 변환이 올바른지 확인하세요
