import streamlit as st
import random
from pathlib import Path

# =====================================================
# CONFIG
# =====================================================

QUESTION_FILES = [
    "questions/fundamentals.txt",
    "questions/patterns.txt",
    "questions/context.txt"
]

CATEGORY_QUOTAS = {
    "OHLC": 3,
    "Anatomy": 3,
    "Candle Meaning": 3,
    "Structure": 4,
    "Trend": 3,
    "Pattern Classification": 12,
    "Context": 8
}

PASSING_SCORE = 80

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Candlestick Pattern Certification Exam",
    layout="wide"
)

st.image(
    "images/banner.png",
    use_container_width='content'
)


# =====================================================
# STYLING
# =====================================================

st.markdown("""
<style>

.main .block-container {
    max-width: 1400px;
}

h1 {
    font-size: 3rem !important;
}

h2 {
    font-size: 2rem !important;
}

h3 {
    font-size: 1.5rem !important;
}

p, li {
    font-size: 1.2rem !important;
}

div[data-testid="stRadio"] label {
    font-size: 1.15rem !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# QUESTION LOADING
# =====================================================

def load_questions(filename):

    questions = []

    path = Path(filename)

    if not path.exists():
        return questions

    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        return questions

    blocks = content.split("\n\n")

    for block in blocks:

        q = {}

        for line in block.split("\n"):

            if "|" not in line:
                continue

            key, value = line.split("|", 1)

            q[key.strip().lower()] = value.strip()

        if "choices" in q:

            choices = [
                c.strip()
                for c in q["choices"].split(";")
            ]

            random.shuffle(choices)

            q["choices"] = choices

        q["points"] = int(q.get("points", 1))

        questions.append(q)

    return questions


def load_all_questions():

    all_questions = []

    for filename in QUESTION_FILES:
        all_questions.extend(load_questions(filename))

    return all_questions

# =====================================================
# EXAM BUILDER
# =====================================================

def build_exam(all_questions):

    exam = []

    for category, quota in CATEGORY_QUOTAS.items():

        category_questions = [
            q for q in all_questions
            if q.get("category") == category
        ]

        if len(category_questions) < quota:

            raise ValueError(
                f"Category '{category}' requires "
                f"{quota} questions but only "
                f"{len(category_questions)} were found."
            )

        random.shuffle(category_questions)

        exam.extend(category_questions[:quota])

    random.shuffle(exam)

    return exam

# =====================================================
# SESSION STATE
# =====================================================

if "exam_started" not in st.session_state:
    st.session_state.exam_started = False

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "exam_questions" not in st.session_state:
    st.session_state.exam_questions = []

# =====================================================
# LOAD QUESTIONS
# =====================================================

all_questions = load_all_questions()

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("Data")

    st.write(
        f"Questions Loaded: {len(all_questions)}"
    )

# =====================================================
# TITLE
# =====================================================

st.title(
    "Candlestick Pattern Certification Exam"
)

st.write(
    "Demonstrate proficiency in candlestick "
    "analysis and market structure."
)

# =====================================================
# START EXAM
# =====================================================

if not st.session_state.exam_started:

    if st.button("Start Exam"):

        try:

            st.session_state.exam_questions = (
                build_exam(all_questions)
            )

            st.session_state.exam_started = True

            st.rerun()

        except Exception as e:

            st.error(str(e))

# =====================================================
# DISPLAY EXAM
# =====================================================

if st.session_state.exam_started:

    st.header("Exam")

    st.info(
        f"{len(st.session_state.exam_questions)} Questions"
    )

    for idx, q in enumerate(
        st.session_state.exam_questions
    ):

        st.markdown("---")

        st.subheader(
            f"Question {idx + 1}"
        )

        st.write(
            q.get("question", "")
        )

        image_path = q.get("image", "")

        if image_path:

            if Path(image_path).exists():

                st.image(image_path)
                
        options = (
            ["-- Select an Answer --"]
            + q["choices"]
        )

        st.radio(
            "Answer",
            options,
            key=f"q_{idx}"
        )

    st.markdown("---")

    if st.button("Submit Exam"):

        unanswered = []

        for idx in range(
            len(st.session_state.exam_questions)
        ):

            answer = st.session_state.get(
                f"q_{idx}"
            )

            if answer == "-- Select an Answer --":

                unanswered.append(
                    idx + 1
                )

        if unanswered:

            st.error(
                f"Please answer all questions. "
                f"Missing: {unanswered}"
            )

        else:

            st.session_state.submitted = True

# =====================================================
# RESULTS
# =====================================================

if st.session_state.submitted:

    score = 0
    possible = 0

    category_scores = {}
    category_totals = {}

    missed_questions = []

    for idx, q in enumerate(
        st.session_state.exam_questions
    ):

        category = q.get(
            "category",
            "General"
        )

        points = q.get(
            "points",
            1
        )

        possible += points

        category_totals[category] = (
            category_totals.get(category, 0)
            + points
        )

        answer = st.session_state.get(
            f"q_{idx}"
        )

        if answer == q["answer"]:

            score += points

            category_scores[category] = (
                category_scores.get(category, 0)
                + points
            )

        else:

            missed_questions.append(
                {
                    "number": idx + 1,
                    "question": q.get(
                        "question",
                        "Unknown Question"
                    ),
                    "your_answer": answer,
                    "correct_answer": q["answer"]
                }
            )

    percent = round(
        (score / possible) * 100,
        2
    )

    st.header("Results")

    st.metric(
        "Final Score",
        f"{percent}%"
    )

    st.write(
        f"{score} / {possible} points"
    )

    if percent >= PASSING_SCORE:

        st.success("PASS")

    else:

        st.error("FAIL")

    st.subheader(
        "Category Breakdown"
    )

    for category in sorted(
        category_totals.keys()
    ):

        earned = category_scores.get(
            category,
            0
        )

        total = category_totals[category]

        pct = round(
            (earned / total) * 100,
            1
        )

        st.write(
            f"{category}: "
            f"{earned}/{total} "
            f"({pct}%)"
        )

    st.markdown("---")

    st.subheader(
        "Missed Questions"
    )

    if len(missed_questions) == 0:

        st.success(
            "Perfect Score!"
        )

    else:

        for m in missed_questions:

            st.error(
                f"Question {m['number']}"
            )

            st.write(
                m["question"]
            )

            st.write(
                f"Your Answer: "
                f"{m['your_answer']}"
            )

            st.write(
                f"Correct Answer: "
                f"{m['correct_answer']}"
            )

            st.write("")
