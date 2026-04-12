# eval-notes.md
_AI PM Workflow — Model Selection Eval_
_Last updated: Session ongoing — Stream 4 Part C complete_

---

## BUCKET 1: THE EVAL JOURNEY

### Purpose
Evaluate Claude Opus 4.6, GPT-5 Thinking, and Gemini Pro across six workflow streams to determine optimal tool allocation for a personal AI PM operating system. Goal is not a single winner — it is a per-agent allocation decision where each agent uses the model best suited to that specific function.

---

### Models evaluated
- Claude Opus 4.6 (Claude Max $100/mo)
- GPT-5 Thinking (ChatGPT Plus $20/mo — usage-capped, not Pro)
- Gemini Pro (Google AI Pro $20/mo)

---

### Scoring rubric

| Dimension | What it measures |
|-----------|-----------------|
| D1 | Premise challenging — questions the framing, not just answers within it |
| D2 | Core problem identification — finds the most important risk |
| D3 | Decision quality — real recommendation, not a hedge |
| D4 | Actionability — can act on this immediately |
| D5 | Domain depth — specific and accurate domain knowledge |
| D6 | Technical calibration — specs hedged, uncertainty acknowledged (added Stream 2) |
| TP | Thinking partner quality — did this make you think better? (subjective 1–3) |

Scale: 1 = poor, 2 = acceptable, 3 = good

---

### Key decisions made and why

**Domain choice: smart trash can (NYC commercial office buildings), not Titato**
ChatGPT has extensive prior Titato context — unfair advantage. Many Titato artifacts were ChatGPT-generated so it would measure self-consistency not capability. Smart trash can is neutral, constraint-rich, and the household → B2G → commercial building progression mirrors real product decision evolution naturally.

**Constraint sensitivity tests added (Streams 1b, 2b)**
A single task tests whether a model can reason. Changing a key constraint tests whether recommendations update coherently — a core PM skill. Finding: all three improved significantly under harder constraints. Gap narrowed under pressure. Key insight: model choice matters less than constraint quality. Well-specified problems reduce performance gaps between models.

**Scoring: Claude Opus as primary scorer with human override**
DeepSeek rejected — insufficient reasoning depth. Grok viable but overhead not worth it. Capability matters more than independence. Real mitigation is Sid's judgment as override layer. Conflict of interest acknowledged: shared training objectives create systematic style bias (brevity, structured reasoning, premise-challenging) — not brand loyalty. Mitigation applied: "would I score this the same if the label said Gemini?" check throughout.

**D6 added to rubric at Stream 2**
All three models made confident hardware spec claims that varied in accuracy. Fast-changing specs require explicit uncertainty acknowledgment. Calibrated uncertainty is a real and differentiated capability for architecture decisions.

**TP column added**
Sid's working style prioritizes a model that sharpens thinking over one that executes. Preference for brevity and actionable density documented as a real workflow criterion, not bias to correct for.

**Architecture stream: Gemini allocated despite tied scores with Claude**
Scores tied on combined totals. Gemini's domain depth and creative reframing compensate for slightly lower calibration. Distributing agents across model families reduces correlated failure modes — architectural resilience argument, not just cost optimization.

**Adversarial triangulation identified as one-shot architectural tool**
Wisdom of crowds only works when errors are independent. LLMs trained on similar data with similar RLHF objectives produce correlated errors — all three missed unit economics math unprompted. Productive pattern: Claude generates recommendation, Gemini stress-tests architecture assumptions, ChatGPT checks coverage gaps and cites domain constraints. Disagreement is the signal, not consensus. Synthesis via structured prompt ("where do they contradict each other and in what order of consequence") — not a fourth LLM.

**Two-category framework for when to use adversarial triangulation**
One-shot architectural decisions (made once, expensive to reverse, everything downstream depends on them) warrant triangulation. Iterative operational decisions need speed. Third signal: irreversibility. Some decisions that feel operational are actually hard to reverse (gold set schema, prompt versioning convention, artifact folder structure). Cost of triangulation should track irreversibility, not just perceived importance.

---

### Surprising findings

