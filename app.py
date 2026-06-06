"""
Quanta - AP Physics Study Companion
A Flask app that uses the Claude API to tutor students through
AP Physics 1, AP Physics 2, AP Physics C: Mechanics, and AP Physics C: E&M.
"""

import os
import json
import re

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import anthropic

load_dotenv()

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Claude API setup
# ---------------------------------------------------------------------------
# Model can be swapped: claude-opus-4-7 (highest quality),
# claude-sonnet-4-6 (balanced - default), claude-haiku-4-5-20251001 (fastest).
MODEL = "claude-sonnet-4-6"

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=API_KEY) if API_KEY else None

SYSTEM_PROMPT = (
    "You are an expert AP Physics tutor with deep knowledge of the College Board "
    "AP Physics 1, AP Physics 2, AP Physics C: Mechanics, and AP Physics C: "
    "Electricity & Magnetism curricula (2024-25 revised frameworks). You explain "
    "physics with clear physical intuition, careful reasoning, and full rigor, and "
    "you always connect explanations to what the AP exam actually tests. "
    "Write all mathematics in LaTeX: inline math wrapped in single dollar signs and "
    "display math wrapped in double dollar signs. Never use unicode math symbols "
    "outside of LaTeX. Be precise but genuinely accessible to a motivated high "
    "school student."
)

