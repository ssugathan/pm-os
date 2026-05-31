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

## Cloud sync
This repo moves between my Mac and Claude Code on the web, with GitHub as the source of truth. Keep the remote current.

- At session start: fetch and fast-forward the working branch before doing anything. If it can't fast-forward, stop and tell me — don't force.
- Ask before pushing: when a logical block is done — a sub-task or fix is complete, the tree builds and tests pass, and the change stands on its own as a single commit — pause and ask whether to push. Show a one-line summary of what changed plus a proposed commit message so I can answer fast.
- Don't ask mid-task, on a broken or failing state, or for trivial edits. Never push without my confirmation.
- Push to the working branch (e.g. fix/sprint-N), never straight to main. main only updates through a PR.