- Benchmarks predicted Gemini would lead on reasoning (GPQA 94.3% vs Claude 91.3%). Custom eval showed Claude leading on the dimensions that matter for PM workflow — premise-challenging, actionability, calibrated uncertainty. Benchmark signal was real but not predictive of PM workflow suitability.
- All three models improved significantly when constraints were harder. The gap between models narrowed under pressure. This suggests investing in better constraint specification is higher ROI than model-switching.
- No model proactively did unit economics math. All three required explicit prompting to calculate the $50/building budget against usage patterns. Quantitative constraint checking is a systematic gap across all three — a correlated failure not independent noise.
- ChatGPT's verbosity is a consistent and measurable workflow cost. Scores well on coverage, loses on actionability, every stream. For a daily-use PM tool the cognitive tax of excavating insight from long responses is real and compounds.
- All three missed NYC specificity when questions became hardware-focused (Stream 2b). Domain depth is harder to maintain when constraint questions pull toward general engineering. Systematic gap worth noting.
- The most dangerous assumption answers in Part C revealed each model's default PM lens: Gemini thinks in compliance and business consequences, Claude thinks in safety and liability, ChatGPT thinks in architecture and abstraction. All three correct. No model named all three. A strong PM holds all three simultaneously.
- Format matters for agents. Claude's structured file output in Part B is more operationally useful than equivalent content in narrative form — ready to drop into a test management system without reformatting.

---

### Scores by stream

#### Stream 1 — Product thinking (household)

| Model | D1 | D2 | D3 | D4 | D5 | Total | TP |
|-------|----|----|----|----|-----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 2 | 14 | 3 |
| GPT-5 Thinking | 3 | 3 | 3 | 2 | 2 | 13 | 2 |
| Gemini Pro | 2 | 2 | 3 | 2 | 3 | 12 | 2 |

Standout: Claude — "training the model on confidently wrong overrides." Gemini — "localized data flywheel" framing. ChatGPT — phased roadmap most structured but buried.

#### Stream 1b — Constraint sensitivity (NYC B2G)

| Model | D1 | D2 | D3 | D4 | D5 | Total | TP |
|-------|----|----|----|----|-----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 3 | 15 | 2 |
| GPT-5 Thinking | 3 | 3 | 3 | 2 | 3 | 14 | 2 |
| Gemini Pro | 3 | 3 | 3 | 3 | 3 | 15 | 3 |

Standout: Gemini — "Facility Audit Mode" (operator as HITL). Claude — "value prop flips from adapts to you to implements policy." ChatGPT — governance argument, cited DSNY contamination data.

#### Stream 2 — Architecture design

| Model | D1 | D2 | D3 | D4 | D5 | D6 | Total | TP |
|-------|----|----|----|----|----|----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | 2 |
| GPT-5 Thinking | 3 | 3 | 3 | 2 | 3 | 2 | 16 | 2 |
| Gemini Pro | 3 | 3 | 2 | 3 | 2 | 2 | 15 | 3 |

Standout: Gemini — "CV model must never predict Recycling, it must predict Aluminum Can." Claude — decision-time vs configuration-time path separation. ChatGPT — "brutal truth: bottleneck is reliable onsite operation."

#### Stream 2b — BOM + subscription constraints

| Model | D1 | D2 | D3 | D4 | D5 | D6 | Total | TP |
|-------|----|----|----|----|----|----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 2 | 3 | 17 | 3 |
| GPT-5 Thinking | 3 | 3 | 2 | 2 | 2 | 3 | 15 | 2 |
| Gemini Pro | 3 | 3 | 3 | 3 | 2 | 3 | 17 | 2 |

Standout: Claude — NIR spectroscopy sensor as premium hardware tier (constraint → product opportunity). Gemini — zone-based fallback logic for compostable cup problem. ChatGPT — "boring is what survives a $300 BOM."

#### Stream 4A — Rubric consistency

| Model | Consistency | Accuracy obvious | Accuracy nuanced | Reasoning quality |
|-------|-------------|-----------------|------------------|------------------|
| Claude Opus 4.6 | 3 — perfect | 3 | 3 | 3 |
| GPT-5 Thinking | 2 — 2 variances | 3 | 2 | 2 |
| Gemini Pro | 3 — perfect | 3 | 2 | 2 |

Standout: Claude — "landfill routing means the context layer isn't working" diagnoses a system failure not just output quality. ChatGPT — 2 variances across 12 dimensions after interruption.

#### Stream 4B — Test coverage and edge cases

| Model | D1 | D2 | D3 | D4 | D5 | D6 | Total | TP |
|-------|----|----|----|----|----|----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | 3 |
| GPT-5 Thinking | 3 | 3 | 3 | 3 | 3 | 2 | 17 | 3 |
| Gemini Pro | 2 | 2 | 2 | 2 | 2 | 3 | 13 | 2 |

