# stage-0-product-sense.md
_Completed once. Update only if core problem framing changes._

---

## Problem statement
Children aged 3–6 with autism, speech delays, or social-communication challenges lack consistent, engaging, affordable ways to practice social skills at home between therapy sessions. Existing tools are too clinical, too passive, or too generic to reflect the specific real-life situations a child is about to face. Parents want to help but lack structured, confidence-building tools for daily use.

---

## Target user and JTBD
**Parent JTBD:** When my child is about to face a new social situation (new school, new class, new friend), I want a fun low-pressure way to help them rehearse — so they feel more confident and I feel less helpless.
**Child JTBD:** When I play with the dino characters, I want to feel brave and good at talking — so I feel ready for the real thing.

---

## Why AI — and why not AI

### Where AI adds clear value
| Function | Why AI, not rules |
|----------|------------------|
| Context-aware scenario adaptation | Parent inputs "starting soccer class" — app adapts story to match. Open-ended input variety exceeds what a decision tree handles well. |
| Adaptive difficulty | System decides whether to repeat, scaffold more, or advance based on multi-variable session performance. Judgment across combinations is brittle in static logic at scale. |
| Parent summary generation | Warm, specific, non-clinical summaries that vary by session outcome. Template text degrades quickly across edge cases. |

### Where AI must NOT be used
| Function | Reason |
|----------|--------|
| Session flow control | Deterministic state machine only. LLM controlling screen transitions = unreliable, unauditable, unsafe for children. |
| Safety rules | Hard-coded filters, not prompted. "Never suggest diagnosis" must be guaranteed, not probabilistic. |
| Story content (MVP) | Pre-written JSON scripts. Generative content is Phase 2+ after engagement is validated. |
| Progress tracking logic | Simple structured data writes. No AI needed or wanted. |

---

## Why AI and at what cost memo

**The opportunity:** A child who is nervous about starting preschool can rehearse "saying hi to a new friend" through a 5-minute dino story the night before. That scenario only works if the app knows about preschool starting. Rules-based logic can cover 10 situations. AI covers 100. That delta is the product value.

**The costs and how we manage them:**

| Risk | Mitigation |
|------|-----------|
| Model produces clinically inappropriate language | Hard pre/post output filters. Human review of all AI-generated content before ship. |
| Literal-language processing children misread AI output | All AI output constrained to simple sentence structure, no idioms, no sarcasm. Tested against gold set before deployment. |
| Latency degrades child experience | All AI calls are async (parent summary) or deferred (Phase 2). Real-time child interaction is 100% deterministic. |
| Privacy risk from sending child context to LLM API | Strip PII before API calls. Send only skill targets and situation type. Never send name, voice, or diagnosis. |
| Model drift degrades output quality over time | Eval agent runs regression check against gold set on every prompt version change. |

---

## Smallest viable AI-powered slice
**Phase 2 only:** Parent inputs a short context ("starting soccer class Monday"). A single LLM call rewrites 3–5 lines of dialogue in the existing Dino Valley story to reference soccer, teammates, and a coach instead of the default scene. Child sees a "personalized" story. Parent sees the connection to their child's real life.

This is one API call, no storage, no agentic behavior. It is the minimum unit of AI value in this product.

---

## Failure modes and trust risks
- AI generates content that inadvertently models incorrect social behavior (child with ASD may internalize as ground truth)
- AI uses figurative language a literal-processing child misreads
- AI escalates emotional intensity when child shows distress signals instead of de-escalating
- Parents lose trust if the app ever feels like it is "watching" the child
- Clinical overclaiming — any language that implies therapeutic efficacy without validation

---

## Explicit non-goals (MVP)
- Not an AAC replacement
- Not a speech articulation tool
- Not for children under 3 or over 6
- Not a diagnostic instrument
- Not a replacement for professional therapy
- Not a real-time adaptive AI conversation partner (Phase 3+)
