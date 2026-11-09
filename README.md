# PM OS

A spec-first build of a multi-agent product management workflow system. The design spec came first (`_system/orchestrator/design.md`, 550+ lines); the code implements it incrementally, with tests at each step. The end goal is a 7-agent pipeline (research, product definition, design, planning, dev & QA, deployment, feedback) that runs a product from idea to shipped software with human approval gates at key decisions.

This repo is the runtime system plus product artifacts. Build-process material (blog drafts, session context, personal notes) lives in a separate `pm-os-build` repo.

## What is implemented and tested (Phase 1)

The orchestrator core, built bottom-up as a walking skeleton and extended module by module. 102 tests, all mocked, no API calls.

- **State machine and state files** (`pmos/state.py`): task states (queued/running/review/complete), per-agent-per-run JSON state files, orchestrator state file, atomic writes via temp file + rename.
- **Dispatch and crash recovery** (`pmos/orchestrator.py`, `pmos/agents/base.py`): agents run ordered sub-tasks; re-running with the same run_id resumes idempotently from the first incomplete sub-task. `recover()` reloads inputs from the state file.
- **Telemetry** (`pmos/telemetry.py`): metadata-only event stream, append-only fsynced JSONL, payload shaped like PostHog's capture format so a backend swap is a one-file change. Names, counts, durations, models, prompt SHAs, error types. Never prompt or output content.
- **Config loading** (`pmos/config.py`): typed dataclasses, defaults from `_system/orchestrator/default_config.yaml`, optional per-product overrides layered by deep merge. Note: context budgets are loaded but not yet enforced at dispatch (see below).
- **Prompt assembly** (`pmos/prompts.py`): markdown templates with YAML frontmatter, assembly of the five prompt components from the spec (project context, sprint context, artifacts, task state, task instructions), and git-based prompt versioning: per-sub-task SHA capture at dispatch plus a dirty flag for uncommitted templates, with a strict mode that refuses to dispatch dirty templates.
- **Claude adapter** (`pmos/adapters/`): `ModelAdapter` ABC with a uniform `Response` shape, plus a Claude implementation that classifies SDK errors into transient / quota / malformed. Claude is the only adapter so far.
- **LLM agent path** (`pmos/agents/llm.py`, `pmos/agents/smoke.py`): `LLMAgent` base wires template loading, SHA capture, assembly, adapter call, retry, and telemetry into one helper. `SmokeAgent` is a one-sub-task agent that proves the full path end to end; no production agent exists yet.
- **Retry** (`pmos/retry.py`): exponential backoff for transient errors (2/4/8/16/32s, max 5 attempts), limited same-prompt retries for malformed responses, no retry on quota errors. The spec's cross-resume attempt counting ("give up after 10 tries across two resumes") is not built.
- **Gates** (`pmos/gate.py`): optional post-agent approval hook on `dispatch()` with approve / reject / modify-requested outcomes and telemetry. Gates between pipeline stages are not built because the pipeline itself is not built.
- **Judgment points** (`pmos/judgment.py`): per-decision automated or collaborative mode, pluggable handlers, decisions appended to a judgment log in the agent state file. Modes are passed to the agent in code; wiring them from config files is not done.
- **Output validation** (`pmos/validation.py`): pluggable validators run before a sub-task is marked complete, with bounded re-runs on failure. Built-in checks are structural only (not-none, required keys, word count). The framework has a content-validation slot, but the spec's LLM-based content checks (input coverage, consistency, hallucination flag, scope compliance) are not implemented.

## Designed but not built

From `_system/orchestrator/design.md`, still spec-only:

- The 7 production agents and their sub-task definitions (research agent spec exists in pm-os-build)
- Pipeline sequencing: multi-agent runs, handoffs, transactional context between agents
- Cycle types (MVP / minor / major), agent activation tables, sprint context generation
- Context budget enforcement: pre-dispatch token estimation and the compression strategy chain
- Interrupt and redirect; per-task autonomous vs collaborative mode defaults
- Multi-turn sub-tasks (everything today is single prompt, single response)
- Gemini and GPT adapters; per-sub-task model allocation
- LLM-based content validation checks
- Config-overrides generation by the product definition agent
- Cross-resume retry accounting and the give-up condition
- PostHog telemetry backend (JSONL only for now); dashboard

## Model evaluation writeups

`_system/model-eval/` contains the model selection eval that drives model allocation: eval notes (original scoring pass and an independent rescore), raw prompts and responses, and a benchmark mapping analysis. This was a manual, single-rater eval. It is directional by design: the goal was a defensible per-capability allocation for one user's workflow, not a publishable benchmark. Two writeups based on it are at https://sid-pm.com/musings.

## Running the tests

```
pip install -e ".[dev]"
pytest
```

Tests mock the Anthropic client; no API key or network access is needed. `ruff check .` for linting.

## Layout

```
pm-os/
  _system/
    orchestrator/        design spec, default_config.yaml (runtime state lands here too)
    model-eval/          model selection eval notes and benchmark mapping
    prompt-templates/    per-agent prompt templates (smoke/ping.md is the only real one yet)
  pmos/                  the package
    orchestrator.py      dispatch, recovery, gate invocation
    state.py             state machine + state file I/O
    telemetry.py         JSONL event stream
    config.py            dataclasses + yaml loading + deep merge
    prompts.py           template parsing, prompt assembly, SHA capture
    retry.py             retry policy wrapper
    gate.py              gate outcomes + handlers
    judgment.py          judgment point modes + handlers
    validation.py        validation framework + structural checks
    adapters/            ModelAdapter ABC + Claude adapter
    agents/              Agent base, LLMAgent, SmokeAgent, NoOpAgent
  products/titato/       product artifacts for the first product built with the system
  tests/                 102 tests
  session-handoff.md     project status ledger for cross-session sync
```
