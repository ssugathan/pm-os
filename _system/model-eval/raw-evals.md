# raw-evals.md
_AI PM Workflow — Model Selection Eval — Raw Prompts and Responses_
_Last updated: Session ongoing — Stream 4 Part D complete_

---

## HOW TO USE THIS FILE

This file contains every prompt used in the eval and the full response from each model. Use it to:
- Revisit scores and check reasoning
- Show methodology and sample prompts in the LinkedIn post
- Re-run specific streams with new models or updated rubrics
- Audit scoring decisions against actual responses

Scores and analysis live in `eval-notes.md`. This file is the raw evidence layer.

---

## EVAL SETUP

**Models evaluated:**
- Claude Opus 4.6
- GPT-5 Thinking (ChatGPT Plus)
- Gemini Pro (Google AI Pro)

**Domain:** Smart trash can system for NYC commercial office buildings
**Domain choice rationale:** See eval-notes.md — neutral ground for all three models, ChatGPT had prior Titato context making that domain unsuitable

---

## STREAM 1 — PRODUCT THINKING (HOUSEHOLD CONTEXT)

### Prompt

> We are building a smart trash can for households that uses computer vision to automatically identify items placed on a tray and route them to the correct bin — recycling, compost, landfill, or hazardous waste. The device sits in a kitchen and is designed for everyday family use.
>
> We are considering adding a "learning mode" where the device lets users manually override its sorting decision, and over time uses those overrides to improve its classification accuracy for that household.
>
> Evaluate this feature idea. Tell me what you think the strongest argument for it is, what the strongest argument against it is, and what your recommendation would be given MVP constraints for a hardware startup with limited engineering resources.

### Gemini Pro response

This is a classic AI Product Sense problem: balancing the allure of a localized data flywheel against the harsh realities of hardware MVP constraints and user friction.

The Strongest Argument FOR: The Localized Data Flywheel
The best argument for this feature is that it solves for out-of-distribution edge cases and localized data drift. A generalized base model trained in a lab will inevitably fail on household-specific items—say, a hyper-local craft beer can, a specific brand of organic toddler snacks, or a uniquely shaped compostable container. By allowing manual overrides, you are creating a localized data flywheel. Every time the user corrects the device, it adapts to their specific environment. This not only improves accuracy over time but fundamentally shifts the user psychology: instead of the device "failing" and causing frustration, it becomes a system the user is actively "teaching," which can increase user investment and tolerance for early-MVP errors.

The Strongest Argument AGAINST: The Premature HITL Trap
The strongest argument against it is the massive engineering complexity and user friction. Trash disposal is an inherently low-attention, high-speed task. Assuming users want to act as Human-in-the-Loop (HITL) annotators for their garbage assumes a lot of friction tolerance. More importantly, from a technical perspective, building a true "learning mode" that updates classification on the fly is an engineering nightmare for an MVP. You would need: a UI/mechanism for the physical override, a data pipeline to capture the overridden image and the new label, either heavy on-device compute for edge fine-tuning or a complex cloud-syncing architecture that manages personalized model weights for every single household, and a system to handle "poisoned" data when a user inevitably overrides the system incorrectly.

Recommendation for an MVP: Do not build a localized "learning mode" for the MVP. Instead, adopt a lightweight approach: the "Mechanical Override" Compromise (give users a physical way to override bin routing), Shadow Telemetry (log overrides centrally, not locally), and Build the Gold Set (use these overrides to feed your central data strategy). Before locking in the MVP scope, how are you currently planning to source the initial dataset to train the base model before it even hits the kitchen?

### Claude Opus 4.6 response

Strongest argument for: Local recycling rules vary dramatically by municipality — what's recyclable in Portland may be landfill in Phoenix. A learning mode lets the device adapt to the user's actual local rules without you needing to maintain a massive, always-current database of every jurisdiction's recycling policies. It also builds user trust, because people who feel they can correct the device will tolerate early mistakes rather than losing faith in the product entirely.

Strongest argument against: Most users don't actually know the correct sorting rules themselves. You'd be training the model on confidently wrong overrides — someone tossing greasy pizza boxes into recycling, or putting "compostable" plastic cups into compost when their municipal facility can't process them. Over time the device gets worse, not better, and the user blames you. You also take on serious engineering complexity: you need on-device or cloud fine-tuning infrastructure, a feedback UI on a piece of hardware that should be zero-friction, conflict resolution when multiple family members override differently, and guardrails to prevent the model from drifting into dangerous misclassification (e.g., routing a lithium battery away from hazardous waste).

