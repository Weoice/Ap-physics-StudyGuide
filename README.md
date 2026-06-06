# Quanta — AP Physics Study Companion

An AI-powered study tool for **AP Physics 1, AP Physics 2, AP Physics C: Mechanics,**
and **AP Physics C: Electricity & Magnetism**, built for **DSH Hacks V1** (theme:
AI × STEM Education).

AP Physics has historically been one of the hardest AP exams. Quanta lowers that
barrier by giving every student an on-demand tutor: deep concept explanations, any
problem worked step by step, and unlimited practice quizzes — all aligned to the
2024–25 revised AP frameworks.

## What it does

- **Learn** — Pick any topic across all four courses and get a deep, exam-focused
  explanation: physical intuition, every key equation, a fully worked example,
  common mistakes, and exam tips.
- **Solve** — Paste any physics problem and get a complete tutorial solution:
  strategy, step-by-step reasoning, a sanity check, and the pitfalls to avoid.
  It teaches the method instead of just printing an answer.
- **Quiz** — Generate fresh AP-style practice questions for any unit (or a mixed
  review) at four difficulty levels. Answer multiple choice with instant
  explanations, optionally add an AI-graded free-response question, and track your
  scores in a study log.
- **Formulas** — A clean, equation-by-equation reference for every course, with a
  note on what each formula is actually for.

## Tech

- **Backend:** Python + Flask
- **AI:** Anthropic Claude API (`anthropic` Python SDK)
- **Frontend:** vanilla HTML / CSS / JavaScript
- **Math rendering:** KaTeX  ·  **Markdown:** marked.js
- The API key lives only in the Flask backend, so it is never exposed to the
  browser (this also avoids CORS issues).

## Setup (VS Code)

1. **Open the folder** in VS Code (`File → Open Folder → quanta`).

2. **Create a virtual environment** in the VS Code terminal:

   ```bash
   python -m venv venv
   ```

   Activate it:
   - Windows: `venv\Scripts\activate`
   - macOS / Linux: `source venv/bin/activate`

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Add your API key.** Copy `.env.example` to a new file named `.env` and paste
   in your key from <https://console.anthropic.com/>:

   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

5. **Run the app:**

   ```bash
   python app.py
   ```

6. Open <http://localhost:5000> in your browser.

## Configuration

In `app.py`, the `MODEL` constant controls which model answers:

| Model                       | Best for                          |
|------------------------------|-----------------------------------|
| `claude-opus-4-7`            | Highest-quality explanations      |
| `claude-sonnet-4-6` (default)| Balanced quality and speed        |
| `claude-haiku-4-5-20251001`  | Fastest, lowest cost              |

The curriculum (`COURSES`) and formula reference (`FORMULAS`) are plain Python
dictionaries in `app.py` — easy to edit if the AP framework changes.

## Notes

- Explanations, solutions, and quizzes are AI-generated. They are strong study
  aids but should be checked against your textbook and the official AP Course and
  Exam Description.
- The study log is stored in your browser's local storage on one device only.
