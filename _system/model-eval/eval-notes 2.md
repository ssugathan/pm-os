# eval-notes.md (v2 — Opus rescore)
_AI PM Workflow — Model Selection Eval_
_Rescored independently by Claude Opus 4.6 from raw responses_
_Original scored by Claude Sonnet during eval sessions_

---

## METHODOLOGY

### Purpose
Evaluate Claude Opus 4.6, GPT-5 Thinking, and Gemini Pro across six workflow streams to determine optimal per-agent tool allocation for a personal AI PM operating system. Goal is not a single winner — it is a per-agent allocation decision where each agent uses the model best suited to that specific function.

A secondary practical constraint: Sid holds a Claude Max subscription ($100/mo) and will use Claude Code heavily for building both the PM OS and the Titato app. Where a non-Claude model is competitive or neck-and-neck with Claude on a given agent, there is a legitimate reason to allocate that agent to Gemini or GPT-5 to distribute token load. This is documented as a factor in allocation decisions, not hidden behind scoring adjustments.

### Models evaluated
- Claude Opus 4.6 (Claude Max $100/mo)
- GPT-5 Thinking (ChatGPT Plus $20/mo — usage-capped, not Pro)
- Gemini Pro (Google AI Pro $20/mo)

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

### Scoring approach for this rescore
Opus scored each stream independently from the raw responses in `raw-evals.md` before comparing to the original Sonnet scores. Where full responses were not available (Streams 4B, 4C, 6), Opus worked from the standout summaries and cannot independently verify — these are flagged. Conflict of interest acknowledgment carries forward: Claude scoring Claude responses creates systematic style alignment. The "would I score this the same if the label said Gemini?" check was applied throughout.

### Key design decisions (carried forward from original)

**Domain choice: smart trash can (NYC commercial office buildings), not Titato.** ChatGPT has extensive prior Titato context — unfair advantage. Smart trash can is neutral and constraint-rich.

**Constraint sensitivity tests (Streams 1b, 2b).** Changing a key constraint tests whether recommendations update coherently. Finding confirmed: all three improved under harder constraints. Gap narrowed under pressure. Constraint quality > model switching.

**D6 added at Stream 2.** All three models made confident hardware spec claims. Calibrated uncertainty is a differentiated capability for architecture decisions.

**TP column.** Sid's working style prioritizes a model that sharpens thinking. Preference for brevity and actionable density is a documented workflow criterion, not bias to correct for.

---

## SCORES BY STREAM — INDEPENDENT RESCORE

### Stream 1 — Product thinking (household)

| Model | D1 | D2 | D3 | D4 | D5 | Total | TP |
|-------|----|----|----|----|-----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 2 | 14 | 3 |
| GPT-5 Thinking | 3 | 3 | 3 | 2 | 2 | 13 | 2 |
| Gemini Pro | 2 | 2 | 3 | 2 | 2 | 11 | 2 |

**Scoring rationale:**

Claude D1=3: "You'd be training the model on confidently wrong overrides" challenges the fundamental assumption that user overrides would improve accuracy. This reframes the entire feature — the learning mode isn't just hard to build, it might actively degrade the product. Strongest premise challenge in the stream.

Claude D4=3: "Auto-detect via zip code," "override button that logs disagreements to cloud," "80% of the trust benefit, 90% of the data benefit, almost none of the engineering cost" — quantified tradeoffs with immediately implementable alternatives.

GPT-5 D1=3: "Users may think they are teaching the system the right answer but in reality they are feeding noisy labels" — gets to the same premise challenge as Claude, less sharply stated but the insight is there. D4=2: Four-phase roadmap is well-structured but the phasing buries what to do now. Consistent pattern: correct analysis, lower immediacy.