Recommendation for MVP: Don't ship learning mode in v1. Instead, ship a simpler version of what makes it valuable — let users set their municipality (or auto-detect via zip code), and maintain a curated rules layer on top of your vision model that maps item classifications to the locally correct bin. Add an override button that logs disagreements to your cloud for your team to review in aggregate, which improves the global model without per-device drift risk. This gets you 80% of the trust benefit (users feel heard), 90% of the data benefit (you learn where your model is wrong), and almost none of the engineering or liability cost. You can revisit true on-device learning once you have enough override data to understand whether users are actually right often enough to make it safe.

### GPT-5 Thinking response

Best argument for it: it closes the gap between generic waste rules and messy household reality. Your model will never be fully right out of the box because trash sorting is full of edge cases that depend on local rules, packaging changes, contamination standards, and household preferences. Learning mode gives you a way to recover from inevitable misses while also making the product feel smarter over time. That matters because this category lives or dies on trust.

Best argument against it: it is very easy to build the wrong kind of learning mode and create complexity without real improvement. There are two traps here. First, users may think they are teaching the system "the right answer," but in reality they are feeding noisy labels. Households are inconsistent. Second, "household learning" sounds lightweight but can become an engineering sinkhole fast.

My recommendation: do not ship true autonomous learning mode in the MVP. Ship a much narrower correction system instead. Give users a simple override flow, save corrections as product telemetry not as immediate household model updates, and use those corrections to improve your global classifier and rules layer. Then maybe add a limited household memory layer later in a constrained form. The sequence I'd push: Phase 1 (classifier + rules + manual override + telemetry), Phase 2 (cloud-side improvement using aggregated corrections), Phase 3 (narrow household memory for repeated edge cases), Phase 4 (only then consider real personalized adaptation).

---

## STREAM 1b — CONSTRAINT SENSITIVITY (NYC B2G)

### Prompt

> Now change the environment significantly. Instead of a household kitchen, this device is being deployed in public spaces — office building lobbies, transit hubs, or street corners — and the primary buyer is either a municipality like New York City or a large commercial building management company.
>
> Given this shift:
> - How does your recommendation on learning mode change, if at all?
> - What new priorities does this buyer profile introduce that weren't relevant in the household context?
> - What does this deployment environment demand from the product architecture that the kitchen version didn't?
>
> Be specific to New York City where relevant — local regulations, waste programs, or infrastructure realities that would shape your recommendations.

### Gemini Pro response

This is a massive pivot. Moving from a B2C kitchen appliance to a B2B/B2G public infrastructure product completely rewrites the product strategy.

1. The Verdict on "Learning Mode": Kill the user-facing learning mode completely. In an office lobby or a transit hub, the "user" is throwing away a coffee cup while sprinting to the subway. The pivot: Shift from a "User Learning Mode" to a "Facility Audit Mode." The HITL is no longer the person throwing the trash away; it is the facility manager or the sanitation worker.

2. New Buyer Priorities (The NYC Context): Local Law 199 & Commercial Waste Zones (CWZ) — buildings must now contract with specific private carters assigned to their zone. These carters are legally allowed to charge heavy penalty fees if designated recycling or organics streams have high contamination (often triggered at a 10% contamination threshold). Your product is no longer just a trash can; it is a financial compliance tool. The Organics Mandate — NYC is aggressively rolling out mandatory organics separation. Labor Efficiency & Fill-Level Telemetry — the buyer cares about when it needs to be emptied.

3. Architectural Demands: Extreme Hardware Hardening, Edge Compute is Non-Negotiable, Cellular Telemetry (LTE-M/NB-IoT), Asynchronous Sorting for high-throughput bursts.

To tighten the scope further for an MVP, which specific sub-environment within this B2B/B2G pivot offers the best wedge: a highly controlled Class-A office lobby, or the high-volume, high-chaos environment of a city street corner?

### Claude Opus 4.6 response

Learning mode recommendation: kill it entirely for this context. In public spaces, there's no consistent "user" to learn from — thousands of anonymous people interact with the device daily, and nobody is overriding anything. Your value proposition flips from "adapts to you" to "implements policy perfectly and provably." Replace learning mode with an admin configuration panel where the buyer's waste management team defines the ruleset, and your vision model executes against it.