Standout: Claude — hazardous waste bin safety is a liability concern not a product concern. ChatGPT — opaque desk bin bag scenario (day-one behavioral failure invisible in lab testing). Gemini — thermal throttling on $70 NPU after 50 consecutive sorts.

#### Stream 4C — Logical flow and assumption analysis

| Model | D1 | D2 | D3 | D4 | D5 | D6 | Total | TP |
|-------|----|----|----|----|----|----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | 3 |
| GPT-5 Thinking | 3 | 3 | 2 | 2 | 2 | 2 | 14 | 3 |
| Gemini Pro | 2 | 3 | 3 | 3 | 3 | 2 | 16 | 3 |

Standout: Gemini — contamination threshold as binary compliance gate not a linear metric. Claude — clustered error distribution (one in three coffee cups misrouted) plus hazardous item liability framing. ChatGPT — "optimization theater" and taxonomy/config abstraction layer as the architectural flaw.

#### Stream 4D — Anchoring and root cause test

| Model | D1 | D2 | D3 | D4 | D5 | D6 | Total | TP |
|-------|----|----|----|----|----|----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 2 | 3 | 17 | 3 |
| GPT-5 Thinking | 3 | 2 | 3 | 2 | 3 | 2 | 15 | 2 |
| Gemini Pro | 2 | 1 | 3 | 3 | 2 | 2 | 13 | 1 |

**Critical finding — anchoring failure confirmed in Gemini.** Gemini scored 1 on D2 (behavioral root cause) and 1 on TP — the only 1 on thinking partner quality across the entire eval. Stayed entirely inside the technical system: material/state blind spot, nested items, confidence thresholds. All technically correct, all at the wrong level of abstraction. This is exactly the failure mode Sid experienced in the Lego app.

Claude was the only model that questioned the core product mechanic: "Should this device auto-sort at all, or should it recommend and let humans place?" Required stepping entirely outside the existing solution. The insight "the device replaced human judgment not just human effort" is the clearest premise challenge of any response across all streams.

ChatGPT identified behavioral change as one of five factors but buried it. Got to the right answer but didn't lead with it. Consistent pattern.

**Stream 4 complete totals:**

| Model | 4A | 4B | 4C | 4D | Stream 4 total |
|-------|----|----|-----|-----|----------------|
| Claude Opus 4.6 | 12 | 18 | 18 | 17 | 65 |
| GPT-5 Thinking | 10 | 17 | 14 | 15 | 56 |
| Gemini Pro | 11 | 13 | 16 | 13 | 53 |

**Stream 4 allocation decision: Claude for eval/QA agent.** Consistent scoring, deep reasoning, strongest test coverage, and — critically — the only model that demonstrated genuine non-anchoring in the debugging scenario. The failure mode Sid specifically wanted to avoid is most pronounced in Gemini and partially present in ChatGPT.

---

### Running tool allocation

| Agent | Leading candidate | Confidence | Key reason |
|-------|------------------|------------|-----------|
| Product thinking | Claude | Medium-high | Brevity, premise-challenging, concrete illustration |
| Architecture design | Gemini | Medium | Token distribution, creative reframing, domain depth |
| Implementation | Claude Code | High | Benchmark data confirmed |
| Eval & QA | Claude | Medium-high | Consistent scoring, reasoning depth, useful output format |
| Synthesis & communication | TBD | Low | Not yet tested |
| Iteration & experimentation | TBD | Low | Not yet tested |

---

## BUCKET 2: OPEN ITEMS / DEFERRED DECISIONS

1. **Adversarial triangulation implementation design** — pattern identified and validated conceptually but not yet specified as a reusable system component. Needs: trigger criteria (what makes a decision high-stakes enough), the three-model query structure, the synthesis prompt template, cost estimate per use.

2. **Decision-type framework formalization** — one-shot architectural vs iterative operational vs reversibility-weighted. Identified but not yet written as a formal artifact in `architecture/decision.md`. Needs to become a reference document before building the orchestrator.

3. **Rubric ambiguity on Response A Appropriateness** — Gemini scored 1, Claude scored 3, ChatGPT shifted 2→3. Genuinely contested based on whether building hauler accepts BPI-certified compostables. Resolution: add "building context assumed" clarification to gold set examples. Not resolved yet.