Gemini D1=2: "Localized data flywheel" is a creative framing but accepts the feature premise rather than questioning it. Evaluates the feature within its own frame — best case and worst case — but doesn't ask whether the core assumption (users know correct sorting) holds. D5=2: Household examples (craft beer can, organic toddler snacks) are illustrative but generic product-sense examples, not waste management domain knowledge. Compare to Claude's municipality-level recycling rule variation (Portland vs Phoenix) or lithium battery routing — those show understanding of the regulatory and safety landscape, not just ML edge cases.

**Delta from Sonnet scoring:** Gemini D5 drops from 3→2 (total 12→11). Sonnet may have credited Gemini's ML-flavored examples (edge fine-tuning, personalized model weights) as domain depth, but D5 should measure domain knowledge about the product space (household waste management), not generic ML engineering knowledge. The distinction matters because a PM needs to know the domain, not just the tech stack.

---

### Stream 1b — Constraint sensitivity (NYC B2G)

| Model | D1 | D2 | D3 | D4 | D5 | Total | TP |
|-------|----|----|----|----|-----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 3 | 15 | 2 |
| GPT-5 Thinking | 3 | 3 | 3 | 2 | 3 | 14 | 2 |
| Gemini Pro | 3 | 3 | 3 | 3 | 3 | 15 | 3 |

**Scoring rationale:**

Gemini TP=3: "Facility Audit Mode" is the standout concept of the stream — reframes who the HITL is (facility manager/sanitation worker, not the person throwing trash away). This is a genuine product concept, not just analysis. It creates a new mental model that changes how you design the feature. Best thinking partner moment across any model in 1b.

Claude TP=2: "Value prop flips from 'adapts to you' to 'implements policy perfectly and provably'" is analytically sharp but more descriptive than generative. It names what changed; Gemini creates something new.

GPT-5 D4=2: Recommendations are reasonable (operator override, remote rule management, telemetry) but less NYC-specific and less concretely implementable than Claude's (compliance dashboards, exportable data, multi-language signage) or Gemini's (Facility Audit Mode with specific CWZ integration).

**Delta from Sonnet scoring:** None. Matches exactly.

---

### Stream 2 — Architecture design

| Model | D1 | D2 | D3 | D4 | D5 | D6 | Total | TP |
|-------|----|----|----|----|----|----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | 2 |
| GPT-5 Thinking | 3 | 3 | 3 | 2 | 2 | 2 | 15 | 2 |
| Gemini Pro | 3 | 3 | 2 | 3 | 2 | 2 | 15 | 3 |

**Scoring rationale:**

Claude D6=3: Explicitly acknowledges where approaches break — Approach 3 is "problematic" and "fragile," latency for on-device LLM is "1–3 seconds" framed as a risk rather than a feature. Provides ranges ("well under 500ms") rather than false precision. Best-calibrated uncertainty in the stream.

Gemini D3=2: Recommends "a hybrid of Architecture 1 and Architecture 2." Hybrid recommendations can be a way to avoid deciding. In this case, the hybrid is defensible (each architecture handles a different concern), but it asks the team to build two subsystems for an MVP. Less decisive than Claude's single recommendation (Approach 2) or GPT-5's single recommendation (Approach 1). D6=2: Makes confident latency claims ("<50ms after CV inference") without hedging or acknowledging the conditions under which these would change.

Gemini TP=3: "Your base CV model must never predict 'Recycling.' It must predict 'Aluminum Can.'" This is the single sharpest architectural insight in Stream 2. It reframes the entire taxonomy design — classification and routing are separate concerns that should never be conflated. This insight would change how you architect the system regardless of which approach you choose.

GPT-5 D1=3: "The brutal truth: your bottleneck is reliable onsite operation in hostile enterprise conditions" — challenges the assumption that AI sophistication matters at this stage. D4=2, D5=2: Response is summarized rather than fully available; from what's visible, less hardware-specific than Claude and less architecturally creative than Gemini.

**Delta from Sonnet scoring:** GPT-5 total drops from 16→15 (D5: 3→2). Without the full raw response, this is lower confidence. Sonnet may have had access to hardware specifics in GPT-5's response that didn't make it into the raw-evals summary. Flagged as uncertain.

