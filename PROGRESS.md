# PROGRESS.md — PM OS status ledger
_Read at session start per AGENTS.md → Project state. Update before every push._
_Last updated: November 8, 2026_

---

## CURRENT STATE (live ledger — read first)
_This block is the authoritative status. Git is authoritative for "done": merged to main = done; an open PR or working branch = in flight. The Background section below is design context._

### Status
**Phase 1 orchestrator is merged to `main`.** In flight: `chore/ci-maintenance` (CI action bumps + Dependabot), PR open, not merged.

**History rewritten (observed 2026-11-09):** `origin/main` was force-updated to a single commit, `4a7d027 Initial public release`. Its tree includes all the work below (CI and hygiene from PR #6, `chore/ci-and-lint`, merged 2026-11-08), but the per-PR commits are no longer in `main`'s history. The PR references below are kept for the record.

- Phase 1 (built May 31 – Jun 2 on `build/phase-1-orchestrator`) plus the Sep 2 safe-refactor pass merged via PR #1 (`refactor/safe-pass-v2`) on 2026-09-05.
- Cross-agent handoff rules merged via PR #2 (`docs/cross-agent-handoff`) on 2026-09-05.
- Cloud workflow test merged via PR #3 (`chore/cloud-workflow-test`) on 2026-11-08.
- Ledger reconcile + privacy cleanup merged via PR #4 (`chore/progress-privacy-reconcile`) and PR #5 (`chore/remove-personal-context`) on 2026-11-08.
- CI and hygiene merged via PR #6 (`chore/ci-and-lint`) on 2026-11-08.
- The branches above are merged; after the history rewrite they no longer share history with `main` and should be deleted, not merged again.

What exists in code (`pmos/`), all covered by the mocked test suite:
- State machine, per-agent-per-run state files, orchestrator state file, atomic writes (`pmos/state.py`)
- Dispatch and crash recovery (`pmos/orchestrator.py`, `pmos/agents/base.py`)
- Telemetry: metadata-only, PostHog-shaped JSONL (`pmos/telemetry.py`)
- Config: dataclasses + `_system/orchestrator/default_config.yaml` + deep-merge overrides (`pmos/config.py`)
- Prompt assembly, git-based prompt SHA capture, strict mode for dirty templates (`pmos/prompts.py`, `pmos/agents/llm.py`)
- Claude adapter with error classification (`pmos/adapters/`)
- `LLMAgent` + `SmokeAgent` (the only agent; `_system/prompt-templates/smoke/ping.md` is the only real template)
- Retry, gates, judgment points, structural output validation (`pmos/retry.py`, `pmos/gate.py`, `pmos/judgment.py`, `pmos/validation.py`)

Not built: the 7 production agents, pipeline sequencing, cycle types, context-budget enforcement, LLM content validation, Gemini/GPT adapters, cross-resume retry accounting, PostHog backend. Full list in `README.md` → "Designed but not built". Stop hook + TDD pre-write hook are deferred to Phase 2 (built alongside Dev & QA).

Verification state (2026-11-08):
- `pytest`: 102 passed on a clean `pip install -e ".[dev]"` in a fresh Python 3.11 venv (anthropic 2.6.0, httpx 0.28.1) — on `main`.
- `ruff check .`: clean with ruff pinned to 0.17.4 and an explicit rule `select` in `pyproject.toml` — on `main`.
- CI: `.github/workflows/ci.yml` (job `lint-and-test`: Python 3.11, ruff, pytest; no keys, no network tests) — on `main`.

### Next up
1. **Owner decision: git-history privacy cleanup** — appears done (`main` is now a single commit as of 2026-11-09); owner to confirm, then drop this item. Personal context was removed from this file on 2026-11-08 but remains in earlier commits of `PROGRESS.md` (and of `session-handoff.md` before the rename), and the repo is intended to be public. Decide whether to leave history as is or rewrite it (owner-only action; agents must not rewrite history). The other files flagged by the 2026-11-08 scan were cleaned in `chore/remove-personal-context`, so their earlier versions are also in history. Kept deliberately: `tests/test_telemetry.py:29,31` (`"sid"` as a test value), the blog URL at `README.md:41`, and the plan names in the eval's model list at `_system/model-eval/raw-evals.md:22-23`.
2. **Enable "require status checks" on `main`** (owner-only, GitHub settings) using the `lint-and-test` check. CI and hygiene are merged.
3. **Fix known bugs a/b/c** (see Known issues) with a regression test for each. Orchestrator state is to be keyed per run, so resuming an old run and starting a new one cannot collide.
4. **Doc fixes.** README layout (still lists `session-handoff.md`; missing `AGENTS.md`, `PROGRESS.md`); `design.md` says agent-state writes are async/background-thread but the code (and AGENTS.md) is synchronous — update the doc to match; add crash-recovery caveats to README (single shared orchestrator state file, stale errors on resume, sub-task drift).
5. Build Phase 2: Dev & QA agent on the existing `LLMAgent` + Stop hook framework; test on the Lego simulator in `qa_only` mode first.
6. Spec + build Planning and Deployment agents (needed for Lego simulator sprints 2 & 3).
7. Remaining agent specs: product definition, design, feedback.
8. Titato app architecture decision (Option A / B / Hybrid) — `products/titato/architecture/options.md` is still a placeholder, so the options need writing up in this repo first.

### Known issues (all reproduced on `main` at 98412be, 2026-11-08)
- **a. Stale run_id.** `Orchestrator._load_or_init_state` (`pmos/orchestrator.py:140-147`) loads whatever `current-state.json` exists without checking `run_id`. Dispatching `run-2` after `run-1` leaves `run_id: run-1` and run-1's `run_started_at_commit`. Happens with a fresh `Orchestrator` instance too.
- **b1. `record.error` not cleared on success.** `pmos/agents/base.py:162-164` marks the sub-task COMPLETE but keeps the old error string after a failed run is recovered.
- **b2. Bare `zip(strict=True)` on sub-task drift.** `pmos/agents/base.py:257` raises an unexplained `ValueError` if the agent's sub-task list changes length between runs; names are never compared, so a reorder silently misaligns records.
- **c. Telemetry failure kills the run.** `pmos/telemetry.py:57-63` has no error handling; an `OSError` on write aborts dispatch, leaving agent/orchestrator state RUNNING. A failure inside the error-path emits (`pmos/orchestrator.py:78`, `pmos/agents/base.py:112`) masks the original exception.
- ~~**Fresh install fails test collection.**~~ Fixed on `chore/ci-and-lint`: `httpx` is now a declared dev dependency (anthropic 2.x depends on `httpx2`, not `httpx`).

### Unverified / open
- Late-October work (bug fixes, planted-bug patches, eval-harness work) is not on GitHub: no ref has a commit between 2026-09-05 and 2026-11-08. It may exist unpushed on the Mac or in Codex history; if not found, treat it as never done.
- `capability-scoring.md`, `benchmark-validation.md` and the research agent spec (`agent-research.md`) are not in this repo; presumed to be in `pm-os-build` (not verified from here).
- The fresh-install `httpx` failure was observed with anthropic 2.6.0 only.

### Work log
- 2026-11-09 — CI maintenance (`chore/ci-maintenance`): `actions/checkout` v4 → v7 and `actions/setup-python` v5 → v7 (latest majors; both declare `using: node24`), `runs-on` pinned to `ubuntu-24.04`; added `.github/dependabot.yml` (weekly, `github-actions` ecosystem only). Ledger reconciled with the 2026-11-09 history rewrite of `main`. Verified: `pytest` 102 passed, `ruff check .` clean; CI result recorded on the PR.
- 2026-11-08 — CI and hygiene (`chore/ci-and-lint`): `httpx` declared as a dev dependency; ruff pinned to 0.17.4 with explicit `select` (E4/E7/E9/F baseline + I001, UP017, UP035, PLW1510 — exactly what 0.17.4 defaults reported); 18 lint errors fixed (16 by `ruff check --fix`, `check=False` on the two git `subprocess.run` calls in `pmos/prompts.py`); added `.github/workflows/ci.yml`; removed stale `.claude/commands/` references (CLAUDE.md, AGENTS.md, .gitignore); `Claude outputs/` gitignored. Verified in a fresh Python 3.11 venv: clean install, `ruff check .` green, 102 tests pass. Not adopted: broader UP/PLW families (would add UP042 `str, Enum` → `StrEnum`, an unsafe fix that changes `str()` output).
- 2026-11-08 — Removed personal context outside PROGRESS.md (`chore/remove-personal-context`): neutral wording in Titato artifacts, eval notes, design.md and a telemetry comment; LinkedIn/blog planning removed from eval notes; deleted the three `.claude/commands/` files (they depended on the private repo). Eval scores and findings unchanged. Verified: 102 tests pass.
- 2026-11-08 — Read-only repo audit, then this ledger reconciled with git/GitHub and stripped of personal context (`chore/progress-privacy-reconcile`). Verified: 102 tests pass, ruff reports 18 errors, bugs a/b/c reproduced on main.
- 2026-11-08 — Verified a Claude Code cloud session can push a branch and open a PR (PR #3, merged same day).
- 2026-09-05 — PR #1 (`refactor/safe-pass-v2`, containing all of Phase 1) and PR #2 (cross-agent handoff rules) merged to main.
- 2026-09-05 — Multi-agent setup: AGENTS.md as canonical instructions, CLAUDE.md as import shim, session-handoff.md renamed to PROGRESS.md, .env.example added.
- 2026-09-02 — refactor/safe-pass-v2 (8 commits on the Phase 1 branch): partial redaction of this ledger (completed 2026-11-08), Phase 1 README, CLAUDE.md reconciled, telemetry/test cleanup. 102/102 tests green.
- 2026-06-02 — Added cloud-sync + project-state workflow to CLAUDE.md; reconciled the handoff ledger with the Phase 1 build.
- 2026-05-31 → 06-02 — Phase 1 orchestrator: skeleton, telemetry, config, prompts + Claude adapter, LLMAgent wiring, retry, gate flow, judgment points, output validation.

---

## BACKGROUND (design context; last substantively revised April 2026)

### Agents and pipeline
Full spec: `_system/orchestrator/design.md`.

| # | Agent | Stages covered |
|---|---|---|
| 1 | Research | Ideation, user research, market/competitive research |
| 2 | Product definition | Product brief, JTBD, MVP scope, metrics, feature decomposition, acceptance criteria |
| 3 | Design | UX flows, architecture, technical design, content/assets |
| 4 | Planning | Prioritization, effort estimation, sprint planning (runs post-design) |
| 5 | Dev & QA | Implementation, testing (iterative loop within agent) |
| 6 | Deployment | CI/CD, hosting, app store submission |
| 7 | Feedback | Analytics, bugs, reviews, outages → feeds back into Planning |

```
Research → Product definition → Design → Planning → Dev & QA → Deployment
                                            ↑                       |
                                            |                       ↓
                                            ←——— Feedback ←————————
```

Key design decisions:
- One agent per stage, clean handoffs.
- Design combines UX + architecture + content because for a solo builder these inform each other tightly.
- Feature decomposition lives in Product definition (still "what are we building").
- Planning runs after Design because sprint scoping needs real design/technical complexity.
- An agent is not 1:1 with an LLM: it is a Python module that calls whatever models or tools each sub-task needs.
- Launch/distribution is manual for now.

### Where things live
- This repo (`pm-os`, public): orchestrator code in `pmos/`, tests in `tests/`, design spec at `_system/orchestrator/design.md`, defaults at `_system/orchestrator/default_config.yaml`, prompt templates in `_system/prompt-templates/`, model eval in `_system/model-eval/`, product artifacts in `products/titato/`.
- `pm-os-build` (private): agent specs, session/personal context, blog drafts, backlog. Never copy that material here.

### Model selection eval — complete
Custom eval of Claude Opus 4.6, GPT-5 Thinking and Gemini Pro across 6 workflow streams plus constraint-sensitivity tests. Files in `_system/model-eval/`: `eval-notes.md` (original Sonnet scoring), `eval-notes-v2.md` (independent Opus rescore), `raw-evals.md` (all prompts and responses), `benchmark-mapping.md`. Overall ranking (unchanged by the rescore): Claude 163, GPT-5 146, Gemini 137.

Revised rubric: D1 premise challenging, D2 core problem identification, D3 risk identification, D4 decision quality, D5 actionability, D6 domain depth, D7 confidence calibration, TP thinking partner.

Capability-level scores (source analysis `capability-scoring.md` is not in this repo):

| Dimension | Claude | GPT | Gemini |
|---|---|---|---|
| D1 Premise challenging | 3.00 | 2.71 | 2.50 |
| D2 Core problem ID | 3.00 | 2.63 | 2.50 |
| D3 Risk identification | 2.88 | 2.43 | 2.50 |
| D4 Decision quality | 3.00 | 2.50 | 2.67 |
| D5 Actionability | 3.00 | 2.00 | 2.50 |
| D6 Domain depth | 2.71 | 2.29 | 2.38 |
| D7 Confidence calibration | 2.86 | 2.14 | 2.14 |
| TP Thinking partner | 2.67 | 2.00 | 2.17 |

Allocation guidance: Claude is the settled leader for premise challenging, actionability and confidence calibration; Gemini is competitive on creative architectural reframing and hardware domain depth; GPT is competitive on coverage checking, edge cases and experiment design. Allocation happens per sub-task as each agent is specced; only unsettled capabilities (factual verification, user journey generation, backlog prioritization, UX reasoning, sprint planning, content/copy) need new evals.

Key findings: public benchmarks did not predict PM-workflow performance (writing preference was the best single predictor; D1 and D3 have no benchmark coverage); all models improve under harder constraints; each model has a default PM lens; no model did unit-economics math unprompted.

### Orchestrator design (summary; details in `_system/orchestrator/design.md`)
Three-layer context (project-context.md, sprint-context.md, transactional state); three cycle types (MVP, minor, major) with per-agent activation; product-level config overrides; four task states (queued → running → review → complete); prompt assembly and git-based prompt versioning (implemented); context budget management (designed, not enforced); crash recovery with a state-consistency hierarchy (agent state > orchestrator state > disk/git; partially implemented); retry with no cross-model fallback (implemented, minus cross-resume give-up); structural validation (implemented) plus LLM content validation (designed only).

### Research agent spec — complete (lives in `pm-os-build`)
10 sub-tasks (8 LLM, 1 tool+LLM, 1 script), 10 config-driven judgment points, self-configures from inputs, Claude for 7 of 8 LLM sub-tasks (competitive analysis open between Gemini and Claude), mandatory gate after completion.

### Titato product artifacts (`products/titato/`)
Real content:
- `context/project-context.md` — compact context every agent reads first
- `product/product-brief.md` — users, JTBD, MVP scope, metrics, risks, voice/tone
- `product/stage-0-product-sense.md` — why AI / why not AI, failure modes, smallest viable slice
- `research/master-synthesis.md` — pain points, techniques, competitive landscape

Placeholders (one-line headers only): `architecture/options.md`, `architecture/decision.md`, `backlog/epics.md`, `backlog/sprint-current.md`, `decisions/log.md`, `eval/rubric.md`, `eval/gold-set.md`, `eval/regression-log.md`, `observability/agent-log.md`, `product/prd.md`, `product/metrics-instrumentation-map.md`, `retro/template.md`.

The app architecture decision is still pending and must be made before any Titato build work starts.

### Open design items
- Adversarial triangulation — designed conceptually, not a system component yet
- Decision reversibility framework — not yet written to `architecture/decision.md`
- Gold set schema — placeholder; high-irreversibility decision
- GPT model tier — may need a higher tier for an iteration/experimentation agent
- Gate placement for the 7-agent pipeline; API quota visibility; project-context.md update mechanism; multi-turn termination conditions (see `design.md` → Open design questions)

### Principles
- The PM OS may be over-engineered for learning — intentional. The Titato app stays lean: no premature agentic complexity.
- Separate concerns: `pm-os` (runtime + product artifacts), `pm-os-build` (build material), Titato app (separate future repo).
- Speed first, learning second for the workflow build.
- Every major product decision gets logged in `products/titato/decisions/log.md` with rationale.
- Model-provider token budgets are a legitimate, documented factor in model allocation.
- Not doing: agentic patterns inside the product; automation before the manual loop is validated; a dashboard before one full product cycle.
