# Orchestrator design spec
_PM OS — `_system/orchestrator/design.md`_
_Last updated: April 12, 2026_

---

## Overview

The orchestrator is the central coordination layer of the PM OS. It routes tasks to specialist agents, manages handoffs between agents using different models, enforces human approval gates, handles crash recovery, and logs every action.

Implementation: raw Python state machine first. Introduce LangGraph after the first full product cycle runs end-to-end manually.

---

## Context model

The system has two layers of context that serve different purposes.

### Layer 1: Persistent project context (markdown files)

These files are the shared knowledge base across all agents. They evolve slowly across the project lifecycle.

- `project-context.md` — compact always-current context. Every agent reads this first, every time.
- Product artifacts (`product-brief.md`, `master-synthesis.md`, `options.md`, etc.) — read by agents as needed for specific tasks.
- Eval artifacts (`rubric.md`, `gold-set.md`) — read by the eval agent.

These files are the long-term memory of the system. They answer: what is this project, what has been decided, what are the constraints?

### Layer 2: Transactional context (orchestrator state)

This is the short-term working memory. It captures what is happening right now in this run of the workflow. It exists because different agents use different models with no shared conversation history — Claude can't see what Gemini just said.

The orchestrator constructs transactional context and passes it to each agent as part of the prompt. It includes:
- What the previous agent produced
- What the human decided at the last gate (if any)
- Caveats, redirects, or constraints from the human
- What the current agent needs to do

This is the relay baton. It travels with each handoff.

### Prompt assembly

The orchestrator constructs each agent's prompt by assembling four components:

1. **Project context** — always `project-context.md`
2. **Relevant artifact files** — varies by agent and task (e.g., synthesis agent reads `master-synthesis.md`, architecture agent reads `options.md`)
3. **Task state** — the transactional context from the orchestrator (what just happened, what was decided, what to do next)
4. **Task instructions** — the specific prompt for this task

The orchestrator is responsible for assembling 1–4 into a single prompt and dispatching it to the correct model.

---

## Task states

Every task in the pipeline moves through four states:

```
queued → running → review → complete
```

- **Queued** — task defined by the orchestrator, waiting to be dispatched to an agent
- **Running** — agent is working. In autonomous mode, the agent produces output and the task moves to complete. In collaborative mode, the agent produces a draft and the task moves to review.
- **Review** — agent output is ready, waiting for human input. This state is entered in three ways: (1) the task is in collaborative mode, (2) the task has reached a scheduled gate, or (3) the user interrupted the pipeline.
- **Complete** — human approved (collaborative/gate) or autonomous task finished. Output written to artifact store. Orchestrator advances to next task.

---

## Interaction patterns

There are three ways a human interacts with the running system.

### 1. Scheduled gates (mandatory pauses)

The three gates defined in the architecture:
- **Post-research** — is this research sufficient? Are we looking at the right things?
- **Post-architecture** — is this the right design direction before we commit to building?
- **Post-eval** — are we ready to ship, or do we need to iterate?

At a gate, the orchestrator stops the pipeline, presents the relevant agent output, and waits for human input. The human can: approve and proceed, request changes (agent re-runs with feedback), or redirect the entire pipeline.

Gates are mandatory. The orchestrator will not advance past a gate without explicit human approval.

### 2. Interrupt and redirect

The user is watching output and wants to stop the pipeline, give feedback, and have the agent redo or adjust.

Mechanism: keyboard interrupt (or equivalent signal) transitions the current task from `running` to `review`. The orchestrator captures the user's feedback, appends it to the task state as a constraint, and re-runs the current agent with updated context. This is equivalent to rolling back to the last checkpoint and re-running with new inputs.

### 3. Depth toggle (autonomous vs collaborative)

Every task dispatched by the orchestrator has an interaction mode:

- **Autonomous** — agent runs, writes output, task moves to complete. No human review unless interrupted.
- **Collaborative** — agent produces a draft, presents it to the human, waits for feedback, iterates, then writes the final output. Task moves through review before complete.

The mode is set by defaults (see below) but can be overridden per-task at runtime.

### Default interaction modes

Defaults are set per task type based on irreversibility and confidence:

| Task type | Default mode | Rationale |
|-----------|-------------|-----------|
| Research synthesis | Autonomous | Low irreversibility, easy to redo |
| Test case generation | Autonomous | Boilerplate, agent handles well |
| Component scaffolding | Autonomous | Standard patterns, low risk |
| Product brief drafting | Collaborative | High-judgment, shapes downstream decisions |
| Architecture decision | Collaborative | High-irreversibility, one-shot |
| Eval rubric design | Collaborative | Hard to change once pipeline is built around it |
| First implementation of a feature | Collaborative | Novel work, edge cases matter |
| Bug fixes on established patterns | Autonomous | Constrained scope, well-defined |