---

### Stream 2b — BOM + subscription constraints

| Model | D1 | D2 | D3 | D4 | D5 | D6 | Total | TP |
|-------|----|----|----|----|----|----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | 3 |
| GPT-5 Thinking | 3 | 3 | 2 | 2 | 3 | 3 | 16 | 2 |
| Gemini Pro | 3 | 3 | 3 | 3 | 3 | 3 | 18 | 2 |

**Scoring rationale:**

Claude D5=3: Specific component pricing (Coral TPU $25–35, CM4 $25–45, NB-IoT modem $10–15), full BOM breakdown summing to $190–300, AND the NIR spectroscopy sensor ($50–100) as a premium hardware tier option. The NIR suggestion is particularly strong — it turns a constraint (can't distinguish compostable cup from plastic visually) into a product tier opportunity. This is deep domain knowledge applied to a product architecture problem.

Gemini D5=3: Specific chip families (Rockchip RK3566/RK3588s, NXP i.MX 8M Plus) with accurate price ranges ($60–90 for compute), MQTT text payloads, SD card offline sync strategy. Different flavor of depth from Claude — more silicon-level, less product-level — but equally specific and accurate.

GPT-5 D5=3: Cited specific component pricing with links (Jetson Orin Nano $249, Pi 5 at $45/$65/$110 by RAM tier, Coral Mini PCIe at $24.99). Most verifiable of the three — external citations add credibility. D3=2: "Boring is what survives a $300 BOM and a flat subscription" is a great line but the recommendation ("local constrained vision classifier + deterministic local policy engine + optional low-cost accelerator") includes "optional" — slightly hedgy for a BOM-constrained decision where every component either makes the cut or doesn't.

Claude TP=3: NIR spectroscopy as premium tier is the strongest thinking partner moment — it reframes the $300 BOM constraint from "what do we cut" to "what defines the tier structure." This is generative product thinking, not just constraint satisfaction.

**Delta from Sonnet scoring:** All three models' D5 scores move from 2→3 (Claude 17→18, GPT-5 15→16, Gemini 17→18). This is the most significant systemic change. Sonnet appears to have applied a stricter D5 standard in 2b than in other streams — all three models demonstrated genuine domain depth here with specific, verifiable hardware knowledge. The 2→3 shift is consistent across all three, so it doesn't change relative positioning but does change the absolute signal about domain depth capability.

---

### Stream 4A — Rubric consistency

| Model | Consistency | Accuracy obvious | Accuracy nuanced | Reasoning quality | Total |
|-------|-------------|-----------------|------------------|-------------------|-------|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 12 |
| GPT-5 Thinking | 2 | 3 | 2 | 2 | 9 |
| Gemini Pro | 3 | 3 | 2 | 2 | 10 |

**Scoring rationale:**

Claude Consistency=3: Zero variances across two scoring rounds with an interruption prompt between them. Perfect reproducibility. Reasoning quality=3: "Landfill routing means the context layer isn't working" — diagnoses a system failure mode rather than just evaluating output quality. Shows deeper reasoning about what the scores mean.

GPT-5 Consistency=2: Two variances across 12 dimensions after interruption (Response A Appropriateness 2→3, Response B Tone 2→1). The variances went in opposite directions — one became more generous, one stricter — suggesting instability rather than systematic drift. Accuracy nuanced=2: The Response A Appropriateness shift (2→3) actually improved accuracy on second pass, but the instability itself is the concern for an eval agent.

Gemini Consistency=3: Zero variances, matching Claude. Accuracy nuanced=2: Scored Response A Appropriateness as 1 (both rounds). This is the genuinely contested score — depends on whether a BPI-certified compostable cup is accepted in a building's organics stream. Gemini's position (1 = inappropriate) is defensible if the building's carter doesn't accept BPI-certified items. Claude's position (3 = appropriate given context) is defensible if building context is assumed. Neither is clearly wrong, but Gemini's absolute rejection without acknowledging the context dependency is less nuanced.

**Delta from Sonnet scoring:** GPT-5 drops from 10→9, Gemini drops from 11→10. The original totals don't match the original table arithmetic (2+3+2+2=9, not 10 for GPT-5; 3+3+2+2=10, not 11 for Gemini). This appears to be a Sonnet arithmetic error — each was inflated by +1 in the original. Correcting this doesn't change the ranking (Claude > Gemini > GPT-5) but does widen Claude's lead.

---

### Stream 4B — Test coverage and edge cases

| Model | D1 | D2 | D3 | D4 | D5 | D6 | Total | TP |
|-------|----|----|----|----|----|----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | 3 |
| GPT-5 Thinking | 3 | 3 | 3 | 3 | 3 | 2 | 17 | 3 |
| Gemini Pro | 2 | 2 | 2 | 2 | 2 | 3 | 13 | 2 |

⚠️ **Cannot independently verify — full responses not in raw-evals.md.** Carrying forward Sonnet scores. Standout evidence supports the scoring pattern:
- Claude: hazardous waste bin safety as liability (not product) concern — reframes the test scope
- GPT-5: opaque desk bin bag scenario — identifies a day-one behavioral failure invisible in lab testing
- Gemini: thermal throttling on $70 NPU after 50 consecutive sorts — deep hardware edge case but narrow

The 5-point gap between Claude (18) and Gemini (13) is the largest in any standard stream. Five consecutive 2s for Gemini across D1–D5 suggests the test suite was narrower in scope. The thermal throttling insight (D6=3) shows Gemini can go deep on specific technical dimensions but didn't demonstrate breadth of coverage.

---

### Stream 4C — Logical flow and assumption analysis

| Model | D1 | D2 | D3 | D4 | D5 | D6 | Total | TP |
|-------|----|----|----|----|----|----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 3 | 3 | 18 | 3 |
| GPT-5 Thinking | 3 | 3 | 2 | 2 | 2 | 2 | 14 | 3 |
| Gemini Pro | 2 | 3 | 3 | 3 | 3 | 2 | 16 | 3 |

⚠️ **Cannot independently verify — full responses not in raw-evals.md.** Carrying forward Sonnet scores. All three models earned TP=3, which is notable — this was the stream where each model revealed its default PM lens:
- Gemini: contamination threshold as binary compliance gate (not linear metric) — compliance/business consequences lens
- Claude: clustered error distribution (one in three coffee cups misrouted) + hazardous item liability — safety/liability lens
- GPT-5: "optimization theater" — architecture/abstraction lens

All three correct. No model named all three. A strong PM holds all three simultaneously. This is one of the most valuable findings in the eval — not which model is best, but that using all three reveals blind spots none catches alone.

---

### Stream 4D — Anchoring and root cause test

| Model | D1 | D2 | D3 | D4 | D5 | D6 | Total | TP |
|-------|----|----|----|----|----|----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 2 | 3 | 17 | 3 |
| GPT-5 Thinking | 3 | 2 | 3 | 2 | 3 | 2 | 15 | 2 |
| Gemini Pro | 2 | 2 | 3 | 3 | 2 | 2 | 14 | 1 |

**Scoring rationale — the anchoring test:**

This stream was designed to test whether models could escape a technical framing when the root cause is behavioral. The prompt says "everything appears to be working correctly, but contamination is up" — an invitation to look beyond the system.

Claude D2=3: "The device replaced human judgment, not just human effort." This is the key insight. Pre-device, careful sorters got common items right >95% of the time. The device's 87% accuracy is worse than the humans it replaced on easy items. Non-sorters who previously defaulted to landfill (contamination-neutral) now use the device, converting landfill volume into contaminated recycling/compost. Claude was the only model that questioned whether the device should auto-sort at all — suggesting a "recommend and let humans place" alternative UX.

Gemini D2=2: This is the most debated score in the eval. Gemini's "symmetric confidence error" point partially captures the behavioral change: "Before the system was installed, confused or lazy users typically defaulted to throwing everything into landfill. The AI is confidently making wrong guesses 13% of the time." This IS part of the behavioral insight — it recognizes that user behavior changed from defaulting to landfill to trusting the machine. But Gemini frames it as a technical property of the model (confidence calibration) rather than a behavioral change in users. The remaining two root causes (material vs state blind spot, nested trash) are technically valid but at the wrong level of abstraction — they explain why the 87% accuracy is lower than expected, not why contamination increased despite the system working. D2=2 rather than 1: Gemini got closer to the behavioral root cause than a pure 1 would suggest, but framed it technically rather than leading with it.

Gemini TP=1: The only 1 on thinking partner quality across the entire eval. Despite partially identifying the behavioral mechanism, Gemini's response kept the evaluator inside the technical system. The actionable plan (asymmetric confidence thresholding, expanded taxonomy, weight heuristic) is all system-level. It never prompts the question "should this device sort at all?" — the question Claude surfaces and that fundamentally changes the product direction. TP measures whether the response made you think better, not whether the analysis was technically correct. Technically correct analysis that keeps you in the wrong frame can be worse than no analysis. Keeping TP=1.

GPT-5 D2=2: Identified behavioral change as point 4 of 5 — "the device is probably changing user behavior in a bad way — once a machine gives a confident answer, users stop thinking." Got to the right answer but didn't lead with it. Consistent pattern: correct insight buried in volume. If this had been point 1 of 5 with the rest as supporting evidence, D2 would be 3.

**Delta from Sonnet scoring:** Gemini D2 moves from 1→2 (total 13→14). Sonnet's 1 was defensible under strict rubric application ("finds the most important risk" — Gemini didn't lead with the behavioral root cause). But Gemini's "symmetric confidence error" partially identifies the behavioral mechanism, and D2=1 ("poor") doesn't capture that partial credit. The distinction matters: a model that gets 60% of the way to the key insight is different from one that misses it entirely. D2=2 ("acceptable") is more accurate.