# ---------------------------------------------------------------------------
# Curriculum data (2024-25 revised AP Physics frameworks)
# ---------------------------------------------------------------------------
COURSES = {
    "physics1": {
        "name": "AP Physics 1",
        "tag": "Algebra-based",
        "calc": False,
        "units": [
            {"n": 1, "title": "Kinematics",
             "topics": ["Position, velocity, and acceleration", "Motion graphs",
                        "Kinematic equations", "Projectile motion", "Relative motion"]},
            {"n": 2, "title": "Force and Translational Dynamics",
             "topics": ["Newton's three laws", "Free-body diagrams", "Friction",
                        "Tension and normal force", "Inclined planes",
                        "Uniform circular motion and centripetal force"]},
            {"n": 3, "title": "Work, Energy, and Power",
             "topics": ["Work and the work-energy theorem", "Kinetic energy",
                        "Gravitational and elastic potential energy",
                        "Conservation of energy", "Power"]},
            {"n": 4, "title": "Linear Momentum",
             "topics": ["Impulse and momentum", "Conservation of momentum",
                        "Elastic and inelastic collisions", "Center of mass"]},
            {"n": 5, "title": "Torque and Rotational Dynamics",
             "topics": ["Torque", "Rotational kinematics", "Moment of inertia",
                        "Newton's second law for rotation", "Rotational equilibrium"]},
            {"n": 6, "title": "Energy and Momentum of Rotating Systems",
             "topics": ["Rotational kinetic energy", "Angular momentum",
                        "Conservation of angular momentum", "Rolling motion"]},
            {"n": 7, "title": "Oscillations",
             "topics": ["Simple harmonic motion", "Springs and pendulums",
                        "Energy in simple harmonic motion", "Equations of motion for SHM"]},
            {"n": 8, "title": "Fluids",
             "topics": ["Density and pressure", "Buoyancy and Archimedes' principle",
                        "The continuity equation", "Bernoulli's equation"]},
        ],
    },
    "physics2": {
        "name": "AP Physics 2",
        "tag": "Algebra-based",
        "calc": False,
        "units": [
            {"n": 1, "title": "Thermodynamics",
             "topics": ["Temperature and thermal equilibrium", "The ideal gas law",
                        "Kinetic theory of gases", "Heat and the first law of thermodynamics",
                        "PV diagrams and thermodynamic processes",
                        "The second law, entropy, and heat engines"]},
            {"n": 2, "title": "Electric Force, Field, and Potential",
             "topics": ["Electric charge and Coulomb's law", "Electric fields",
                        "Electric potential energy and potential", "Equipotential lines",
                        "Conductors and insulators"]},
            {"n": 3, "title": "Electric Circuits",
             "topics": ["Current and resistance", "Ohm's law",
                        "Series and parallel circuits", "Kirchhoff's rules",
                        "Power in circuits", "Capacitors and RC circuits"]},
            {"n": 4, "title": "Magnetism and Electromagnetic Induction",
             "topics": ["Magnetic fields", "Magnetic force on charges and currents",
                        "Sources of magnetic field", "Magnetic flux",
                        "Faraday's and Lenz's laws"]},
            {"n": 5, "title": "Geometric Optics",
             "topics": ["Reflection and refraction", "Snell's law", "Mirrors and lenses",
                        "Ray diagrams", "Image formation and the thin-lens equation"]},
            {"n": 6, "title": "Waves, Sound, and Physical Optics",
             "topics": ["Wave properties", "Superposition and interference",
                        "Standing waves", "Sound and the Doppler effect",
                        "Diffraction", "Double-slit and thin-film interference"]},
            {"n": 7, "title": "Modern Physics",
             "topics": ["The photoelectric effect", "Photons and wave-particle duality",
                        "Atomic energy levels", "Nuclear physics",
                        "Mass-energy equivalence", "Blackbody radiation and Compton scattering"]},
        ],
    },
    "physicsc_mech": {
        "name": "AP Physics C: Mechanics",
        "tag": "Calculus-based",
        "calc": True,
        "units": [
            {"n": 1, "title": "Kinematics",
             "topics": ["Calculus-based motion", "Derivatives and integrals of motion",
                        "Variable acceleration", "Two-dimensional and projectile motion"]},
            {"n": 2, "title": "Newton's Laws of Motion",
             "topics": ["Force analysis", "Velocity-dependent (drag) forces",
                        "Differential equations of motion"]},
            {"n": 3, "title": "Work, Energy, and Power",
             "topics": ["The work integral", "Conservative forces and potential energy functions",
                        "Energy diagrams", "Power"]},
            {"n": 4, "title": "Systems of Particles and Linear Momentum",
             "topics": ["Center of mass by integration", "Impulse and momentum",
                        "Conservation of momentum", "Collisions"]},
            {"n": 5, "title": "Rotation",
             "topics": ["Moment of inertia by integration", "Torque and rotational dynamics",
                        "Angular momentum", "Rolling without slipping"]},
            {"n": 6, "title": "Oscillations",
             "topics": ["Simple harmonic motion", "The differential equation of SHM",
                        "Physical and torsional pendulums", "Damped oscillation"]},
            {"n": 7, "title": "Gravitation",
             "topics": ["Newton's law of universal gravitation",
                        "Gravitational fields and potential", "Orbits and Kepler's laws",
                        "Escape velocity"]},
        ],
    },
    "physicsc_em": {
        "name": "AP Physics C: E&M",
        "tag": "Calculus-based",
        "calc": True,
        "units": [
            {"n": 1, "title": "Electric Charges, Fields, and Gauss's Law",
             "topics": ["Coulomb's law", "Electric field by integration", "Gauss's law",
                        "Fields of continuous charge distributions"]},
            {"n": 2, "title": "Electric Potential",
             "topics": ["Potential from fields and from charges", "Electric potential energy",
                        "Relating field and potential"]},
            {"n": 3, "title": "Conductors and Capacitors",
             "topics": ["Conductors in electrostatic equilibrium", "Capacitance",
                        "Dielectrics", "Energy stored in capacitors"]},
            {"n": 4, "title": "Electric Circuits",
             "topics": ["Current and resistance", "Kirchhoff's rules", "RC circuits",
                        "Transient circuit behavior"]},
            {"n": 5, "title": "Magnetic Fields",
             "topics": ["Magnetic force", "The Biot-Savart law", "Ampere's law",
                        "Fields of current configurations"]},
            {"n": 6, "title": "Electromagnetism",
             "topics": ["Faraday's law and induced EMF", "Inductance and LR circuits",
                        "Maxwell's equations overview"]},
        ],
    },
}

