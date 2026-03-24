# Agent SDK — TypeScript

Claude Agent SDK는 내장 도구, 안전 기능, 에이전트 기능을 갖춘 AI 에이전트를 구축하기 위한 상위 수준 인터페이스를 제공합니다.

## 설치

```bash
npm install @anthropic-ai/claude-agent-sdk
```

---

## 빠른 시작

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Explain this codebase",
  options: { allowedTools: ["Read", "Glob", "Grep"] },
})) {
  if ("result" in message) {
    console.log(message.result);
  }
}
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

## 권한 시스템

```typescript
for await (const message of query({
  prompt: "Refactor the authentication module",
  options: {
    allowedTools: ["Read", "Edit", "Write"],
    permissionMode: "acceptEdits",
  },
})) {
  if ("result" in message) console.log(message.result);
}
```

권한 모드:

- `"default"`: 위험한 작업에 대해 프롬프트 표시
- `"plan"`: 계획만, 실행 없음
- `"acceptEdits"`: 파일 편집 자동 수락
- `"dontAsk"`: 프롬프트를 표시하지 않음 — 사전 승인되지 않은 항목은 **거부**됨 (자동 승인 모드가 아님)
- `"bypassPermissions"`: 모든 프롬프트 건너뛰기 (옵션에서 `allowDangerouslySkipPermissions: true` 필요)

---

## MCP (Model Context Protocol) 지원

```typescript
for await (const message of query({
  prompt: "Open example.com and describe what you see",
  options: {
    mcpServers: {
      playwright: { command: "npx", args: ["@playwright/mcp@latest"] },
    },
  },
})) {
  if ("result" in message) console.log(message.result);
}
```

### 인프로세스 MCP 도구

`tool()`과 `createSdkMcpServer`를 사용하여 인프로세스에서 실행되는 커스텀 도구를 정의할 수 있습니다:

```typescript
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const myTool = tool("my-tool", "Description", { input: z.string() }, async (args) => {
  return { content: [{ type: "text", text: "result" }] };
});

const server = createSdkMcpServer({ name: "my-server", tools: [myTool] });

// Pass to query
for await (const message of query({
  prompt: "Use my-tool to do something",
  options: { mcpServers: { myServer: server } },
})) {
  if ("result" in message) console.log(message.result);
}
```

---

## 훅

```typescript
import { query, HookCallback } from "@anthropic-ai/claude-agent-sdk";
import { appendFileSync } from "fs";

const logFileChange: HookCallback = async (input) => {
  const filePath = (input as any).tool_input?.file_path ?? "unknown";
  appendFileSync(
    "./audit.log",
    `${new Date().toISOString()}: modified ${filePath}\n`,
  );
  return {};
};

for await (const message of query({
  prompt: "Refactor utils.py to improve readability",
  options: {
    allowedTools: ["Read", "Edit", "Write"],
    permissionMode: "acceptEdits",
    hooks: {
      PostToolUse: [{ matcher: "Edit|Write", hooks: [logFileChange] }],
    },
  },
})) {
  if ("result" in message) console.log(message.result);
}
```

도구 수명주기 이벤트(`PreToolUse`, `PostToolUse`, `PostToolUseFailure`)의 훅 이벤트 입력에는 `agent_id`와 `agent_type` 필드가 포함되어, 어떤 에이전트(메인 또는 하위 에이전트)가 도구 호출을 트리거했는지 훅에서 식별할 수 있습니다.

사용 가능한 훅 이벤트: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `Notification`, `UserPromptSubmit`, `SessionStart`, `SessionEnd`, `Stop`, `SubagentStart`, `SubagentStop`, `PreCompact`, `PermissionRequest`, `Setup`, `TeammateIdle`, `TaskCompleted`, `ConfigChange`, `Elicitation`, `ElicitationResult`, `WorktreeCreate`, `WorktreeRemove`, `InstructionsLoaded`

---

## 공통 옵션

`query()`는 최상위 `prompt` (문자열)와 `options` 객체를 받습니다:

```typescript
query({ prompt: "...", options: { ... } })
```

| 옵션                              | 타입   | 설명                                                                |
| ----------------------------------- | ------ | -------------------------------------------------------------------------- |
| `cwd`                               | string | 파일 작업을 위한 작업 디렉토리                                      |
| `allowedTools`                      | array  | 에이전트가 사용할 수 있는 도구 (예: `["Read", "Edit", "Bash"]`)                |
| `tools`                             | array \| preset | 사용 가능하게 할 내장 도구 (`string[]` 또는 `{type:'preset', preset:'claude_code'}`) |
| `disallowedTools`                   | array  | 명시적으로 허용하지 않을 도구                                               |
| `permissionMode`                    | string | 권한 프롬프트 처리 방법                                           |
| `allowDangerouslySkipPermissions`   | bool   | `permissionMode: "bypassPermissions"` 사용 시 `true`여야 함                |
| `mcpServers`                        | object | 연결할 MCP 서버                                                  |
| `hooks`                             | object | 동작 커스터마이징을 위한 훅                                             |
| `systemPrompt`                      | string \| preset | 커스텀 시스템 프롬프트 (`string` 또는 `{type:'preset', preset:'claude_code', append?:string}`) |
| `maxTurns`                          | number | 중지 전 최대 에이전트 턴 수                                        |
| `maxBudgetUsd`                      | number | 쿼리의 최대 예산 (USD)                                        |
| `model`                             | string | 모델 ID (기본값: CLI에 의해 결정)                                      |
| `agents`                            | object | 하위 에이전트 정의 (`Record<string, AgentDefinition>`)                   |
| `outputFormat`                      | object | 구조화된 출력 스키마                                                   |
| `thinking`                          | object | 사고/추론 제어                                                 |
| `betas`                             | array  | 활성화할 베타 기능 (예: `["context-1m-2025-08-07"]`)               |
| `settingSources`                    | array  | 로드할 설정 (예: `["project"]`). 기본값: 없음 (CLAUDE.md 파일 없음) |
| `env`                               | object | 세션에 설정할 환경 변수                               |
| `agentProgressSummaries`            | bool   | `task_progress` 이벤트에서 주기적 AI 생성 진행 요약 활성화  |