4. **Gold set schema** — identified as a high-irreversibility decision (hard to change once eval pipeline is built around it). Needs adversarial triangulation before locking in. Currently a placeholder in `eval/gold-set.md`.

5. **Streams 5 and 6 not yet run** — synthesis/communication and iteration/experimentation. Tool allocation for these agents still TBD.

6. **ChatGPT tier clarification** — currently on Plus ($20) not Pro ($200). Some benchmark comparisons in the eval used Pro-tier model specs. Worth noting that a Pro subscription might close some of the gap on actionability if longer context window and unlimited usage reduce the verbosity tax.

7. **Prompt versioning convention** — identified as high-irreversibility in the decision framework but not yet designed. Needs a concrete spec before the orchestrator is built.

8. **Final tool allocation model** — pending completion of all six streams. Current hypotheses are medium confidence at best.

---

## BUCKET 3: ACTION ITEMS

### For Sid

- [ ] Run Stream 4 Part D (anchoring test) — paste into all three models, come back with responses
- [ ] Run Streams 5 and 6 after Part D
- [ ] Commit this eval-notes.md to `pm-os/eval/` at end of session
- [ ] Add "adversarial triangulation" and "decision reversibility framework" to `pm-os/architecture/decision.md` as named patterns before building orchestrator
- [ ] Resolve rubric ambiguity on Response A Appropriateness — add building context clarification to gold set schema
- [ ] Make explicit decision on ChatGPT tier — is Plus sufficient or does the verbosity tax justify Pro for specific agents?

### For Claude (this session and future sessions)

- [ ] Update this file after every stream and every significant decision
- [ ] Deliver final formatted version at end of eval as LinkedIn-ready artifact
- [ ] After all streams complete: write the tool allocation model as a formal one-page artifact
- [ ] After all streams complete: write the LinkedIn post draft using the three most compelling findings

### LinkedIn post — disclaimer and transparency note
The post must include an explicit disclaimer: this eval reflects subjective assessment of best fit for a specific personal workflow and use case. No assertions are made about absolute model quality or general capability rankings. To make the methodology transparent and defensible, the post should include or link to: the scoring rubric with all six dimensions defined, two or three sample prompts used in the eval, the domain choice rationale (why smart trash can, not Titato), and the conflict of interest acknowledgment (Claude used as scorer, human override applied). The goal is "here is how I thought about this and here is the work behind it" — not "Claude is better than GPT." That framing is both more honest and more compelling to a technical audience at the companies you're targeting.

### Future enhancements and ideas to develop

**Adversarial triangulation pattern — needs full design spec:**
- Trigger criteria: use when decision is (a) one-shot or hard to reverse AND (b) high consequence if wrong AND (c) models are likely to have correlated blind spots on this topic
- Cost model: three API calls + synthesis call + human review. Estimate ~15 min overhead per use. Worth it for maybe 5–6 decisions per product lifecycle.
- Query structure: Claude generates recommendation, Gemini stress-tests architecture assumptions, ChatGPT checks coverage gaps and cites domain constraints
- Synthesis prompt template: "here are three responses — identify every point where they contradict each other or reach different conclusions, list in order of consequence"
- Output: disagreement map, not consensus. Human resolves the flagged disagreements.

**Decision reversibility framework — needs formalization:**
- Three signals for when to invest more rigor: importance (consequence if wrong), frequency (how often this type of decision recurs), irreversibility (cost to change later)
- Not all architectural decisions are hard to reverse — model selection per agent can change in one config line
- Not all operational decisions are easy to reverse — gold set schema, prompt versioning convention, artifact folder structure are hard to change once the pipeline is built around them
- Framework should live in `architecture/decision.md` as a reference before orchestrator build

**PM OS dashboard (deferred) — trigger condition:**
- Build after first full Titato product cycle is complete
- Not before — need to run the loop manually first to understand which parts are genuinely painful without a UI

**Correlated failure mode monitoring:**
- All three models missed unit economics math unprompted — systematic gap
- Consider adding an explicit "quantitative check" step to the PM reasoning agent prompt template that forces the model to work through key numbers before giving a recommendation
- Could be a prompt-level fix rather than a system-level one

**Model-as-judge limitations to document:**
- Scoring models share training alignment with the models they evaluate
- The right mitigation is human judgment as override layer, not model-switching
- Document this explicitly in the eval rubric so future eval runs start with the right posture
