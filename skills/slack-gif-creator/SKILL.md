---
name: slack-gif-creator
description: Slack에 최적화된 애니메이션 GIF를 만들기 위한 지식과 유틸리티. 제약 조건, 검증 도구 및 애니메이션 개념을 제공합니다. 사용자가 "Slack용으로 X가 Y하는 GIF 만들어줘"와 같이 Slack용 애니메이션 GIF를 요청할 때 사용하세요.
license: Complete terms in LICENSE.txt
---

# Slack GIF 생성기

Slack에 최적화된 애니메이션 GIF를 만들기 위한 유틸리티와 지식을 제공하는 툴킷입니다.

## Slack 요구 사항

**크기:**
- 이모지 GIF: 128x128 (권장)
- 메시지 GIF: 480x480

**매개변수:**
- FPS: 10-30 (낮을수록 파일 크기가 작음)
- 색상: 48-128 (적을수록 파일 크기가 작음)
- 길이: 이모지 GIF의 경우 3초 미만 유지

## 핵심 워크플로우

```python
from core.gif_builder import GIFBuilder
from PIL import Image, ImageDraw

# 1. Create builder
builder = GIFBuilder(width=128, height=128, fps=10)

# 2. Generate frames
for i in range(12):
    frame = Image.new('RGB', (128, 128), (240, 248, 255))
    draw = ImageDraw.Draw(frame)

    # Draw your animation using PIL primitives
    # (circles, polygons, lines, etc.)

    builder.add_frame(frame)

# 3. Save with optimization
builder.save('output.gif', num_colors=48, optimize_for_emoji=True)
```

## 그래픽 그리기

### 사용자 업로드 이미지 작업
사용자가 이미지를 업로드한 경우, 의도를 파악하세요:
- **직접 사용** (예: "이것을 애니메이션으로 만들어줘", "이것을 프레임으로 분할해줘")
- **영감으로 사용** (예: "이것과 비슷하게 만들어줘")

PIL을 사용하여 이미지를 불러오고 작업하세요:
```python
from PIL import Image

uploaded = Image.open('file.png')
# Use directly, or just as reference for colors/style
```

### 처음부터 그리기
처음부터 그래픽을 그릴 때는 PIL ImageDraw 기본 도형을 사용하세요:

```python
from PIL import ImageDraw

draw = ImageDraw.Draw(frame)

# Circles/ovals
draw.ellipse([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)

# Stars, triangles, any polygon
points = [(x1, y1), (x2, y2), (x3, y3), ...]
draw.polygon(points, fill=(r, g, b), outline=(r, g, b), width=3)

# Lines
draw.line([(x1, y1), (x2, y2)], fill=(r, g, b), width=5)

# Rectangles
draw.rectangle([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)
```

**사용하지 마세요:** 이모지 폰트(플랫폼 간 불안정) 또는 이 스킬에 미리 패키지된 그래픽이 있다고 가정하는 것.

### 그래픽을 보기 좋게 만들기

그래픽은 기본적인 수준이 아닌, 세련되고 창의적으로 보여야 합니다. 방법은 다음과 같습니다:

**두꺼운 선 사용** - 외곽선과 선에는 항상 `width=2` 이상으로 설정하세요. 얇은 선(width=1)은 거칠고 아마추어처럼 보입니다.

**시각적 깊이 추가**:
- 배경에 그라데이션 사용 (`create_gradient_background`)
- 복잡한 표현을 위해 여러 도형을 겹쳐 사용 (예: 큰 별 안에 작은 별)

**도형을 더 흥미롭게 만들기**:
- 단순한 원만 그리지 마세요 - 하이라이트, 링 또는 패턴을 추가하세요
- 별에 광채 효과를 줄 수 있습니다 (뒤에 더 크고 반투명한 버전을 그리기)
- 여러 도형을 조합하세요 (별 + 반짝임, 원 + 링)

**색상에 주의하세요**:
- 생동감 있고 보색 관계의 색상을 사용하세요
- 대비를 추가하세요 (밝은 도형에 어두운 외곽선, 어두운 도형에 밝은 외곽선)
- 전체적인 구도를 고려하세요

**복잡한 도형의 경우** (하트, 눈송이 등):
- 다각형과 타원의 조합을 사용하세요
- 대칭을 위해 점을 정확하게 계산하세요
- 세부 사항을 추가하세요 (하트에 하이라이트 곡선, 눈송이에 정교한 가지)

창의적이고 세밀하게 만드세요! 좋은 Slack GIF는 임시 그래픽이 아닌 세련된 모습이어야 합니다.

## 사용 가능한 유틸리티

### GIFBuilder (`core.gif_builder`)
프레임을 조합하고 Slack에 최적화합니다:
```python
builder = GIFBuilder(width=128, height=128, fps=10)
builder.add_frame(frame)  # Add PIL Image
builder.add_frames(frames)  # Add list of frames
builder.save('out.gif', num_colors=48, optimize_for_emoji=True, remove_duplicates=True)
```

### 검증기 (`core.validators`)
GIF가 Slack 요구 사항을 충족하는지 확인합니다:
```python
from core.validators import validate_gif, is_slack_ready

# Detailed validation
passes, info = validate_gif('my.gif', is_emoji=True, verbose=True)

# Quick check
if is_slack_ready('my.gif'):
    print("Ready!")
```

