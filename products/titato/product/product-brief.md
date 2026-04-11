# product-brief.md
_Living document. Update when scope, metrics, or risks change materially._

---

## Product name
Titato (featuring characters from the Fossil Friends comic series)

## One-liner
A story-driven app where children aged 3–6 practice real-world social skills through short adventures with the Fossil Friends dinosaur characters — so families can turn everyday moments into confident communication.

---

## Target user
**Primary persona:** Parent of a 3–6 year old with autism, speech delay, or social-communication challenges. Stretched for time. Has some therapy support but wants more home practice. Worried about screen time but wants it to be purposeful. Not looking for clinical software — looking for something their child will actually want to use.

**Secondary persona:** Parent of a neurotypical 3–6 year old preparing for kindergarten or navigating social milestones (new school, new sibling, new class).

**End user:** Child aged 3–6. Engages through play. Never positioned as having a problem.

---

## Job to be done
When my child is about to face a new or challenging social situation, I want a quick, engaging way to help them rehearse what to say and do — so they feel more prepared and I feel like I'm doing something that actually helps.

---

## MVP scope
**In scope:**
- Parent-led session mode
- One story world: Dino Valley (3–4 scenes)
- Skills covered: greeting a new peer, joining play, waiting a turn, trying something new
- Child Parasaurolophus avatar, named after child
- Guide character (Boo or Tara) leads session
- Push-to-talk practice moments (on-device, audio discarded)
- End-of-session parent summary with home follow-up tip
- Offline only, no login, local storage

**Not in scope (MVP):**
- Child-led mode
- AI-personalized scenarios
- Cloud sync or parent accounts
- Android
- Subscription or billing
- Voice actor recordings
- Multiple story worlds
- Progress dashboard

---

## Success metrics
| Metric | Definition | Instrumentation |
|--------|-----------|----------------|
| Session completion rate | % of started sessions where child reaches the parent summary screen | Event: `session_started` → `session_completed` |
| Push-to-talk attempt rate | % of practice moments where child makes a vocal attempt | Event: `ptt_prompted` → `ptt_attempted` |
| Return rate (D7) | % of installing families who start a second session within 7 days | Event: `session_started` with `session_count > 1` within 7 days |
| Parent summary view rate | % of completed sessions where parent views the summary screen | Event: `summary_screen_viewed` |
| Parent-reported engagement | Post-session rating: "Was your child engaged and comfortable?" (3-point) | In-app prompt after session 1 and session 5 |

---

## Guardrail metrics
| Metric | Threshold | Action if breached |
|--------|-----------|-------------------|
| Session abandonment at practice moment | >40% abandon at any single push-to-talk beat | Review that beat's prompt language and timing |
| Negative parent feedback rate | >15% rate session as "not comfortable" | Halt that scene, review tone and pacing |
| Crash rate | >2% of sessions | Block release |

---

## Risk register
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Children don't engage with push-to-talk | Medium | High | Test with 5-year-old in-house before build; design fallback tap-response alternative |
| Parents skip end-of-session summary | High | Medium | Make summary one screen, skimmable in 10 seconds |
| App misclassified as tic-tac-toe in App Store | Medium | Medium | Strong subtitle + keyword strategy; dino visuals dominant |
| Content tone feels corrective to sensitive children | Medium | High | All language reviewed by child development consultant before ship; gold set includes distress-signal scenarios |
| Trademark conflict on "Titato" | Low | High | Complete USPTO check before public launch |
| Scope creep into Phase 2 features during build | High | Medium | Hard MVP cut line enforced in backlog; deferred features logged not deleted |

---

## Non-goals
- Not a therapy replacement — never claim clinical efficacy
- Not for children under 3 or over 6
- Not an AAC tool or articulation trainer
- Not a diagnostic instrument
- Not a real-time AI conversation partner
- Not a school or clinic platform (Phase 3+)

---

## Phase roadmap
| Phase | Timeline | Goal |
|-------|----------|------|
| 1 — MVP | Months 0–4 | Validate engagement. Ship offline iOS app with Dino Valley. TestFlight with 10–20 parent testers. |
| 2 — Smart personalization | Months 5–9 | Add AI context adaptation. Optional cloud sync. Expand story set. |
| 3 — Scale | Months 10–18 | Subscription tier. Android. School/clinic pilot partnerships. |
