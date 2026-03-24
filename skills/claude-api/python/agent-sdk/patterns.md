# Agent SDK 패턴 — Python

## 기본 에이전트

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def main():
    async for message in query(
        prompt="Explain what this repository does",
        options=ClaudeAgentOptions(
            cwd="/path/to/project",
            allowed_tools=["Read", "Glob", "Grep"]
        )
    ):
        if isinstance(message, ResultMessage):
            print(message.result)

anyio.run(main)
```

---

## 사용자 정의 도구

사용자 정의 도구에는 MCP 서버가 필요합니다. 완전한 제어를 위해 `ClaudeSDKClient`를 사용합니다 (사용자 정의 SDK MCP 도구는 `ClaudeSDKClient`가 필요합니다 — `query()`는 외부 stdio/http MCP 서버만 지원합니다).

```python
import anyio
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
)

@tool("get_weather", "Get the current weather for a location", {"location": str})
async def get_weather(args):
    location = args["location"]
    return {"content": [{"type": "text", "text": f"The weather in {location} is sunny and 72°F."}]}

server = create_sdk_mcp_server("weather-tools", tools=[get_weather])

async def main():
    options = ClaudeAgentOptions(mcp_servers={"weather": server})
    async with ClaudeSDKClient(options=options) as client:
        await client.query("What's the weather in Paris?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

anyio.run(main)
```

---

## 훅

### 도구 사용 후 훅

편집 후 파일 변경 사항을 기록합니다:

```python
import anyio
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher, ResultMessage

async def log_file_change(input_data, tool_use_id, context):
    file_path = input_data.get('tool_input', {}).get('file_path', 'unknown')
    with open('./audit.log', 'a') as f:
        f.write(f"{datetime.now()}: modified {file_path}\n")
    return {}

async def main():
    async for message in query(
        prompt="Refactor utils.py to improve readability",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Write"],
            permission_mode="acceptEdits",
            hooks={
                "PostToolUse": [HookMatcher(matcher="Edit|Write", hooks=[log_file_change])]
            }
        )
    ):
        if isinstance(message, ResultMessage):
            print(message.result)

anyio.run(main)
```

---

## 하위 에이전트

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition, ResultMessage

async def main():
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

anyio.run(main)
```

---

## MCP 서버 통합

### 브라우저 자동화 (Playwright)

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def main():
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

anyio.run(main)
```

### 데이터베이스 액세스 (PostgreSQL)

```python
import os
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def main():
    async for message in query(
        prompt="Show me the top 10 users by order count",
        options=ClaudeAgentOptions(
            mcp_servers={
                "postgres": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-postgres"],
                    "env": {"DATABASE_URL": os.environ["DATABASE_URL"]}
                }
            }
        )
    ):
        if isinstance(message, ResultMessage):
            print(message.result)

anyio.run(main)
```

---

## 권한 모드

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    # Default: 위험한 작업 시 확인 요청
    async for message in query(
        prompt="Delete all test files",
        options=ClaudeAgentOptions(
            allowed_tools=["Bash"],
            permission_mode="default"  # Will prompt before deleting
        )
    ):
        pass

    # Plan: 에이전트가 변경 전에 계획을 작성
    async for message in query(
        prompt="Refactor the auth system",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit"],
            permission_mode="plan"
        )
    ):
        pass

    # Accept edits: 파일 편집 자동 승인
    async for message in query(
        prompt="Refactor this module",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit"],
            permission_mode="acceptEdits"
        )
    ):
        pass

    # Bypass: 모든 확인 건너뛰기 (주의해서 사용)
    async for message in query(
        prompt="Set up the development environment",
        options=ClaudeAgentOptions(
            allowed_tools=["Bash", "Write"],
            permission_mode="bypassPermissions"
        )
    ):
        pass

anyio.run(main)
```

---

## 오류 복구

```python
import anyio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    ResultMessage,
)

async def run_with_recovery():
    try:
        async for message in query(
            prompt="Fix the failing tests",
            options=ClaudeAgentOptions(
                allowed_tools=["Read", "Edit", "Bash"],
                max_turns=10
            )
        ):
            if isinstance(message, ResultMessage):
                print(message.result)
    except CLINotFoundError:
        print("Claude Code CLI not found. Install with: pip install claude-agent-sdk")
    except CLIConnectionError as e:
        print(f"Connection error: {e}")
    except ProcessError as e:
        print(f"Process error: {e}")

anyio.run(run_with_recovery)
```

---

## 세션 재개

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, SystemMessage

async def main():
    session_id = None

    # 첫 번째 쿼리: 세션 ID 캡처
    async for message in query(
        prompt="Read the authentication module",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Glob"])
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            session_id = message.data.get("session_id")

    # 첫 번째 쿼리의 전체 컨텍스트로 재개
    async for message in query(
        prompt="Now find all places that call it",  # "it" = auth module
        options=ClaudeAgentOptions(resume=session_id)
    ):
        if isinstance(message, ResultMessage):
            print(message.result)

anyio.run(main)
```

---

## 세션 기록

```python
from claude_agent_sdk import list_sessions, get_session_messages

# 과거 세션 목록 조회 (동기 함수 — await 불필요)
sessions = list_sessions()
for session in sessions:
    print(f"Session {session.session_id} in {session.cwd}")

# 가장 최근 세션의 메시지 조회 (동기 함수 — await 불필요)
if sessions:
    messages = get_session_messages(session_id=sessions[0].session_id)
    for msg in messages:
        print(msg)
```

---

## 세션 변경

```python
from claude_agent_sdk import rename_session, tag_session

session_id = "your-session-id"

# 세션 이름 변경
rename_session(session_id=session_id, title="Refactoring auth module")

# 필터링을 위한 세션 태그 지정
tag_session(session_id=session_id, tag="experiment-v2")

# 태그 삭제
tag_session(session_id=session_id, tag=None)

# 특정 프로젝트 디렉터리로 범위 지정
rename_session(session_id=session_id, title="New title", directory="/path/to/project")
```

---

## 사용자 정의 시스템 프롬프트

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def main():
    async for message in query(
        prompt="Review this code",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep"],
            system_prompt="""You are a senior code reviewer focused on:
1. Security vulnerabilities
2. Performance issues
3. Code maintainability

Always provide specific line numbers and suggestions for improvement."""
        )
    ):
        if isinstance(message, ResultMessage):
            print(message.result)

anyio.run(main)
```
