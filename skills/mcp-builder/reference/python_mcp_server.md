# Python MCP 서버 구현 가이드

## 개요

이 문서는 MCP Python SDK를 사용하여 MCP 서버를 구현하기 위한 Python 전용 모범 사례와 예제를 제공합니다. 서버 설정, 도구 등록 패턴, Pydantic을 활용한 입력 유효성 검사, 오류 처리, 그리고 완전한 동작 예제를 다룹니다.

---

## 빠른 참조

### 주요 Import
```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum
import httpx
```

### 서버 초기화
```python
mcp = FastMCP("service_mcp")
```

### 도구 등록 패턴
```python
@mcp.tool(name="tool_name", annotations={...})
async def tool_function(params: InputModel) -> str:
    # 구현
    pass
```

---

## MCP Python SDK와 FastMCP

공식 MCP Python SDK는 MCP 서버 구축을 위한 고수준 프레임워크인 FastMCP를 제공합니다. FastMCP가 제공하는 기능은 다음과 같습니다:
- 함수 시그니처와 docstring으로부터 자동 description 및 inputSchema 생성
- 입력 유효성 검사를 위한 Pydantic 모델 통합
- `@mcp.tool` 데코레이터 기반 도구 등록

**전체 SDK 문서는 WebFetch를 사용하여 로드하세요:**
`https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`

## 서버 네이밍 규칙

Python MCP 서버는 다음 네이밍 패턴을 따라야 합니다:
- **형식**: `{service}_mcp` (소문자와 밑줄 사용)
- **예시**: `github_mcp`, `jira_mcp`, `stripe_mcp`

이름은 다음과 같아야 합니다:
- 일반적 (특정 기능에 종속되지 않음)
- 통합하려는 서비스/API를 설명적으로 표현
- 작업 설명에서 쉽게 유추 가능
- 버전 번호나 날짜를 포함하지 않음

## 도구 구현

### 도구 네이밍

도구 이름에는 snake_case를 사용하며 (예: "search_users", "create_project", "get_channel_info"), 명확하고 동작 지향적인 이름을 지정합니다.

**이름 충돌 방지**: 겹침을 방지하기 위해 서비스 컨텍스트를 포함하세요:
- "send_message" 대신 "slack_send_message" 사용
- "create_issue" 대신 "github_create_issue" 사용
- "list_tasks" 대신 "asana_list_tasks" 사용

### FastMCP를 사용한 도구 구조

도구는 `@mcp.tool` 데코레이터와 입력 유효성 검사를 위한 Pydantic 모델을 사용하여 정의합니다:

```python
from pydantic import BaseModel, Field, ConfigDict
from mcp.server.fastmcp import FastMCP

# MCP 서버 초기화
mcp = FastMCP("example_mcp")

# 입력 유효성 검사를 위한 Pydantic 모델 정의
class ServiceToolInput(BaseModel):
    '''서비스 도구 작업을 위한 입력 모델.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,  # 문자열에서 공백 자동 제거
        validate_assignment=True,    # 할당 시 유효성 검사
        extra='forbid'              # 추가 필드 금지
    )

    param1: str = Field(..., description="First parameter description (e.g., 'user123', 'project-abc')", min_length=1, max_length=100)
    param2: Optional[int] = Field(default=None, description="Optional integer parameter with constraints", ge=0, le=1000)
    tags: Optional[List[str]] = Field(default_factory=list, description="List of tags to apply", max_items=10)

@mcp.tool(
    name="service_tool_name",
    annotations={
        "title": "Human-Readable Tool Title",
        "readOnlyHint": True,     # 도구가 환경을 수정하지 않음
        "destructiveHint": False,  # 도구가 파괴적 작업을 수행하지 않음
        "idempotentHint": True,    # 반복 호출해도 추가 효과 없음
        "openWorldHint": False     # 도구가 외부 엔티티와 상호작용하지 않음
    }
)
async def service_tool_name(params: ServiceToolInput) -> str:
    '''도구 설명이 자동으로 'description' 필드가 됩니다.

    이 도구는 서비스에서 특정 작업을 수행합니다. 처리 전에
    ServiceToolInput Pydantic 모델을 사용하여 모든 입력의 유효성을 검사합니다.

    Args:
        params (ServiceToolInput): 다음을 포함하는 유효성 검사된 입력 매개변수:
            - param1 (str): 첫 번째 매개변수 설명
            - param2 (Optional[int]): 기본값이 있는 선택적 매개변수
            - tags (Optional[List[str]]): 태그 목록

    Returns:
        str: 작업 결과를 포함하는 JSON 형식의 응답
    '''
    # 여기에 구현
    pass
```