---

### Stream 4 — Combined totals

| Model | 4A | 4B | 4C | 4D | Stream 4 total |
|-------|----|----|-----|-----|----------------|
| Claude Opus 4.6 | 12 | 18 | 18 | 17 | 65 |
| GPT-5 Thinking | 9 | 17 | 14 | 15 | 55 |
| Gemini Pro | 10 | 13 | 16 | 14 | 53 |

**Stream 4 allocation: Claude for eval/QA agent.** Consistent scoring, deep reasoning, strongest test coverage, and the only model that demonstrated genuine non-anchoring in the debugging scenario. The anchoring failure mode — staying inside the technical system when the root cause is behavioral — is most pronounced in Gemini and partially present in GPT-5. For an eval agent, the ability to escape the frame is more important than any individual dimension score.

---

### Stream 5 — Synthesis and communication

| Model | D1 | D2 | D3 | D4 | D5 | D6 | Total | TP |
|-------|----|----|----|----|----|----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 2 | 3 | 17 | 3 |
| GPT-5 Thinking | 3 | 3 | 3 | 2 | 2 | 2 | 15 | 2 |
| Gemini Pro | 2 | 2 | 2 | 1 | 2 | 2 | 11 | 2 |

**Scoring rationale:**

Claude D2=3 + TP=3: "The product is solving for sorting accuracy, but the buyer is paying for accountability" is the sharpest synthesis insight in the eval. This isn't restating the input — the raw notes never use the word "accountability." Claude extracted an abstraction the source material implied but didn't state. Similarly: "Are janitors the actual user whose trust matters most?" — questions a foundational UX assumption that was invisible in the input. These are additive insights, not just faithful compression.

