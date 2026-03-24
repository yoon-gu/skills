---
name: xlsx
description: "스프레드시트 파일이 주요 입력 또는 출력인 모든 경우에 이 스킬을 사용하세요. 기존 .xlsx, .xlsm, .csv, .tsv 파일 열기/읽기/편집/수정(열 추가, 수식 계산, 서식, 차트, 데이터 정리), 새 스프레드시트 생성, 표 형식 파일 간 변환이 포함됩니다. 사용자가 스프레드시트 파일을 이름이나 경로로 참조할 때 트리거합니다. 잘못된 행, 헤더 오류, 불필요한 데이터가 있는 표 형식 파일을 정리/재구성할 때도 사용합니다. Word 문서, HTML 보고서, Python 스크립트, DB 파이프라인, Google Sheets API 통합이 주요 산출물인 경우에는 사용하지 마세요."
license: Proprietary. LICENSE.txt has complete terms
---

# 출력물 요구사항

## 모든 Excel 파일

### 전문적인 폰트
- 사용자가 달리 지시하지 않는 한, 모든 결과물에 일관되고 전문적인 폰트(예: Arial, Times New Roman)를 사용하세요

### 수식 오류 제로
- 모든 Excel 모델은 수식 오류(#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?) 없이 제공되어야 합니다

### 기존 템플릿 유지 (템플릿 업데이트 시)
- 파일 수정 시 기존 형식, 스타일, 관례를 정확히 맞추세요
- 확립된 패턴이 있는 파일에 표준화된 서식을 강제하지 마세요
- 기존 템플릿 관례가 항상 이 가이드라인보다 우선합니다

## 재무 모델

### 색상 코딩 표준
사용자나 기존 템플릿에서 달리 명시하지 않는 한

#### 업계 표준 색상 관례
- **파란색 텍스트 (RGB: 0,0,255)**: 하드코딩된 입력값, 사용자가 시나리오를 위해 변경할 숫자
- **검은색 텍스트 (RGB: 0,0,0)**: 모든 수식 및 계산
- **초록색 텍스트 (RGB: 0,128,0)**: 같은 워크북 내 다른 워크시트에서 가져오는 링크
- **빨간색 텍스트 (RGB: 255,0,0)**: 다른 파일로의 외부 링크
- **노란색 배경 (RGB: 255,255,0)**: 주의가 필요한 핵심 가정이나 업데이트가 필요한 셀

### 숫자 서식 표준

#### 필수 서식 규칙
- **연도**: 텍스트 문자열로 서식 지정(예: "2024", "2,024" 아님)
- **통화**: $#,##0 서식 사용; 항상 헤더에 단위 명시("Revenue ($mm)")
- **제로값**: 숫자 서식으로 모든 0을 "-"로 표시, 백분율 포함(예: "$#,##0;($#,##0);-")
- **백분율**: 기본 0.0% 서식(소수점 한 자리)
- **배수**: 밸류에이션 배수(EV/EBITDA, P/E)에 0.0x 서식 사용
- **음수**: 마이너스 -123이 아닌 괄호 (123) 사용

### 수식 구성 규칙

#### 가정값 배치
- 모든 가정값(성장률, 마진, 배수 등)을 별도의 가정 셀에 배치하세요
- 수식에 하드코딩된 값 대신 셀 참조를 사용하세요
- 예: =B5*1.05 대신 =B5*(1+$B$6) 사용

#### 수식 오류 방지
- 모든 셀 참조가 올바른지 확인하세요
- 범위에서 오프바이원 오류를 확인하세요
- 모든 예측 기간에서 일관된 수식을 확보하세요
- 극단값(제로값, 음수)으로 테스트하세요
- 의도하지 않은 순환 참조가 없는지 확인하세요

#### 하드코딩 문서화 요구사항
- 셀에 주석을 달거나 옆에 기재하세요(테이블 끝인 경우). 형식: "Source: [시스템/문서], [날짜], [구체적 참조], [해당되는 경우 URL]"
- 예시:
  - "Source: Company 10-K, FY2024, Page 45, Revenue Note, [SEC EDGAR URL]"
  - "Source: Company 10-Q, Q2 2025, Exhibit 99.1, [SEC EDGAR URL]"
  - "Source: Bloomberg Terminal, 8/15/2025, AAPL US Equity"
  - "Source: FactSet, 8/20/2025, Consensus Estimates Screen"

# XLSX 생성, 편집 및 분석

## 개요

사용자가 .xlsx 파일을 생성, 편집 또는 분석하도록 요청할 수 있습니다. 다양한 작업에 사용할 수 있는 여러 도구와 워크플로우가 있습니다.

## 중요 요구사항

**수식 재계산을 위해 LibreOffice 필수**: 수식 값 재계산에 LibreOffice가 설치되어 있다고 가정할 수 있으며, `scripts/recalc.py` 스크립트를 사용합니다. 이 스크립트는 첫 실행 시 자동으로 LibreOffice를 구성하며, Unix 소켓이 제한된 샌드박스 환경도 처리합니다(`scripts/office/soffice.py`로 처리).

## 데이터 읽기 및 분석

### pandas를 사용한 데이터 분석
데이터 분석, 시각화, 기본 작업에는 강력한 데이터 조작 기능을 제공하는 **pandas**를 사용하세요:

```python
import pandas as pd

# Read Excel
df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict

# Analyze
df.head()      # Preview data
df.info()      # Column info
df.describe()  # Statistics

# Write Excel
df.to_excel('output.xlsx', index=False)
```

## Excel 파일 워크플로우

## 중요: 하드코딩된 값 대신 수식 사용

**항상 Python에서 값을 계산하고 하드코딩하는 대신 Excel 수식을 사용하세요.** 이렇게 하면 스프레드시트가 동적이고 업데이트 가능하게 유지됩니다.

### 잘못된 예 - 계산된 값 하드코딩
```python
# Bad: Calculating in Python and hardcoding result
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000

# Bad: Computing growth rate in Python
growth = (df.iloc[-1]['Revenue'] - df.iloc[0]['Revenue']) / df.iloc[0]['Revenue']
sheet['C5'] = growth  # Hardcodes 0.15

# Bad: Python calculation for average
avg = sum(values) / len(values)
sheet['D20'] = avg  # Hardcodes 42.5
```

### 올바른 예 - Excel 수식 사용
```python
# Good: Let Excel calculate the sum
sheet['B10'] = '=SUM(B2:B9)'

# Good: Growth rate as Excel formula
sheet['C5'] = '=(C4-C2)/C2'

# Good: Average using Excel function
sheet['D20'] = '=AVERAGE(D2:D19)'
```

이것은 모든 계산(합계, 백분율, 비율, 차이 등)에 적용됩니다. 스프레드시트는 원본 데이터가 변경되면 재계산할 수 있어야 합니다.

## 공통 워크플로우
1. **도구 선택**: 데이터에는 pandas, 수식/서식에는 openpyxl
2. **생성/로드**: 새 워크북 생성 또는 기존 파일 로드
3. **수정**: 데이터, 수식, 서식 추가/편집
4. **저장**: 파일로 작성
5. **수식 재계산 (수식 사용 시 필수)**: scripts/recalc.py 스크립트 사용
   ```bash
   python scripts/recalc.py output.xlsx
   ```
6. **오류 확인 및 수정**:
   - 스크립트는 오류 세부사항이 포함된 JSON을 반환합니다
   - `status`가 `errors_found`이면 `error_summary`에서 특정 오류 유형 및 위치를 확인하세요
   - 식별된 오류를 수정하고 다시 재계산하세요
   - 수정할 일반적인 오류:
     - `#REF!`: 잘못된 셀 참조
     - `#DIV/0!`: 0으로 나누기
     - `#VALUE!`: 수식에 잘못된 데이터 유형
     - `#NAME?`: 인식되지 않는 수식 이름

### 새 Excel 파일 생성

```python
# Using openpyxl for formulas and formatting
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

# Add data
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['Row', 'of', 'data'])

# Add formula
sheet['B2'] = '=SUM(A1:A10)'

# Formatting
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')

# Column width
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

### 기존 Excel 파일 편집

```python
# Using openpyxl to preserve formulas and formatting
from openpyxl import load_workbook

# Load existing file
wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName'] for specific sheet

# Working with multiple sheets
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    print(f"Sheet: {sheet_name}")

# Modify cells
sheet['A1'] = 'New Value'
sheet.insert_rows(2)  # Insert row at position 2
sheet.delete_cols(3)  # Delete column 3

# Add new sheet
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'

wb.save('modified.xlsx')
```

## 수식 재계산

openpyxl로 생성하거나 수정한 Excel 파일은 수식을 문자열로 포함하지만 계산된 값은 없습니다. 수식을 재계산하려면 제공된 `scripts/recalc.py` 스크립트를 사용하세요:

```bash
python scripts/recalc.py <excel_file> [timeout_seconds]
```

예시:
```bash
python scripts/recalc.py output.xlsx 30
```

스크립트 기능:
- 첫 실행 시 LibreOffice 매크로 자동 설정
- 모든 시트의 모든 수식 재계산
- 모든 셀에서 Excel 오류(#REF!, #DIV/0! 등) 스캔
- 세부 오류 위치 및 개수가 포함된 JSON 반환
- Linux와 macOS 모두에서 작동

## 수식 검증 체크리스트

수식이 올바르게 작동하는지 확인하기 위한 빠른 점검 사항:

### 필수 검증
- [ ] **샘플 참조 2-3개 테스트**: 전체 모델 구축 전에 올바른 값을 가져오는지 확인
- [ ] **열 매핑**: Excel 열이 일치하는지 확인(예: 64번째 열 = BL, BK가 아님)
- [ ] **행 오프셋**: Excel 행은 1부터 시작함을 기억(DataFrame 행 5 = Excel 행 6)

### 일반적인 함정
- [ ] **NaN 처리**: `pd.notna()`로 null 값 확인
- [ ] **맨 오른쪽 열**: FY 데이터는 종종 50+ 열에 있음
- [ ] **다중 일치**: 첫 번째뿐만 아니라 모든 항목 검색
- [ ] **0으로 나누기**: 수식에서 `/` 사용 전 분모 확인(#DIV/0!)
- [ ] **잘못된 참조**: 모든 셀 참조가 의도한 셀을 가리키는지 확인(#REF!)
- [ ] **시트 간 참조**: 시트 연결 시 올바른 형식(Sheet1!A1) 사용

### 수식 테스트 전략
- [ ] **소규모로 시작**: 광범위하게 적용하기 전에 2-3개 셀에서 수식 테스트
- [ ] **의존성 확인**: 수식에서 참조하는 모든 셀이 존재하는지 확인
- [ ] **극단값 테스트**: 0, 음수, 매우 큰 값 포함

### scripts/recalc.py 출력 해석
스크립트는 오류 세부사항이 포함된 JSON을 반환합니다:
```json
{
  "status": "success",           // or "errors_found"
  "total_errors": 0,              // Total error count
  "total_formulas": 42,           // Number of formulas in file
  "error_summary": {              // Only present if errors found
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

## 모범 사례

### 라이브러리 선택
- **pandas**: 데이터 분석, 대량 작업, 간단한 데이터 내보내기에 최적
- **openpyxl**: 복잡한 서식, 수식, Excel 전용 기능에 최적

### openpyxl 사용 시
- 셀 인덱스는 1부터 시작(row=1, column=1은 셀 A1을 가리킴)
- 계산된 값을 읽으려면 `data_only=True` 사용: `load_workbook('file.xlsx', data_only=True)`
- **주의**: `data_only=True`로 열어서 저장하면 수식이 값으로 대체되어 영구적으로 손실됩니다
- 대용량 파일의 경우: 읽기에 `read_only=True`, 쓰기에 `write_only=True` 사용
- 수식은 보존되지만 평가되지 않습니다 - 값을 업데이트하려면 scripts/recalc.py를 사용하세요

### pandas 사용 시
- 추론 문제를 방지하려면 데이터 유형 지정: `pd.read_excel('file.xlsx', dtype={'id': str})`
- 대용량 파일의 경우 특정 열 읽기: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- 날짜 올바르게 처리: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## 코드 스타일 가이드라인
**중요**: Excel 작업을 위한 Python 코드 생성 시:
- 불필요한 주석 없이 최소한의 간결한 Python 코드 작성
- 장황한 변수명과 불필요한 작업 피하기
- 불필요한 print문 피하기

**Excel 파일 자체에 대해**:
- 복잡한 수식이나 중요한 가정이 있는 셀에 주석 추가
- 하드코딩된 값의 데이터 출처 문서화
- 주요 계산 및 모델 섹션에 대한 메모 포함
