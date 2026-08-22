import json
import os
from utils.config_loader import load_config

# Load configuration for thresholds
CONFIG = load_config()
OVERALL_THRESHOLDS = CONFIG.get('overall_score_thresholds', {'strong': 80, 'weak': 60})
STRONG_THRESHOLD = OVERALL_THRESHOLDS.get('strong', 80)
WEAK_THRESHOLD = OVERALL_THRESHOLDS.get('weak', 60)
from datetime import datetime


# =====================================================
# SCREENING SCORING CONFIGURATION
# =====================================================

SCORING_WEIGHTS = {

    "clarity": 0.25,

    "relevance": 0.30,

    "completeness": 0.25,

    "consistency": 0.20

}


# =====================================================
# QUESTION IMPORTANCE
# =====================================================

QUESTION_IMPORTANCE = {

    "INTRO_001": 5,

    "INTRO_002": 8,

    "EDU_001": 7,

    "EXP_001": 10,

    "EXP_002": 9,

    "SKILL_001": 10,

    "SKILL_002": 9,

    "SKILL_003": 10,

    "SKILL_004": 10,

    "LOC_001": 7,

    "LOC_002": 6,

    "SALARY_001": 7,

    "SALARY_002": 4,

    "NOTICE_001": 8,

    "NOTICE_002": 8

}


# =====================================================
# NORMALIZE TEXT
# =====================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =====================================================
# NORMALIZE SCORE
# =====================================================

def normalize_score(score, minimum=0, maximum=100):

    try:
        score = float(score)

    except (TypeError, ValueError):
        return minimum

    score = max(
        minimum,
        min(maximum, score)
    )

    return round(score, 2)


# =====================================================
# SCORE CLARITY
# =====================================================

def score_clarity(answer):

    text = normalize_text(answer)

    if not text:
        return 0

    words = text.split()

    score = 100

    # Very short answers reduce clarity

    if len(words) < 3:
        score -= 50

    elif len(words) < 6:
        score -= 25

    # Repeated filler words

    filler_words = [

        "um",
        "uh",
        "hmm",
        "basically",
        "actually",
        "like"

    ]

    filler_count = 0

    for filler in filler_words:

        filler_count += len(

            re.findall(

                r"\b"
                + re.escape(filler)
                + r"\b",

                text

            )

        )

    score -= filler_count * 5

    # Excessively long answers

    if len(words) > 150:
        score -= 10

    return normalize_score(score)


# =====================================================
# SCORE RELEVANCE
# =====================================================

def score_relevance(answer_object):

    quality = answer_object.get(

        "quality",

        {}

    )

    intent = answer_object.get(

        "intent",

        {}

    )

    intent_name = intent.get(

        "name",

        "unknown"

    )

    intent_confidence = intent.get(

        "confidence",

        0

    )

    if quality.get(

        "off_topic",

        False

    ):

        return 0

    if intent_name in [

        "unknown",
        "off_topic",
        "missing"

    ]:

        return 20

    score = float(

        intent_confidence

    ) * 100

    return normalize_score(score)


# =====================================================
# SCORE COMPLETENESS
# =====================================================

def score_completeness(answer_object):

    quality = answer_object.get(

        "quality",

        {}

    )

    answer = answer_object.get(

        "answer",

        {}

    )

    normalized_text = answer.get(

        "normalized_text",

        ""

    )

    if not normalized_text:

        return 0

    if quality.get(

        "missing_information",

        False

    ):

        return 30

    if quality.get(

        "vague",

        False

    ):

        return 40

    word_count = len(

        normalized_text.split()

    )

    score = 100

    if word_count < 5:

        score -= 40

    elif word_count < 10:

        score -= 15

    return normalize_score(score)


# =====================================================
# SCORE CONSISTENCY
# =====================================================

def score_consistency(answer_object):

    quality = answer_object.get(

        "quality",

        {}

    )

    entities = answer_object.get(

        "entities",

        {}

    )

    score = 100

    # Off-topic response

    if quality.get(

        "off_topic",

        False

    ):

        return 0

    # Vague response

    if quality.get(

        "vague",

        False

    ):

        score -= 40

    # Missing information

    if quality.get(

        "missing_information",

        False

    ):

        score -= 30

    # Check for recognized information

    has_information = False

    for value in entities.values():

        if value:

            if isinstance(value, list):

                if len(value) > 0:
                    has_information = True

            elif isinstance(value, dict):

                if any(

                    v is not None

                    for v in value.values()

                ):

                    has_information = True

    if not has_information:

        score -= 20

    return normalize_score(score)