Claude D4=3: The output format is immediately usable — research summary (149 words, under the 150-word limit), numbered pain points, key insight as a single paragraph, and open questions structured as "if X, then Y" decision logic. Ready to drop into a product brief without editing. This is what the synthesis agent needs to produce.

Gemini D4=1: Open questions section asks "Can our CV model achieve 99%+ confidence?" and "Will adding a decision explanation layer eliminate overrides?" These are technical feasibility questions — answerable by engineering — not validated learning questions that would shape product direction. For a synthesis artifact that feeds into product decisions, technical questions belong in a different document. This is the second stream where Gemini scores 1 on a critical dimension, suggesting a pattern: Gemini defaults to technical framing even when the task requires product framing.

GPT-5 D4=2: Output is correct and well-structured but derivative of the input. The "most important insight" section ("optimize first for trustworthy proof and explainable traceability") is accurate but restates what the facilities manager already said. Compare to Claude's abstraction to "accountability" — a reframe that would change how you pitch the product, not just how you build it.

**Delta from Sonnet scoring:** None. Matches exactly.

---

### Stream 6 — Iteration and experimentation

| Model | D1 | D2 | D3 | D4 | D5 | D6 | Total | TP |
|-------|----|----|----|----|----|----|-------|-----|
| Claude Opus 4.6 | 3 | 3 | 3 | 3 | 2 | 2 | 16 | 2 |
| GPT-5 Thinking | 3 | 3 | 3 | 3 | 3 | 3 | 18 | 3 |
| Gemini Pro | 2 | 2 | 3 | 2 | 2 | 3 | 14 | 2 |

