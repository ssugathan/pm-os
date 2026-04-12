# Benchmark Mapping Analysis
_How well do public benchmarks predict PM workflow performance?_
_Compiled April 2026 from Artificial Analysis, LM Council, BenchLM, and independent evaluations_

---

## The headline finding from the eval, restated

> "Benchmarks predicted Gemini would lead on reasoning. Custom eval showed Claude leading on the dimensions that matter for PM workflow."

This analysis tests that claim against the full 2026 benchmark landscape — not just GPQA — to see which benchmarks are predictive, which are misleading, and which gaps no public benchmark covers at all.

---

## Benchmark landscape (April 2026 scores)

### Reasoning & knowledge

| Benchmark | What it tests | Claude Opus 4.6 | GPT-5.4 | Gemini 3.1 Pro |
|-----------|--------------|-----------------|---------|----------------|
| GPQA Diamond | Graduate-level science reasoning | ~90.5% | ~92.0% | ~94.3% |
| MMLU-Pro | 12K graduate questions, 14 subjects | ~90.5% | ~91.4% | ~94.1% |
| HLE | Expert-vetted frontier questions | ~67.6% | ~74.1% | ~79.6% |
| ARC-AGI-2 | Novel pattern recognition | ~68.8% | ~52.9% | ~77.1% |
| Intelligence Index (AA) | Composite of 10 benchmarks | ~55 | ~57.2 | ~57.2 |

**Benchmark prediction:** Gemini leads reasoning. GPT-5.4 is second. Claude is third.
**Eval result:** Claude leads on premise-challenging (D1) and core problem identification (D2) — both reasoning tasks.
**Match: Poor.** These benchmarks measure structured reasoning within defined frames. PM reasoning requires questioning the frame itself, which is a different cognitive operation.

### Factual accuracy & calibration

| Benchmark | What it tests | Claude Opus 4.6 | GPT-5.4 | Gemini 3.1 Pro |
|-----------|--------------|-----------------|---------|----------------|
| TruthfulQA | Avoiding plausible-sounding wrong answers | Leads | — | — |
| SimpleQA | Factual recall without retrieval | — | Leads (~97) | Strong |
| Omniscience (AA) | Knowledge + hallucination rate | — | — | — |

**Benchmark prediction:** Claude is best at avoiding confidently wrong answers. GPT-5.4 is best at factual recall.
**Eval result:** Claude led on D6 (technical calibration — hedging specs, acknowledging uncertainty). Gemini made the most overconfident technical claims.
**Match: Moderate.** TruthfulQA directionally predicts D6 — models that avoid plausible-sounding errors also tend to hedge appropriately. But TruthfulQA tests knowledge of common misconceptions, not the ability to say "I'm not sure about this specific latency estimate." The calibration our eval tested is about epistemic humility on uncertain technical claims, which is a subtler skill than avoiding known trick questions.

### Real-world professional tasks

| Benchmark | What it tests | Claude Opus 4.6 | GPT-5.4 | Gemini 3.1 Pro |
|-----------|--------------|-----------------|---------|----------------|
| GDPval-AA (ELO) | 44 occupations, real deliverables | ~1619 | ~1676 | ~1315 |
| Chatbot Arena | Blind human preference | Top 3 (writing) | Top 3 | Top 3 (accuracy) |

**Benchmark prediction:** GPT-5.4 leads on professional work output. Gemini significantly trails. Claude strong on writing/helpfulness.
**Eval result:** Claude led on synthesis (S5) and product thinking (S1). GPT-5.4 led on iteration (S6). Gemini trailed on synthesis but was competitive on architecture.
**Match: Moderate-to-good.** GDPval is the most predictive benchmark for PM workflow because it tests real deliverables, not isolated reasoning tasks. The Gemini gap (~300 ELO below Claude/GPT) aligns with the eval's finding that Gemini struggles with structured artifact generation (D4=1 in Stream 5). The Claude-GPT gap is smaller in GDPval than in the eval, likely because GDPval tests breadth across occupations while the PM eval tests depth on a single workflow. Claude's edge in the PM eval comes from premise-challenging and synthesis — narrow skills that GDPval's breadth doesn't isolate.

### Coding

| Benchmark | What it tests | Claude Opus 4.6 | GPT-5.4 | Gemini 3.1 Pro |
|-----------|--------------|-----------------|---------|----------------|
| SWE-bench Verified | Real GitHub issue resolution | ~80.8% | ~80% | ~80.6% |
| Terminal-Bench | CLI/agentic execution | ~65.4% | ~75.1% | ~68.5% |
| LiveCodeBench | Fresh competitive programming | — | — | Leads |

