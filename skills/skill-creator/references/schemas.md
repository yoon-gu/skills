# JSON 스키마

이 문서는 skill-creator에서 사용하는 JSON 스키마를 정의합니다.

---

## evals.json

스킬의 평가를 정의합니다. 스킬 디렉토리 내 `evals/evals.json`에 위치합니다.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Description of expected result",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "The output includes X",
        "The skill used script Y"
      ]
    }
  ]
}
```

**필드:**
- `skill_name`: 스킬의 프론트매터와 일치하는 이름
- `evals[].id`: 고유 정수 식별자
- `evals[].prompt`: 실행할 작업
- `evals[].expected_output`: 사람이 읽을 수 있는 성공 설명
- `evals[].files`: 선택 사항, 입력 파일 경로 목록 (스킬 루트 기준 상대 경로)
- `evals[].expectations`: 검증 가능한 진술 목록

---

## history.json

개선 모드에서 버전 진행을 추적합니다. 작업 공간 루트에 위치합니다.

```json
{
  "started_at": "2026-01-15T10:30:00Z",
  "skill_name": "pdf",
  "current_best": "v2",
  "iterations": [
    {
      "version": "v0",
      "parent": null,
      "expectation_pass_rate": 0.65,
      "grading_result": "baseline",
      "is_current_best": false
    },
    {
      "version": "v1",
      "parent": "v0",
      "expectation_pass_rate": 0.75,
      "grading_result": "won",
      "is_current_best": false
    },
    {
      "version": "v2",
      "parent": "v1",
      "expectation_pass_rate": 0.85,
      "grading_result": "won",
      "is_current_best": true
    }
  ]
}
```

**필드:**
- `started_at`: 개선이 시작된 ISO 타임스탬프
- `skill_name`: 개선 중인 스킬의 이름
- `current_best`: 최고 성능 버전의 식별자
- `iterations[].version`: 버전 식별자 (v0, v1, ...)
- `iterations[].parent`: 파생된 부모 버전
- `iterations[].expectation_pass_rate`: 채점에서의 통과율
- `iterations[].grading_result`: "baseline", "won", "lost", 또는 "tie"
- `iterations[].is_current_best`: 현재 최고 버전인지 여부

---

## grading.json

채점 에이전트의 출력입니다. `<run-dir>/grading.json`에 위치합니다.

```json
{
  "expectations": [
    {
      "text": "The output includes the name 'John Smith'",
      "passed": true,
      "evidence": "Found in transcript Step 3: 'Extracted names: John Smith, Sarah Johnson'"
    },
    {
      "text": "The spreadsheet has a SUM formula in cell B10",
      "passed": false,
      "evidence": "No spreadsheet was created. The output was a text file."
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "execution_metrics": {
    "tool_calls": {
      "Read": 5,
      "Write": 2,
      "Bash": 8
    },
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0,
    "output_chars": 12450,
    "transcript_chars": 3200
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "grader_duration_seconds": 26.0,
    "total_duration_seconds": 191.0
  },
  "claims": [
    {
      "claim": "The form has 12 fillable fields",
      "type": "factual",
      "verified": true,
      "evidence": "Counted 12 fields in field_info.json"
    }
  ],
  "user_notes_summary": {
    "uncertainties": ["Used 2023 data, may be stale"],
    "needs_review": [],
    "workarounds": ["Fell back to text overlay for non-fillable fields"]
  },
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "The output includes the name 'John Smith'",
        "reason": "A hallucinated document that mentions the name would also pass"
      }
    ],
    "overall": "Assertions check presence but not correctness."
  }
}
```

**필드:**
- `expectations[]`: 증거와 함께 채점된 기대 사항
- `summary`: 통과/실패 집계 수
- `execution_metrics`: 도구 사용 및 출력 크기 (실행기의 metrics.json에서)
- `timing`: 실시간 타이밍 (timing.json에서)
- `claims`: 출력에서 추출 및 검증된 주장
- `user_notes_summary`: 실행기가 표시한 문제
- `eval_feedback`: (선택 사항) 평가에 대한 개선 제안, 채점기가 제기할 가치가 있는 문제를 식별한 경우에만 존재

---

## metrics.json

실행기 에이전트의 출력입니다. `<run-dir>/outputs/metrics.json`에 위치합니다.

```json
{
  "tool_calls": {
    "Read": 5,
    "Write": 2,
    "Bash": 8,
    "Edit": 1,
    "Glob": 2,
    "Grep": 0
  },
  "total_tool_calls": 18,
  "total_steps": 6,
  "files_created": ["filled_form.pdf", "field_values.json"],
  "errors_encountered": 0,
  "output_chars": 12450,
  "transcript_chars": 3200
}
```

**필드:**
- `tool_calls`: 도구 유형별 횟수
- `total_tool_calls`: 모든 도구 호출의 합계
- `total_steps`: 주요 실행 단계 수
- `files_created`: 생성된 출력 파일 목록
- `errors_encountered`: 실행 중 발생한 오류 수
- `output_chars`: 출력 파일의 전체 문자 수
- `transcript_chars`: 트랜스크립트의 문자 수

---

## timing.json

실행의 실시간 타이밍입니다. `<run-dir>/timing.json`에 위치합니다.

**캡처 방법:** 서브에이전트 작업이 완료되면, 작업 알림에 `total_tokens`와 `duration_ms`가 포함됩니다. 즉시 저장하세요 — 다른 곳에 영구적으로 저장되지 않으며 이후에 복구할 수 없습니다.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3,
  "executor_start": "2026-01-15T10:30:00Z",
  "executor_end": "2026-01-15T10:32:45Z",
  "executor_duration_seconds": 165.0,
  "grader_start": "2026-01-15T10:32:46Z",
  "grader_end": "2026-01-15T10:33:12Z",
  "grader_duration_seconds": 26.0
}
```

