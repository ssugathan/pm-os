# PM OS

Multi-agent orchestrator for end-to-end product workflow. 7 agents: research, product definition, design, planning, dev & QA, deployment, feedback.

## Repo structure
- `_system/orchestrator/` — orchestrator code and design spec
- `_system/orchestrator/design.md` — READ THIS for full architecture (context model, crash recovery, validation, error handling, cycle types)
- `_system/prompt-templates/` — reusable prompt templates per agent
- `products/titato/` — Titato app product artifacts
- `products/titato/context/project-context.md` — compact project context, every agent reads first

## Key concepts
- Agents are Python modules, not 1:1 with an LLM. Each agent has sub-tasks that may call different models.
- Models allocated per sub-task based on capability eval scores (see pm-os-build/model-eval/).
- Three context layers: project-context.md (persistent), sprint-context.md (per-sprint), orchestrator state (transactional).
- Agent state files: one JSON per agent per run, async writes, atomic rename via temp file.
- Config-driven judgment points: each decision point is automated or collaborative per config.yaml.

## Conventions
- Artifacts are structured markdown
- Config in yaml, state in json, artifacts in md
- Git commit after every agent completion
- Agent outputs go to known locations in the product folder (see design.md "Agent output conventions")

## Build artifacts live elsewhere
Design specs, eval docs, blog drafts, and session context live in the pm-os-build repo, not here. This repo is runtime only.