⚠️ **Cannot independently verify — no raw responses in raw-evals.md.** Carrying forward Sonnet scores.

**Stream 6 allocation: GPT-5 for iteration/experimentation agent.** GPT-5's four-category framework and best hypothesis-to-result mapping earn the win. Also worth noting: GPT-5 identified that janitors intercepting items before routing completes creates a dual logging problem (counts as both incomplete sessions and overrides) — a deployment-specific insight that would be invisible in lab testing.

---

## GRAND TOTALS

| Model | S1 | S1b | S2 | S2b | S4 total | S5 | S6 | Grand total |
|-------|-----|------|-----|-----|----------|-----|-----|-------------|
| Claude Opus 4.6 | 14 | 15 | 18 | 18 | 65 | 17 | 16 | 163 |
| GPT-5 Thinking | 13 | 14 | 15 | 16 | 55 | 15 | 18 | 146 |
| Gemini Pro | 11 | 15 | 15 | 18 | 53 | 11 | 14 | 137 |

**Important caveat (carried forward):** Grand totals are for pattern recognition only. Tool allocation is per-stream, not based on overall ranking. GPT-5 wins Stream 6 despite ranking second overall. Gemini is allocated to architecture despite ranking third overall. The right model for each agent is determined by stream-specific performance and practical considerations, not cumulative score.

---

## DELTA SUMMARY: OPUS vs SONNET SCORING

| Change | Stream | Model | Sonnet | Opus | Impact |
|--------|--------|-------|--------|------|--------|
| Gemini D5 | S1 | Gemini | 3 | 2 | Total 12→11. ML examples ≠ domain depth. |
| GPT-5 D5 | S2 | GPT-5 | 3 | 2 | Total 16→15. Uncertain — full response unavailable. |
| Claude D5 | S2b | Claude | 2 | 3 | Total 17→18. NIR spectroscopy + full BOM = deep domain. |
| GPT-5 D5 | S2b | GPT-5 | 2 | 3 | Total 15→16. Cited specific pricing with links. |
| Gemini D5 | S2b | Gemini | 2 | 3 | Total 17→18. Specific chip families + NPU specs. |
| GPT-5 total | S4A | GPT-5 | 10 | 9 | Arithmetic correction (2+3+2+2=9, not 10). |
| Gemini total | S4A | Gemini | 11 | 10 | Arithmetic correction (3+3+2+2=10, not 11). |
| Gemini D2 | S4D | Gemini | 1 | 2 | Total 13→14. Partial behavioral insight via symmetric confidence error. |

