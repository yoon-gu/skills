# Agent SDK — Python

Claude Agent SDK는 내장 도구, 안전 기능, 에이전트 기능을 갖춘 AI 에이전트를 구축하기 위한 상위 수준 인터페이스를 제공합니다.

## 설치

```bash
pip install claude-agent-sdk
```

---

## 빠른 시작

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def main():
    async for message in query(
        prompt="Explain this codebase",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"])
    ):
        if isinstance(message, ResultMessage):
            print(message.result)

anyio.run(main)
```

---

## 내장 도구

| 도구      | 설명                          |
| --------- | ------------------------------------ |
| Read      | 워크스페이스의 파일 읽기          |
| Write     | 새 파일 생성                     |
| Edit      | 기존 파일에 정밀한 편집 수행 |
| Bash      | 셸 명령 실행               |
| Glob      | 패턴으로 파일 찾기                |
| Grep      | 내용으로 파일 검색              |
| WebSearch | 웹에서 정보 검색       |
| WebFetch        | 웹 페이지 가져오기 및 분석          |
| AskUserQuestion | 사용자에게 명확한 질문하기         |
| Agent           | 하위 에이전트 생성                      |

---

## 주요 인터페이스

### `query()` — 간단한 일회성 사용

`query()` 함수는 에이전트를 실행하는 가장 간단한 방법입니다. 메시지의 비동기 이터레이터를 반환합니다.

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async for message in query(
    prompt="Explain this codebase",
    options=ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"])
):
    if isinstance(message, ResultMessage):
        print(message.result)
```

### `ClaudeSDKClient` — 완전한 제어

`ClaudeSDKClient`는 에이전트 생명주기에 대한 완전한 제어를 제공합니다. 사용자 정의 도구, 훅, 스트리밍 또는 실행 중단 기능이 필요할 때 사용합니다.

```python
import anyio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

async def main():
    options = ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"])
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Explain this codebase")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

anyio.run(main)
```

`ClaudeSDKClient`는 다음을 지원합니다:

- **컨텍스트 매니저** (`async with`)를 통한 자동 리소스 정리
- **`client.query(prompt)`**로 에이전트에 프롬프트 전송
- **`receive_response()`**로 완료까지 메시지 스트리밍
- **`interrupt()`**로 작업 중 에이전트 실행 중단
- **사용자 정의 도구에 필수** (SDK MCP 서버를 통해)

---

## 권한 시스템

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async for message in query(
    prompt="Refactor the authentication module",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Write"],
        permission_mode="acceptEdits"  # Auto-accept file edits
    )
):
    if isinstance(message, ResultMessage):
        print(message.result)
```

권한 모드:

- `"default"`: 위험한 작업 시 확인 요청
- `"plan"`: 계획 수립만, 실행하지 않음
- `"acceptEdits"`: 파일 편집 자동 승인
- `"bypassPermissions"`: 모든 확인 건너뛰기 (주의해서 사용)

---

## MCP (Model Context Protocol) 지원

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async for message in query(
    prompt="Open example.com and describe what you see",
    options=ClaudeAgentOptions(
        mcp_servers={
            "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}
        }
    )
):
    if isinstance(message, ResultMessage):
        print(message.result)
```

---

## 훅

콜백 함수를 사용하여 훅으로 에이전트 동작을 사용자 정의합니다:

```python
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher, ResultMessage

async def log_file_change(input_data, tool_use_id, context):
    file_path = input_data.get('tool_input', {}).get('file_path', 'unknown')
    print(f"Modified: {file_path}")
    return {}

async for message in query(
    prompt="Refactor utils.py",
    options=ClaudeAgentOptions(
        permission_mode="acceptEdits",
        hooks={
            "PostToolUse": [HookMatcher(matcher="Edit|Write", hooks=[log_file_change])]
        }
    )
):
    if isinstance(message, ResultMessage):
        print(message.result)
```

도구 생명주기 이벤트(`PreToolUse`, `PostToolUse`, `PostToolUseFailure`)의 훅 콜백 입력에는 `agent_id`와 `agent_type` 필드가 포함되어, 훅이 어떤 에이전트(메인 또는 하위 에이전트)가 도구 호출을 트리거했는지 식별할 수 있습니다.

사용 가능한 훅 이벤트: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `PreCompact`, `Notification`, `SubagentStart`, `PermissionRequest`

---

## 공통 옵션

`query()`는 최상위 `prompt` (문자열)와 `options` 객체 (`ClaudeAgentOptions`)를 받습니다:

```python
async for message in query(prompt="...", options=ClaudeAgentOptions(...)):
```

