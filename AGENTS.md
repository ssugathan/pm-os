# PM OS — Agent Instructions

Canonical instructions for ANY coding agent working in this repo (Claude Code, Codex, Cursor, or others). CLAUDE.md imports this file; do not duplicate content there.

## What this is

A spec-first build of a multi-agent product management workflow system. `README.md` is the accurate map of what is implemented and tested versus designed-only; `_system/orchestrator/design.md` is the full architecture spec. Read both before structural changes.

## Repo structure

- `pmos/` — orchestrator code (state, dispatch, telemetry, config, prompts, adapters, agents, retry, gate, judgment, validation)
- `tests/` — pytest suite (all mocked, no API calls, no key needed)
- `_system/orchestrator/` — design spec + default_config.yaml; runtime state lands here too
- `_system/model-eval/` — model selection eval notes and benchmark mapping
- `_system/prompt-templates/` — per-agent prompt templates
- `products/titato/` — Titato product artifacts; `products/titato/context/project-context.md` is the compact context every agent reads first
- `PROGRESS.md` — the cross-session status ledger (see Project state below)

## Key concepts

- Agents are Python modules, not 1:1 with an LLM. Each agent has sub-tasks that may call different models.
- Models allocated per sub-task based on capability eval scores (see `_system/model-eval/`).
- Three context layers: project-context.md (persistent), sprint-context.md (per-sprint), orchestrator state (transactional).
- Agent state files: one JSON per agent per run, written synchronously at each transition, atomic rename via temp file.
- Config-driven judgment points: each decision point is automated or collaborative. Modes are currently passed to agents in code; yaml wiring is pending.

## Commands

- `pip install -e ".[dev]"` — install (Python 3.11+)
- `pytest` — run the suite (must be green before any push)
- `ruff check .` — lint

## Conventions

- Artifacts are structured markdown. Config in yaml, state in json, artifacts in md.
- Git commit after every agent completion (design convention — not yet automated by the orchestrator).
- Agent outputs go to known locations in the product folder (see design.md "Agent output conventions").
- No secrets in code or committed files, ever. Runtime keys go in `.env` (gitignored); see `.env.example`.
- Personal/session context and blog drafts live in the private `pm-os-build` repo, never here. This repo is public.

## Cloud sync

This repo moves between a Mac, Claude Code on the web, and other coding agents, with GitHub as the source of truth. Keep the remote current.

- At session start: fetch and fast-forward the working branch before doing anything. If it can't fast-forward, stop and tell me — don't force.
- Ask before pushing: when a logical block is done — a sub-task or fix is complete, the tree builds and tests pass, and the change stands on its own as a single commit — pause and ask whether to push. Show a one-line summary of what changed plus a proposed commit message so I can answer fast.
- Don't ask mid-task, on a broken or failing state, or for trivial edits. Never push without my confirmation.
- Push to the working branch (e.g. fix/sprint-N), never straight to main. main only updates through a PR.

## Project state

The repo is the source of truth for what's done and pending, because sessions start cold and run across machines and tools.

- At the start of every session (after the Cloud sync fetch): read `PROGRESS.md`, then check the recent git log and any open PRs. Reconcile them — if the log or PRs show work the file doesn't reflect, update the file. Never start work without doing this.
- Before ending any session or asking to push: update `PROGRESS.md` — move finished items to done, add a one-line Work log entry, set Next up — and stage it with the code so it travels in the same commit. Never end a session with unpushed commits or a stale ledger.
- Git is authoritative for "done": merged to main = done; an open PR or working branch = in flight. `PROGRESS.md` holds the "why" and "what's next" git can't express.

## Tool-specific notes

- `.claude/commands/` holds Claude Code slash commands; other agents can ignore that directory.
- CLAUDE.md exists only as an import shim for Claude Code plus Claude-specific notes.