Before each run begins, the orchestrator presents the planned tasks and their default modes. The user confirms or tweaks defaults for this run. This handles the case where a normally-autonomous task needs deeper attention for a specific product (e.g., research for a compliance-heavy app needs collaborative mode even though research is normally autonomous).

---

## Crash recovery

### Transactional state file

The orchestrator writes a state file to disk at every state transition. Location: `_system/orchestrator/current-state.json`

The state file captures:
- Current pipeline run ID
- List of all tasks in the pipeline with their current state (queued/running/review/complete)
- The currently active task
- The active agent and model
- Inputs to the active task
- The last completed agent output (file path in artifact store)
- The last gate decision (if any)
- Timestamp

### Checkpoint granularity

Checkpoints happen at agent completion, not mid-agent. If the coding agent is halfway through writing a file when the system crashes, the orchestrator re-runs the coding agent with the same inputs on restart. It does not attempt to resume mid-agent.

This means:
- Checkpoint after every agent completes and writes output
- Checkpoint after every gate decision
- Checkpoint after every user interrupt and redirect
- No checkpoint during agent execution

### Restart behavior

On restart, the orchestrator reads `current-state.json` and determines where to resume:

| State at crash | Restart behavior |
|---------------|-----------------|
| Task was `queued` | Dispatch the task normally |
| Task was `running` | Re-run the agent with the same inputs (idempotent re-execution) |
| Task was `review` | Re-present the output to the user for review |
| Task was `complete` | Advance to next task |

### Idempotency

Agent tasks should be designed to be idempotent where possible. Re-running an agent with the same inputs should produce roughly equivalent output. This makes crash recovery cheap — just redo the last agent's work.

For tasks that are not naturally idempotent (e.g., implementation tasks that modify files), the state file captures enough context to reconstruct the starting conditions.

---

## Agent output conventions

Each agent writes its output to a known location in the artifact store. The orchestrator uses these locations to construct the next agent's inputs.

| Agent | Output location | Format |
|-------|----------------|--------|
| Research | `research/raw/[timestamp]-[topic].md` | Structured markdown with sources |
| PM Synthesis | `product/[artifact-name].md` | Product brief, PRD, or synthesis doc |
| Architecture | `architecture/options.md` or `architecture/decision.md` | Options analysis or decision record |
| Coding | Working directory + git commit | Code files, committed to repo |
| Eval | `eval/[test-type]-[timestamp].md` | Scored results, test coverage, recommendations |

The orchestrator knows where each agent writes and where the next agent reads. This is the routing logic.

---

## Observability log

Every agent action is logged to `_system/orchestrator/run-log.md` (or a structured log file) with:
- Timestamp
- Agent name and model
- Task description
- Input files read
- Output files written
- Duration
- Interaction mode (autonomous/collaborative)
- Gate decisions (if applicable)
- User interrupts and feedback (if applicable)

The log serves two purposes: audit trail for debugging, and recoverable context if the state file is corrupted.

---

## Relationship to CLAUDE.md

CLAUDE.md is a Claude Code-specific file that lives in the repo root. It provides persistent session context for the coding agent only.

When the orchestrator dispatches a task to Claude Code, Claude Code reads CLAUDE.md automatically as part of its session startup. The orchestrator's prompt assembly (project-context.md + artifacts + task state + instructions) is separate from and complementary to CLAUDE.md.

CLAUDE.md should contain:
- Repo structure overview
- Build/test/lint commands
- Code style conventions
- References to artifact files the coding agent should read for product context

CLAUDE.md is not a substitute for the orchestrator's transactional context. It provides "how to work in this codebase" context. The orchestrator provides "what to do right now" context.

---

## Open design questions

1. **State file format** — JSON is simple but may want to move to SQLite if the run log grows large. Start with JSON, migrate if needed.
2. **Multi-model API management** — the orchestrator needs API clients for Claude, Gemini, and GPT. Consider a thin adapter layer so swapping models per agent is a config change, not a code change.
3. **Adversarial triangulation integration** — currently a manual pattern (query all three, compare). Could be formalized as a special orchestrator mode where a single task is dispatched to all three models and the user gets a disagreement map. Not needed for v1.
4. **Prompt versioning** — identified as high-irreversibility. Needs a convention before the orchestrator is built. Options: git-based (prompts are files, versioned by commit), or explicit version numbers in filenames.
5. **Context window management** — as artifact files grow, the assembled prompt may exceed model context limits. Need a strategy for selective loading (only the relevant sections of large files) or summarization.
