# PptxGenJS 튜토리얼

## 설정 및 기본 구조

```javascript
const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';  // or 'LAYOUT_16x10', 'LAYOUT_4x3', 'LAYOUT_WIDE'
pres.author = 'Your Name';
pres.title = 'Presentation Title';

let slide = pres.addSlide();
slide.addText("Hello World!", { x: 0.5, y: 0.5, fontSize: 36, color: "363636" });

pres.writeFile({ fileName: "Presentation.pptx" });
```

## 레이아웃 치수

슬라이드 치수 (좌표 단위: 인치):
- `LAYOUT_16x9`: 10" x 5.625" (기본값)
- `LAYOUT_16x10`: 10" x 6.25"
- `LAYOUT_4x3`: 10" x 7.5"
- `LAYOUT_WIDE`: 13.3" x 7.5"

---

## 텍스트 및 서식

```javascript
// Basic text
slide.addText("Simple Text", {
  x: 1, y: 1, w: 8, h: 2, fontSize: 24, fontFace: "Arial",
  color: "363636", bold: true, align: "center", valign: "middle"
});

// Character spacing (use charSpacing, not letterSpacing which is silently ignored)
slide.addText("SPACED TEXT", { x: 1, y: 1, w: 8, h: 1, charSpacing: 6 });

// Rich text arrays
slide.addText([
  { text: "Bold ", options: { bold: true } },
  { text: "Italic ", options: { italic: true } }
], { x: 1, y: 3, w: 8, h: 1 });

// Multi-line text (requires breakLine: true)
slide.addText([
  { text: "Line 1", options: { breakLine: true } },
  { text: "Line 2", options: { breakLine: true } },
  { text: "Line 3" }  // Last item doesn't need breakLine
], { x: 0.5, y: 0.5, w: 8, h: 2 });

// Text box margin (internal padding)
slide.addText("Title", {
  x: 0.5, y: 0.3, w: 9, h: 0.6,
  margin: 0  // Use 0 when aligning text with other elements like shapes or icons
});
```

**팁:** 텍스트 박스는 기본적으로 내부 여백이 있습니다. 동일한 x 위치에 있는 도형, 선 또는 아이콘과 텍스트를 정확하게 정렬해야 할 때는 `margin: 0`으로 설정하세요.

---

## 목록 및 글머리 기호

```javascript
// ✅ CORRECT: Multiple bullets
slide.addText([
  { text: "First item", options: { bullet: true, breakLine: true } },
  { text: "Second item", options: { bullet: true, breakLine: true } },
  { text: "Third item", options: { bullet: true } }
], { x: 0.5, y: 0.5, w: 8, h: 3 });

// ❌ WRONG: Never use unicode bullets
slide.addText("• First item", { ... });  // Creates double bullets

// Sub-items and numbered lists
{ text: "Sub-item", options: { bullet: true, indentLevel: 1 } }
{ text: "First", options: { bullet: { type: "number" }, breakLine: true } }
```

---

## 도형

```javascript
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.8, w: 1.5, h: 3.0,
  fill: { color: "FF0000" }, line: { color: "000000", width: 2 }
});

slide.addShape(pres.shapes.OVAL, { x: 4, y: 1, w: 2, h: 2, fill: { color: "0000FF" } });

slide.addShape(pres.shapes.LINE, {
  x: 1, y: 3, w: 5, h: 0, line: { color: "FF0000", width: 3, dashType: "dash" }
});

// With transparency
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "0088CC", transparency: 50 }
});

// Rounded rectangle (rectRadius only works with ROUNDED_RECTANGLE, not RECTANGLE)
// ⚠️ Don't pair with rectangular accent overlays — they won't cover rounded corners. Use RECTANGLE instead.
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "FFFFFF" }, rectRadius: 0.1
});

// With shadow
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "FFFFFF" },
  shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.15 }
});
```

그림자 옵션:

| 속성 | 타입 | 범위 | 비고 |
|------|------|------|------|
| `type` | string | `"outer"`, `"inner"` | |
| `color` | string | 6자리 hex (예: `"000000"`) | `#` 접두사 없음, 8자리 hex 안 됨 - 일반적인 실수 참조 |
| `blur` | number | 0-100 pt | |
| `offset` | number | 0-200 pt | **반드시 음이 아닌 값** - 음수 값은 파일을 손상시킴 |
| `angle` | number | 0-359도 | 그림자가 떨어지는 방향 (135 = 오른쪽 아래, 270 = 위쪽) |
| `opacity` | number | 0.0-1.0 | 투명도에 사용, 색상 문자열에 절대 인코딩하지 마세요 |

그림자를 위로 표시하려면(예: 푸터 바), 양수 offset과 함께 `angle: 270`을 사용하세요 - 음수 offset을 사용하지 **마세요**.

**참고**: 그라데이션 채우기는 기본적으로 지원되지 않습니다. 대신 그라데이션 이미지를 배경으로 사용하세요.

---

## 이미지

### 이미지 소스

```javascript
// From file path
slide.addImage({ path: "images/chart.png", x: 1, y: 1, w: 5, h: 3 });

// From URL
slide.addImage({ path: "https://example.com/image.jpg", x: 1, y: 1, w: 5, h: 3 });

// From base64 (faster, no file I/O)
slide.addImage({ data: "image/png;base64,iVBORw0KGgo...", x: 1, y: 1, w: 5, h: 3 });
```

### 이미지 옵션

```javascript
slide.addImage({
  path: "image.png",
  x: 1, y: 1, w: 5, h: 3,
  rotate: 45,              // 0-359 degrees
  rounding: true,          // Circular crop
  transparency: 50,        // 0-100
  flipH: true,             // Horizontal flip
  flipV: false,            // Vertical flip
  altText: "Description",  // Accessibility
  hyperlink: { url: "https://example.com" }
});
```

### 이미지 크기 조정 모드

```javascript
// Contain - fit inside, preserve ratio
{ sizing: { type: 'contain', w: 4, h: 3 } }

// Cover - fill area, preserve ratio (may crop)
{ sizing: { type: 'cover', w: 4, h: 3 } }

// Crop - cut specific portion
{ sizing: { type: 'crop', x: 0.5, y: 0.5, w: 2, h: 2 } }
```

### 치수 계산 (가로세로 비율 유지)

```javascript
const origWidth = 1978, origHeight = 923, maxHeight = 3.0;
const calcWidth = maxHeight * (origWidth / origHeight);
const centerX = (10 - calcWidth) / 2;

slide.addImage({ path: "image.png", x: centerX, y: 1.2, w: calcWidth, h: maxHeight });
```

### 지원 형식

- **표준**: PNG, JPG, GIF (애니메이션 GIF는 Microsoft 365에서 작동)
- **SVG**: 최신 PowerPoint/Microsoft 365에서 작동

---

## 아이콘

react-icons를 사용하여 SVG 아이콘을 생성한 다음, 범용 호환성을 위해 PNG로 래스터화합니다.

### 설정

```javascript
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { FaCheckCircle, FaChartLine } = require("react-icons/fa");

function renderIconSvg(IconComponent, color = "#000000", size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}
```

### 슬라이드에 아이콘 추가

```javascript
const iconData = await iconToBase64Png(FaCheckCircle, "#4472C4", 256);

slide.addImage({
  data: iconData,
  x: 1, y: 1, w: 0.5, h: 0.5  // Size in inches
});
```

**참고**: 선명한 아이콘을 위해 크기 256 이상을 사용하세요. 크기 매개변수는 래스터화 해상도를 제어하며, 슬라이드의 표시 크기(`w`와 `h`, 인치 단위)와는 다릅니다.

### 아이콘 라이브러리

설치: `npm install -g react-icons react react-dom sharp`