# =====================================================
# CALCULATE QUESTION SCORE
# =====================================================

def calculate_question_score(

    answer_object

):

    answer = (

        answer_object

        .get("answer", {})

        .get("normalized_text", "")

    )

    clarity = score_clarity(

        answer

    )

    relevance = score_relevance(

        answer_object

    )

    completeness = score_completeness(

        answer_object

    )

    consistency = score_consistency(

        answer_object

    )

    weighted_score = (

        clarity
        * SCORING_WEIGHTS["clarity"]

        +

        relevance
        * SCORING_WEIGHTS["relevance"]

        +

        completeness
        * SCORING_WEIGHTS["completeness"]

        +

        consistency
        * SCORING_WEIGHTS["consistency"]

    )

    normalized_final_score = normalize_score(

        weighted_score

    )

    question_id = answer_object.get(

        "question_id",

        "UNKNOWN"

    )

    importance = QUESTION_IMPORTANCE.get(

        question_id,

        5

    )

    return {

        "question_id":

            question_id,

        "question":

            answer_object.get(

                "question",

                ""

            ),

        "score_breakdown": {

            "clarity":

                clarity,

            "relevance":

                relevance,

            "completeness":

                completeness,

            "consistency":

                consistency

        },

        "weights":

            SCORING_WEIGHTS,

        "question_score":

            normalized_final_score,

        "importance":

            importance

    }


# =====================================================
# EXPLAIN QUESTION SCORE
# =====================================================

def explain_question_score(

    answer_object,

    score_result

):

    explanation = []

    quality = answer_object.get(

        "quality",

        {}

    )

    score = score_result[

        "score_breakdown"

    ]

    if quality.get(

        "off_topic",

        False

    ):

        explanation.append(

            "The response was detected as off-topic, reducing relevance and consistency."

        )

    if quality.get(

        "vague",

        False

    ):

        explanation.append(

            "The response was identified as vague."

        )

    if quality.get(

        "missing_information",

        False

    ):

        reason = quality.get(

            "missing_reason",

            "Required information was missing."

        )

        explanation.append(

            f"Missing information: {reason}"

        )

    if score["clarity"] >= 80:

        explanation.append(

            "The response was clear and understandable."

        )

    elif score["clarity"] < 50:

        explanation.append(

            "The response was too short or unclear."

        )

    if score["relevance"] >= 80:

        explanation.append(

            "The response was relevant to the screening question."

        )

    elif score["relevance"] < 40:

        explanation.append(

            "The response had low relevance to the expected question."

        )

    if score["completeness"] >= 80:

        explanation.append(

            "The response contained sufficient information."

        )

    elif score["completeness"] < 50:

        explanation.append(

            "The response did not provide complete information."

        )

    if score["consistency"] >= 80:

        explanation.append(

            "The extracted information was internally consistent."

        )

    return explanation


# =====================================================
# EVALUATE SINGLE QUESTION
# =====================================================

def evaluate_question(

    answer_object

):

    score_result = calculate_question_score(

        answer_object

    )

    explanation = explain_question_score(

        answer_object,

        score_result

    )

    score_result["explanation"] = explanation

    return score_result


# =====================================================
# CALCULATE TOTAL SCREENING SCORE
# =====================================================

def calculate_total_screening_score(

    question_results

):

    if not question_results:

        return {

            "total_score": 0,

            "total_weight": 0

        }

    weighted_total = 0

    total_importance = 0

    for result in question_results:

        score = result.get(

            "question_score",

            0

        )

        importance = result.get(

            "importance",

            5

        )

        weighted_total += (

            score * importance

        )

        total_importance += importance

    final_score = (

        weighted_total /

        total_importance

        if total_importance > 0

        else 0

    )

    return {

        "total_score":

            normalize_score(

                final_score

            ),

        "total_weight":

            total_importance

    }


# =====================================================
# DETERMINE SCREENING RESULT
# =====================================================

def determine_screening_result(
    total_score
):
    # Use configurable thresholds
    if total_score >= STRONG_THRESHOLD:
        return "Strong Pass"
    elif total_score >= OVERALL_THRESHOLDS.get('weak', 60):
        # Between weak and strong is a Pass
        return "Pass"
    elif total_score >= 45:
        return "Review"
    return "Needs Improvement"