## Pydantic v2 주요 기능

- 중첩된 `Config` 클래스 대신 `model_config` 사용
- 더 이상 사용되지 않는 `validator` 대신 `field_validator` 사용
- 더 이상 사용되지 않는 `dict()` 대신 `model_dump()` 사용
- 유효성 검사기에 `@classmethod` 데코레이터 필요
- 유효성 검사 메서드에 타입 힌트 필수

```python
from pydantic import BaseModel, Field, field_validator, ConfigDict

class CreateUserInput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    name: str = Field(..., description="User's full name", min_length=1, max_length=100)
    email: str = Field(..., description="User's email address", pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(..., description="User's age", ge=0, le=150)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Email cannot be empty")
        return v.lower()
```

## 응답 형식 옵션

유연성을 위해 여러 출력 형식을 지원합니다:

```python
from enum import Enum

class ResponseFormat(str, Enum):
    '''도구 응답의 출력 형식.'''
    MARKDOWN = "markdown"
    JSON = "json"

class UserSearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )
```

**Markdown 형식**:
- 명확성을 위해 헤더, 목록, 서식을 사용
- 타임스탬프를 사람이 읽을 수 있는 형식으로 변환 (예: epoch 대신 "2024-01-15 10:30:00 UTC")
- 표시 이름과 함께 괄호 안에 ID를 표시 (예: "@john.doe (U123456)")
- 상세한 메타데이터 생략 (예: 모든 크기가 아닌 하나의 프로필 이미지 URL만 표시)
- 관련 정보를 논리적으로 그룹화

**JSON 형식**:
- 프로그래밍 처리에 적합한 완전하고 구조화된 데이터 반환
- 사용 가능한 모든 필드와 메타데이터 포함
- 일관된 필드 이름과 타입 사용

## 페이지네이션 구현

리소스를 나열하는 도구의 경우:

```python
class ListInput(BaseModel):
    limit: Optional[int] = Field(default=20, description="Maximum results to return", ge=1, le=100)
    offset: Optional[int] = Field(default=0, description="Number of results to skip for pagination", ge=0)

async def list_items(params: ListInput) -> str:
    # 페이지네이션을 적용하여 API 요청
    data = await api_request(limit=params.limit, offset=params.offset)

    # 페이지네이션 정보 반환
    response = {
        "total": data["total"],
        "count": len(data["items"]),
        "offset": params.offset,
        "items": data["items"],
        "has_more": data["total"] > params.offset + len(data["items"]),
        "next_offset": params.offset + len(data["items"]) if data["total"] > params.offset + len(data["items"]) else None
    }
    return json.dumps(response, indent=2)
```

## 오류 처리

명확하고 실행 가능한 오류 메시지를 제공합니다:

```python
def _handle_api_error(e: Exception) -> str:
    '''모든 도구에서 일관된 오류 형식화.'''
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Error: Resource not found. Please check the ID is correct."
        elif e.response.status_code == 403:
            return "Error: Permission denied. You don't have access to this resource."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    return f"Error: Unexpected error occurred: {type(e).__name__}"
```

## 공유 유틸리티

공통 기능을 재사용 가능한 함수로 추출합니다:

```python
# 공유 API 요청 함수
async def _make_api_request(endpoint: str, method: str = "GET", **kwargs) -> dict:
    '''모든 API 호출을 위한 재사용 가능한 함수.'''
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            f"{API_BASE_URL}/{endpoint}",
            timeout=30.0,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
```

## Async/Await 모범 사례

네트워크 요청과 I/O 작업에는 항상 async/await를 사용합니다:

```python
# 올바른 예: 비동기 네트워크 요청
async def fetch_data(resource_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/resource/{resource_id}")
        response.raise_for_status()
        return response.json()

# 잘못된 예: 동기 요청
def fetch_data(resource_id: str) -> dict:
    response = requests.get(f"{API_URL}/resource/{resource_id}")  # 블로킹
    return response.json()
```

## 타입 힌트

전체 코드에서 타입 힌트를 사용합니다:

```python
from typing import Optional, List, Dict, Any

async def get_user(user_id: str) -> Dict[str, Any]:
    data = await fetch_user(user_id)
    return {"id": data["id"], "name": data["name"]}
```

## 도구 Docstring

모든 도구에는 명시적 타입 정보가 포함된 포괄적인 docstring이 있어야 합니다:

```python
async def search_users(params: UserSearchInput) -> str:
    '''
    Example 시스템에서 이름, 이메일 또는 팀으로 사용자를 검색합니다.

    이 도구는 Example 플랫폼의 모든 사용자 프로필을 검색하며,
    부분 일치와 다양한 검색 필터를 지원합니다. 사용자를
    생성하거나 수정하지 않으며, 기존 사용자만 검색합니다.

    Args:
        params (UserSearchInput): 다음을 포함하는 유효성 검사된 입력 매개변수:
            - query (str): 이름/이메일과 매칭할 검색 문자열 (예: "john", "@example.com", "team:marketing")
            - limit (Optional[int]): 반환할 최대 결과 수, 1-100 사이 (기본값: 20)
            - offset (Optional[int]): 페이지네이션을 위해 건너뛸 결과 수 (기본값: 0)

    Returns:
        str: 다음 스키마를 포함하는 JSON 형식의 검색 결과 문자열:

        성공 응답:
        {
            "total": int,           # 발견된 전체 일치 수
            "count": int,           # 이 응답의 결과 수
            "offset": int,          # 현재 페이지네이션 오프셋
            "users": [
                {
                    "id": str,      # 사용자 ID (예: "U123456789")
                    "name": str,    # 전체 이름 (예: "John Doe")
                    "email": str,   # 이메일 주소 (예: "john@example.com")
                    "team": str     # 팀 이름 (예: "Marketing") - 선택적
                }
            ]
        }

        오류 응답:
        "Error: <오류 메시지>" 또는 "No users found matching '<query>'"

    Examples:
        - 사용 시점: "마케팅 팀 멤버 전체 찾기" -> query="team:marketing"으로 params 설정
        - 사용 시점: "John의 계정 검색" -> query="john"으로 params 설정
        - 사용하지 않을 때: 사용자를 생성해야 하는 경우 (대신 example_create_user 사용)
        - 사용하지 않을 때: 사용자 ID가 있고 전체 세부 정보가 필요한 경우 (대신 example_get_user 사용)

    오류 처리:
        - 입력 유효성 검사 오류는 Pydantic 모델이 처리
        - 요청이 너무 많으면 "Error: Rate limit exceeded" 반환 (429 상태)
        - API 키가 유효하지 않으면 "Error: Invalid API authentication" 반환 (401 상태)
        - 결과의 형식화된 목록 또는 "No users found matching 'query'" 반환
    '''
```

## 전체 예제

아래에서 완전한 Python MCP 서버 예제를 확인하세요:

```python
#!/usr/bin/env python3
'''
Example 서비스용 MCP 서버.

이 서버는 사용자 검색, 프로젝트 관리, 데이터 내보내기 기능을 포함하여
Example API와 상호작용하는 도구를 제공합니다.
'''

from typing import Optional, List, Dict, Any
from enum import Enum
import httpx
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP

# MCP 서버 초기화
mcp = FastMCP("example_mcp")

# 상수
API_BASE_URL = "https://api.example.com/v1"

# 열거형
class ResponseFormat(str, Enum):
    '''도구 응답의 출력 형식.'''
    MARKDOWN = "markdown"
    JSON = "json"

# 입력 유효성 검사를 위한 Pydantic 모델
class UserSearchInput(BaseModel):
    '''사용자 검색 작업을 위한 입력 모델.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    query: str = Field(..., description="Search string to match against names/emails", min_length=2, max_length=200)
    limit: Optional[int] = Field(default=20, description="Maximum results to return", ge=1, le=100)
    offset: Optional[int] = Field(default=0, description="Number of results to skip for pagination", ge=0)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()

# 공유 유틸리티 함수
async def _make_api_request(endpoint: str, method: str = "GET", **kwargs) -> dict:
    '''모든 API 호출을 위한 재사용 가능한 함수.'''
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            f"{API_BASE_URL}/{endpoint}",
            timeout=30.0,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

def _handle_api_error(e: Exception) -> str:
    '''모든 도구에서 일관된 오류 형식화.'''
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Error: Resource not found. Please check the ID is correct."
        elif e.response.status_code == 403:
            return "Error: Permission denied. You don't have access to this resource."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    return f"Error: Unexpected error occurred: {type(e).__name__}"

# 도구 정의
@mcp.tool(
    name="example_search_users",
    annotations={
        "title": "Search Example Users",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def example_search_users(params: UserSearchInput) -> str:
    '''Example 시스템에서 이름, 이메일 또는 팀으로 사용자를 검색합니다.

    [위에 표시된 전체 docstring]
    '''
    try:
        # 유효성 검사된 매개변수를 사용하여 API 요청
        data = await _make_api_request(
            "users/search",
            params={
                "q": params.query,
                "limit": params.limit,
                "offset": params.offset
            }
        )

        users = data.get("users", [])
        total = data.get("total", 0)

        if not users:
            return f"No users found matching '{params.query}'"

        # 요청된 형식에 따라 응답 포맷팅
        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [f"# User Search Results: '{params.query}'", ""]
            lines.append(f"Found {total} users (showing {len(users)})")
            lines.append("")

            for user in users:
                lines.append(f"## {user['name']} ({user['id']})")
                lines.append(f"- **Email**: {user['email']}")
                if user.get('team'):
                    lines.append(f"- **Team**: {user['team']}")
                lines.append("")

            return "\n".join(lines)

        else:
            # 기계 판독 가능한 JSON 형식
            import json
            response = {
                "total": total,
                "count": len(users),
                "offset": params.offset,
                "users": users
            }
            return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_api_error(e)

if __name__ == "__main__":
    mcp.run()
```

---

## 고급 FastMCP 기능

### Context 매개변수 주입

FastMCP는 로깅, 진행 상황 보고, 리소스 읽기, 사용자 상호작용과 같은 고급 기능을 위해 `Context` 매개변수를 도구에 자동으로 주입할 수 있습니다:

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("example_mcp")

@mcp.tool()
async def advanced_search(query: str, ctx: Context) -> str:
    '''로깅과 진행 상황을 위한 컨텍스트 접근이 가능한 고급 도구.'''

    # 장시간 작업에 대한 진행 상황 보고
    await ctx.report_progress(0.25, "Starting search...")

    # 디버깅을 위한 정보 로깅
    await ctx.log_info("Processing query", {"query": query, "timestamp": datetime.now()})

    # 검색 수행
    results = await search_api(query)
    await ctx.report_progress(0.75, "Formatting results...")

    # 서버 설정 접근
    server_name = ctx.fastmcp.name

    return format_results(results)

@mcp.tool()
async def interactive_tool(resource_id: str, ctx: Context) -> str:
    '''사용자에게 추가 입력을 요청할 수 있는 도구.'''

    # 필요 시 민감한 정보 요청
    api_key = await ctx.elicit(
        prompt="Please provide your API key:",
        input_type="password"
    )

    # 제공된 키 사용
    return await api_call(resource_id, api_key)
```

**Context 기능:**
- `ctx.report_progress(progress, message)` - 장시간 작업에 대한 진행 상황 보고
- `ctx.log_info(message, data)` / `ctx.log_error()` / `ctx.log_debug()` - 로깅
- `ctx.elicit(prompt, input_type)` - 사용자에게 입력 요청
- `ctx.fastmcp.name` - 서버 설정 접근
- `ctx.read_resource(uri)` - MCP 리소스 읽기

### 리소스 등록

효율적인 템플릿 기반 접근을 위해 데이터를 리소스로 노출합니다:

```python
@mcp.resource("file://documents/{name}")
async def get_document(name: str) -> str:
    '''문서를 MCP 리소스로 노출합니다.

    리소스는 복잡한 매개변수가 필요하지 않은 정적 또는 반정적 데이터에
    유용합니다. 유연한 접근을 위해 URI 템플릿을 사용합니다.
    '''
    document_path = f"./docs/{name}"
    with open(document_path, "r") as f:
        return f.read()

