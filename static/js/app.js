/* ===========================================================
   Quanta - frontend logic
   =========================================================== */

document.addEventListener('DOMContentLoaded', () => {

  const DATA = JSON.parse(document.getElementById('site-data').textContent);
  const COURSES = DATA.courses;
  const FORMULAS = DATA.formulas;
  const DIFFICULTIES = DATA.difficulties;
  const COURSE_IDS = Object.keys(COURSES);

  /* ---------- math + markdown rendering ---------- */
  function typeset(el) {
    if (window.renderMathInElement) {
      window.renderMathInElement(el, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$',  right: '$',  display: false }
        ],
        throwOnError: false
      });
    }
  }

  // Protect math spans from the markdown parser, then restore them.
  function protect(text) {
    const math = [];
    let t = text.replace(/\$\$([\s\S]+?)\$\$/g, (m) => {
      math.push(m); return `MJX${math.length - 1}MJX`;
    });
    t = t.replace(/\$([^$\n]+?)\$/g, (m) => {
      math.push(m); return `MJX${math.length - 1}MJX`;
    });
    return { t, math };
  }
  function restore(html, math) {
    return html.replace(/MJX(\d+)MJX/g, (_, i) => math[+i] || '');
  }

  function renderMarkdown(el, text) {
    const { t, math } = protect(text);
    el.innerHTML = restore(marked.parse(t), math);
    el.classList.add('md');
    typeset(el);
  }
  function renderInline(el, text) {
    const { t, math } = protect(text);
    el.innerHTML = restore(marked.parseInline(t), math);
    typeset(el);
  }

  /* ---------- small helpers ---------- */
  function el(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function showLoading(box, msg) {
    box.innerHTML = '';
    const wrap = el('div', 'loading');
    wrap.appendChild(el('div', 'spinner'));
    wrap.appendChild(el('span', null, msg));
    box.appendChild(wrap);
  }
  function showError(box, msg) {
    box.innerHTML = '';
    box.appendChild(el('div', 'errorbox', msg));
  }
  async function postJSON(url, body) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed.');
    return data;
  }

  /* ---------- populate selects ---------- */
  function fillCourses(select) {
    COURSE_IDS.forEach((id) => {
      const o = el('option', null, COURSES[id].name);
      o.value = id;
      select.appendChild(o);
    });
  }
  function fillUnits(select, courseId, mixedOption) {
    select.innerHTML = '';
    if (mixedOption) {
      const o = el('option', null, 'Mixed review (all units)');
      o.value = '__all__';
      select.appendChild(o);
    }
    COURSES[courseId].units.forEach((u) => {
      const o = el('option', null, `Unit ${u.n}: ${u.title}`);
      o.value = String(u.n);
      select.appendChild(o);
    });
  }
  function getUnit(courseId, n) {
    return COURSES[courseId].units.find((u) => String(u.n) === String(n));
  }

  /* =====================================================
     TABS
     ===================================================== */
  document.querySelectorAll('.tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
      document.querySelectorAll('.panel').forEach((p) => p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById('panel-' + tab.dataset.tab).classList.add('active');
    });
  });

  /* =====================================================
     LEARN
     ===================================================== */
  const learnCourse = document.getElementById('learn-course');
  const learnUnit   = document.getElementById('learn-unit');
  const learnTopics = document.getElementById('learn-topics');
  const learnInput  = document.getElementById('learn-topic');
  const learnOut    = document.getElementById('learn-output');
  const learnGo     = document.getElementById('learn-go');

  fillCourses(learnCourse);

  function renderTopicChips() {
    learnTopics.innerHTML = '';
    const unit = getUnit(learnCourse.value, learnUnit.value);
    if (!unit) return;
    unit.topics.forEach((topic) => {
      const chip = el('button', 'chip', topic);
      chip.addEventListener('click', () => {
        document.querySelectorAll('#learn-topics .chip')
          .forEach((c) => c.classList.remove('active'));
        chip.classList.add('active');
        learnInput.value = topic;
      });
      learnTopics.appendChild(chip);
    });
  }

  learnCourse.addEventListener('change', () => {
    fillUnits(learnUnit, learnCourse.value, false);
    renderTopicChips();
  });
  learnUnit.addEventListener('change', renderTopicChips);

  learnGo.addEventListener('click', async () => {
    const topic = learnInput.value.trim();
    if (!topic) { learnInput.focus(); return; }
    const unit = getUnit(learnCourse.value, learnUnit.value);
    learnGo.disabled = true;
    showLoading(learnOut, 'Building a deep explanation\u2026');
    try {
      const data = await postJSON('/api/explain', {
        course: learnCourse.value,
        unit: unit ? `Unit ${unit.n}: ${unit.title}` : '',
        topic
      });
      renderMarkdown(learnOut, data.markdown);
    } catch (e) {
      showError(learnOut, e.message);
    } finally {
      learnGo.disabled = false;
    }
  });
  learnInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') learnGo.click();
  });

  /* =====================================================
     SOLVE
     ===================================================== */
  const solveCourse  = document.getElementById('solve-course');
  const solveProblem = document.getElementById('solve-problem');
  const solveOut     = document.getElementById('solve-output');
  const solveGo      = document.getElementById('solve-go');

  fillCourses(solveCourse);

  solveGo.addEventListener('click', async () => {
    const problem = solveProblem.value.trim();
    if (!problem) { solveProblem.focus(); return; }
    solveGo.disabled = true;
    showLoading(solveOut, 'Working through the problem\u2026');
    try {
      const data = await postJSON('/api/solve', {
        course: solveCourse.value,
        problem
      });
      renderMarkdown(solveOut, data.markdown);
    } catch (e) {
      showError(solveOut, e.message);
    } finally {
      solveGo.disabled = false;
    }
  });

  /* =====================================================
     QUIZ
     ===================================================== */
  const quizCourse = document.getElementById('quiz-course');
  const quizUnit   = document.getElementById('quiz-unit');
  const quizDiff   = document.getElementById('quiz-difficulty');
  const quizCount  = document.getElementById('quiz-count');
  const quizFrq    = document.getElementById('quiz-frq');
  const quizOut    = document.getElementById('quiz-output');
  const quizGo     = document.getElementById('quiz-go');

  fillCourses(quizCourse);
  fillUnits(quizUnit, quizCourse.value, true);
  DIFFICULTIES.forEach((d, i) => {
    const o = el('option', null, d);
    o.value = d;
    if (i === 1) o.selected = true;
    quizDiff.appendChild(o);
  });
  quizCourse.addEventListener('change', () => {
    fillUnits(quizUnit, quizCourse.value, true);
  });

  quizGo.addEventListener('click', async () => {
    const courseId = quizCourse.value;
    let unitLabel;
    if (quizUnit.value === '__all__') {
      unitLabel = 'a mix of all units in the course';
    } else {
      const u = getUnit(courseId, quizUnit.value);
      unitLabel = `Unit ${u.n}: ${u.title}`;
    }
    quizGo.disabled = true;
    showLoading(quizOut, 'Writing your practice questions\u2026');
    try {
      const data = await postJSON('/api/quiz', {
        course: courseId,
        unit: unitLabel,
        difficulty: quizDiff.value,
        count: parseInt(quizCount.value, 10),
        include_frq: quizFrq.checked
      });
      renderQuiz(data.questions, courseId, quizUnit.value === '__all__'
        ? 'Mixed review' : unitLabel);
    } catch (e) {
      showError(quizOut, e.message);
    } finally {
      quizGo.disabled = false;
    }
  });

  function renderQuiz(questions, courseId, unitLabel) {
    quizOut.innerHTML = '';
    const mcqs = questions.filter((q) => q.type === 'mcq');
    let answered = 0, correct = 0;
    const scoreSlot = el('div');
    quizOut.appendChild(scoreSlot);

    questions.forEach((q, idx) => {
      if (q.type === 'frq') {
        quizOut.appendChild(buildFRQ(q, idx));
      } else {
        quizOut.appendChild(buildMCQ(q, idx, () => {
          answered++;
          // recount correctness from DOM-independent tally below
        }, (wasRight) => {
          if (wasRight) correct++;
          if (answered === mcqs.length && mcqs.length) {
            showScore(scoreSlot, correct, mcqs.length);
            saveLog({
              course: COURSES[courseId].name,
              unit: unitLabel,
              score: correct,
              total: mcqs.length,
              ts: Date.now()
            });
            renderLog();
          }
        }));
      }
    });
  }

  function buildMCQ(q, idx, onAnswered, onScored) {
    const card = el('div', 'quiz-q');
    card.appendChild(el('div', 'qnum', `Question ${idx + 1}`));
    const qt = el('div', 'qtext');
    renderInline(qt, q.question || '');
    card.appendChild(qt);

    const choicesWrap = el('div', 'choices');
    const letters = ['A', 'B', 'C', 'D', 'E', 'F'];
    let locked = false;

    (q.choices || []).forEach((choiceText, ci) => {
      const btn = el('button', 'choice');
      const letter = el('span', 'letter', letters[ci]);
      const txt = el('span');
      renderInline(txt, String(choiceText));
      btn.appendChild(letter);
      btn.appendChild(txt);

      btn.addEventListener('click', () => {
        if (locked) return;
        locked = true;
        const right = ci === q.answer;
        [...choicesWrap.children].forEach((c, k) => {
          c.classList.add('locked');
          if (k === q.answer) c.classList.add('correct');
        });
        if (!right) btn.classList.add('wrong');

        const exp = el('div', 'explain ' + (right ? 'good' : 'bad'));
        const verdict = el('strong', null,
          right ? 'Correct. ' : `Not quite \u2014 the answer is ${letters[q.answer]}. `);
        exp.appendChild(verdict);
        const expText = el('span');
        renderInline(expText, q.explanation || '');
        exp.appendChild(expText);
        card.appendChild(exp);

        onAnswered();
        onScored(right);
      });
      choicesWrap.appendChild(btn);
    });

    card.appendChild(choicesWrap);
    return card;
  }

  function buildFRQ(q, idx) {
    const card = el('div', 'quiz-q frq-q');
    card.appendChild(el('div', 'qnum', `Free Response \u00b7 Question ${idx + 1}`));
    const qt = el('div', 'qtext');
    renderMarkdown(qt, q.question || '');
    card.appendChild(qt);

    const ta = document.createElement('textarea');
    ta.rows = 6;
    ta.placeholder = 'Write your full solution here \u2014 show your reasoning and equations.';
    card.appendChild(ta);

    const btn = el('button', 'primary', 'Submit for grading');
    card.appendChild(btn);

    const feedback = el('div');
    card.appendChild(feedback);

    btn.addEventListener('click', async () => {
      if (!ta.value.trim()) { ta.focus(); return; }
      btn.disabled = true;
      showLoading(feedback, 'Grading your response\u2026');
      try {
        const data = await postJSON('/api/grade', {
          question: q.question,
          rubric: q.rubric || '',
          answer: ta.value.trim()
        });
        feedback.innerHTML = '';
        const fb = el('div');
        renderMarkdown(fb, data.markdown);
        feedback.appendChild(fb);

        const rub = el('div', 'rubric');
        rub.appendChild(el('div', 'rubric-label', 'Model solution & rubric'));
        const rubBody = el('div');
        renderMarkdown(rubBody, q.rubric || 'No rubric provided.');
        rub.appendChild(rubBody);
        feedback.appendChild(rub);
      } catch (e) {
        showError(feedback, e.message);
      } finally {
        btn.disabled = false;
      }
    });
    return card;
  }

  function showScore(slot, correct, total) {
    slot.innerHTML = '';
    const pct = Math.round((correct / total) * 100);
    const card = el('div', 'scorecard');
    const left = el('div');
    left.appendChild(el('div', 'big', `${correct}/${total}`));
    left.appendChild(el('div', 'label', 'multiple-choice correct'));
    const right = el('div');
    right.appendChild(el('div', 'big', `${pct}%`));
    let msg = 'Keep drilling \u2014 review the explanations above.';
    if (pct >= 80) msg = 'Excellent. You have a strong grip on this unit.';
    else if (pct >= 60) msg = 'Solid work. Tighten up the misses and go again.';
    right.appendChild(el('div', 'label', msg));
    card.appendChild(left);
    card.appendChild(right);
    slot.appendChild(card);
    slot.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /* =====================================================
     STUDY LOG  (localStorage)
     ===================================================== */
  const LOG_KEY = 'quanta_study_log';
  const logBox = document.getElementById('studylog');

  function loadLog() {
    try { return JSON.parse(localStorage.getItem(LOG_KEY)) || []; }
    catch (e) { return []; }
  }
  function saveLog(entry) {
    const log = loadLog();
    log.unshift(entry);
    localStorage.setItem(LOG_KEY, JSON.stringify(log.slice(0, 40)));
  }
  function pctClass(p) { return p >= 70 ? 'hi' : p >= 50 ? 'mid' : 'lo'; }

  function renderLog() {
    const log = loadLog();
    logBox.innerHTML = '';
    logBox.appendChild(el('h3', null, 'Study Log'));

    if (!log.length) {
      const sub = el('p', 'sub', 'Your quiz results are saved here on this device.');
      logBox.appendChild(sub);
      logBox.appendChild(el('div', 'log-empty', 'No quizzes taken yet.'));
      return;
    }

    const avg = Math.round(
      log.reduce((s, e) => s + (e.score / e.total) * 100, 0) / log.length
    );
    logBox.appendChild(el('p', 'sub',
      `${log.length} quiz${log.length === 1 ? '' : 'zes'} taken \u00b7 ${avg}% average`));

    log.slice(0, 6).forEach((e) => {
      const p = Math.round((e.score / e.total) * 100);
      const row = el('div', 'log-row');
      const where = el('div');
      where.appendChild(el('div', 'where', `${e.course} \u2014 ${e.unit}`));
      where.appendChild(el('div', 'when', new Date(e.ts).toLocaleString()));
      row.appendChild(where);
      const pct = el('div', 'pct ' + pctClass(p), `${e.score}/${e.total} \u00b7 ${p}%`);
      row.appendChild(pct);
      logBox.appendChild(row);
    });

    const clr = el('button', 'log-clear', 'Clear study log');
    clr.addEventListener('click', () => {
      localStorage.removeItem(LOG_KEY);
      renderLog();
    });
    logBox.appendChild(clr);
  }

  /* =====================================================
     FORMULAS
     ===================================================== */
  const formulaCourse = document.getElementById('formula-course');
  const formulaGrid   = document.getElementById('formula-grid');

  fillCourses(formulaCourse);

  function renderFormulas() {
    formulaGrid.innerHTML = '';
    const groups = FORMULAS[formulaCourse.value] || [];
    groups.forEach((group) => {
      const card = el('div', 'formula-card');
      card.appendChild(el('h3', null, group.group));
      group.items.forEach((item) => {
        const row = el('div', 'formula-row');
        const eq = el('div', 'eq');
        eq.textContent = '$$' + item.eq + '$$';
        row.appendChild(eq);
        row.appendChild(el('div', 'use', item.use));
        card.appendChild(row);
      });
      formulaGrid.appendChild(card);
      typeset(card);
    });
  }
  formulaCourse.addEventListener('change', renderFormulas);

  /* =====================================================
     INITIAL RENDER
     ===================================================== */
  fillUnits(learnUnit, learnCourse.value, false);
  renderTopicChips();
  renderFormulas();
  renderLog();
});