---

## 하위 에이전트

```typescript
for await (const message of query({
  prompt: "Use the code-reviewer agent to review this codebase",
  options: {
    allowedTools: ["Read", "Glob", "Grep", "Agent"],
    agents: {
      "code-reviewer": {
        description: "Expert code reviewer for quality and security reviews.",
        prompt: "Analyze code quality and suggest improvements.",
        tools: ["Read", "Glob", "Grep"],
      },
    },
  },
})) {
  if ("result" in message) console.log(message.result);
}
```

---

## 메시지 타입

```typescript
for await (const message of query({
  prompt: "Find TODO comments",
  options: { allowedTools: ["Read", "Glob", "Grep"] },
})) {
  if ("result" in message) {
    console.log(message.result);
    console.log(`Stop reason: ${message.stop_reason}`); // e.g., "end_turn", "tool_use", "max_tokens"
  } else if (message.type === "system" && message.subtype === "init") {
    const sessionId = message.session_id; // Capture for resuming later
  }
}
```

하위 에이전트 작업에 대해서도 태스크 관련 시스템 메시지가 발생합니다:
- `task_started` — 하위 에이전트 태스크가 등록될 때 발생
- `task_progress` — 누적 사용량 메트릭, 도구 카운트, 지속 시간을 포함한 실시간 진행 업데이트 (`agentProgressSummaries` 옵션을 활성화하면 `summary` 필드를 통해 주기적 AI 생성 요약 제공)
- `task_notification` — 태스크 완료 알림 (원래 도구 호출과 연결하기 위한 `tool_use_id` 포함)

---

## 세션 기록

과거 세션 데이터를 조회합니다:

```typescript
import { listSessions, getSessionMessages, getSessionInfo } from "@anthropic-ai/claude-agent-sdk";

// List all past sessions (supports pagination via limit/offset)
const sessions = await listSessions({ limit: 20, offset: 0 });
for (const session of sessions) {
  console.log(`${session.sessionId}: ${session.cwd} (tag: ${session.tag})`);
}

// Get metadata for a single session
const sessionId = sessions[0]?.sessionId;
const info = await getSessionInfo(sessionId);
console.log(info.tag, info.createdAt);

// Get messages from a specific session (supports pagination via limit/offset)
const messages = await getSessionMessages(sessionId, { limit: 50, offset: 0 });
for (const msg of messages) {
  console.log(msg);
}
```

### 세션 변경

세션 이름 변경, 태그 지정 또는 포크:

```typescript
import { renameSession, tagSession, forkSession } from "@anthropic-ai/claude-agent-sdk";

// Rename a session
await renameSession(sessionId, "My refactoring session");

// Tag a session
await tagSession(sessionId, "experiment");

// Clear a tag
await tagSession(sessionId, null);

// Fork a session — branch a conversation from a specific point
const { sessionId: forkedId } = await forkSession(sessionId);
```

---

## MCP 서버 관리

실행 중인 쿼리에서 런타임에 MCP 서버를 관리합니다:

```typescript
// Reconnect a disconnected MCP server
await queryHandle.reconnectMcpServer("my-server");

// Toggle an MCP server on/off
await queryHandle.toggleMcpServer("my-server", false);  // (name, enabled) — both required

// Get status of ALL configured MCP servers — returns an ARRAY
const statuses: McpServerStatus[] = await queryHandle.mcpServerStatus();
for (const s of statuses) {
  console.log(s.name, s.scope, s.tools.length, s.error);
}
```

---

## 모범 사례

1. **항상 allowedTools를 지정하세요** — 에이전트가 사용할 수 있는 도구를 명시적으로 나열하세요
2. **작업 디렉토리를 설정하세요** — 파일 작업 시 항상 `cwd`를 지정하세요
3. **적절한 권한 모드를 사용하세요** — `"default"`로 시작하고 필요한 경우에만 에스컬레이션하세요
4. **모든 메시지 타입을 처리하세요** — `result` 속성을 확인하여 에이전트 출력을 가져오세요
5. **maxTurns를 제한하세요** — 합리적인 제한으로 무한 실행 에이전트를 방지하세요