# ---------------------------------------------------------------------------
# Formula reference (key equations grouped by topic)
# ---------------------------------------------------------------------------
FORMULAS = {
    "physics1": [
        {"group": "Kinematics", "items": [
            {"eq": r"v = v_0 + at", "use": "Velocity with constant acceleration"},
            {"eq": r"x = x_0 + v_0 t + \tfrac{1}{2}at^2", "use": "Position with constant acceleration"},
            {"eq": r"v^2 = v_0^2 + 2a(x - x_0)", "use": "Velocity without time"},
        ]},
        {"group": "Dynamics", "items": [
            {"eq": r"\vec{F}_{net} = m\vec{a}", "use": "Newton's second law"},
            {"eq": r"F_f \le \mu F_N", "use": "Friction force"},
            {"eq": r"a_c = \dfrac{v^2}{r}", "use": "Centripetal acceleration"},
        ]},
        {"group": "Energy and Momentum", "items": [
            {"eq": r"W = Fd\cos\theta", "use": "Work done by a force"},
            {"eq": r"KE = \tfrac{1}{2}mv^2", "use": "Kinetic energy"},
            {"eq": r"PE_g = mgh,\quad PE_s = \tfrac{1}{2}kx^2", "use": "Potential energy"},
            {"eq": r"P = \dfrac{W}{\Delta t} = Fv", "use": "Power"},
            {"eq": r"\vec{p} = m\vec{v},\quad \vec{J} = \vec{F}\Delta t = \Delta\vec{p}", "use": "Momentum and impulse"},
        ]},
        {"group": "Rotation", "items": [
            {"eq": r"\tau = rF\sin\theta", "use": "Torque"},
            {"eq": r"\tau_{net} = I\alpha", "use": "Newton's second law for rotation"},
            {"eq": r"KE_{rot} = \tfrac{1}{2}I\omega^2", "use": "Rotational kinetic energy"},
            {"eq": r"L = I\omega", "use": "Angular momentum"},
        ]},
        {"group": "Oscillations and Fluids", "items": [
            {"eq": r"T_s = 2\pi\sqrt{\dfrac{m}{k}},\quad T_p = 2\pi\sqrt{\dfrac{L}{g}}", "use": "Periods of SHM"},
            {"eq": r"P = P_0 + \rho g h", "use": "Pressure with depth"},
            {"eq": r"F_b = \rho_{fluid}\, V g", "use": "Buoyant force"},
            {"eq": r"A_1 v_1 = A_2 v_2", "use": "Continuity equation"},
        ]},
    ],
    "physics2": [
        {"group": "Thermodynamics", "items": [
            {"eq": r"PV = nRT", "use": "Ideal gas law"},
            {"eq": r"\tfrac{1}{2}m\overline{v^2} = \tfrac{3}{2}k_B T", "use": "Average kinetic energy of a gas particle"},
            {"eq": r"\Delta U = Q + W", "use": "First law of thermodynamics"},
        ]},
        {"group": "Electrostatics", "items": [
            {"eq": r"F = k\dfrac{q_1 q_2}{r^2}", "use": "Coulomb's law"},
            {"eq": r"E = \dfrac{F}{q},\quad E = k\dfrac{q}{r^2}", "use": "Electric field"},
            {"eq": r"V = k\dfrac{q}{r},\quad U = qV", "use": "Potential and potential energy"},
        ]},
        {"group": "Circuits", "items": [
            {"eq": r"V = IR", "use": "Ohm's law"},
            {"eq": r"R_s = \sum R_i,\quad \dfrac{1}{R_p} = \sum \dfrac{1}{R_i}", "use": "Series and parallel resistance"},
            {"eq": r"P = IV = I^2R", "use": "Electrical power"},
            {"eq": r"C = \dfrac{Q}{V}", "use": "Capacitance"},
        ]},
        {"group": "Magnetism and Waves", "items": [
            {"eq": r"F = qvB\sin\theta,\quad F = BIL\sin\theta", "use": "Magnetic force"},
            {"eq": r"\varepsilon = -\dfrac{\Delta\Phi_B}{\Delta t}", "use": "Faraday's law"},
            {"eq": r"n_1\sin\theta_1 = n_2\sin\theta_2", "use": "Snell's law"},
            {"eq": r"\dfrac{1}{f} = \dfrac{1}{s_o} + \dfrac{1}{s_i}", "use": "Thin-lens / mirror equation"},
        ]},
        {"group": "Modern Physics", "items": [
            {"eq": r"E = hf", "use": "Photon energy"},
            {"eq": r"K_{max} = hf - \phi", "use": "Photoelectric effect"},
            {"eq": r"E = mc^2", "use": "Mass-energy equivalence"},
        ]},
    ],
    "physicsc_mech": [
        {"group": "Kinematics and Dynamics", "items": [
            {"eq": r"\vec{v} = \dfrac{d\vec{r}}{dt},\quad \vec{a} = \dfrac{d\vec{v}}{dt}", "use": "Calculus definitions of motion"},
            {"eq": r"\vec{F}_{net} = m\vec{a} = \dfrac{d\vec{p}}{dt}", "use": "Newton's second law"},
        ]},
        {"group": "Energy and Momentum", "items": [
            {"eq": r"W = \int \vec{F}\cdot d\vec{r}", "use": "Work as an integral"},
            {"eq": r"F_x = -\dfrac{dU}{dx}", "use": "Force from a potential energy function"},
            {"eq": r"\vec{r}_{cm} = \dfrac{1}{M}\int \vec{r}\,dm", "use": "Center of mass"},
        ]},
        {"group": "Rotation and Oscillations", "items": [
            {"eq": r"I = \int r^2\,dm", "use": "Moment of inertia by integration"},
            {"eq": r"\vec{\tau} = \dfrac{d\vec{L}}{dt},\quad \vec{L} = I\vec{\omega}", "use": "Torque and angular momentum"},
            {"eq": r"\dfrac{d^2x}{dt^2} = -\omega^2 x", "use": "Differential equation of SHM"},
        ]},
        {"group": "Gravitation", "items": [
            {"eq": r"F = G\dfrac{m_1 m_2}{r^2}", "use": "Universal gravitation"},
            {"eq": r"U = -G\dfrac{m_1 m_2}{r}", "use": "Gravitational potential energy"},
            {"eq": r"v_{esc} = \sqrt{\dfrac{2GM}{r}}", "use": "Escape velocity"},
        ]},
    ],
    "physicsc_em": [
        {"group": "Electric Fields", "items": [
            {"eq": r"\vec{E} = \dfrac{1}{4\pi\varepsilon_0}\int \dfrac{dq}{r^2}\hat{r}", "use": "Field of a continuous distribution"},
            {"eq": r"\oint \vec{E}\cdot d\vec{A} = \dfrac{Q_{enc}}{\varepsilon_0}", "use": "Gauss's law"},
        ]},
        {"group": "Potential and Capacitance", "items": [
            {"eq": r"V = -\int \vec{E}\cdot d\vec{l}", "use": "Potential from field"},
            {"eq": r"E_x = -\dfrac{dV}{dx}", "use": "Field from potential"},
            {"eq": r"C = \dfrac{Q}{V},\quad U = \tfrac{1}{2}CV^2", "use": "Capacitance and stored energy"},
        ]},
        {"group": "Magnetism", "items": [
            {"eq": r"\vec{F} = q\vec{v}\times\vec{B}", "use": "Magnetic force on a charge"},
            {"eq": r"d\vec{B} = \dfrac{\mu_0}{4\pi}\dfrac{I\,d\vec{l}\times\hat{r}}{r^2}", "use": "Biot-Savart law"},
            {"eq": r"\oint \vec{B}\cdot d\vec{l} = \mu_0 I_{enc}", "use": "Ampere's law"},
        ]},
        {"group": "Induction", "items": [
            {"eq": r"\Phi_B = \int \vec{B}\cdot d\vec{A}", "use": "Magnetic flux"},
            {"eq": r"\varepsilon = -\dfrac{d\Phi_B}{dt}", "use": "Faraday's law"},
            {"eq": r"\varepsilon = -L\dfrac{dI}{dt}", "use": "Inductor EMF"},
        ]},
    ],
}

