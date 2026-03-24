# Claude API — Ruby

> **참고:** Ruby SDK는 Claude API를 지원합니다. 도구 실행기는 `client.beta.messages.tool_runner()`를 통해 베타로 제공됩니다. Agent SDK는 아직 Ruby에서 사용할 수 없습니다.

## 설치

```bash
gem install anthropic
```

## 클라이언트 초기화

```ruby
require "anthropic"

# Default (uses ANTHROPIC_API_KEY env var)
client = Anthropic::Client.new

# Explicit API key
client = Anthropic::Client.new(api_key: "your-api-key")
```

---

## 기본 메시지 요청

```ruby
message = client.messages.create(
  model: :"claude-opus-4-6",
  max_tokens: 16000,
  messages: [
    { role: "user", content: "What is the capital of France?" }
  ]
)
# content is an array of polymorphic block objects (TextBlock, ThinkingBlock,
# ToolUseBlock, ...). .type is a Symbol — compare with :text, not "text".
# .text raises NoMethodError on non-TextBlock entries.
message.content.each do |block|
  puts block.text if block.type == :text
end
```

---

## 스트리밍

```ruby
stream = client.messages.stream(
  model: :"claude-opus-4-6",
  max_tokens: 64000,
  messages: [{ role: "user", content: "Write a haiku" }]
)

stream.text.each { |text| print(text) }
```

---

## 도구 사용

Ruby SDK는 원시 JSON 스키마 정의를 통한 도구 사용을 지원하며, 자동 도구 실행을 위한 베타 도구 실행기도 제공합니다.

### 도구 실행기 (베타)

```ruby
class GetWeatherInput < Anthropic::BaseModel
  required :location, String, doc: "City and state, e.g. San Francisco, CA"
end

class GetWeather < Anthropic::BaseTool
  doc "Get the current weather for a location"

  input_schema GetWeatherInput

  def call(input)
    "The weather in #{input.location} is sunny and 72°F."
  end
end

client.beta.messages.tool_runner(
  model: :"claude-opus-4-6",
  max_tokens: 16000,
  tools: [GetWeather.new],
  messages: [{ role: "user", content: "What's the weather in San Francisco?" }]
).each_message do |message|
  puts message.content
end
```

### 수동 루프

도구 정의 형식과 에이전트 루프 패턴에 대해서는 [공유 도구 사용 개념](../shared/tool-use-concepts.md)을 참조하세요.