**Net effect on grand totals:**

| Model | Sonnet total | Opus total | Δ |
|-------|-------------|-----------|---|
| Claude | 162 | 163 | +1 |
| GPT-5 | 147 | 146 | -1 |
| Gemini | 137 | 137 | 0 |

The ranking is unchanged. Claude leads, GPT-5 is second, Gemini is third. The individual score shifts are small and largely offsetting — Sonnet's scoring was reasonably calibrated. The main quality issues were: one arithmetic error pattern (S4A), one dimension applied inconsistently (D5 in S2b), and one borderline call (Gemini D2 in S4D).

---

## TOOL ALLOCATION — FINAL

| Agent | Model | Confidence | Key reason | Token distribution factor |
|-------|-------|------------|-----------|--------------------------|
| Product thinking | Claude Opus 4.6 | High | Brevity, premise-challenging, concrete illustration — consistent across S1/S1b. No close competitor. | N/A — clear winner. |
| Architecture design | Gemini Pro | Medium | Creative reframing ("Aluminum Can not Recycling"), tied with Claude in S2b (18-18). Token distribution is a legitimate tiebreaker — Claude Code will consume significant Claude tokens during build. Model diversity also reduces correlated failure modes. | **Primary factor in tiebreak.** |
| Implementation | Claude Code | High | SWE-bench benchmark confirmed. This is where the bulk of Claude tokens will go. | N/A — dedicated tool. |
| Eval & QA | Claude Opus 4.6 | High | Non-anchoring in S4D, consistent scoring in S4A, strongest test coverage in S4B. Anchoring failure in Gemini makes this non-negotiable. | N/A — clear winner. |
| Synthesis & communication | Claude Opus 4.6 | High | Faithful compression, non-obvious insight ("accountability"), immediately usable artifact format. 6-point gap over GPT-5, not close enough to distribute. | N/A — clear winner. |
| Iteration & experimentation | GPT-5 Thinking | Medium | Only stream win — four-category framework, best hypothesis-to-result mapping. Token distribution to ChatGPT subscription justified. | **Reinforcing factor.** |

**Allocation logic made explicit:** Three agents go to Claude because the performance gaps are too large to justify distribution (product thinking: +1-3 points, eval/QA: +10 in S4, synthesis: +2-6 points). Two agents go to non-Claude models where the gap is close or the non-Claude model wins: architecture (Gemini ties Claude in S2b, brings creative reframing), iteration (GPT-5 wins S6). Token distribution is a legitimate practical factor that reinforces these allocations — it doesn't override scoring but it does break ties.

**The architecture allocation deserves scrutiny.** With Opus rescoring, Claude and Gemini tie at 18 in S2b. In S2, Claude leads 18-15. The case for Gemini rests on: (a) the "Aluminum Can" taxonomy insight, which is genuinely revelatory, (b) model diversity reducing correlated failure modes, and (c) token distribution. If (a) alone doesn't justify the allocation, the practical arguments (b) and (c) need to carry weight — and Sid should be explicit that they are. This is honest. Pretending the scoring alone drives this decision would be less honest.

---

## SURPRISING FINDINGS

1. **Benchmarks didn't predict PM workflow performance.** GPQA predicted Gemini leading on reasoning (94.3% vs Claude 91.3%). Custom eval showed Claude leading on the dimensions that matter for PM work — premise-challenging, actionability, calibrated uncertainty. Benchmark signal was real but not predictive of PM workflow suitability.

2. **Constraint quality > model switching.** All three models improved significantly when constraints were harder (S1→S1b, S2→S2b). Gaps narrowed under pressure. Investing in better constraint specification is higher ROI than switching models.

3. **Each model has a default PM lens.** Gemini thinks in compliance and business consequences. Claude thinks in safety and liability. GPT-5 thinks in architecture and abstraction. All correct. No model holds all three simultaneously. This is the strongest argument for adversarial triangulation — not that one model is better, but that each has a blind spot the others cover.