@mcp.resource("config://settings/{key}")
async def get_setting(key: str, ctx: Context) -> str:
    '''컨텍스트를 사용하여 설정을 리소스로 노출합니다.'''
    settings = await load_settings()
    return json.dumps(settings.get(key, {}))
```

**리소스 vs 도구 사용 시점:**
- **리소스**: 간단한 매개변수(URI 템플릿)를 사용한 데이터 접근
- **도구**: 유효성 검사와 비즈니스 로직이 필요한 복잡한 작업

### 구조화된 출력 타입

FastMCP는 문자열 외에도 여러 반환 타입을 지원합니다:

```python
from typing import TypedDict
from dataclasses import dataclass
from pydantic import BaseModel

# 구조화된 반환을 위한 TypedDict
class UserData(TypedDict):
    id: str
    name: str
    email: str

@mcp.tool()
async def get_user_typed(user_id: str) -> UserData:
    '''구조화된 데이터를 반환합니다 - FastMCP가 직렬화를 처리합니다.'''
    return {"id": user_id, "name": "John Doe", "email": "john@example.com"}

# 복잡한 유효성 검사를 위한 Pydantic 모델
class DetailedUser(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    metadata: Dict[str, Any]

@mcp.tool()
async def get_user_detailed(user_id: str) -> DetailedUser:
    '''Pydantic 모델을 반환합니다 - 자동으로 스키마를 생성합니다.'''
    user = await fetch_user(user_id)
    return DetailedUser(**user)
```

### 수명 주기 관리

요청 간에 유지되는 리소스를 초기화합니다:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan():
    '''서버의 수명 동안 유지되는 리소스를 관리합니다.'''
    # 연결 초기화, 설정 로드 등
    db = await connect_to_database()
    config = load_configuration()

    # 모든 도구에서 사용 가능하도록 제공
    yield {"db": db, "config": config}

    # 종료 시 정리
    await db.close()

mcp = FastMCP("example_mcp", lifespan=app_lifespan)

@mcp.tool()
async def query_data(query: str, ctx: Context) -> str:
    '''컨텍스트를 통해 수명 주기 리소스에 접근합니다.'''
    db = ctx.request_context.lifespan_state["db"]
    results = await db.query(query)
    return format_results(results)
```

### 전송 옵션

FastMCP는 두 가지 주요 전송 메커니즘을 지원합니다:

```python
# stdio 전송 (로컬 도구용) - 기본값
if __name__ == "__main__":
    mcp.run()

# Streamable HTTP 전송 (원격 서버용)
if __name__ == "__main__":
    mcp.run(transport="streamable_http", port=8000)
```

**전송 방식 선택:**
- **stdio**: 커맨드라인 도구, 로컬 통합, 서브프로세스 실행
- **Streamable HTTP**: 웹 서비스, 원격 접근, 다중 클라이언트

---

## 코드 모범 사례

### 코드 조합성과 재사용성

구현 시 반드시 조합성과 코드 재사용을 우선시해야 합니다:

1. **공통 기능 추출**:
   - 여러 도구에서 사용되는 작업을 위한 재사용 가능한 헬퍼 함수 생성
   - 코드 중복 대신 HTTP 요청을 위한 공유 API 클라이언트 구축
   - 유틸리티 함수에서 오류 처리 로직 중앙화
   - 조합 가능한 전용 함수로 비즈니스 로직 추출
   - 공유 Markdown 또는 JSON 필드 선택 및 포맷팅 기능 추출

2. **중복 방지**:
   - 도구 간에 유사한 코드를 절대 복사-붙여넣기하지 않음
   - 유사한 로직을 두 번 작성하게 되면 함수로 추출
   - 페이지네이션, 필터링, 필드 선택, 포맷팅과 같은 공통 작업은 공유해야 함
   - 인증/권한 부여 로직은 중앙화해야 함

### Python 전용 모범 사례

1. **타입 힌트 사용**: 함수 매개변수와 반환 값에 항상 타입 어노테이션 포함
2. **Pydantic 모델**: 모든 입력 유효성 검사를 위한 명확한 Pydantic 모델 정의
3. **수동 유효성 검사 지양**: Pydantic이 제약 조건을 통해 입력 유효성 검사를 처리하도록 함
4. **적절한 Import**: Import를 그룹화 (표준 라이브러리, 서드파티, 로컬)
5. **오류 처리**: 일반적인 Exception이 아닌 특정 예외 타입 사용 (httpx.HTTPStatusError 등)
6. **비동기 컨텍스트 매니저**: 정리가 필요한 리소스에 `async with` 사용
7. **상수**: 모듈 수준에서 UPPER_CASE로 상수 정의

## 품질 체크리스트

Python MCP 서버 구현을 완료하기 전에 다음을 확인하세요:

### 전략적 설계
- [ ] 도구가 단순한 API 엔드포인트 래퍼가 아닌 완전한 워크플로우를 가능하게 함
- [ ] 도구 이름이 자연스러운 작업 세분화를 반영함
- [ ] 응답 형식이 에이전트 컨텍스트 효율성에 최적화됨
- [ ] 적절한 곳에 사람이 읽을 수 있는 식별자 사용
- [ ] 오류 메시지가 에이전트를 올바른 사용법으로 안내함

### 구현 품질
- [ ] 집중된 구현: 가장 중요하고 가치 있는 도구가 구현됨
- [ ] 모든 도구에 설명적인 이름과 문서가 있음
- [ ] 유사한 작업에서 반환 타입이 일관됨
- [ ] 모든 외부 호출에 오류 처리가 구현됨
- [ ] 서버 이름이 `{service}_mcp` 형식을 따름
- [ ] 모든 네트워크 작업이 async/await를 사용함
- [ ] 공통 기능이 재사용 가능한 함수로 추출됨
- [ ] 오류 메시지가 명확하고, 실행 가능하며, 교육적임
- [ ] 출력이 적절히 유효성 검사되고 포맷팅됨

### 도구 설정
- [ ] 모든 도구가 데코레이터에 'name'과 'annotations'를 구현함
- [ ] 어노테이션이 올바르게 설정됨 (readOnlyHint, destructiveHint, idempotentHint, openWorldHint)
- [ ] 모든 도구가 Field() 정의와 함께 Pydantic BaseModel을 입력 유효성 검사에 사용함
- [ ] 모든 Pydantic Field에 명시적 타입과 제약 조건이 포함된 설명이 있음
- [ ] 모든 도구에 명시적 입출력 타입이 포함된 포괄적인 docstring이 있음
- [ ] Docstring에 dict/JSON 반환에 대한 완전한 스키마 구조가 포함됨
- [ ] Pydantic 모델이 입력 유효성 검사를 처리함 (수동 유효성 검사 불필요)

### 고급 기능 (해당하는 경우)
- [ ] 로깅, 진행 상황 또는 요청에 Context 주입 사용
- [ ] 적절한 데이터 엔드포인트에 리소스가 등록됨
- [ ] 영구 연결을 위한 수명 주기 관리가 구현됨
- [ ] 구조화된 출력 타입 사용 (TypedDict, Pydantic 모델)
- [ ] 적절한 전송 방식 설정 (stdio 또는 Streamable HTTP)

### 코드 품질
- [ ] 파일에 Pydantic import를 포함한 적절한 import가 있음
- [ ] 해당하는 곳에 페이지네이션이 적절히 구현됨
- [ ] 잠재적으로 큰 결과 집합에 대한 필터링 옵션이 제공됨
- [ ] 모든 비동기 함수가 `async def`로 적절히 정의됨
- [ ] HTTP 클라이언트 사용이 적절한 컨텍스트 매니저와 함께 비동기 패턴을 따름
- [ ] 코드 전체에서 타입 힌트가 사용됨
- [ ] 상수가 모듈 수준에서 UPPER_CASE로 정의됨

### 테스트
- [ ] 서버가 성공적으로 실행됨: `python your_server.py --help`
- [ ] 모든 import가 올바르게 해결됨
- [ ] 샘플 도구 호출이 예상대로 작동함
- [ ] 오류 시나리오가 우아하게 처리됨
