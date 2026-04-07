Title: AI Agent Config — Stacknaut

Description: How Stacknaut's AGENTS.md, custom commands, and skills help AI coding agents write correct, consistent code from the first prompt.

Source: https://stacknaut.com/docs/ai-agent-config

---

[Stacknaut](https://stacknaut.com/)
[About](https://stacknaut.com/about)
[Articles](https://stacknaut.com/articles)
[Docs](https://stacknaut.com/docs)
[FAQ](https://stacknaut.com/faq)
[Pricing](https://stacknaut.com/pricing)
[Get Stacknaut](https://stacknaut.com/)
[Docs](https://stacknaut.com/docs)

Stacknaut includes a curated AI coding agent setup — an AGENTS.md file, custom commands, and skills — designed to help your AI assistant write correct, consistent code from the first prompt. This is what makes Stacknaut different from other starter kits.

AI coding agents are only as good as the context you give them. Without project-specific instructions, they'll guess at conventions, use wrong patterns, and produce inconsistent code. With a well-crafted AGENTS.md, they follow your patterns, use your libraries, and write code that fits your codebase.
Stacknaut's AGENTS.md isn't a generic template. It's extracted from thousands of hours of real AI-assisted development on production SaaS products. Every rule exists because an AI agent got something wrong without it.

### Project-Level AGENTS.md
The app repo includes a comprehensive AGENTS.md in the project root that covers:
- Code style — TypeScript conventions, naming rules, function style, Vue patterns
- Architecture — Pure functions, side effect isolation, data flow
- Project structure — Where files go, path aliases, module boundaries
- Database — Drizzle ORM patterns, schema location, migration workflow
- Environment variables — How to add new env vars across all services
- Logging — Backend (pino) and frontend patterns
- Validation — Zod schemas, error format
- Deployment — Kamal commands, deploy workflow
- Testing — Test framework, file locations
- Git — Commit conventions, message format
This file works with Claude Code, Factory Droid, Codex CLI, Cursor, and any tool that reads markdown instruction files.

### Global AGENTS.md
A separate personal-preferences AGENTS.md in agent-setup/ that you symlink to your home directory. This covers tool configurations, task tracking, and workflow preferences that apply across all your projects.

```
agent-setup/
```

### Custom Commands
The setup supports slash commands stored as .md files in a commands directory:

```
.md
```

- Invoked with /command-name arguments
- Useful for repetitive workflows
- You add your own as you develop your workflow

```
/command-name arguments
```

### Skills
More complex multi-step workflows:
- setup-app — Interactively customizes the starter kit for your project: renames the app, configures integrations, replaces the example feature

## How It Works
The agent-setup directory contains everything. You copy it to your machine and symlink it so all your AI tools read from the same source:

```
~/.claude/CLAUDE.md → ~/my-agent-config/AGENTS.md ~/.factory/AGENTS.md → ~/my-agent-config/AGENTS.md ~/.codex/AGENTS.md → ~/my-agent-config/AGENTS.md
```


```
~/.claude/CLAUDE.md → ~/my-agent-config/AGENTS.md ~/.factory/AGENTS.md → ~/my-agent-config/AGENTS.md ~/.codex/AGENTS.md → ~/my-agent-config/AGENTS.md
```

One file, shared across all tools. Edit once, every tool picks it up.
The project also has its own AGENTS.md in the repo root with project-specific rules. The global file has your personal preferences; the project file has project conventions. Both are applied together, with project-level rules taking precedence.

## Supported Tools
```
.factory/AGENTS.md
```


```
.claude/CLAUDE.md
```


```
.codex/AGENTS.md
```

## Setup
1. Copy the agent-setup repo to your machine
2. Create the tool config directories (~/.claude, ~/.factory, ~/.codex)
3. Symlink the AGENTS.md, commands, and skills directories
4. Open your preferred tool and verify it picks up the instructions

```
agent-setup
```


```
~/.claude
```


```
~/.factory
```


```
~/.codex
```

Detailed steps are in agent-setup/setup-guide.md.

```
agent-setup/setup-guide.md
```

## Extending
Add your own commands by creating .md files in the commands directory. Add skills by creating a directory with a SKILL.md file. The AGENTS.md is yours to customize — add your personal coding preferences, tool configurations, and workflow rules.

```
.md
```


```
SKILL.md
```

## Key Files
```
agent-setup/ AGENTS.md — Global AI agent instructions setup-guide.md — Step-by-step setup instructions skills/ setup-app/SKILL.md — Interactive project customization skill
```


```
agent-setup/ AGENTS.md — Global AI agent instructions setup-guide.md — Step-by-step setup instructions skills/ setup-app/SKILL.md — Interactive project customization skill
```

The project's own AGENTS.md in the repo root is the project-level instruction file that agents read when working in the codebase.

```
AGENTS.md
```

c2d2c5e2