DIFFICULTY_GUIDE = {
    "Foundational": "single-concept questions that check core definitions and direct formula use",
    "On-level": "typical AP exam questions that combine two ideas and require a short chain of reasoning",
    "Challenging": "multi-step questions that integrate several concepts and require careful setup",
    "Exam-level": "questions that closely mirror the hardest released AP free-response and multiple-choice items",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def ask_claude(user_prompt, max_tokens=2600):
    """Send a single-turn request to Claude and return the text response."""
    if client is None:
        raise RuntimeError(
            "No ANTHROPIC_API_KEY found. Copy .env.example to .env and add your key."
        )
    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(block.text for block in message.content if block.type == "text")


def extract_json(text):
    """Pull a JSON array or object out of a model response, tolerating fences."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise


def course_name(course_id):
    return COURSES.get(course_id, {}).get("name", "AP Physics")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    site_data = {"courses": COURSES, "formulas": FORMULAS,
                 "difficulties": list(DIFFICULTY_GUIDE.keys())}
    return render_template("index.html", site_data=json.dumps(site_data),
                           has_key=bool(API_KEY))


@app.route("/api/explain", methods=["POST"])
def api_explain():
    data = request.get_json(force=True)
    course = data.get("course", "physics1")
    unit = data.get("unit", "")
    topic = (data.get("topic") or "").strip()
    if not topic:
        return jsonify({"error": "Please choose or enter a topic."}), 400

    calc_line = ("Because this is a calculus-based course, include the relevant "
                 "calculus (derivatives, integrals, differential equations).") \
        if COURSES.get(course, {}).get("calc") else ""

    prompt = f"""A student studying {course_name(course)} wants to deeply understand this topic:

Topic: {topic}
Unit: {unit}

Write a thorough, well-structured explanation in Markdown using these exact section headings:

## Core Idea
The physical intuition in plain language - what is really going on and why it matters.

## Key Equations
Each relevant equation, with every variable defined and a note on when to use it.

## Going Deeper
Derivations, important edge cases, and connections to other topics. {calc_line}

## Worked Example
One fully solved AP-style example. Show the reasoning at every step, not just the algebra.

## Common Mistakes
Specific, concrete errors that AP students make on this topic.

## Exam Tips
How this topic shows up on the AP {course_name(course)} exam and how to approach those questions.

Be rigorous but accessible to a motivated high school student. Use LaTeX for all math."""

    try:
        return jsonify({"markdown": ask_claude(prompt, max_tokens=3000)})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


@app.route("/api/solve", methods=["POST"])
def api_solve():
    data = request.get_json(force=True)
    course = data.get("course", "physics1")
    problem = (data.get("problem") or "").strip()
    if not problem:
        return jsonify({"error": "Please paste a physics problem to solve."}), 400

    prompt = f"""A student needs help with this {course_name(course)} problem:

\"\"\"{problem}\"\"\"

Provide a complete tutorial solution in Markdown using these exact section headings:

## Understanding the Problem
Restate what is being asked. List the known quantities and the unknowns.

## Strategy
Which physics principles apply here, and why those and not others.

## Solution
Work through the problem step by step. Solve symbolically first, then substitute
numbers. Explain the reasoning behind each step so the student learns the method.

## Answer
State the final answer clearly, with correct units and significant figures.

## Check
Sanity-check the result: units, order of magnitude, and limiting cases.

## Watch Out
Common mistakes students make on this type of problem.

Teach the method - do not simply give the answer. Use LaTeX for all math."""

    try:
        return jsonify({"markdown": ask_claude(prompt, max_tokens=2800)})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


@app.route("/api/quiz", methods=["POST"])
def api_quiz():
    data = request.get_json(force=True)
    course = data.get("course", "physics1")
    unit = data.get("unit", "")
    difficulty = data.get("difficulty", "On-level")
    count = max(2, min(int(data.get("count", 5)), 10))
    include_frq = bool(data.get("include_frq", False))

    diff_desc = DIFFICULTY_GUIDE.get(difficulty, DIFFICULTY_GUIDE["On-level"])

    frq_block = ""
    if include_frq:
        frq_block = """
Also include exactly ONE free-response question as the final array element, in this shape:
{
  "type": "frq",
  "question": "the multi-part free-response prompt",
  "rubric": "a model solution with point-by-point grading criteria",
  "explanation": "the key concepts this question assesses"
}
"""

    prompt = f"""Generate {count} multiple-choice practice questions for {course_name(course)},
{unit}, at "{difficulty}" difficulty ({diff_desc}).

Return ONLY a valid JSON array. No markdown, no code fences, no commentary before or after.

Each multiple-choice element must have this exact shape:
{{
  "type": "mcq",
  "question": "the question text (LaTeX allowed, wrapped in $ delimiters)",
  "choices": ["choice A", "choice B", "choice C", "choice D"],
  "answer": 0,
  "explanation": "why the correct choice is right and why the tempting wrong choices are wrong"
}}

The "answer" field is the 0-indexed position of the correct choice.
{frq_block}
Requirements:
- Questions must be physically accurate and realistic for the actual AP exam.
- Cover a range of subtopics within the unit, not just one idea.
- Make the wrong choices reflect genuine, common student misconceptions.
- Vary the position of the correct answer across questions."""

    try:
        raw = ask_claude(prompt, max_tokens=3600)
        questions = extract_json(raw)
        if not isinstance(questions, list) or not questions:
            raise ValueError("Model did not return a question list.")
        return jsonify({"questions": questions})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Could not build the quiz: {exc}"}), 500


@app.route("/api/grade", methods=["POST"])
def api_grade():
    data = request.get_json(force=True)
    question = (data.get("question") or "").strip()
    rubric = (data.get("rubric") or "").strip()
    answer = (data.get("answer") or "").strip()
    if not answer:
        return jsonify({"error": "Write an answer before submitting for grading."}), 400

    prompt = f"""You are grading a student's AP Physics free-response answer.

QUESTION:
{question}

MODEL SOLUTION AND RUBRIC:
{rubric}

STUDENT'S ANSWER:
{answer}

Give feedback in Markdown using these exact section headings:

## Score
A score out of the rubric's total points, with a one-line justification.

## What You Did Well
Specific things the student got right.

## What Was Missing
Specific gaps, errors, or unjustified steps.

## How to Fix It
The correct approach for anything the student missed, explained so they learn from it.

Be encouraging but honest and precise. Use LaTeX for all math."""

    try:
        return jsonify({"markdown": ask_claude(prompt, max_tokens=1800)})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    if not API_KEY:
        print("\n  WARNING: ANTHROPIC_API_KEY is not set.")
        print("  Copy .env.example to .env and add your key, then restart.\n")
    app.run(debug=True, port=5000)
