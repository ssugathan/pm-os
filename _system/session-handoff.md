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
- **5 specialist agents:** research, PM synthesis, architecture, coding (Claude Code), eval/QA
- **Orchestrator:** lightweight Python (LangGraph or custom state machine) routing tasks between agents
- **Artifact store:** structured markdown repo at `pm-os/products/titato/` on GitHub (github.com/ssugathan/pm-os)
- **Human approval gates** at: post-research, post-architecture, post-eval
- **Observability log** capturing every agent action

Architecture diagram finalized and published (see blog post 1).

The PM OS repo structure:
```
pm-os/
  _system/
    orchestrator/
      design.md            ← NEW: orchestrator design spec (crash recovery, interaction patterns, task states)
    eval-scripts/
    prompt-templates/
    model-eval/
      eval-notes.md        ← original Sonnet scoring
      eval-notes-v2.md     ← NEW: Opus rescore with independent scoring and delta analysis
      raw-evals.md         ← all prompts and responses
      benchmark-mapping.md ← NEW: public benchmarks mapped to eval dimensions
  products/
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
        options.md         ← Option A vs B vs Hybrid for app
        decision.md        ← not yet written
      prompts/
      eval/
        rubric.md
        gold-set.md        ← placeholder
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

**Final tool allocation:**

| Agent | Model | Confidence | Key reason | Token distribution factor |
|-------|-------|------------|-----------|--------------------------|
| Product thinking | Claude Opus 4.6 | High | Brevity, premise-challenging, concrete illustration | N/A — clear winner |
| Architecture design | Gemini Pro | Medium | Creative reframing, tied with Claude in S2b. Token distribution is legitimate tiebreaker. | Primary factor in tiebreak |
| Implementation | Claude Code | High | SWE-bench benchmark confirmed | N/A — dedicated tool |
| Eval & QA | Claude Opus 4.6 | High | Non-anchoring, consistent scoring, strongest test coverage | N/A — clear winner |
| Synthesis & communication | Claude Opus 4.6 | High | Faithful compression, non-obvious insight, usable format | N/A — clear winner |
| Iteration & experimentation | GPT-5 Thinking | Medium | Best hypothesis-to-result mapping, four-category framework | Reinforcing factor |

**Key findings from eval:**
- Benchmarks (GPQA etc.) didn't predict PM workflow performance — custom eval was essential
- All models improve under harder constraints — investing in better constraint specification beats model-switching
- Each model has a default PM lens: Gemini → compliance/business, Claude → safety/liability, GPT → architecture/abstraction. No model holds all three.
- Gemini is strongest at creative reframing but anchors hardest when debugging (tested and confirmed in Stream 4D)
- ChatGPT's verbosity is a measurable daily workflow cost — actionability suffers consistently
- No model proactively did unit economics math — systematic gap requiring explicit prompting
- Adversarial triangulation identified as a pattern for high-stakes one-shot decisions

### Benchmark mapping analysis — COMPLETE
Mapped public benchmarks (GPQA, SWE-bench, GDPval, TruthfulQA, ARC-AGI-2, etc.) to eval dimensions. Key findings:
- Benchmarks predict well for coding (SWE-bench) and writing quality (human preference)
- Benchmarks are misleading for PM reasoning (GPQA predicts Gemini leads; eval shows Claude leads on PM-relevant reasoning)
- Three capabilities that mattered most in eval have zero benchmark coverage: premise-challenging, anchoring resistance, lens diversity
- GDPval-AA is the most predictive single benchmark for PM workflow (real deliverables, not isolated reasoning)

Full analysis in `benchmark-mapping.md`.

### Orchestrator design spec — COMPLETE
Design decisions documented in `_system/orchestrator/design.md`. Covers:
- **Two-layer context model:** persistent project context (md files) + transactional context (orchestrator task state)
- **Crash recovery:** transactional state file (`current-state.json`) written at every agent completion. Checkpoint = agent completion, not mid-agent. Tasks designed to be idempotent for safe re-run.
- **Three interaction patterns:** scheduled gates (mandatory pauses), interrupt and redirect (user stops pipeline, gives feedback, agent re-runs), depth toggle (autonomous vs collaborative mode per task)
- **Four task states:** queued → running → review → complete. Interrupt transitions any running task to review. Autonomous tasks skip review.
- **Prompt assembly:** orchestrator constructs each agent prompt as: project-context.md + relevant artifact files + task state from orchestrator + task instructions
- **Default interaction modes:** set per task type, user confirms/tweaks defaults before each run begins

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

**1. Publish blog post 2 and LinkedIn post 2** — eval process posts are drafted and ready.

**2. Architecture decision for Titato app** — Option A vs B vs Hybrid. This is a one-shot high-irreversibility decision and warrants adversarial triangulation (query all three models, look for disagreement, Sid resolves). Options documented in `architecture/options.md`.

**3. Build PM OS orchestrator** — first Claude Code ticket: scaffold the orchestrator skeleton in Python. Design spec is now written at `_system/orchestrator/design.md`. Start with raw Python state machine, introduce LangGraph after first full loop runs.

**4. Build Phase 1 of Titato app** — Flutter project setup, one complete Dino Valley scene, TTS working, parent setup screen. Target: demoable on device by end of Week 3 of the build plan.

---

## IMPORTANT CONTEXT AND PREFERENCES

**Repo:** github.com/ssugathan/pm-os (live, scaffolded, seed artifacts committed)

**Blog:** sid-pm.com/musings

**Subscriptions:**
- Claude Max $100/mo (Opus 4.6 access)
- ChatGPT Plus $20/mo (GPT-5 Thinking, usage-capped)
- Google AI Pro $20/mo (Gemini Pro)
- Cursor $20/mo (primarily for coding and prototyping)

**Key design principles Sid has established:**
- AI PM workflow may be over-engineered for learning — that is intentional
- Titato app must be lean and pragmatic — no premature agentic complexity
- Two separate repos, two separate concerns
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
- Publish eval posts (blog 2 + LinkedIn 2)
- Run the architecture decision session for Titato
- Build the PM OS orchestrator (design spec exists at `_system/orchestrator/design.md`)
- Write any outstanding artifacts (decision reversibility framework, adversarial triangulation spec, CLAUDE.md for the repo)
- Continue any part of the Titato product build
- Write blog posts 3 and 4

Ask Sid which of these he wants to tackle first rather than assuming.