react-icons의 인기 아이콘 세트:
- `react-icons/fa` - Font Awesome
- `react-icons/md` - Material Design
- `react-icons/hi` - Heroicons
- `react-icons/bi` - Bootstrap Icons

---

## 슬라이드 배경

```javascript
// Solid color
slide.background = { color: "F1F1F1" };

// Color with transparency
slide.background = { color: "FF3399", transparency: 50 };

// Image from URL
slide.background = { path: "https://example.com/bg.jpg" };

// Image from base64
slide.background = { data: "image/png;base64,iVBORw0KGgo..." };
```

---

## 테이블

```javascript
slide.addTable([
  ["Header 1", "Header 2"],
  ["Cell 1", "Cell 2"]
], {
  x: 1, y: 1, w: 8, h: 2,
  border: { pt: 1, color: "999999" }, fill: { color: "F1F1F1" }
});

// Advanced with merged cells
let tableData = [
  [{ text: "Header", options: { fill: { color: "6699CC" }, color: "FFFFFF", bold: true } }, "Cell"],
  [{ text: "Merged", options: { colspan: 2 } }]
];
slide.addTable(tableData, { x: 1, y: 3.5, w: 8, colW: [4, 4] });
```

---

## 차트

```javascript
// Bar chart
slide.addChart(pres.charts.BAR, [{
  name: "Sales", labels: ["Q1", "Q2", "Q3", "Q4"], values: [4500, 5500, 6200, 7100]
}], {
  x: 0.5, y: 0.6, w: 6, h: 3, barDir: 'col',
  showTitle: true, title: 'Quarterly Sales'
});

// Line chart
slide.addChart(pres.charts.LINE, [{
  name: "Temp", labels: ["Jan", "Feb", "Mar"], values: [32, 35, 42]
}], { x: 0.5, y: 4, w: 6, h: 3, lineSize: 3, lineSmooth: true });

// Pie chart
slide.addChart(pres.charts.PIE, [{
  name: "Share", labels: ["A", "B", "Other"], values: [35, 45, 20]
}], { x: 7, y: 1, w: 5, h: 4, showPercent: true });
```

### 더 보기 좋은 차트

기본 차트는 구식으로 보입니다. 현대적이고 깔끔한 외관을 위해 다음 옵션을 적용하세요:

```javascript
slide.addChart(pres.charts.BAR, chartData, {
  x: 0.5, y: 1, w: 9, h: 4, barDir: "col",

  // Custom colors (match your presentation palette)
  chartColors: ["0D9488", "14B8A6", "5EEAD4"],

  // Clean background
  chartArea: { fill: { color: "FFFFFF" }, roundedCorners: true },

  // Muted axis labels
  catAxisLabelColor: "64748B",
  valAxisLabelColor: "64748B",

  // Subtle grid (value axis only)
  valGridLine: { color: "E2E8F0", size: 0.5 },
  catGridLine: { style: "none" },

  // Data labels on bars
  showValue: true,
  dataLabelPosition: "outEnd",
  dataLabelColor: "1E293B",

  // Hide legend for single series
  showLegend: false,
});
```

**주요 스타일링 옵션:**
- `chartColors: [...]` - 시리즈/세그먼트의 hex 색상
- `chartArea: { fill, border, roundedCorners }` - 차트 배경
- `catGridLine/valGridLine: { color, style, size }` - 격자선 (`style: "none"`으로 숨기기)
- `lineSmooth: true` - 곡선 (꺾은선 차트)
- `legendPos: "r"` - 범례 위치: "b", "t", "l", "r", "tr"

---

## 슬라이드 마스터

```javascript
pres.defineSlideMaster({
  title: 'TITLE_SLIDE', background: { color: '283A5E' },
  objects: [{
    placeholder: { options: { name: 'title', type: 'title', x: 1, y: 2, w: 8, h: 2 } }
  }]
});

let titleSlide = pres.addSlide({ masterName: "TITLE_SLIDE" });
titleSlide.addText("My Title", { placeholder: "title" });
```