---

## benchmark.json

벤치마크 모드의 출력입니다. `benchmarks/<timestamp>/benchmark.json`에 위치합니다.

```json
{
  "metadata": {
    "skill_name": "pdf",
    "skill_path": "/path/to/pdf",
    "executor_model": "claude-sonnet-4-20250514",
    "analyzer_model": "most-capable-model",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },

  "runs": [
    {
      "eval_id": 1,
      "eval_name": "Ocean",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "tool_calls": 18,
        "errors": 0
      },
      "expectations": [
        {"text": "...", "passed": true, "evidence": "..."}
      ],
      "notes": [
        "Used 2023 data, may be stale",
        "Fell back to text overlay for non-fillable fields"
      ]
    }
  ],

  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05, "min": 0.80, "max": 0.90},
      "time_seconds": {"mean": 45.0, "stddev": 12.0, "min": 32.0, "max": 58.0},
      "tokens": {"mean": 3800, "stddev": 400, "min": 3200, "max": 4100}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08, "min": 0.28, "max": 0.45},
      "time_seconds": {"mean": 32.0, "stddev": 8.0, "min": 24.0, "max": 42.0},
      "tokens": {"mean": 2100, "stddev": 300, "min": 1800, "max": 2500}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },

  "notes": [
    "Assertion 'Output is a PDF file' passes 100% in both configurations - may not differentiate skill value",
    "Eval 3 shows high variance (50% ± 40%) - may be flaky or model-dependent",
    "Without-skill runs consistently fail on table extraction expectations",
    "Skill adds 13s average execution time but improves pass rate by 50%"
  ]
}
```

**필드:**
- `metadata`: 벤치마크 실행에 대한 정보
  - `skill_name`: 스킬의 이름
  - `timestamp`: 벤치마크가 실행된 시점
  - `evals_run`: 평가 이름 또는 ID 목록
  - `runs_per_configuration`: 구성당 실행 횟수 (예: 3)
