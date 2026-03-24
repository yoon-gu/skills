# Agent SDK 패턴 — TypeScript

## 기본 에이전트

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  for await (const message of query({
    prompt: "Explain what this repository does",
    options: {
      cwd: "/path/to/project",
      allowedTools: ["Read", "Glob", "Grep"],
    },
  })) {
    if ("result" in message) {
      console.log(message.result);
    }
  }
}

main();
```

---

## 훅

### 도구 사용 후 훅

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

---

## 하위 에이전트

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

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

## MCP 서버 통합

### 브라우저 자동화 (Playwright)

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

---

## 세션 재개

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

let sessionId: string | undefined;

// First query: capture the session ID
for await (const message of query({
  prompt: "Read the authentication module",
  options: { allowedTools: ["Read", "Glob"] },
})) {
  if (message.type === "system" && message.subtype === "init") {
    sessionId = message.session_id;
  }
}

// Resume with full context from the first query
for await (const message of query({
  prompt: "Now find all places that call it",
  options: { resume: sessionId },
})) {
  if ("result" in message) console.log(message.result);
}
```

---

## 세션 기록

```typescript
import { listSessions, getSessionMessages, getSessionInfo } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  // List past sessions (supports pagination via limit/offset)
  const sessions = await listSessions();
  for (const session of sessions) {
    console.log(`Session ${session.sessionId} in ${session.cwd} (tag: ${session.tag})`);
  }

  // Get metadata for a single session
  if (sessions.length > 0) {
    const info = await getSessionInfo(sessions[0].sessionId);
    console.log(`Created: ${info.createdAt}, Tag: ${info.tag}`);
  }

  // Retrieve messages from the most recent session
  if (sessions.length > 0) {
    const messages = await getSessionMessages(sessions[0].sessionId, { limit: 50 });
    for (const msg of messages) {
      console.log(msg);
    }
  }
}

main();
```

---

## 세션 변경

```typescript
import { renameSession, tagSession, forkSession } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  const sessionId = "your-session-id";

  // Rename a session
  await renameSession(sessionId, "Refactoring auth module");

  // Tag a session for filtering
  await tagSession(sessionId, "experiment-v2");

  // Clear a tag
  await tagSession(sessionId, null);

  // Fork a conversation to branch from a point
  const { sessionId: forkedId } = await forkSession(sessionId);
  console.log(`Forked session: ${forkedId}`);
}

main();
```

---

## 커스텀 시스템 프롬프트

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Review this code",
  options: {
    allowedTools: ["Read", "Glob", "Grep"],
    systemPrompt: `You are a senior code reviewer focused on:
1. Security vulnerabilities
2. Performance issues
3. Code maintainability

Always provide specific line numbers and suggestions for improvement.`,
  },
})) {
  if ("result" in message) console.log(message.result);
}
```