### 이징 함수 (`core.easing`)
선형 대신 부드러운 움직임을 제공합니다:
```python
from core.easing import interpolate

# Progress from 0.0 to 1.0
t = i / (num_frames - 1)

# Apply easing
y = interpolate(start=0, end=400, t=t, easing='ease_out')

# Available: linear, ease_in, ease_out, ease_in_out,
#           bounce_out, elastic_out, back_out
```

### 프레임 헬퍼 (`core.frame_composer`)
일반적인 작업을 위한 편의 함수:
```python
from core.frame_composer import (
    create_blank_frame,         # Solid color background
    create_gradient_background,  # Vertical gradient
    draw_circle,                # Helper for circles
    draw_text,                  # Simple text rendering
    draw_star                   # 5-pointed star
)
```

## 애니메이션 개념

### 흔들림/진동
진동으로 객체 위치를 오프셋합니다:
- 프레임 인덱스와 함께 `math.sin()` 또는 `math.cos()` 사용
- 자연스러운 느낌을 위해 작은 랜덤 변화 추가
- x 및/또는 y 위치에 적용

### 맥동/심장 박동
객체 크기를 리듬감 있게 조절합니다:
- 부드러운 맥동을 위해 `math.sin(t * frequency * 2 * math.pi)` 사용
- 심장 박동의 경우: 두 번의 빠른 맥동 후 정지 (사인파 조정)
- 기본 크기의 0.8에서 1.2 사이로 스케일링

### 바운스
객체가 떨어지고 튕깁니다:
- 착지에는 `interpolate()`와 `easing='bounce_out'` 사용
- 낙하(가속)에는 `easing='ease_in'` 사용
- 매 프레임마다 y 속도를 증가시켜 중력 적용

### 회전/스핀
중심을 기준으로 객체를 회전합니다:
- PIL: `image.rotate(angle, resample=Image.BICUBIC)`
- 흔들림 효과: 선형 대신 사인파를 각도에 사용

### 페이드 인/아웃
점차적으로 나타나거나 사라집니다:
- RGBA 이미지를 생성하여 알파 채널 조정
- 또는 `Image.blend(image1, image2, alpha)` 사용
- 페이드 인: 알파 0에서 1로
- 페이드 아웃: 알파 1에서 0으로

### 슬라이드
화면 밖에서 위치로 객체를 이동합니다:
- 시작 위치: 프레임 경계 밖
- 끝 위치: 목표 위치
- 부드러운 정지를 위해 `interpolate()`와 `easing='ease_out'` 사용
- 오버슈트 효과: `easing='back_out'` 사용

### 줌
줌 효과를 위한 크기 조절과 위치 지정:
- 줌 인: 0.1에서 2.0으로 스케일링, 중앙 크롭
- 줌 아웃: 2.0에서 1.0으로 스케일링
- 극적인 효과를 위해 모션 블러 추가 가능 (PIL 필터)

### 폭발/파티클 버스트
바깥으로 퍼져나가는 파티클을 생성합니다:
- 랜덤한 각도와 속도로 파티클 생성
- 각 파티클 업데이트: `x += vx`, `y += vy`
- 중력 추가: `vy += gravity_constant`
- 시간이 지남에 따라 파티클 페이드 아웃 (알파 감소)

## 최적화 전략

파일 크기를 줄여달라는 요청이 있을 때만 다음 방법 중 몇 가지를 구현하세요:

1. **프레임 수 줄이기** - 낮은 FPS (20 대신 10) 또는 짧은 길이
2. **색상 수 줄이기** - 128 대신 `num_colors=48`
3. **크기 줄이기** - 480x480 대신 128x128
4. **중복 제거** - save()에서 `remove_duplicates=True`
5. **이모지 모드** - `optimize_for_emoji=True`로 자동 최적화

```python
# Maximum optimization for emoji
builder.save(
    'emoji.gif',
    num_colors=48,
    optimize_for_emoji=True,
    remove_duplicates=True
)
```

## 철학

이 스킬이 제공하는 것:
- **지식**: Slack의 요구 사항과 애니메이션 개념
- **유틸리티**: GIFBuilder, 검증기, 이징 함수
- **유연성**: PIL 기본 도형을 사용하여 애니메이션 로직 생성

이 스킬이 제공하지 않는 것:
- 고정된 애니메이션 템플릿이나 미리 만들어진 함수
- 이모지 폰트 렌더링 (플랫폼 간 불안정)
- 스킬에 내장된 미리 패키지된 그래픽 라이브러리

**사용자 업로드에 대한 참고 사항**: 이 스킬에는 미리 만들어진 그래픽이 포함되어 있지 않지만, 사용자가 이미지를 업로드하면 PIL을 사용하여 불러오고 작업하세요 - 직접 사용할 것인지 영감으로만 사용할 것인지 사용자의 요청에 따라 판단하세요.

창의적이 되세요! 개념을 조합하고 (바운스 + 회전, 맥동 + 슬라이드 등) PIL의 모든 기능을 활용하세요.

## 의존성

```bash
pip install pillow imageio numpy
```