**Benchmark prediction:** Effectively tied on real-world coding. GPT-5.4 leads on terminal/agentic tasks.
**Eval result:** Claude Code allocated as implementation agent (SWE-bench confirmed).
**Match: Good.** SWE-bench was explicitly cited in the eval as validation for the Claude Code allocation, and the near-tie across models confirms this was a reasonable choice rather than a clear mandate. The Terminal-Bench gap (GPT leading) is worth noting — if the orchestrator involves heavy CLI/terminal work, GPT might deserve a look for implementation too.

### Instruction following

| Benchmark | What it tests | Claude Opus 4.6 | GPT-5.4 | Gemini 3.1 Pro |
|-----------|--------------|-----------------|---------|----------------|
| IFBench | Novel instruction-following generalization | ~58% (Opus 4.5) | Limited data | Limited data |

**Match: Inconclusive.** IFBench has limited coverage of the models evaluated. The eval's D4 (actionability) is related but distinct — it measures whether output can be acted on immediately, not whether the model followed format constraints. Claude's D4 advantage in the eval is about output structure and density, not instruction compliance per se.

### Writing quality (human evaluation)

| Benchmark | What it tests | Claude Opus 4.6 | GPT-5.4 | Gemini 3.1 Pro |
|-----------|--------------|-----------------|---------|----------------|
| Blind human preference (Q1 2026) | Writing quality, tone, coherence | 47% preferred | 29% preferred | 24% preferred |

**Benchmark prediction:** Claude leads writing quality by a wide margin.
**Eval result:** Claude led on synthesis (S5: 17 vs 15 vs 11) and consistently produced more structured, immediately usable artifacts.
**Match: Good.** Human writing preference is a strong proxy for the synthesis/communication agent. The preference gap (Claude 47% vs Gemini 24%) aligns almost exactly with the Stream 5 scoring gap. If you need a model to compress messy input into a clean, usable artifact, writing quality benchmarks are predictive.

---

## Dimension-by-dimension: which benchmarks predict what

| Eval dimension | Best proxy benchmark | Predictive? | Why / why not |
|---------------|---------------------|-------------|---------------|
| D1 — Premise challenging | **None** | N/A | No public benchmark tests the ability to question a problem's framing. Closest might be ARC-AGI-2 (novel patterns) but that tests pattern recognition, not meta-cognitive reframing. This is a genuine gap in the benchmark landscape. |
| D2 — Core problem ID | **GPQA Diamond** (partial) | Poor | GPQA tests whether you can solve a hard problem. D2 tests whether you can identify which problem matters most in an ambiguous situation. Academic benchmarks present clear problems; PM work requires finding the problem first. |
| D3 — Decision quality | **GDPval-AA** | Moderate | GDPval tests real deliverables requiring judgment, but across 44 occupations. It doesn't isolate the willingness to commit to a clear recommendation vs hedging. |
| D4 — Actionability | **GDPval-AA + writing preference** | Moderate | GDPval's deliverable format requirement and writing quality benchmarks are partial proxies. But actionability in PM context means "can I act on this in the next 30 minutes" — a density and prioritization skill no benchmark explicitly measures. |
| D5 — Domain depth | **SimpleQA + MMLU-Pro** | Poor | SimpleQA tests broad factual recall. MMLU-Pro tests academic knowledge. Neither tests whether a model can cite specific NYC waste management regulations, name specific ARM chipsets with accurate pricing, or identify that NIR spectroscopy solves the compostable cup problem. Domain depth in a product context is about applied specificity, not breadth. |
| D6 — Technical calibration | **TruthfulQA** | Moderate | Best available proxy — tests resistance to confident errors. But our D6 specifically tests appropriate hedging on uncertain technical claims (latency ranges, BOM estimates), which is about calibrated uncertainty, not just accuracy. |
| TP — Thinking partner | **Chatbot Arena** | Weak | Arena measures general preference. TP measures whether a response made you think differently — a much narrower, more subjective quality. |

---

## The predictive gap: what benchmarks can't tell you

Three capabilities that mattered most in the PM eval have zero benchmark coverage:

**1. Premise challenging (D1).** The ability to say "you're solving the wrong problem" is arguably the most valuable PM skill and no benchmark tests it. The closest proxy is ARC-AGI-2 (novel pattern recognition), where Gemini leads — but Gemini scored lowest on D1 in multiple streams. Novel pattern recognition within a defined frame is different from questioning whether the frame is right.

**2. Anchoring resistance.** Stream 4D tested whether models could escape a technical framing when the root cause was behavioral. This is the PM equivalent of "sunk cost fallacy" — can the model abandon its existing analysis when the evidence points elsewhere? No benchmark tests this. The closest might be TruthfulQA's resistance to common misconceptions, but anchoring on your own prior analysis is a different failure mode from anchoring on common knowledge errors.

**3. Lens diversity.** The eval's most valuable finding was that each model has a default PM lens (Gemini: compliance, Claude: safety/liability, GPT: architecture/abstraction). No benchmark captures this because benchmarks test single-model performance, not the interaction pattern between models. This finding only emerges from running the same prompt across multiple models and comparing what each one prioritizes.

---

## Where benchmarks DO predict well

Two areas where public benchmarks aligned with eval results:

**1. Writing/synthesis quality.** Human writing preference (Claude 47%) predicted Stream 5 performance (Claude led with 17 vs 15 vs 11). If your agent needs to produce clean, structured, immediately usable artifacts, writing quality benchmarks are your best signal.

**2. Coding capability.** SWE-bench Verified (Claude ~80.8%, near-tie) validated the Claude Code allocation. Terminal-Bench (GPT 75.1% vs Claude 65.4%) correctly identifies that GPT has an edge for CLI-heavy agentic work. Coding benchmarks are the most mature and predictive of the lot.

---

## What this means for the eval's validity

The eval's central claim — "benchmarks didn't predict PM workflow performance" — holds up with important nuance:

**True for reasoning.** GPQA, HLE, and ARC-AGI-2 all predict Gemini leading. The eval found Claude leading on the reasoning dimensions that matter for PM work (premise-challenging, core problem ID). The benchmark scores weren't wrong — Gemini genuinely is a stronger academic reasoner. But academic reasoning and PM reasoning test different cognitive operations.

**Partially true for professional tasks.** GDPval directionally predicts the right ranking (Claude/GPT ahead, Gemini behind) but doesn't capture the specific skills that drive PM workflow suitability. It's a useful coarse filter, not a substitute for domain-specific eval.

**False for coding and writing.** SWE-bench and writing preference benchmarks predicted eval results reasonably well. These benchmarks are more mature and test capabilities that transfer directly to the PM workflow agents they proxy for.

The takeaway for the LinkedIn post: benchmarks are not useless — they're useful for some capabilities (coding, writing quality) and misleading for others (reasoning quality in ambiguous domains, premise-challenging, calibrated uncertainty). The value of a custom eval is not that it contradicts benchmarks, but that it measures capabilities benchmarks don't cover.

---

## Appendix: Benchmark scores consolidated

_All scores approximate, drawn from multiple sources as of April 2026. Numbers vary by evaluation framework, reasoning effort settings, and measurement methodology. Treat as directional, not precise._

| Benchmark | Claude Opus 4.6 | GPT-5.4 | Gemini 3.1 Pro | Leader |
|-----------|-----------------|---------|----------------|--------|
| GPQA Diamond | ~90.5% | ~92.0% | ~94.3% | Gemini |
| MMLU-Pro | ~90.5% | ~91.4% | ~94.1% | Gemini |
| HLE | ~67.6% | ~74.1% | ~79.6% | Gemini |
| ARC-AGI-2 | ~68.8% | ~52.9% | ~77.1% | Gemini |
| Intelligence Index | ~55 | ~57.2 | ~57.2 | Tied GPT/Gemini |
| SWE-bench Verified | ~80.8% | ~80% | ~80.6% | Near-tie |
| Terminal-Bench | ~65.4% | ~75.1% | ~68.5% | GPT |
| GDPval-AA (ELO) | ~1619 | ~1676 | ~1315 | GPT |
| TruthfulQA | Leads | — | — | Claude |
| SimpleQA | — | Leads (~97) | Strong | GPT |
| Writing preference | 47% | 29% | 24% | Claude |
| LiveCodeBench | — | — | Leads | Gemini |

**Pattern:** Gemini leads academic reasoning. GPT leads professional tasks and factual recall. Claude leads writing quality and calibrated uncertainty. No model dominates across categories — which is exactly what the PM eval found for the narrower PM workflow domain.