- `runs[]`: 개별 실행 결과
  - `eval_id`: 숫자 평가 식별자
  - `eval_name`: 사람이 읽을 수 있는 평가 이름 (뷰어에서 섹션 헤더로 사용)
  - `configuration`: 반드시 `"with_skill"` 또는 `"without_skill"` (뷰어가 이 정확한 문자열을 그룹화 및 색상 코딩에 사용)
  - `run_number`: 정수 실행 번호 (1, 2, 3...)
  - `result`: `pass_rate`, `passed`, `total`, `time_seconds`, `tokens`, `errors`를 포함한 중첩 객체
- `run_summary`: 구성별 통계 집계
  - `with_skill` / `without_skill`: 각각 `mean`과 `stddev` 필드를 가진 `pass_rate`, `time_seconds`, `tokens` 객체 포함
  - `delta`: `"+0.50"`, `"+13.0"`, `"+1700"` 같은 차이 문자열
- `notes`: 분석기의 자유 형식 관찰

**중요:** 뷰어는 이 필드 이름을 정확히 읽습니다. `configuration` 대신 `config`를 사용하거나, `pass_rate`를 `result` 아래가 아닌 실행의 최상위 수준에 놓으면 뷰어가 빈/영 값을 표시합니다. benchmark.json을 수동으로 생성할 때 항상 이 스키마를 참조하세요.

---

## comparison.json

블라인드 비교기의 출력입니다. `<grading-dir>/comparison-N.json`에 위치합니다.

```json
{
  "winner": "A",
  "reasoning": "Output A provides a complete solution with proper formatting and all required fields. Output B is missing the date field and has formatting inconsistencies.",
  "rubric": {
    "A": {
      "content": {
        "correctness": 5,
        "completeness": 5,
        "accuracy": 4
      },
      "structure": {
        "organization": 4,
        "formatting": 5,
        "usability": 4
      },
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content": {
        "correctness": 3,
        "completeness": 2,
        "accuracy": 3
      },
      "structure": {
        "organization": 3,
        "formatting": 2,
        "usability": 3
      },
      "content_score": 2.7,
      "structure_score": 2.7,
      "overall_score": 5.4
    }
  },
  "output_quality": {
    "A": {
      "score": 9,
      "strengths": ["Complete solution", "Well-formatted", "All fields present"],
      "weaknesses": ["Minor style inconsistency in header"]
    },
    "B": {
      "score": 5,
      "strengths": ["Readable output", "Correct basic structure"],
      "weaknesses": ["Missing date field", "Formatting inconsistencies", "Partial data extraction"]
    }
  },
  "expectation_results": {
    "A": {
      "passed": 4,
      "total": 5,
      "pass_rate": 0.80,
      "details": [
        {"text": "Output includes name", "passed": true}
      ]
    },
    "B": {
      "passed": 3,
      "total": 5,
      "pass_rate": 0.60,
      "details": [
        {"text": "Output includes name", "passed": true}
      ]
    }
  }
}
```

---

## analysis.json

사후 분석기의 출력입니다. `<grading-dir>/analysis.json`에 위치합니다.

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner/skill",
    "loser_skill": "path/to/loser/skill",
    "comparator_reasoning": "Brief summary of why comparator chose winner"
  },
  "winner_strengths": [
    "Clear step-by-step instructions for handling multi-page documents",
    "Included validation script that caught formatting errors"
  ],
  "loser_weaknesses": [
    "Vague instruction 'process the document appropriately' led to inconsistent behavior",
    "No script for validation, agent had to improvise"
  ],
  "instruction_following": {
    "winner": {
      "score": 9,
      "issues": ["Minor: skipped optional logging step"]
    },
    "loser": {
      "score": 6,
      "issues": [
        "Did not use the skill's formatting template",
        "Invented own approach instead of following step 3"
      ]
    }
  },
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Replace 'process the document appropriately' with explicit steps",
      "expected_impact": "Would eliminate ambiguity that caused inconsistent behavior"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "Read skill -> Followed 5-step process -> Used validation script",
    "loser_execution_pattern": "Read skill -> Unclear on approach -> Tried 3 different methods"
  }
}
```
