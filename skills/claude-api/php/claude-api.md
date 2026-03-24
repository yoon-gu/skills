# Claude API — PHP

> **참고:** PHP SDK는 PHP용 공식 Anthropic SDK입니다. 도구 실행기와 Agent SDK는 사용할 수 없습니다. Bedrock, Vertex AI, Foundry 클라이언트가 지원됩니다.

## 설치

```bash
composer require "anthropic-ai/sdk"
```

## 클라이언트 초기화

```php
use Anthropic\Client;

// Using API key from environment variable
$client = new Client(apiKey: getenv("ANTHROPIC_API_KEY"));
```

### Amazon Bedrock

```php
use Anthropic\Bedrock;

// Constructor is private — use the static factory. Reads AWS credentials from env.
$client = Bedrock\Client::fromEnvironment(region: 'us-east-1');
```

### Google Vertex AI

```php
use Anthropic\Vertex;

// Constructor is private. Parameter is `location`, not `region`.
$client = Vertex\Client::fromEnvironment(
    location: 'us-east5',
    projectId: 'my-project-id',
);
```

### Anthropic Foundry

```php
use Anthropic\Foundry;

// Constructor is private. baseUrl or resource is required.
$client = Foundry\Client::withCredentials(
    authToken: getenv('ANTHROPIC_FOUNDRY_AUTH_TOKEN'),
    baseUrl: 'https://<resource>.services.ai.azure.com/anthropic',
);
```

---

## 기본 메시지 요청

```php
$message = $client->messages->create(
    model: 'claude-opus-4-6',
    maxTokens: 16000,
    messages: [
        ['role' => 'user', 'content' => 'What is the capital of France?'],
    ],
);

// content is an array of polymorphic blocks (TextBlock, ToolUseBlock,
// ThinkingBlock). Accessing ->text on content[0] without checking the block
// type will throw if the first block is not a TextBlock (e.g., when extended
// thinking is enabled and a ThinkingBlock comes first). Always guard:
foreach ($message->content as $block) {
    if ($block->type === 'text') {
        echo $block->text;
    }
}
```

첫 번째 텍스트 블록만 필요한 경우:

```php
foreach ($message->content as $block) {
    if ($block->type === 'text') {
        echo $block->text;
        break;
    }
}
```

---

## 스트리밍

> **SDK v0.5.0 이상 필요.** v0.4.0 이하에서는 단일 `$params` 배열을 사용했습니다. 명명된 매개변수로 호출하면 `Unknown named parameter $model` 오류가 발생합니다. 업그레이드: `composer require "anthropic-ai/sdk:^0.6"`

```php
use Anthropic\Messages\RawContentBlockDeltaEvent;
use Anthropic\Messages\TextDelta;

$stream = $client->messages->createStream(
    model: 'claude-opus-4-6',
    maxTokens: 64000,
    messages: [
        ['role' => 'user', 'content' => 'Write a haiku'],
    ],
);

foreach ($stream as $event) {
    if ($event instanceof RawContentBlockDeltaEvent && $event->delta instanceof TextDelta) {
        echo $event->delta->text;
    }
}
```

---

## 도구 사용 (수동 루프)

도구는 배열로 전달됩니다. **SDK는 camelCase 키를 사용합니다** (`inputSchema`, `toolUseID`, `stopReason`). v0.5.0부터 API의 snake_case로 자동 매핑됩니다. 루프 패턴에 대해서는 [공유 도구 사용 개념](../shared/tool-use-concepts.md)을 참조하세요.

