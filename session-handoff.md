# session-handoff.md
_Context document for continuing this work in a new Claude session._
_Paste this file at the start of a new conversation to restore full context._

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

The PM OS repo structure:
```
pm-os/
  _system/
    orchestrator/
    eval-scripts/
    prompt-templates/
    model-eval/
      eval-notes.md        ← completed eval documentation
      raw-evals.md         ← all prompts and responses
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

**Final tool allocation:**

| Agent | Model | Confidence | Key reason |
|-------|-------|------------|-----------|
| Product thinking | Claude Opus 4.6 | High | Brevity, premise-challenging, concrete illustration |
| Architecture design | Gemini Pro | Medium | Token distribution, creative reframing, domain depth |
| Implementation | Claude Code | High | SWE-bench benchmark confirmed |
| Eval & QA | Claude Opus 4.6 | High | Non-anchoring, consistent scoring, structured output |
| Synthesis & communication | Claude Opus 4.6 | High | Faithful compression, non-obvious insight, usable format |
| Iteration & experimentation | GPT-5 Thinking | Medium | Best hypothesis-to-result mapping, four-category framework |

**Key findings from eval:**
- Benchmarks (GPQA etc.) didn't predict PM workflow performance — custom eval was essential
- All models improve under harder constraints — investing in better constraint specification beats model-switching
- Gemini is strongest at creative reframing but anchors hardest when debugging (tested and confirmed)
- ChatGPT's verbosity is a measurable daily workflow cost — actionability suffers consistently
- No model proactively did unit economics math — systematic gap requiring explicit prompting
- Adversarial triangulation identified as a pattern for high-stakes one-shot decisions: Claude generates, Gemini stress-tests, ChatGPT checks coverage. Disagreement is the signal, not consensus.

Full details in `pm-os/_system/model-eval/eval-notes.md`

### The Titato product artifacts
Four seed artifacts written and in the repo:
- `project-context.md` — compact always-current context (under 500 words, all agents read first)
- `stage-0-product-sense.md` — why AI, why not AI, failure modes, smallest viable slice
- `master-synthesis.md` — compressed research including Hanen/ESDM techniques, competitive landscape, evidence base
- `product-brief.md` — target user, JTBD, MVP scope, success metrics with instrumentation, guardrail metrics, risk register, voice/tone guidelines
- `epics.md` — full backlog imported from ClickUp, 6 epics, RAG tasks flagged as architecture-decision-dependent
- `rubric.md` — 5-dimension eval rubric grounded in C-ESDM domains
- `architecture/options.md` — Option A (JSON only) vs Option B (RAG + strategy cards) vs Hybrid

**App architecture decision still pending** — must be made before any build work starts. Options documented in `architecture/options.md`.

---

## WHAT IS NEXT

### Immediate next steps (in priority order)

**1. LinkedIn post** — summarize the model eval journey as a public artifact. Key requirements:
- Disclaimer: this is subjective assessment for a specific use case, not absolute model rankings
- Include methodology: scoring rubric, sample prompts, domain choice rationale, conflict of interest acknowledgment
- Frame as "here is how I thought about this" not "Claude is better than GPT"
- Three most compelling findings: benchmark gap vs custom eval results, constraint quality > model switching, Gemini creative reframing vs anchoring failure

**2. Architecture decision for Titato app** — Option A vs B vs Hybrid. This is a one-shot high-irreversibility decision and warrants adversarial triangulation (query all three models, look for disagreement, Sid resolves). Options documented in `architecture/options.md`.

**3. Build PM OS orchestrator** — first Claude Code ticket: scaffold the orchestrator skeleton in Python. Start with raw Python state machine, introduce LangGraph after first full loop runs.

**4. Build Phase 1 of Titato app** — Flutter project setup, one complete Dino Valley scene, TTS working, parent setup screen. Target: demoable on device by end of Week 3 of the build plan.

---

## IMPORTANT CONTEXT AND PREFERENCES

**Repo:** github.com/ssugathan/pm-os (live, scaffolded, four seed artifacts committed)

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
- Continue building the PM OS orchestrator
- Draft the LinkedIn post
- Run the architecture decision session for Titato
- Write any of the outstanding artifacts (decision reversibility framework, adversarial triangulation spec, tool allocation one-pager)
- Continue any part of the Titato product build

Ask Sid which of these he wants to tackle first rather than assuming.