---

## 일반적인 실수

이 문제들은 파일 손상, 시각적 버그 또는 깨진 출력을 유발합니다. 피하세요.

1. **hex 색상에 "#"을 절대 사용하지 마세요** - 파일 손상을 유발합니다
   ```javascript
   color: "FF0000"      // ✅ CORRECT
   color: "#FF0000"     // ❌ WRONG
   ```

2. **hex 색상 문자열에 불투명도를 절대 인코딩하지 마세요** - 8자리 색상(예: `"00000020"`)은 파일을 손상시킵니다. 대신 `opacity` 속성을 사용하세요.
   ```javascript
   shadow: { type: "outer", blur: 6, offset: 2, color: "00000020" }          // ❌ CORRUPTS FILE
   shadow: { type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.12 }  // ✅ CORRECT
   ```

3. **`bullet: true`를 사용하세요** - "•"같은 유니코드 기호를 절대 사용하지 마세요 (이중 글머리 기호 생성)

4. **배열 항목 사이에 `breakLine: true`를 사용하세요** 그렇지 않으면 텍스트가 함께 실행됩니다

5. **글머리 기호와 함께 `lineSpacing`을 피하세요** - 과도한 간격을 유발합니다; 대신 `paraSpaceAfter`를 사용하세요

6. **각 프레젠테이션에는 새 인스턴스가 필요합니다** - `pptxgen()` 객체를 재사용하지 마세요

7. **호출 간에 옵션 객체를 절대 재사용하지 마세요** - PptxGenJS는 객체를 내부에서 변경합니다(예: 그림자 값을 EMU로 변환). 여러 호출 간에 하나의 객체를 공유하면 두 번째 도형이 손상됩니다.
   ```javascript
   const shadow = { type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 };
   slide.addShape(pres.shapes.RECTANGLE, { shadow, ... });  // ❌ second call gets already-converted values
   slide.addShape(pres.shapes.RECTANGLE, { shadow, ... });

   const makeShadow = () => ({ type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 });
   slide.addShape(pres.shapes.RECTANGLE, { shadow: makeShadow(), ... });  // ✅ fresh object each time
   slide.addShape(pres.shapes.RECTANGLE, { shadow: makeShadow(), ... });
   ```

8. **`ROUNDED_RECTANGLE`를 악센트 테두리와 함께 사용하지 마세요** - 직사각형 오버레이 바가 둥근 모서리를 덮지 못합니다. 대신 `RECTANGLE`을 사용하세요.
   ```javascript
   // ❌ WRONG: Accent bar doesn't cover rounded corners
   slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 1, y: 1, w: 3, h: 1.5, fill: { color: "FFFFFF" } });
   slide.addShape(pres.shapes.RECTANGLE, { x: 1, y: 1, w: 0.08, h: 1.5, fill: { color: "0891B2" } });

   // ✅ CORRECT: Use RECTANGLE for clean alignment
   slide.addShape(pres.shapes.RECTANGLE, { x: 1, y: 1, w: 3, h: 1.5, fill: { color: "FFFFFF" } });
   slide.addShape(pres.shapes.RECTANGLE, { x: 1, y: 1, w: 0.08, h: 1.5, fill: { color: "0891B2" } });
   ```

---

## 빠른 참조

- **도형**: RECTANGLE, OVAL, LINE, ROUNDED_RECTANGLE
- **차트**: BAR, LINE, PIE, DOUGHNUT, SCATTER, BUBBLE, RADAR
- **레이아웃**: LAYOUT_16x9 (10"x5.625"), LAYOUT_16x10, LAYOUT_4x3, LAYOUT_WIDE
- **정렬**: "left", "center", "right"
- **차트 데이터 레이블**: "outEnd", "inEnd", "center"
