> **참고:** 이 저장소는 Anthropic의 Claude용 스킬 구현체를 포함하고 있습니다. Agent Skills 표준에 대한 정보는 [agentskills.io](https://yoon-gu.github.io/agentskills/)를 참조하세요.

# 스킬

스킬은 Claude가 전문 작업의 성능을 향상시키기 위해 동적으로 로드하는 지침, 스크립트, 리소스의 폴더입니다. 스킬은 회사의 브랜드 가이드라인에 맞는 문서 작성, 조직의 특정 워크플로를 사용한 데이터 분석, 개인 작업 자동화 등 특정 작업을 반복 가능한 방식으로 완료하는 방법을 Claude에게 가르칩니다.

자세한 내용은 다음을 참조하세요:
- [스킬이란 무엇인가?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Claude에서 스킬 사용하기](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [커스텀 스킬 만드는 방법](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Agent Skills로 실세계에 대비한 에이전트 구축하기](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

# 이 저장소에 대하여

이 저장소는 Claude의 스킬 시스템으로 가능한 것들을 보여주는 스킬들을 포함합니다. 이 스킬들은 창작 애플리케이션(예술, 음악, 디자인)부터 기술 작업(웹 앱 테스트, MCP 서버 생성)까지, 그리고 엔터프라이즈 워크플로(커뮤니케이션, 브랜딩 등)까지 다양합니다.

각 스킬은 Claude가 사용하는 지침과 메타데이터를 포함하는 `SKILL.md` 파일과 함께 자체 폴더에 독립적으로 포함되어 있습니다. 이 스킬들을 탐색하여 자신만의 스킬에 대한 영감을 얻거나 다양한 패턴과 접근 방식을 이해하세요.

이 저장소의 많은 스킬은 오픈 소스(Apache 2.0)입니다. 또한 [`skills/docx`](./skills/docx), [`skills/pdf`](./skills/pdf), [`skills/pptx`](./skills/pptx), [`skills/xlsx`](./skills/xlsx) 하위 폴더에 [Claude의 문서 기능](https://www.anthropic.com/news/create-files)을 구동하는 문서 생성 및 편집 스킬도 포함했습니다. 이것들은 소스 공개이지만 오픈 소스는 아닙니다. 프로덕션 AI 애플리케이션에서 실제로 사용되는 더 복잡한 스킬의 참고 자료로 개발자들과 공유하고자 합니다.

## 면책 조항

**이 스킬들은 시연 및 교육 목적으로만 제공됩니다.** Claude에서 일부 기능을 사용할 수 있지만, Claude에서 받는 구현과 동작은 이 스킬에 표시된 것과 다를 수 있습니다. 이 스킬들은 패턴과 가능성을 보여주기 위한 것입니다. 중요한 작업에 사용하기 전에 항상 자신의 환경에서 스킬을 철저히 테스트하세요.

# 스킬 세트
- [./skills](./skills): 크리에이티브 & 디자인, 개발 & 기술, 엔터프라이즈 & 커뮤니케이션, 문서 스킬 예제
- [./spec](./spec): Agent Skills 사양
- [./template](./template): 스킬 템플릿

# Claude Code, Claude.ai, API에서 사용해보기

## Claude Code
Claude Code에서 다음 명령을 실행하여 이 저장소를 Claude Code 플러그인 마켓플레이스로 등록할 수 있습니다:
```
/plugin marketplace add anthropics/skills
```

특정 스킬 세트를 설치하려면:
1. `Browse and install plugins` 선택
2. `anthropic-agent-skills` 선택
3. `document-skills` 또는 `example-skills` 선택
4. `Install now` 선택

또는 다음을 통해 플러그인을 직접 설치할 수 있습니다:
```
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

플러그인을 설치한 후에는 스킬을 언급하기만 하면 사용할 수 있습니다. 예를 들어, 마켓플레이스에서 `document-skills` 플러그인을 설치한 경우 Claude Code에 다음과 같이 요청할 수 있습니다: "PDF 스킬을 사용하여 `path/to/some-file.pdf`에서 양식 필드를 추출해주세요"

## Claude.ai

이 예제 스킬들은 Claude.ai의 유료 플랜에서 모두 사용할 수 있습니다.

이 저장소의 스킬을 사용하거나 커스텀 스킬을 업로드하려면 [Claude에서 스킬 사용하기](https://support.claude.com/en/articles/12512180-using-skills-in-claude#h_a4222fa77b)의 지침을 따르세요.

## Claude API

Claude API를 통해 Anthropic의 사전 구축된 스킬을 사용하고 커스텀 스킬을 업로드할 수 있습니다. 자세한 내용은 [Skills API 빠른 시작](https://docs.claude.com/en/api/skills-guide#creating-a-skill)을 참조하세요.

# 기본 스킬 만들기

스킬은 YAML 프론트매터와 지침을 포함하는 `SKILL.md` 파일이 있는 폴더로 간단하게 만들 수 있습니다. 이 저장소의 **template-skill**을 시작점으로 사용할 수 있습니다:

```markdown
---
name: my-skill-name
description: 이 스킬이 무엇을 하고 언제 사용해야 하는지에 대한 명확한 설명
---

# 내 스킬 이름

[이 스킬이 활성화되었을 때 Claude가 따를 지침을 여기에 추가하세요]

## 예시
- 사용 예시 1
- 사용 예시 2

## 가이드라인
- 가이드라인 1
- 가이드라인 2
```

프론트매터에는 두 개의 필드만 필요합니다:
- `name` - 스킬의 고유 식별자 (소문자, 공백 대신 하이픈 사용)
- `description` - 스킬이 무엇을 하고 언제 사용해야 하는지에 대한 완전한 설명

아래의 마크다운 콘텐츠에는 Claude가 따를 지침, 예시, 가이드라인이 포함됩니다. 자세한 내용은 [커스텀 스킬 만드는 방법](https://support.claude.com/en/articles/12512198-creating-custom-skills)을 참조하세요.

# 파트너 스킬

스킬은 Claude가 특정 소프트웨어를 더 잘 사용할 수 있도록 가르치는 좋은 방법입니다. 파트너의 우수한 예제 스킬을 발견하면 여기에 소개할 수 있습니다:

- **Notion** - [Claude를 위한 Notion 스킬](https://www.notion.so/notiondevs/Notion-Skills-for-Claude-28da4445d27180c7af1df7d8615723d0)
