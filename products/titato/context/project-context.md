# project-context.md
_Last updated: [date] — keep under 500 words. Update in place, never append. Every agent reads this first._

---

## Product summary
**Titato** (app name)
A story-driven social communication app for children aged 3–6, including those with autism, speech delays, or social-communication challenges. The app features characters from **Fossil Friends** — an independently co-created comic book series — whose traits map naturally onto social-emotional learning archetypes. Children practice real-world social skills through short interactive story missions with familiar dino characters. Not a therapy replacement; a home-practice companion grounded in evidence-based principles (ESDM, Hanen, Social Stories, PRT).

---

## Target user
**Primary:** Parents of children aged 3–6 with autism, speech delays, or social-communication challenges.
**Secondary:** Parents of neurotypical 3–6 year olds wanting social-emotional skill reinforcement.
**End user:** The child, engaged through play — never framed as having a deficit.

---

## Current MVP slice
Parent-led session mode only. One story world: Dino Valley. 3–4 scenes covering: greeting a new peer, joining play, waiting a turn, trying something new. Child plays as a Parasaurolophus avatar named after them. Guide character (Boo or Tara) leads sessions. Push-to-talk practice moments with on-device speech detection. End-of-session parent summary. Fully offline, no login, local storage only.

---

## Architecture decisions
- **Frontend:** Flutter (iOS first, Android later)
- **Animation:** Rive (light stateful motion, not full cartoon)
- **Voice:** TTS at MVP (Google Cloud TTS or ElevenLabs); human VO deferred
- **Content engine:** JSON-driven story scripts rendered by Flutter
- **Speech practice:** Push-to-talk, on-device STT, audio discarded immediately after feedback
- **Progress tracking:** Local structured summaries only — no raw audio, no transcripts, no PII
- **Backend:** None at MVP. Firebase/Firestore in Phase 2. VPC-secured cloud in Phase 3.
- **AI personalization:** Deferred to Phase 2 (Gemini Flash or GPT-4o mini for context-aware story adaptation)
- **CI/CD:** GitHub + Codemagic → TestFlight

---

## Safety constraints (non-negotiable)
- Never store child voice data
- Never collect PHI or diagnosis information
- No diagnosis language — frame as "practicing brave and kind behaviors"
- No shaming or corrective tone — always warm, always encouraging
- Parental gate required before any data collection
- COPPA-compliant by design; GDPR-ready by data minimization

---

## PM workflow stack
- Primary reasoning model: TBD (pending architectural eval)
- Coding agent: Claude Code
- Artifact store: `pm-os/products/titato/` (within shared `pm-os/` repo)
- Orchestrator: lightweight Python (LangGraph or custom state machine)
- Eval: Python script against shared gold set

---

## Naming
**Titato** = the app name. **Fossil Friends** = the comic book series (co-created with a 5-year-old) whose characters are licensed/leveraged for the app. These are two distinct creative properties — Fossil Friends is not a sub-brand of Titato; it's a source IP. Marketing: "Titato — featuring characters from Fossil Friends." Trademark check on Titato pending — not yet registered. Tagline candidates: "Talk. Play. Grow." / "Tiny talks. Big confidence."

---

## Current sprint goal
Seed PM workflow artifacts. Complete Stage 0, research synthesis, product brief. Run architectural eval to finalize model allocation.