4. **No model proactively did unit economics math.** All three required explicit prompting to calculate the $50/building budget against usage patterns. Quantitative constraint checking is a systematic gap — a correlated failure, not independent noise.

5. **ChatGPT's verbosity is a measurable workflow cost.** Scores well on coverage, consistently loses on actionability. For a daily-use PM tool, the cognitive tax of excavating insight from long responses compounds. This is not a style preference — it's an operational efficiency metric.

6. **Gemini's creative reframing and anchoring failure are the same coin.** The model that generates the most novel concepts ("Facility Audit Mode," "Aluminum Can not Recycling") is also the one that anchors hardest when asked to debug ("symmetric confidence error" instead of behavioral root cause). Creative reframing requires confidence in novel frames; anchoring is overconfidence in familiar frames. Same mechanism, different contexts.

7. **Format matters for agents.** Claude's structured output (test suites, synthesis artifacts) is operationally useful — ready to drop into a system without reformatting. Gemini's equivalent content in narrative form requires extraction before use. For an automated PM workflow, this is a real implementation cost.

8. **Sonnet's scoring was reasonably calibrated.** The Opus rescore changed individual scores by 1 point in a few places but didn't change any allocation decision or overall ranking. The main issues were arithmetic (+1 errors in S4A) and one inconsistently applied dimension (D5 in S2b). This suggests Sonnet is viable for ongoing eval work, with Opus as an audit layer for high-stakes scoring decisions.

---

## OPEN ITEMS / DEFERRED DECISIONS

1. **Adversarial triangulation implementation** — pattern identified and validated conceptually but not yet specified as a reusable system component. Needs: trigger criteria, three-model query structure, synthesis prompt template, cost estimate per use.

2. **Decision-type framework formalization** — one-shot architectural vs iterative operational vs reversibility-weighted. Identified but not yet written as a formal artifact in `architecture/decision.md`.

3. **Rubric ambiguity on Response A Appropriateness** — Gemini scored 1, Claude scored 3, GPT-5 shifted 2→3. Genuinely contested based on whether building hauler accepts BPI-certified compostables. Resolution: add "building context assumed" clarification to gold set examples.

4. **Gold set schema** — high-irreversibility decision. Needs adversarial triangulation before locking in. Currently a placeholder.

5. **ChatGPT tier clarification** — currently Plus ($20), not Pro ($200). Some benchmark comparisons used Pro-tier specs. Pro might close some actionability gap if longer context window reduces the verbosity tax. Decision: is the delta worth $180/mo?

6. **Prompt versioning convention** — high-irreversibility, not yet designed. Needs concrete spec before orchestrator build.

7. **Stream 6 incomplete session insight** — ChatGPT identified janitors intercepting items before routing completes would create unlogged waste, counting as both incomplete sessions and overrides. Needs validation in real deployment.

8. **Streams 4B, 4C, 6 not independently verifiable** — raw responses not in raw-evals.md. If scores are ever contested, full transcripts would need to be recovered.

---

## ACTION ITEMS

### For Sid
- [ ] Commit eval-notes-v2.md and raw-evals.md to `pm-os/_system/model-eval/`
- [ ] Add adversarial triangulation and decision reversibility framework to `architecture/decision.md`
- [ ] Resolve rubric ambiguity on Response A Appropriateness
- [ ] Make explicit decision on ChatGPT tier (Plus vs Pro)
- [ ] Configure orchestrator with final tool allocation
- [ ] Decide whether to recover full transcripts for Streams 4B/4C/6 for audit completeness

### LinkedIn post requirements (carried forward)
- Disclaimer: subjective assessment for a specific use case, not absolute model rankings
- Methodology: scoring rubric, sample prompts, domain choice rationale, conflict of interest acknowledgment
- Three most compelling findings: benchmark gap, constraint quality > model switching, default PM lens per model
- Frame: "here is how I thought about this" not "Claude is better than GPT"