# =====================================================
# CREATE FINAL SCREENING SCORE OBJECT
# =====================================================

def evaluate_screening_session(

    candidate_id,

    job_id,

    answer_objects

):

    question_results = []

    for answer_object in answer_objects:

        result = evaluate_question(

            answer_object

        )

        question_results.append(

            result

        )

    total = calculate_total_screening_score(

        question_results

    )

    screening_result = determine_screening_result(

        total["total_score"]

    )

    final_object = {

        "candidate_id":

            candidate_id,

        "job_id":

            job_id,

        "evaluation_timestamp":

            datetime.utcnow().isoformat(),

        "scoring_parameters": [

            "clarity",

            "relevance",

            "completeness",

            "consistency"

        ],

        "question_scores":

            question_results,

        "final_screening_score":

            total["total_score"],

        "screening_result":

            screening_result,

        "total_question_weight":

            total["total_weight"]

    }

    return final_object


# =====================================================
# SAVE SCREENING RESULT
# =====================================================

def save_screening_result(

    result,

    filename="ats_engine/screening_score.json"

):

    with open(

        filename,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            result,

            file,

            indent=4,

            ensure_ascii=False

        )

    return filename


# =====================================================
# SAMPLE ANSWER OBJECTS
# FROM DAY 25
# =====================================================

TEST_ANSWERS = [

    {

        "question_id": "SKILL_001",

        "question":
            "What are your strongest technical skills?",

        "answer": {

            "raw_text":
                "My strongest skills are Python, Django and SQL.",

            "normalized_text":
                "my strongest skills are python django and sql"

        },

        "intent": {

            "name":

                "skills",

            "confidence":

                0.90

        },

        "entities": {

            "skills": [

                "python",

                "django",

                "sql"

            ]

        },

        "quality": {

            "off_topic":

                False,

            "vague":

                False,

            "missing_information":

                False,

            "missing_reason":

                None

        }

    },

    {

        "question_id": "EXP_001",

        "question":
            "How many years of experience do you have?",

        "answer": {

            "raw_text":
                "I have three years of experience in software development.",

            "normalized_text":
                "i have three years of experience in software development"

        },

        "intent": {

            "name":

                "experience",

            "confidence":

                0.92

        },

        "entities": {

            "experience": {

                "years":

                    3,

                "months":

                    0

            }

        },

        "quality": {

            "off_topic":

                False,

            "vague":

                False,

            "missing_information":

                False,

            "missing_reason":

                None

        }

    },

    {

        "question_id": "SALARY_001",

        "question":
            "What are your salary expectations?",

        "answer": {

            "raw_text":
                "I am expecting around 6 LPA.",

            "normalized_text":
                "i am expecting around 6 lpa"

        },

        "intent": {

            "name":

                "salary",

            "confidence":

                0.88

        },

        "entities": {

            "salary": {

                "amount":

                    6,

                "currency":

                    "INR",

                "unit":

                    "LPA"

            }

        },

        "quality": {

            "off_topic":

                False,

            "vague":

                False,

            "missing_information":

                False,

            "missing_reason":

                None

        }

    },

    {

        "question_id": "NOTICE_001",

        "question":
            "What is your notice period?",

        "answer": {

            "raw_text":
                "I can join immediately.",

            "normalized_text":
                "i can join immediately"

        },

        "intent": {

            "name":

                "availability",

            "confidence":

                0.85

        },

        "entities": {

            "availability": {

                "available":

                    True,

                "start_time":

                    "immediate"

            }

        },

        "quality": {

            "off_topic":

                False,

            "vague":

                False,

            "missing_information":

                False,

            "missing_reason":

                None

        }

    },

    {

        "question_id": "SKILL_002",

        "question":
            "How would you rate your Python skills?",

        "answer": {

            "raw_text":
                "I watched a movie yesterday.",

            "normalized_text":
                "i watched a movie yesterday"

        },

        "intent": {

            "name":

                "off_topic",

            "confidence":

                0.85

        },

        "entities": {},

        "quality": {

            "off_topic":

                True,

            "vague":

                False,

            "missing_information":

                True,

            "missing_reason":

                    "No skill information found"

        }

    }

]


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    result = evaluate_screening_session(

        candidate_id="C101",

        job_id="JOB001",

        answer_objects=TEST_ANSWERS

    )

    save_screening_result(

        result

    )

    print(

        json.dumps(

            result,

            indent=4,

            ensure_ascii=False

        )

    )