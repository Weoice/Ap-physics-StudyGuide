# Quanta — DSH Hacks V1 Submission

**Theme:** AI × STEM Education
**Category:** Web application / AI-driven learning tool

## Inspiration

AP Physics is one of the hardest exams a high school student can take. Before the
2025 redesign, AP Physics 1 had one of the lowest pass rates of any AP exam —
under half of students passed. The subject is unforgiving: it rewards deep
conceptual reasoning, not memorization, and most students do not have access to a
tutor who can explain a concept three different ways or work through a problem with
them at 11 p.m. the night before a test.

Quanta exists to give every AP Physics student that tutor.

## What it does

Quanta covers all four AP Physics courses — Physics 1, Physics 2, Physics C:
Mechanics, and Physics C: E&M — aligned to the 2024–25 revised frameworks. It has
four tools:

1. **Learn** — deep, exam-focused explanations of any topic, structured into
   intuition, key equations, a derivation/deeper dive, a worked example, common
   mistakes, and exam tips.
2. **Solve** — a problem tutor that takes any physics problem and returns a full
   worked solution that teaches the *method*: strategy, symbolic-then-numeric
   steps, a sanity check, and pitfalls.
3. **Quiz** — unlimited AP-style practice questions for any unit or a mixed
   review, at four difficulty levels, with instant explanations, an optional
   AI-graded free-response question, and a study log that tracks progress.
4. **Formulas** — a clean equation reference for every course.

## How we built it

- **Backend:** Python + Flask, with four JSON API endpoints (`/explain`,
  `/solve`, `/quiz`, `/grade`).
- **AI:** the Anthropic Claude API. Each endpoint uses a carefully engineered
  prompt with a shared physics-tutor system prompt. The quiz endpoint asks the
  model for strict JSON and parses it into an interactive UI.
- **Frontend:** vanilla HTML/CSS/JS — no framework — with KaTeX for real
  equation rendering and marked.js for formatting.
- **Curriculum:** the unit structure and formula reference are stored as data in
  the backend, verified against the College Board's 2024–25 revised frameworks.

## Technical depth

- **Math-safe markdown pipeline:** LaTeX spans are extracted and protected before
  markdown parsing, then restored and rendered with KaTeX, so equations never get
  mangled by the formatter.
- **Structured AI output:** the quiz feature prompts for and parses strict JSON,
  with fence-tolerant extraction, turning a language model into a reliable
  question generator.
- **Secure architecture:** the API key stays server-side in Flask, never reaching
  the browser — which also sidesteps CORS entirely.

## Real-world impact

Quanta is genuinely usable by any of the hundreds of thousands of students who
take an AP Physics exam each year. Because the content is AI-generated rather than
a fixed question bank, the practice material is effectively unlimited and adapts to
whatever unit, difficulty, or specific problem a student is stuck on. It directly
serves students who cannot afford a private tutor.

## Challenges

- Getting LaTeX to survive a markdown parser cleanly.
- Designing prompts that produce rigorous, exam-accurate physics rather than
  hand-wavy explanations.
- Verifying the curriculum against the recent AP redesign, since most prep
  material online is still outdated.

## What's next

- Per-topic mastery tracking and spaced-repetition review.
- Diagram and free-body-diagram generation.
- Photo upload so students can solve a problem straight from their worksheet.