| 옵션                              | 타입   | 설명                                                                |
| ----------------------------------- | ------ | -------------------------------------------------------------------------- |
| `cwd`                               | string | 파일 작업을 위한 작업 디렉터리                                      |
| `allowed_tools`                     | list   | 에이전트가 사용할 수 있는 도구 (예: `["Read", "Edit", "Bash"]`)                |
| `tools`                             | list   | 사용 가능하게 할 내장 도구 (기본 세트를 제한)               |
| `disallowed_tools`                  | list   | 명시적으로 허용하지 않을 도구                                               |
| `permission_mode`                   | string | 권한 확인 처리 방법                                           |
| `mcp_servers`                       | dict   | 연결할 MCP 서버                                                  |
| `hooks`                             | dict   | 동작 사용자 정의를 위한 훅                                             |
| `system_prompt`                     | string | 사용자 정의 시스템 프롬프트                                                       |
| `max_turns`                         | int    | 중단 전 최대 에이전트 턴 수                                        |
| `max_budget_usd`                    | float  | 쿼리의 최대 예산 (USD)                                        |
| `model`                             | string | 모델 ID (기본값: CLI에 의해 결정)                                      |
| `agents`                            | dict   | 하위 에이전트 정의 (`dict[str, AgentDefinition]`)                        |
| `output_format`                     | dict   | 구조화된 출력 스키마                                                   |
| `thinking`                          | dict   | 사고/추론 제어                                                 |
| `betas`                             | list   | 활성화할 베타 기능 (예: `["context-1m-2025-08-07"]`)               |
| `setting_sources`                   | list   | 로드할 설정 (예: `["project"]`). 기본값: 없음 (CLAUDE.md 파일 없음) |
| `env`                               | dict   | 세션에 설정할 환경 변수                               |

---

## 메시지 타입

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, SystemMessage

async for message in query(
    prompt="Find TODO comments",
    options=ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"])
):
    if isinstance(message, ResultMessage):
        print(message.result)
        print(f"Stop reason: {message.stop_reason}")  # e.g., "end_turn", "max_turns"
    elif isinstance(message, SystemMessage) and message.subtype == "init":
        session_id = message.data.get("session_id")  # Capture for resuming later
```

하위 에이전트 작업 이벤트를 처리할 때 더 나은 타입 안전성을 위해 타입이 지정된 작업 메시지 하위 클래스를 사용할 수 있습니다:
- `TaskStartedMessage` — 하위 에이전트 작업이 등록될 때 발생
- `TaskProgressMessage` — 누적 사용량 메트릭이 포함된 실시간 진행 업데이트
- `TaskNotificationMessage` — 작업 완료 알림

`RateLimitEvent`는 속도 제한 상태가 전환될 때 (예: `allowed`에서 `allowed_warning` 또는 `rejected`로) 발생합니다. 사용자에게 경고하거나 점진적으로 대기하는 데 사용합니다:

```python
from claude_agent_sdk import query, ClaudeAgentOptions, RateLimitEvent

async for message in query(prompt="...", options=ClaudeAgentOptions()):
    if isinstance(message, RateLimitEvent):
        print(f"Rate limit status: {message.rate_limit_info.status}")
        if message.rate_limit_info.resets_at:
            print(f"Resets at: {message.rate_limit_info.resets_at}")
```

---

## 하위 에이전트

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition, ResultMessage

async for message in query(
    prompt="Use the code-reviewer agent to review this codebase",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep", "Agent"],
        agents={
            "code-reviewer": AgentDefinition(
                description="Expert code reviewer for quality and security reviews.",
                prompt="Analyze code quality and suggest improvements.",
                tools=["Read", "Glob", "Grep"]
            )
        }
    )
):
    if isinstance(message, ResultMessage):
        print(message.result)
```

---

## 오류 처리

```python
from claude_agent_sdk import query, ClaudeAgentOptions, CLINotFoundError, CLIConnectionError, ResultMessage

try:
    async for message in query(
        prompt="...",
        options=ClaudeAgentOptions(allowed_tools=["Read"])
    ):
        if isinstance(message, ResultMessage):
            print(message.result)
except CLINotFoundError:
    print("Claude Code CLI not found. Install with: pip install claude-agent-sdk")
except CLIConnectionError as e:
    print(f"Connection error: {e}")
```

---

## 세션 기록

최상위 함수로 과거 세션 데이터를 조회합니다:

```python
from claude_agent_sdk import list_sessions, get_session_messages

# List all past sessions (sync function — no await)
sessions = list_sessions()
for session in sessions:
    print(f"{session.session_id}: {session.cwd}")

# Get messages from a specific session (sync function — no await)
messages = get_session_messages(session_id="...")
for msg in messages:
    print(msg)
```

### 세션 변경

세션 이름 변경 또는 태그 지정 (동기 함수 — await 불필요):

```python
from claude_agent_sdk import rename_session, tag_session

# Rename a session
rename_session(session_id="...", title="My refactoring session")

# Tag a session (tags are Unicode-sanitized automatically)
tag_session(session_id="...", tag="experiment")

# Clear a tag
tag_session(session_id="...", tag=None)

# Optionally scope to a specific project directory
rename_session(session_id="...", title="New title", directory="/path/to/project")
```

---

## MCP 서버 관리

`ClaudeSDKClient`를 사용하여 런타임에 MCP 서버를 관리합니다:

```python
async with ClaudeSDKClient(options=options) as client:
    # Reconnect a disconnected MCP server
    await client.reconnect_mcp_server("my-server")

    # Toggle an MCP server on/off
    await client.toggle_mcp_server("my-server", enabled=False)

    # Get status of all MCP servers
    status = await client.get_mcp_status()  # returns McpStatusResponse
```

---

## 모범 사례

1. **항상 allowed_tools를 지정** — 에이전트가 사용할 수 있는 도구를 명시적으로 나열
2. **작업 디렉터리 설정** — 파일 작업 시 항상 `cwd`를 지정
3. **적절한 권한 모드 사용** — `"default"`로 시작하고 필요할 때만 권한 상승
4. **모든 메시지 타입 처리** — `ResultMessage`를 확인하여 에이전트 출력 획득
5. **max_turns 제한** — 합리적인 제한으로 무한 실행 에이전트 방지
