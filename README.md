# Quanta — AP Physics Study Companion

An AI-powered study tool for AP Physics 1, AP Physics 2, AP Physics C: Mechanics,
and AP Physics C: Electricity & Magnetism

AP Physics has historically been one of the hardest AP exams. I myself 
have struggled greatly as I took those courses, unfortunately, I could 
not find a tool that could help me with my AP Physics journey, that is 
why I made one myself. Quanta lowers that barrier by giving every student
an on-demand tutor: deep concept explanations, any
problem worked step by step, and unlimited practice quizzes

## What it does

- Pick any topic across all four courses and get a deep, exam-focused
  explanation: physical intuition, every key equation, a fully worked example,
  common mistakes and exam tips.
- Paste any physics problem and get a complete tutorial solution:
  strategy, step-by-step reasoning, a sanity check, and the pitfalls to avoid.
  It teaches the method instead of just printing an answer.
- Generate fresh AP-style practice questions for any unit (or a mixed
  review) at four difficulty levels. Answer multiple choice with instant
  explanations, optionally add an AI-graded free-response question, and track your
  scores in a study log.
- A clean, equation-by-equation reference for every course, with a
  note on what each formula is actually for.

## Tech

- Backend: Python + Flask
- AI: Anthropic Claude API (anthropic Python SDK)
- Frontend: vanilla HTML / CSS / JavaScript
- Math rendering: KaTeX  -  Markdown: marked.js
- The API key lives only in the Flask backend, so it is never exposed to the
  browser (this also avoids CORS issues).



- Explanations, solutions, and quizzes are AI-generated. They are strong study
  aids but should be checked against your textbook and the official AP Course and
  Exam Description.
- The study log is stored in your browser's local storage on one device only.
