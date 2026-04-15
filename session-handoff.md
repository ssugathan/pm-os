# session-handoff.md
_Context document for continuing this work in a new Claude session._
_Paste this file at the start of a new conversation to restore full context._
_Last updated: April 12, 2026_

---

## WHO YOU ARE TALKING TO

Sid Sugathan — Product Manager with 8 years PM experience, ~15 years total across business analysis, startups, and enterprise. Currently preparing for AI PM roles at OpenAI, Anthropic, Google/DeepMind, and Meta. Building two connected systems simultaneously:

1. **AI PM Workflow (personal operating system)** — a multi-agent system that simulates end-to-end PM work, optimized for learning, interview prep, and building real products efficiently
2. **Titato app** — a social communication practice app for neurodiverse children aged 3–6, featuring characters from the Fossil Friends comic series (co-created with Sid's 5-year-old son)

Sid's working style: strongest at the logical layer, prefers brevity and actionable density over comprehensive coverage, values models that challenge assumptions over models that agree, treats AI as a thinking partner not a search engine.

---

## WHAT HAS BEEN COMPLETED

### The AI PM workflow architecture
Designed and iterated through multiple versions. Final architecture is a multi-agent system with:
- **7 agents** (revised from original 5 — see agent list below)
- **Orchestrator:** lightweight Python state machine (introduce LangGraph after first full loop). Routes tasks, manages handoffs, enforces gates.
- **Artifact store:** structured markdown repo at `pm-os/products/titato/` on GitHub (github.com/ssugathan/pm-os)
- **Human approval gates** at key decision points (gate placement TBD with 7-agent structure)
- **Observability log** capturing every agent action

Architecture diagram published in blog post 1 (based on original 5-agent structure — needs updating for 7 agents).

**Revised agent list and pipeline:**

| # | Agent | Stages covered |
|---|---|---|
| 1 | Research | Ideation, user research, market/competitive research |
| 2 | Product definition | Product brief, JTBD, MVP scope, metrics, feature decomposition, acceptance criteria |
| 3 | Design | UX flows, architecture, technical design, content/assets |
| 4 | Planning | Prioritization, effort estimation, sprint planning (runs post-design) |
| 5 | Dev & QA | Implementation, testing (iterative loop within agent) |
| 6 | Deployment | CI/CD, hosting, app store submission |
| 7 | Feedback | Analytics, bugs, reviews, outages → feeds back into Planning |

Pipeline flow:
```
Research → Product definition → Design → Planning → Dev & QA → Deployment
                                            ↑                       |
                                            |                       ↓
                                            ←——— Feedback ←————————
```

Launch/distribution is manual for now — potential future agent at scale.

**Key design decisions on agents:**
- One agent per stage, clean handoffs. No agent handles multiple lifecycle stages that happen at different times.
- Design agent combines UX + architecture + content because for a solo builder these inform each other tightly.
- Feature decomposition lives in Product definition (not Planning) because it's still "what are we building."
- Planning runs after Design because sprint scoping requires knowing real design/technical complexity.
- An agent is NOT 1:1 with an LLM model. An agent is a Python module that owns a responsibility and calls whatever models or tools it needs per sub-task (see eval framework below).

**Two repos:**

`pm-os-build/` — Stream 1: building the system (design specs, eval docs, blog drafts, session context). Temporary/archival.
```
pm-os-build/
  session-handoff.md
  backlog.md
  model-eval/
    eval-notes-v2.md
    raw-evals.md
    benchmark-mapping.md
  blog/
    blog-post-vision.md
    blog-post-eval.md
    linkedin-post-vision.md
    linkedin-post-eval.md
    hero-image-agentic-pm.svg
```

`pm-os/` — Streams 2 + 3: runtime system + product artifacts.
```
pm-os/
  _system/                         ← Stream 2: runtime
    orchestrator/
      design.md
      orchestrator.py              ← (future) actual code
      current-state.json           ← (future) runtime task state
      config.yaml                  ← (future) model allocation, default modes
    prompt-templates/
    eval-framework/
    conventions.md
  products/                        ← Stream 3: product-specific
    titato/
      context/
        project-context.md
      research/
        raw/
          hanen-esdm-techniques.md
        master-synthesis.md
      product/
        stage-0-product-sense.md
        product-brief.md
      architecture/
        options.md
        decision.md                ← not yet written
      eval/
        rubric.md
        gold-set.md                ← placeholder
      backlog/
        epics.md
      decisions/
        log.md
      retro/
```

### The model selection eval — COMPLETE
Ran a full custom evaluation across Claude Opus 4.6, GPT-5 Thinking, and Gemini Pro across 6 workflow streams plus constraint sensitivity tests. All streams complete. Tool allocation finalized.

**Two scoring passes completed:**
1. **Sonnet scoring** (original, during eval sessions) — documented in `eval-notes.md`
2. **Opus rescore** (independent, from raw responses) — documented in `eval-notes-v2.md`

Opus rescore confirmed Sonnet's calibration was reasonable. Key deltas: Gemini D2 in Stream 4D moved 1→2 (partial behavioral insight via symmetric confidence error), Claude D5 in Stream 2b moved 2→3 (NIR spectroscopy + full BOM), arithmetic corrections in Stream 4A. Overall ranking unchanged: Claude 163, GPT-5 146, Gemini 137.

**Final tool allocation (from original eval — will be remapped to sub-task level):**

The original eval allocated one model per agent. The revised framework allocates models at the sub-task level within each agent. The eval results still hold as capability-level findings — they just map differently:

| Capability | Eval result | Settled? |
|---|---|---|
| Premise challenging | Claude leads | Yes |
| Synthesis / compression | Claude leads | Yes |
| Creative option generation | Gemini leads (close) | Mostly |
| Root cause / debugging | Claude leads | Yes |
| Test coverage generation | Claude leads | Yes |
| Hypothesis-to-experiment mapping | GPT leads | Yes |
| Rubric consistency | Claude leads | Yes |
| Factual verification / source eval | Not tested | No — needs eval |
| User journey generation | Not tested | No — needs eval |
| Backlog prioritization | Not tested | No — needs eval |

Model allocation per sub-task will be determined as each agent is designed. Existing eval results carry forward for settled capabilities. Only unsettled capabilities need new evals.

**Key findings from eval:**
- Benchmarks (GPQA etc.) didn't predict PM workflow performance — custom eval was essential
- All models improve under harder constraints — investing in better constraint specification beats model-switching
- Each model has a default PM lens: Gemini → compliance/business, Claude → safety/liability, GPT → architecture/abstraction. No model holds all three.
- Gemini is strongest at creative reframing but anchors hardest when debugging (tested and confirmed in Stream 4D)
- ChatGPT's verbosity is a measurable daily workflow cost — actionability suffers consistently
- No model proactively did unit economics math — systematic gap requiring explicit prompting
- Adversarial triangulation identified as a pattern for high-stakes one-shot decisions

### Eval framework — REVISED
The original eval used a universal rubric across all streams. The revised framework is more targeted:

**Revised rubric (7 dimensions + TP):**

| Dimension | What it measures |
|---|---|
| D1 | Premise challenging — questions the framing, not just answers within it |
| D2 | Core problem identification — what's actually going on here |
| D3 (new) | Risk identification — what could go wrong (stack, regulatory, deployment, user behavior) |
| D4 | Decision quality — real recommendation, not a hedge |
| D5 | Actionability — can act on this immediately |
| D6 | Domain depth — specific, accurate domain knowledge |
| D7 (revised) | Confidence calibration — asserts with appropriate certainty; flags unknowns, assumptions, outdated info (broadened from "technical calibration" to cover all claim types) |
| TP | Thinking partner — did this make you think better? |

Key changes from original: D2 narrowed to core problem only (risk split out to D3). D6 renamed and broadened from "technical calibration" to "confidence calibration" covering regulatory, factual, and domain claims — not just hardware specs.

**Eval approach:**
1. Define each agent's sub-tasks
2. For each sub-task, determine execution type: LLM call, deterministic script, or tool call
3. For LLM sub-tasks, identify 2–3 primary dimensions from the rubric
4. Map primary dimensions to existing eval results — if settled, carry allocation forward
5. Only run new evals for unsettled capability gaps
6. Allocate model per sub-task based on results

**Dimensions are not universal per agent.** Each sub-task has its own primary dimensions. Some dimensions (like confidence calibration) apply broadly. Others (like premise challenging) only apply to specific sub-tasks. The sub-task breakdown determines which dimensions matter where.

### Benchmark mapping analysis — COMPLETE
Mapped public benchmarks (GPQA, SWE-bench, GDPval, TruthfulQA, ARC-AGI-2, etc.) to eval dimensions. Key findings:
- Benchmarks predict well for coding (SWE-bench) and writing quality (human preference)
- Benchmarks are misleading for PM reasoning (GPQA predicts Gemini leads; eval shows Claude leads on PM-relevant reasoning)
- Three capabilities that mattered most in eval have zero benchmark coverage: premise-challenging, anchoring resistance, lens diversity
- GDPval-AA is the most predictive single benchmark for PM workflow (real deliverables, not isolated reasoning)

Full analysis in `benchmark-mapping.md`.

### Orchestrator design spec — MAJOR UPDATE
Design decisions documented in `_system/orchestrator/design.md`. Now covers:
- **Three-layer context model:** project-context.md (persistent, rarely changes) + sprint-context.md (per-sprint, generated by planning agent) + transactional state (orchestrator task state for agent-to-agent handoffs)
- **Three cycle types:** MVP build (full pipeline), minor fix (most agents shallow/skipped), major release (targeted depth). Planning agent determines agent activation per cycle.
- **Agent activation table:** per cycle, each agent is full/targeted/skipped. Captured in sprint-context.md.
- **Config-overrides.yaml:** generated by product definition agent based on product characteristics. Cascades into all downstream agents. Covers judgment point mode flips, operational parameters, required sub-tasks.
- **Research agent self-configuration:** runs before product definition, so self-configures from inputs. Logged as judgment calls.
- **Crash recovery:** transactional state file at every agent completion. Agent-level state file with async writes and atomic temp-file rename pattern. State consistency hierarchy: agent state > orchestrator state > disk/git.
- **Three interaction patterns:** scheduled gates, interrupt and redirect, config-driven judgment points (per-decision automated/collaborative, not per-agent)
- **Four task states:** queued → running → review → complete
- **Prompt assembly:** project-context + sprint-context + artifacts + task state + task instructions (with cycle-type prompt variants)
- **Context budget management:** pre-dispatch token check, compression strategies (selective inclusion → summarization → fallback model → fail), logged
- **Output validation:** structural (deterministic, always) + content (configurable, may use LLM). Validation results in agent state file.
- **Agent state file:** one JSON file per agent per run. Captures inputs, sub-task status, judgment calls, outputs. Async writes with atomic temp-file rename. Background thread so writes don't block main execution.

### Capability-level scoring — COMPLETE
Rescored all raw eval responses across revised 7-dimension rubric, aggregated by dimension not stream. Key findings:

| Dimension | Claude | GPT | Gemini | Leader |
|---|---|---|---|---|
| D1 — Premise challenging | 3.00 | 2.71 | 2.50 | Claude (+0.50) |
| D2 — Core problem ID | 3.00 | 2.63 | 2.50 | Claude (+0.37) |
| D3 — Risk identification | 2.88 | 2.43 | 2.50 | Claude (+0.38) |
| D4 — Decision quality | 3.00 | 2.50 | 2.67 | Claude (+0.33) |
| D5 — Actionability | 3.00 | 2.00 | 2.50 | Claude (+1.00) |
| D6 — Domain depth | 2.71 | 2.29 | 2.38 | Claude (+0.33) |
| D7 — Confidence calibration | 2.86 | 2.14 | 2.14 | Claude (+0.72) |
| TP — Thinking partner | 2.67 | 2.00 | 2.17 | Claude (+0.50) |

Claude leads every dimension. Allocation guidance is based on gap size and per-response spiky strengths:
- Claude: settled leader for premise challenging, actionability, confidence calibration (large gaps)
- Gemini: competitive on creative architectural reframing and hardware domain depth (spiky, not consistent)
- GPT: competitive on coverage checking, edge case identification, experiment design

Full analysis in `capability-scoring.md` and `benchmark-validation.md`.

### Benchmark validation — COMPLETE
Cross-referenced capability scores against public benchmarks. Key findings:
- Writing preference is the best single predictor of PM workflow performance (correctly predicts D4, D5, TP ordering)
- Knowledge benchmarks (MMLU-Pro, SimpleQA, GPQA) are inversely correlated with applied domain depth (D6)
- 2 of 7 dimensions have zero benchmark coverage (D1 premise challenging, D3 risk identification)
- GDPval is unreliable for PM-specific work — rewards coverage not actionability

### Research agent spec — COMPLETE
Full specification in `agent-research.md`. Covers:
- 10 sub-tasks (8 LLM, 1 tool+LLM, 1 script)
- 10 identified judgment points with config-driven automated/collaborative mode
- Self-configuration based on inputs (runs before product definition agent)
- Model allocation: Claude for 7 of 8 LLM sub-tasks. Competitive analysis (sub-task 5) is open — Gemini or Claude.
- Decision log format for automated mode accountability
- Config-driven judgment points with one-line summary review at completion
- Mandatory gate after completion regardless of mode

### System design review — COMPLETE
Reviewed full system end-to-end. 10 items identified:
- **Implemented:** context budget management (#3), state consistency (#5), output validation (#6)
- **Resolved via design pattern:** product definition agent generates config-overrides for downstream agents (#9), research agent self-configures (#9), Dev & QA iteration limits recommended by product definition (#8)
- **Deferred with format:** feedback agent input format — define now, plug in channels later (#10)
- **Open question:** API usage/quota visibility — do subscriptions expose remaining quota via API? (#7)
- **Captured in design:** API fallback strategy (#2), multi-turn sub-tasks (#1), project-context.md update mechanism (#4)

### Blog and LinkedIn posts — PUBLISHED / DRAFTED

**Published:**
- Blog post 1: "Building an agentic PM workflow: Vision and Plan" — live at sid-pm.com/musings/building-agentic-pm-1
- LinkedIn post 1: vision and plan summary — published

**Drafted (ready to publish):**
- Blog post 2: "Building an agentic PM workflow: the eval process" — covers methodology, rubric, streams, findings, allocation, what I'd do differently
- LinkedIn post 2: eval process summary

**Planned (not yet written):**
- Blog post 3: the actual build
- Blog post 4: test runs

### The Titato product artifacts
Seed artifacts written and in the repo:
- `project-context.md` — compact always-current context (under 500 words, all agents read first)
- `stage-0-product-sense.md` — why AI, why not AI, failure modes, smallest viable slice
- `master-synthesis.md` — compressed research including Hanen/ESDM techniques, competitive landscape, evidence base
- `product-brief.md` — target user, JTBD, MVP scope, success metrics with instrumentation, guardrail metrics, risk register, voice/tone guidelines
- `epics.md` — full backlog imported from ClickUp, 6 epics, RAG tasks flagged as architecture-decision-dependent
- `rubric.md` — 5-dimension eval rubric grounded in C-ESDM domains
- `architecture/options.md` — Option A (JSON only) vs Option B (RAG + strategy cards) vs Hybrid

**App architecture decision still pending** — must be made before any build work starts.

### CLAUDE.md relationship clarified
CLAUDE.md is a Claude Code-specific file that provides persistent session context for the coding agent. It is distinct from the PM OS artifact files. When the orchestrator is built:
- CLAUDE.md will live in the pm-os repo root, orienting Claude Code on repo structure, commands, and conventions
- It will reference the artifact files (e.g., "read project-context.md before making architecture decisions")
- project-context.md serves as the equivalent of CLAUDE.md for all agents, not just Claude Code

---

## WHAT IS NEXT

### Immediate next steps (in priority order)

**1. Define remaining 6 agent specs** — product definition, design, planning, dev & QA, deployment, feedback. Research agent is done. Same template: inputs, outputs, sub-tasks, judgment points, model allocation.

**2. Publish blog post 2 and LinkedIn post 2** — eval process posts are drafted and ready.

**3. Run targeted evals for unsettled capabilities** — user journey generation, backlog prioritization, UX reasoning, sprint planning, content/copy. Only after sub-task definitions reveal which gaps matter.

**4. Architecture decision for Titato app** — Option A vs B vs Hybrid. One-shot high-irreversibility decision. Options documented in `architecture/options.md`.

**5. Build PM OS orchestrator** — scaffold in Python. Design spec at `_system/orchestrator/design.md` is substantially complete. Start with raw Python state machine.

**6. Build Phase 1 of Titato app** — Flutter project setup, one complete Dino Valley scene, TTS working, parent setup screen.

---

## IMPORTANT CONTEXT AND PREFERENCES

**Repos:**
- github.com/ssugathan/pm-os — runtime system + product artifacts (Streams 2 + 3)
- github.com/ssugathan/pm-os-build — build artifacts, eval docs, blog drafts, session context (Stream 1)

**Blog:** sid-pm.com/musings

**Subscriptions:**
- Claude Max $100/mo (Opus 4.6 access)
- ChatGPT Plus $20/mo (GPT-5 Thinking, usage-capped)
- Google AI Pro $20/mo (Gemini Pro)
- Cursor $20/mo (primarily for coding and prototyping)

**Key design principles Sid has established:**
- AI PM workflow may be over-engineered for learning — that is intentional
- Titato app must be lean and pragmatic — no premature agentic complexity
- Three repos, three concerns: pm-os (runtime), pm-os-build (build artifacts), titato app (separate, future)
- Speed is priority 1 for the workflow build, learning is priority 2
- Every major decision gets logged in `decisions/log.md` with rationale
- Token distribution across subscriptions is a legitimate practical factor in model allocation — documented honestly, not hidden

**Sid's communication style (for writing posts):**
- Conversational, first-person, no hype
- Framed as experiment and learning, not "look at my creation"
- Substance over headlines — targeting recruiters/hiring managers who visit his profile, not viral reach
- Concrete examples over abstract frameworks
- Comfortable referencing past builds (Lego app, smart trash can) but doesn't name Titato publicly yet
- Blog link in LinkedIn comments, feedback ask at the end of posts

**Open items requiring decisions:**
- Adversarial triangulation — designed conceptually, not yet implemented as a system component
- Decision reversibility framework — identified, not yet written to `architecture/decision.md`
- Gold set schema — placeholder only, high-irreversibility decision needing careful design
- ChatGPT tier — currently Plus, may need Pro for iteration/experimentation agent
- Prompt versioning convention — not yet specified

**Things Sid is NOT doing:**
- Over-indexing on agentic patterns in the product
- Building automation before the manual loop is validated
- Using the PM OS dashboard before completing one full product cycle

---

## HOW TO CONTINUE

If Sid pastes this document at the start of a new session, you have full context to:
- Define remaining agent specs (product definition agent is next — use research agent spec as template)
- Run targeted evals for unsettled capabilities
- Publish eval posts (blog 2 + LinkedIn 2)
- Run the architecture decision session for Titato
- Build the PM OS orchestrator (design spec is substantially complete)
- Write any outstanding artifacts (decision reversibility framework, adversarial triangulation spec, CLAUDE.md for the repo)
- Continue any part of the Titato product build
- Write blog posts 3 and 4
- Update the architecture diagram for 7-agent structure with cycle types and sprint context

Key files to reference:
- `orchestrator-design.md` — full system design spec
- `agent-research.md` — research agent spec (template for other agents)
- `capability-scoring.md` — per-dimension model scores for sub-task allocation
- `benchmark-validation.md` — public benchmark cross-reference

Ask Sid which of these he wants to tackle first rather than assuming.