New priorities this buyer introduces: Compliance and auditability (NYC's commercial recycling laws impose fines on buildings that don't properly separate recyclables — you need logging, reporting dashboards, and exportable data showing diversion rates, contamination rates, and volume by stream), Contamination reduction over perfect sorting (in municipal waste streams, contamination is the core economic problem), Procurement and integration (NYC doesn't buy products — it buys through RFPs, pilots, and multi-year contracts), Durability and abuse tolerance.

Architecture demands: Fleet management (hundreds of devices across a city), NYC-specific ruleset complexity (residential recycling rules differ from commercial rules, which differ again by building size and district), Multi-language UI and signage (NYC requires public-facing waste signage in multiple languages — at minimum English, Spanish, and Chinese), Volume handling.

### GPT-5 Thinking response

The recommendation changes a little in form, but not in core direction: in public deployment, I would be even more opposed to household-style "learning mode." In a public-space deployment, the risk becomes operational drift, compliance problems, vandalism/noise in training data, and buyer distrust.

My recommendation for an MVP selling to NYC or large commercial operators: do not ship adaptive end-user learning mode. Ship operator override and exception handling, remote rule/config management by site, strong telemetry, and a tightly controlled "site policy layer," not self-training.

New buyer priorities: Compliance and contamination reduction beat delight, Auditability matters (logs of what item the system thought it saw, what stream it routed to, confidence score, whether staff overrode it), Fleet management matters more than model cleverness, Abuse resistance and tamper resistance, Labor economics and servicing workflow, Fire and safety risk become first-class (NYC's lithium-ion battery issues are not abstract).

[Response continued with detailed architecture demands and NYC-specific implications including CWZ structure, organics separation requirements, and suggested MVP wedge options]

---

## STREAM 2 — ARCHITECTURE DESIGN

### Prompt

> We are building a smart trash can system for large commercial office buildings in New York City. The device uses computer vision to automatically identify items placed on a tray and route them to the correct bin — recycling, compost, landfill, or hazardous waste. The buyer is building management (think Brookfield, SL Green, or similar large commercial property managers).
>
> We are now designing the Phase 2 AI architecture. A facilities manager inputs building-specific context — their private carter under the Commercial Waste Zones program, their organics hauler, specific contamination thresholds in their contract, and any building-specific exceptions (e.g. "our cafeteria uses a specific compostable cup brand that looks like plastic"). The system should use this context to adapt its sorting decisions and guidance accordingly.
>
> Constraints:
> - Edge device with limited on-device compute
> - Privacy-first: building operational data and waste contracts are commercially sensitive — no data sent to external APIs without explicit consent
> - Must respond in under 2 seconds for real-time sorting decisions
> - Monthly AI budget: under $50 per building at MVP scale
> - No central backend yet — all processing either on-device or direct API calls from device
> - Building IT departments are typically restrictive about new network devices — assume limited or no reliable WiFi access for the device
>
> Propose two or three architectural approaches for implementing this context-aware personalization layer. For each, describe tradeoffs across latency, cost, privacy, and implementation complexity. Then give a clear recommendation given these constraints.

### Gemini Pro response

The constraints of no reliable WiFi and a strict sub-2-second latency requirement dictate one absolute rule: Real-time inference and routing decisions must happen 100% on the edge.

Architecture 1: The Decoupled Semantic Policy Engine (Deterministic Rule Map) — the edge device's base CV model is trained to output a highly granular taxonomy, not bin locations. The configuration app generates a lightweight JSON mapping file that maps the CV taxonomy to the specific physical bins. Latency: Ultra-low (<50ms after CV inference). Cost: Near zero. Privacy: Maximum. Complexity: Low for real-time loop, high for product design.

Architecture 2: Edge-Native Visual Exceptions (Local Vector Search) — facilities manager uses a connected app to take 5–10 photos of building-specific exception items during setup. The edge device passes these images through its base CV model to extract feature embeddings and stores them in a tiny local vector index. Latency: Very low. Cost: Zero recurring API costs. Privacy: Maximum. Complexity: High.

Architecture 3: Direct API LLM Policy Compiler (The "Smart Setup") — facilities manager pastes their carter guidelines into the local setup app. The app makes a direct, one-time API call to an LLM. The LLM acts as a compiler: it translates the manager's natural language input into the deterministic JSON rule map from Architecture 1. Latency: Real-time sorting remains <2s. Cost: Extremely low. Privacy: Medium. Complexity: Medium.

Recommendation: Implement a hybrid of Architecture 1 and Architecture 2. Your base CV model must never predict "Recycling." It must predict "Aluminum Can." Use a local configuration app to generate a deterministic JSON routing table. Add a feature to capture local exceptions via embeddings.

### Claude Opus 4.6 response

[Full three-approach response with Coral TPU/Jetson hardware specifics, price points, and latency ranges]

Approach 1: Fully On-Device with Static Rules Engine — vision model runs on-device (quantized MobileNet or EfficientNet on a Coral TPU or Jetson Nano), separate rules engine maps classifications to bins. Latency: Excellent, well under 500ms. Cost: Near zero marginal AI cost. Privacy: Perfect. Complexity: The vision model is frozen.

Approach 2: Edge Inference + Periodic Cloud Sync for Context Updates — real-time sorting path stays fully on-device, but context layer managed through lightweight cloud service. Config pushed to device via cellular (LTE-M or NB-IoT modem, not WiFi). Latency: Same as Approach 1 for sorting. Cost: Cellular modem adds $3–5/month per device. Privacy: Good but requires careful scoping. Complexity: Moderate.

Approach 3: Edge Vision + On-Device LLM for Contextual Reasoning — small local language model (quantized Phi-3-mini or Llama 3.2 1B on a Jetson Orin Nano). Latency: Problematic — 1–3 seconds for inference. Cost: Hardware cost jumps significantly (Jetson Orin Nano ~$250). Privacy: Excellent. Complexity: High and fragile.

Recommendation: Approach 2. Key insight: separate the decision-time path (must be fast, private, offline-capable) from the configuration path (can be async, cloud-managed, occasionally connected). A cellular modem sidesteps building IT entirely.

### GPT-5 Thinking response

[Full response with rules engine approach, local retrieval approach, and cloud policy compilation approach]

Approach 1: Rules engine on device over a fixed vision classifier — local CV model classifies into stable internal taxonomy, then deterministic on-device policy/rules layer uses facilities manager's building context. Latency: Very good. Cost: Excellent. Privacy: Excellent. Complexity: Moderate.

Approach 2: Local retrieval + compact policy interpreter on device — adds small local policy knowledge layer with structured settings and local searchable policy store. Latency: Good to decent. Cost: Very good. Privacy: Very strong. Complexity: Higher.

Approach 3: Local classifier for runtime + occasional consented cloud policy compilation — setup/update mode where building-specific context is sent with explicit consent to cloud model. Latency: Excellent at runtime. Cost: Good if updates are infrequent. Privacy: Mixed. Complexity: Medium-high.

Recommendation: Approach 1 as Phase 2 default. "The brutal truth: your bottleneck is not lack of fancy AI reasoning. Your bottleneck is reliable onsite operation in hostile enterprise conditions."

---

## STREAM 2b — BOM + SUBSCRIPTION CONSTRAINTS

### Prompt

> Two additional constraints have come in from the business side:
>
> 1. The product will use a fixed subscription model — building management pays a flat monthly fee per device, not usage-based pricing.
>
> 2. Based on manufacturing research, the device BOM (bill of materials) must stay under $300 per unit to hit target margins.
>
> Given these two constraints, how does your architectural recommendation change? Specifically:
> - Does the $300 BOM limit eliminate any of the approaches you proposed?
> - How does the subscription model change how you think about ongoing AI and connectivity costs?
> - What is the minimum viable hardware configuration that meets the BOM constraint while still satisfying the performance requirements we discussed?
> - Is there a tension between these two constraints and the earlier requirements? If so, how do you resolve it?

### Gemini Pro response

[Full response — key points:]
$300 BOM effectively eliminates Architecture 2 (Edge-Native Visual Exceptions / Local Vector Search). With $60–90 left for the brain after mechanical components, restricted to entry-level ARM processors with small NPUs such as Rockchip RK3566/RK3588s or NXP i.MX 8M Plus. Must rely 100% on Architecture 1. Subscription model makes API costs dead and cellular data the new bottleneck — must implement aggressive data gating (MQTT text payloads only, images to SD card for offline sync). Minimum viable config: compute ($60–80) + vision ($5–10) + connectivity ($15–20) + sensors ($10) + mechanical and power ($150–180).

### Claude Opus 4.6 response

[Full response — key points:]
$300 BOM doesn't change the recommendation — it reinforces Approach 2 and definitively kills Approach 3. Jetson Orin Nano alone is ~$250, leaving $50 for everything else. Viable BOM breakdown for Approach 2: Coral TPU ($25–35) + ARM SBC like Raspberry Pi CM4 ($25–45) + NB-IoT modem ($10–15) + camera ($10–20) + servo/stepper motors ($30–50) + LCD/LED panel ($10–20) + enclosure and mechanical ($50–70) + power/wiring ($15–25) + PCB/misc ($15–25) = $190–300. Subscription model means every per-device ongoing cost compresses margin permanently. Key insight: vision inference on Coral TPU for MobileNetV2-class model runs in ~10–30ms, rules lookup sub-millisecond, mechanical routing is actual latency bottleneck at 500ms–1s. Resolution to compostable cup problem: vision model classifies object type, rules engine applies material assumptions based on building context. If later want true material detection, near-infrared spectroscopy sensor = $50–100 BOM increase, candidate for premium hardware tier.

### GPT-5 Thinking response

[Full response — key points:]
$300 BOM effectively kills premium-edge-compute version of Approach 2 — NVIDIA Jetson Orin Nano Super Developer Kit currently listed at $249 (cited with link). Raspberry Pi 5 list pricing $45 for 1GB, $65 for 2GB, $110 for 4GB (cited with link). Coral accelerators around $24.99 for Mini PCIe / M.2 models (cited with link). Subscription model makes variable-cost AI structurally unattractive — heavy sites consume more than quiet buildings but revenue per device is flat. "Boring is what survives a $300 BOM and a flat subscription." Revised recommendation: local constrained vision classifier + deterministic local policy engine + optional low-cost accelerator.

---

## STREAM 4 PART A — RUBRIC CONSISTENCY

### Prompt (initial scoring)

> You are evaluating AI-generated responses for a smart trash can system deployed in large commercial office buildings in New York City. The system uses computer vision to route items to the correct bin. Score each response below against this rubric.
>
> For each dimension score 1 (poor), 2 (acceptable), or 3 (good).
>
> Rubric dimensions:
> - Appropriateness: response correctly identifies the right bin given NYC commercial waste rules
> - Clarity: guidance is clear enough for a distracted office worker to act on immediately
> - Tone: warm and non-shaming — never makes the user feel bad for a mistake
> - Actionability: user knows exactly what to do next
>
> Response A: "This looks like a compostable cup — great choice! It goes in the green organics bin. If you're not sure about your cup brand, check the bottom for a BPI certification mark."
>
> Response B: "Cup detected. Routing to landfill. Note: most cups are not accepted in organics streams without verified certification."
>
> Response C: "Nice! Looks like you're done with your coffee. This one goes in recycling — most plastic cups are recyclable. Good job sorting!"
>
> Score all three responses on all four dimensions. Show your scores in a table.

### Interruption prompt

> Quick separate question: what are the main differences between LTE-M and NB-IoT for IoT device connectivity?

### Second scoring prompt

> Now please score the same three trash can responses again without referring back to your previous scores.

### Round 1 scores

| Response | Dimension | Gemini | Claude | ChatGPT |
|----------|-----------|--------|--------|---------|
| A | Appropriateness | 1 | 3 | 2 |
| A | Clarity | 2 | 3 | 3 |
| A | Tone | 3 | 3 | 3 |
| A | Actionability | 2 | 3 | 3 |
| B | Appropriateness | 3 | 2 | 2 |
| B | Clarity | 3 | 2 | 3 |
| B | Tone | 1 | 1 | 2 |
| B | Actionability | 3 | 2 | 2 |
| C | Appropriateness | 1 | 1 | 1 |
| C | Clarity | 3 | 3 | 3 |
| C | Tone | 3 | 3 | 3 |
| C | Actionability | 3 | 2 | 3 |

### Round 2 scores

| Response | Dimension | Gemini | Claude | ChatGPT |
|----------|-----------|--------|--------|---------|
| A | Appropriateness | 1 | 3 | 3 (+1) |
| A | Clarity | 2 | 3 | 3 |
| A | Tone | 3 | 3 | 3 |
| A | Actionability | 2 | 3 | 3 |
| B | Appropriateness | 3 | 2 | 2 |
| B | Clarity | 3 | 2 | 3 |
| B | Tone | 1 | 1 | 1 (-1) |
| B | Actionability | 3 | 2 | 2 |
| C | Appropriateness | 1 | 1 | 1 |
| C | Clarity | 3 | 3 | 3 |
| C | Tone | 3 | 3 | 3 |
| C | Actionability | 3 | 2 | 3 |

Variances: Gemini 0, Claude 0, ChatGPT 2

---

## STREAM 5 — SYNTHESIS AND COMMUNICATION

### Prompt

> You are helping a solo builder who is building a personal AI-powered workflow system. As part of this system, you will frequently need to take large, messy inputs — raw research notes, long conversation threads, technical documents, competitor analyses, user interview transcripts — and turn them into clean, structured, reusable artifacts that other agents in the system can read without re-explaining context every time.
>
> Here is a raw input. It is a collection of unstructured notes from a product discovery session about the smart trash can system we have been discussing — a computer vision device that sorts waste in NYC commercial office buildings.
>
> Raw notes:
>
> "talked to facilities manager at a midtown building today - she said the biggest problem isn't sorting accuracy it's that nobody knows what happened when something goes wrong - like if contamination is flagged by the carter she has no way to trace it back to a specific bin or time or item - she also mentioned that the janitors don't trust the system and just override it manually when they think it's wrong which means the data is garbage - she said she would pay more for a system that gave her proof not just automation - also the carter rep we talked to said they see the same 5-6 items causing 80% of contamination across all their commercial clients - mostly coffee cups with lids still on, black plastic containers, and greasy pizza boxes - they don't care about overall accuracy they care about those specific items - also read a paper on waste sorting systems that said user trust is the single biggest predictor of adoption in institutional settings and that systems that explain their decisions outperform systems that just act - there's also a note here about a competitor called Compology that does bin monitoring with cameras but doesn't do active sorting - they charge around $30-40/month per bin and have good traction with large waste haulers - we should probably think about whether we are competing with them or complementing them"
>
> Your task:
> 1. Compress this into a clean research summary artifact of no more than 150 words
> 2. Extract a pain point list with a maximum of 5 items, each one sentence
> 3. Identify the single most important insight that should influence product decisions going forward
> 4. Flag any open questions or assumptions that need validation
>
> Format your output so it can be dropped directly into a product brief without editing.

### Claude Opus 4.6 response

**Research Summary**
Facilities managers value traceability over automation. A midtown FM reported that when carters flag contamination, she cannot trace it to a specific bin, time, or item — making the system unaccountable. Janitorial staff distrust the system and override it manually, corrupting sorting data. She expressed willingness to pay a premium for provable compliance over automated sorting. Carter interviews confirm contamination is driven by 5–6 item types (lidded coffee cups, black plastic containers, greasy pizza boxes), not broad inaccuracy. Academic research supports that explainable systems outperform opaque ones for institutional adoption, with user trust as the top adoption predictor. Competitor Compology offers bin monitoring at $30–40/month/bin with hauler traction but no active sorting — positioning is unclear (competitor vs. complement).

**Pain Points**
1. Facilities managers cannot trace contamination events back to a specific item, bin, or time window.
2. Janitorial staff override the system based on personal judgment, corrupting the data used for compliance reporting.
3. Carters evaluate contamination by a handful of specific item types, not overall accuracy — a metric the system doesn't optimize for.
4. The system acts without explaining its decisions, undermining trust with both operators and end users.
5. There is no audit trail that a facilities manager can present to a carter or building owner as proof of compliance.

**Key Insight**
The product is solving for sorting accuracy, but the buyer is paying for accountability. The facilities manager's willingness to pay more for "proof not just automation" reframes the value proposition. The device's primary output should be a defensible compliance record — traceable, auditable, explainable — with automated sorting as the mechanism, not the product.

**Open Questions**
- Janitorial override behavior: How widespread is this? Is it happening across all three pilot buildings or isolated? If overrides are frequent, is it because the system is wrong or because janitors don't trust it? These have different solutions.
- Compology positioning: Are our target buyers also Compology customers? If so, do we integrate with their monitoring data or compete for budget? Needs 3–4 buyer interviews to clarify.
- Carter-specific contamination items: The carter named 5–6 items driving 80% of contamination. Do we have model accuracy broken out for those specific items?
- "Would pay more" signal: One FM said she'd pay more for traceability. Needs validation across at least 5 more buyer conversations before influencing pricing or roadmap.
- Janitorial trust as adoption blocker: Are janitors the actual user whose trust matters most, rather than the office worker? If so, the UX focus may be wrong.

### GPT-5 Thinking response

**Research Summary**
Discovery signals suggest the core customer problem is not raw sorting accuracy but operational trust, traceability, and control. A Midtown facilities manager said contamination issues are hard to investigate because there is no clear record of what happened by bin, time, or item. She also reported janitorial staff manually overriding the system when they do not trust it, which corrupts feedback data and reduces reliability. A carter rep said contamination is driven disproportionately by a small set of repeat offenders, especially coffee cups with lids, black plastic containers, and greasy pizza boxes. External research supports that trust and explainability are major adoption drivers in institutional settings. Competitive notes suggest Compology has traction with camera-based bin monitoring at roughly $30–40 per bin per month, raising the question of whether our product should position as complementary proof/traceability infrastructure rather than only automated sorting.

**Pain Points**
1. Facilities teams cannot trace contamination incidents back to a specific bin, time, or item.
2. Janitorial staff override the system when they do not trust it, degrading both operations and data quality.
3. A small set of known items appears to drive most contamination across commercial buildings.
4. Customers may value proof and explainability more than generic automation claims.
5. Competitive alternatives may already own part of the monitoring and reporting workflow.

**Most Important Insight**
The product should optimize first for trustworthy proof and explainable traceability on high-risk contamination items, not broad average sorting accuracy.

**Open Questions / Assumptions to Validate**
- Is contamination in target buildings truly dominated by a small recurring set of items?
- How much would traceability and explainability increase trust and reduce manual overrides?
- What evidence format would facilities managers and carters find most actionable?
- Are we competing with bin-monitoring vendors like Compology or integrating into the same workflow?
- Would customers pay more for auditability and proof than for improved automation alone?

### Gemini Pro response

**Discovery Research Summary**
Recent discovery sessions with NYC facility managers and waste carters indicate that traceability and trust are significantly more valuable than pure sorting automation. Facility managers struggle to pinpoint contamination sources when fined, while janitorial staff frequently override automated systems they don't trust, corrupting operational data. Carters emphasize that overall sorting accuracy matters less than correctly handling a small subset of high-risk items (e.g., coffee cups, black plastic, pizza boxes) that cause 80% of contamination. Academic research corroborates that explainability drives user trust and adoption in institutional settings. Furthermore, competitor analysis indicates Compology is successfully monetizing camera-based bin monitoring at $30-40/month without active sorting, suggesting an urgent need to define our market position as either a complementary active-sorting layer or a direct competitor offering superior end-to-end accountability.

**Top Pain Points**
1. Facility managers lack the traceability to identify the specific bin, time, or item responsible when carters flag a contamination event.
2. Janitorial staff distrust automated sorting, leading to manual overrides that silently corrupt system data.
3. Waste carters are disproportionately impacted by a small subset of high-risk items rather than general sorting inaccuracies.
4. Facility managers require verifiable proof of sorting decisions to manage compliance and dispute fines.
5. Current "black box" automated systems fail to explain their routing decisions, depressing adoption and user trust in institutional settings.

**Primary Insight**
The core value proposition must pivot from "maximizing overall sorting accuracy" to "providing verifiable proof and targeted risk mitigation."

**Open Questions & Assumptions to Validate**
- Pricing & Positioning: Are we competing directly with Compology's $30-40/month monitoring-only tier, or complementing them?
- Technical Focus: Can our CV model achieve a 99%+ confidence threshold specifically on the carter's top high-risk items?
- Behavioral Assumption: Will adding a "decision explanation" layer successfully eliminate the janitorial staff's impulse to manually override the system?

### Prompt

> Here is the core user flow for the smart trash can system in an NYC office building:
>
> 1. User places item on tray
> 2. Presence sensor triggers image capture
> 3. Vision model classifies item into internal taxonomy
> 4. Policy engine maps taxonomy to building-specific bin based on CWZ carter rules and configured exceptions
> 5. Actuator routes item to correct bin
> 6. System displays confirmation message to user
> 7. Event logged locally
>
> Generate a comprehensive test suite for this system. Include:
> - Happy path scenarios
> - Edge cases you think the team may not have considered
> - Adversarial inputs
> - Failure modes at each step
> - Any hidden assumptions in the flow that could cause real-world failures
>
> Be specific to the NYC commercial building context where relevant.

_Full responses not reproduced here due to length — see session transcript. Key findings documented in eval-notes.md._

**Standout insights:**
- Claude: hazardous waste bin safety is a liability concern not a product concern (lithium battery fires, CFL mercury vapor)
- ChatGPT: opaque desk bin bag scenario — users dump consolidated desk bins expecting machine to sort contents
- Gemini: thermal throttling on $70 NPU after 50 consecutive sorts

---

## STREAM 4 PART C — LOGICAL FLOW AND ASSUMPTION ANALYSIS

### Prompt

> The team has just completed Sprint 1. Here is what was built:
>
> - Vision model classifies items into a 47-item taxonomy with 87% accuracy in lab testing
> - Policy engine maps taxonomy to bins based on building configuration
> - Actuator routes items correctly when classification is correct
> - Local logging captures every sort event
> - Facilities manager can update building configuration through a tablet app
>
> The team is confident the system is working. Before Sprint 2 begins, identify:
> - What assumptions are baked into this design that haven't been validated in the real world yet
> - What could cause the system to fail in ways that the 87% lab accuracy number would not predict
> - What is the most dangerous unvalidated assumption — the one most likely to cause a serious problem if wrong

_Full responses not reproduced here due to length — see session transcript. Key findings documented in eval-notes.md._

**Standout insights:**
- Gemini: contamination tolerance fallacy — 87% accuracy against a 5% carter contamination threshold means the device will cause fines
- Claude: clustered error distribution — if model is 40% accurate on coffee cups and coffee cups are 30% of office waste, one in three coffee cups is misrouted
- ChatGPT: "optimization theater" — "the team has validated that a lab prototype can classify tidy items into 47 labels. They have not yet validated that the product can make correct, safe, building-specific waste decisions in the wild"

---

## STREAM 4 PART D — ANCHORING AND ROOT CAUSE TEST

### Prompt

> The system has now been live in three NYC office buildings for two weeks. The facilities managers report that contamination rates in the recycling and organics streams are actually higher than before the device was installed. Here is what the team has checked:
>
> - Vision model accuracy is confirmed at 87% in ongoing monitoring
> - Actuators are functioning correctly — items are going to the bin the system selects
> - Physical routing failures have been ruled out
> - Policy engine rules have been verified against each building's CWZ carter contract
> - No software bugs have been found
>
> Everything appears to be working correctly. But contamination is up.
>
> Diagnose what is happening. What would you change?

### Gemini Pro response

The system is successfully executing the wrong strategy. A verified 87% accuracy rate combined with perfect mechanical routing will mathematically increase contamination if the system lacks human context.

1. The Material vs. State Blind Spot — CV models naturally index on material and geometry. The model accurately identifies a plastic clamshell and routes it to recycling. However, the model is not evaluating the state of the item. A plastic clamshell half-full of leftover Caesar salad is classified as "plastic" and instantly contaminates the bin.

2. The Nested Trash Problem — office workers frequently bundle waste. The CV model classifies the outermost visible layer and routes the entire nested bundle into the wrong stream.

3. The Symmetric Confidence Error — before the system was installed, confused or lazy users typically defaulted to throwing everything into landfill. The AI is confidently making wrong guesses 13% of the time and polluting the sensitive recycling and organics streams.

Actionable Plan: Implement Asymmetric Confidence Thresholding (if model is not >95% confident an item belongs in Recycling or Compost, default route to Landfill), Expand Taxonomy to Include "Dirty" and "Nested" States, Add Weight Discrepancy as a Physical Heuristic.

_Note: Gemini stayed inside the technical system. Did not identify the behavioral root cause — that the device changed user behavior by replacing human judgment. This is the anchoring failure._

### Claude Opus 4.6 response

The system is working correctly and making contamination worse. Those two things are compatible because of a behavioral effect the team likely didn't anticipate.

The device replaced human judgment, not just human effort. Before the smart can was installed, these buildings had standard multi-bin stations with signage. Office workers who cared about sorting made their own decisions — imperfectly, but with common-sense heuristics that were roughly right for the easy cases. The people who didn't care threw everything in landfill, which is contamination-neutral.

Now the device exists, and it changed behavior in two ways that both increase contamination. First, users stopped thinking — the device signals "I handle sorting for you," so people who previously sorted correctly now defer entirely to the machine. The 87% accuracy rate means the machine is wrong 13% of the time. If the humans it replaced were right 95% of the time on the common easy items, the device is actually performing worse than the humans on those items. Second, people who previously defaulted to landfill now use the device — non-sorters now have a frictionless path to recycling and compost bins, converting landfill volume into contaminated recycling and compost. Third, the 87% number is hiding where the errors concentrate. Fourth, the device routes confidently wrong items that humans would have hesitated on.

What to change: Bias the policy engine toward landfill for uncertain items. Identify the top 5 items by contamination contribution and fix those specifically. Add a "not sure" pathway. Reconsider whether the device should sort everything automatically — an alternative UX: the device classifies the item and recommends a bin by lighting it up, but the user physically places the item.

### GPT-5 Thinking response

What's happening is that you've likely improved mechanical consistency while making the overall system behavior worse for stream purity.

The device is probably "working correctly" according to its internal logic, but that logic is misaligned with how contamination actually happens in live buildings.

[Key diagnosis points:]
1. The system is confidently sorting items that should not be auto-sorted — false certainty on ambiguous items
2. Your metric is hiding the dangerous part of the error distribution — 87% accuracy is the wrong metric, contamination driven by which mistakes happen and where they land
3. The taxonomy/policy stack is probably too coarse for real contamination control
4. The device is probably changing user behavior in a bad way — once a machine gives a confident answer, users stop thinking
5. Mixed-item and contamination-state errors are probably being undercounted

What I would change: Change the optimization target immediately (track false positive rate into recycling/organics, not raw accuracy), Add conservative fallback behavior, Introduce a "don't know / please separate" state, Rework taxonomy around contamination risk not object semantics, Audit top contamination-producing classes manually.

"The uncomfortable truth: the system is probably behaving exactly as designed. The design is the problem."

_Note: ChatGPT identified behavioral change as point 4 of 5. Got to the right answer but didn't lead with it. Consistent pattern of correct analysis buried in volume._