```php
use Anthropic\Messages\ToolUseBlock;

$tools = [
    [
        'name' => 'get_weather',
        'description' => 'Get the current weather in a given location',
        'inputSchema' => [  // camelCase, not input_schema
            'type' => 'object',
            'properties' => [
                'location' => ['type' => 'string', 'description' => 'City and state'],
            ],
            'required' => ['location'],
        ],
    ],
];

$messages = [['role' => 'user', 'content' => 'What is the weather in SF?']];

$response = $client->messages->create(
    model: 'claude-opus-4-6',
    maxTokens: 16000,
    tools: $tools,
    messages: $messages,
);

while ($response->stopReason === 'tool_use') {  // camelCase property
    $toolResults = [];
    foreach ($response->content as $block) {
        if ($block instanceof ToolUseBlock) {
            // $block->name  : string               — tool name to dispatch on
            // $block->input : array<string,mixed>  — parsed JSON input
            // $block->id    : string               — pass back as toolUseID
            $result = executeYourTool($block->name, $block->input);
            $toolResults[] = [
                'type' => 'tool_result',
                'toolUseID' => $block->id,  // camelCase, not tool_use_id
                'content' => $result,
            ];
        }
    }

    // Append assistant turn + user turn with tool results
    $messages[] = ['role' => 'assistant', 'content' => $response->content];
    $messages[] = ['role' => 'user', 'content' => $toolResults];

    $response = $client->messages->create(
        model: 'claude-opus-4-6',
        maxTokens: 16000,
        tools: $tools,
        messages: $messages,
    );
}

// Final text response
foreach ($response->content as $block) {
    if ($block->type === 'text') {
        echo $block->text;
    }
}
```

`$block->type === 'tool_use'`도 사용 가능합니다. `instanceof ToolUseBlock`은 PHPStan을 위해 타입을 좁혀줍니다.


---

## 확장 사고

**적응형 사고는 Claude 4.6+ 모델에 권장되는 모드입니다.** Claude가 언제, 얼마나 사고할지 동적으로 결정합니다.

```php
use Anthropic\Messages\ThinkingBlock;

$message = $client->messages->create(
    model: 'claude-opus-4-6',
    maxTokens: 16000,
    thinking: ['type' => 'adaptive'],
    messages: [
        ['role' => 'user', 'content' => 'Solve: 27 * 453'],
    ],
);

// ThinkingBlock(s) precede TextBlock in content
foreach ($message->content as $block) {
    if ($block instanceof ThinkingBlock) {
        echo "Thinking:\n{$block->thinking}\n\n";
        // $block->signature is an opaque string — preserve verbatim if
        // passing thinking blocks back in multi-turn conversations
    } elseif ($block->type === 'text') {
        echo "Answer: {$block->text}\n";
    }
}
```

> **지원 중단:** `['type' => 'enabled', 'budgetTokens' => N]` (고정 예산 확장 사고)는 Claude 4.6에서 여전히 작동하지만 지원 중단되었습니다. 위의 적응형 사고를 사용하세요.

`$block->type === 'thinking'`도 확인에 사용할 수 있습니다. `instanceof`는 PHPStan을 위해 타입을 좁혀줍니다.

---

## 베타 기능 및 서버 측 도구

**`betas:`는 `$client->messages->create()`의 매개변수가 아닙니다** — 베타 네임스페이스에만 존재합니다. 명시적 옵트인 헤더가 필요한 기능에 사용하세요:

```php
use Anthropic\Beta\Messages\BetaRequestMCPServerURLDefinition;

$response = $client->beta->messages->create(
    model: 'claude-opus-4-6',
    maxTokens: 16000,
    mcpServers: [
        BetaRequestMCPServerURLDefinition::with(
            name: 'my-server',
            url: 'https://example.com/mcp',
        ),
    ],
    betas: ['mcp-client-2025-11-20'],  // only valid on ->beta->messages
    messages: [['role' => 'user', 'content' => 'Use the MCP tools']],
);
```

**서버 측 도구** (bash, web_search, text_editor, code_execution)는 GA이며 두 경로 모두에서 작동합니다 — 비베타용 `Anthropic\Messages\ToolBash20250124` / `WebSearchTool20260209` / `ToolTextEditor20250728` / `CodeExecutionTool20260120`, 베타용 `Anthropic\Beta\Messages\BetaToolBash20250124` / `BetaWebSearchTool20260209` / `BetaToolTextEditor20250728` / `BetaCodeExecutionTool20260120`. 이들에는 `betas:` 헤더가 필요하지 않습니다.
