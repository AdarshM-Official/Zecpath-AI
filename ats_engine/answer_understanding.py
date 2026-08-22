import re
import json
from datetime import datetime


# =====================================================
# INTENT TYPES
# =====================================================

INTENTS = [
    "introduction",
    "education",
    "experience",
    "skills",
    "availability",
    "salary",
    "location",
    "notice_period",
    "motivation",
    "off_topic",
    "vague",
    "missing",
    "unknown"
]


# =====================================================
# SKILL DICTIONARY
# =====================================================

SKILL_DB = {

    "python": [
        "python",
        "py"
    ],

    "java": [
        "java"
    ],

    "javascript": [
        "javascript",
        "js"
    ],

    "react": [
        "react",
        "reactjs",
        "react.js"
    ],

    "node": [
        "node",
        "nodejs",
        "node.js"
    ],

    "django": [
        "django"
    ],

    "flask": [
        "flask"
    ],

    "sql": [
        "sql",
        "mysql",
        "postgresql",
        "postgres"
    ],

    "mongodb": [
        "mongodb",
        "mongo"
    ],

    "html": [
        "html"
    ],

    "css": [
        "css"
    ],

    "docker": [
        "docker"
    ],

    "git": [
        "git",
        "github"
    ],

    "machine learning": [
        "machine learning",
        "ml"
    ],

    "deep learning": [
        "deep learning",
        "dl"
    ],

    "tensorflow": [
        "tensorflow"
    ],

    "pytorch": [
        "pytorch"
    ],

    "communication": [
        "communication",
        "communication skills"
    ],

    "leadership": [
        "leadership",
        "team leadership"
    ]

}


# =====================================================
# INTENT KEYWORDS
# =====================================================

INTENT_KEYWORDS = {

    "introduction": [
        "my name",
        "i am",
        "i'm",
        "myself",
        "introduce",
        "about me"
    ],

    "education": [
        "degree",
        "graduated",
        "graduation",
        "bachelor",
        "master",
        "mca",
        "btech",
        "b.tech",
        "college",
        "university",
        "education"
    ],

    "experience": [
        "experience",
        "worked",
        "working",
        "company",
        "developer",
        "years",
        "months",
        "job",
        "project"
    ],

    "skills": [
        "skill",
        "skills",
        "python",
        "java",
        "javascript",
        "react",
        "django",
        "sql",
        "mongodb",
        "docker",
        "machine learning"
    ],

    "availability": [
        "available",
        "availability",
        "join",
        "joining",
        "start",
        "immediately",
        "can join"
    ],

    "salary": [
        "salary",
        "package",
        "ctc",
        "compensation",
        "pay",
        "expected",
        "lpa"
    ],

    "location": [
        "location",
        "located",
        "live",
        "reside",
        "city",
        "relocate",
        "relocation"
    ],

    "notice_period": [
        "notice period",
        "notice",
        "days",
        "weeks",
        "month notice"
    ],

    "motivation": [
        "interested",
        "interest",
        "why",
        "motivation",
        "career",
        "reason",
        "opportunity"
    ]

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
# EXTRACT SKILLS
# =====================================================

def extract_skills(text):

    text = normalize_text(text)

    extracted = []

    for skill, variants in SKILL_DB.items():

        for variant in variants:

            pattern = (
                r"\b"
                + re.escape(variant)
                + r"\b"
            )

            if re.search(pattern, text):

                extracted.append(skill)

                break

    return list(set(extracted))


# =====================================================
# EXTRACT EXPERIENCE
# =====================================================

def extract_experience(text):

    text = normalize_text(text)

    experience = {

        "years": None,

        "months": None,

        "raw_value": None

    }

    word_to_num = {
        "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8",
        "nine": "9", "ten": "10"
    }
    for word, num in word_to_num.items():
        text = re.sub(r'\b' + word + r'\b', num, text)

    patterns = [

        r"(\d+(?:\.\d+)?)\s*\+?\s*years?",

        r"(\d+)\s*years?\s*(?:and)?\s*(\d+)?\s*months?"

    ]

    for pattern in patterns:

        match = re.search(

            pattern,

            text

        )

        if match:

            experience["raw_value"] = (
                match.group(0)
            )

            try:

                experience["years"] = float(
                    match.group(1)
                )

            except (ValueError, TypeError):

                pass

            if match.lastindex and match.lastindex >= 2:

                try:

                    if match.group(2):

                        experience["months"] = int(
                            match.group(2)
                        )

                except (ValueError, TypeError):

                    pass

            break

    # Detect fresher

    if any(

        phrase in text

        for phrase in [

            "fresher",
            "no experience",
            "no professional experience",
            "recent graduate"

        ]

    ):

        experience["years"] = 0

        experience["months"] = 0

        experience["raw_value"] = "fresher"

    return experience


# =====================================================
# EXTRACT SALARY
# =====================================================

def extract_salary(text):

    text = normalize_text(text)

    salary = {

        "amount": None,

        "currency": "INR",

        "unit": None,

        "raw_value": None

    }

    # Examples:
    # 6 LPA
    # 6.5 lakh
    # 50000 per month
    # 50k monthly

    lpa_pattern = re.search(

        r"(\d+(?:\.\d+)?)\s*"
        r"(?:lpa|lakhs?|lakh\s+per\s+annum)",

        text

    )

    if lpa_pattern:

        amount = float(

            lpa_pattern.group(1)

        )

        salary["amount"] = amount

        salary["unit"] = "LPA"

        salary["raw_value"] = (
            lpa_pattern.group(0)
        )

        return salary

    monthly_pattern = re.search(

        r"(?:₹|rs\.?|inr)?\s*"
        r"(\d+(?:,\d+)?)\s*"
        r"(?:per month|monthly)",

        text

    )

    if monthly_pattern:

        amount = int(

            monthly_pattern
            .group(1)
            .replace(",", "")

        )

        salary["amount"] = amount

        salary["unit"] = "monthly"

        salary["raw_value"] = (
            monthly_pattern.group(0)
        )

        return salary

    return salary


# =====================================================
# EXTRACT AVAILABILITY
# =====================================================

def extract_availability(text):

    text = normalize_text(text)

    availability = {

        "available": None,

        "start_time": None,

        "immediate": False

    }

    immediate_words = [

        "immediately",
        "right away",
        "can join immediately",
        "available immediately"

    ]

    for phrase in immediate_words:

        if phrase in text:

            availability["available"] = True

            availability["immediate"] = True

            availability["start_time"] = "immediate"

            return availability

    if any(

        phrase in text

        for phrase in [

            "available",
            "can join",
            "ready to join"

        ]

    ):

        availability["available"] = True

    # Days

    day_match = re.search(

        r"(\d+)\s*days?",

        text

    )

    if day_match:

        availability["start_time"] = (

            f"{day_match.group(1)} days"

        )

    # Weeks

    week_match = re.search(

        r"(\d+)\s*weeks?",

        text

    )

    if week_match:

        availability["start_time"] = (

            f"{week_match.group(1)} weeks"

        )

    # Months

    month_match = re.search(

        r"(\d+)\s*months?",

        text

    )

    if month_match:

        availability["start_time"] = (

            f"{month_match.group(1)} months"

        )

    return availability


# =====================================================
# EXTRACT LOCATION
# =====================================================

def extract_location(text):

    text = normalize_text(text)

    common_locations = [

        "trivandrum",
        "thiruvananthapuram",
        "kochi",
        "ernakulam",
        "calicut",
        "kozhikode",
        "bangalore",
        "bengaluru",
        "chennai",
        "hyderabad",
        "mumbai",
        "delhi",
        "pune"

    ]

    found = []

    for location in common_locations:

        if location in text:

            found.append(location)

    return list(set(found))


# =====================================================
# INTENT CLASSIFICATION
# =====================================================

def classify_intent(

    answer,

    expected_category=None

):

    text = normalize_text(answer)

    # Empty answer

    if not text:

        return {

            "intent": "missing",

            "confidence": 1.0

        }

    # Very short answer

    if len(text.split()) <= 2:

        return {

            "intent": "vague",

            "confidence": 0.80

        }

    scores = {

        intent: 0

        for intent in INTENT_KEYWORDS

    }

    for intent, keywords in INTENT_KEYWORDS.items():

        for keyword in keywords:

            if keyword in text:

                scores[intent] += 1

    best_intent = max(

        scores,

        key=scores.get

    )

    best_score = scores[best_intent]

    # Expected question category gets priority

    if expected_category:

        expected = normalize_text(

            expected_category

        )

        category_map = {

            "introduction":
                "introduction",

            "education":
                "education",

            "experience":
                "experience",

            "skills":
                "skills",

            "availability":
                "availability",

            "salary":
                "salary",

            "location":
                "location",

            "notice period":
                "notice_period",

            "motivation":
                "motivation"

        }

        expected_intent = category_map.get(

            expected

        )

        if expected_intent:

            if scores.get(

                expected_intent,

                0

            ) > 0:

                best_intent = expected_intent

                best_score = scores[

                    expected_intent

                ]

    if best_score == 0:

        return {

            "intent": "off_topic",

            "confidence": 0.75

        }

    confidence = min(

        0.95,

        0.50 + (

            best_score * 0.10

        )

    )

    return {

        "intent": best_intent,

        "confidence": round(

            confidence,

            2

        )

    }


# =====================================================
# DETECT VAGUE ANSWER
# =====================================================

def detect_vague_answer(text):

    text = normalize_text(text)

    if not text:

        return True

    vague_phrases = [

        "i don't know",

        "not sure",

        "maybe",

        "probably",

        "anything",

        "whatever",

        "i guess",

        "no idea",

        "nothing"

    ]

    for phrase in vague_phrases:

        if phrase in text:

            return True

    if len(text.split()) <= 2:

        return True

    return False


# =====================================================
# DETECT OFF-TOPIC ANSWER
# =====================================================

def detect_off_topic(

    answer,

    expected_category

):

    classification = classify_intent(

        answer,

        expected_category

    )

    return classification["intent"] == "off_topic"


# =====================================================
# DETECT MISSING INFORMATION
# =====================================================

def detect_missing_information(

    answer,

    expected_category

):

    text = normalize_text(answer)

    if not text:

        return {

            "missing": True,

            "reason": "No answer provided"

        }

    if expected_category.lower() == "skills":

        if not extract_skills(text):

            return {

                "missing": True,

                "reason":
                    "No recognizable skills found"

            }

    if expected_category.lower() == "experience":

        experience = extract_experience(text)

        if experience["years"] is None:

            return {

                "missing": True,

                "reason":
                    "Experience duration not found"

            }

    if expected_category.lower() == "salary":

        salary = extract_salary(text)

        if salary["amount"] is None:

            return {

                "missing": True,

                "reason":
                    "Salary expectation not found"

            }

    return {

        "missing": False,

        "reason": None

    }


# =====================================================
# BUILD SEMANTIC ANSWER OBJECT
# =====================================================

def understand_answer(

    answer,

    question_id,

    question,

    expected_category

):

    classification = classify_intent(

        answer,

        expected_category

    )

    skills = extract_skills(answer)

    experience = extract_experience(answer)

    salary = extract_salary(answer)

    availability = extract_availability(answer)

    location = extract_location(answer)

    vague = detect_vague_answer(answer)

    off_topic = detect_off_topic(

        answer,

        expected_category

    )

    missing = detect_missing_information(

        answer,

        expected_category

    )

    semantic_object = {

        "question_id":

            question_id,

        "question":

            question,

        "answer": {

            "raw_text":

                answer,

            "normalized_text":

                normalize_text(answer)

        },

        "intent": {

            "name":

                classification["intent"],

            "confidence":

                classification["confidence"]

        },

        "entities": {

            "skills":

                skills,

            "experience":

                experience,

            "salary":

                salary,

            "availability":

                availability,

            "location":

                location

        },

        "quality": {

            "off_topic":

                off_topic,

            "vague":

                vague,

            "missing_information":

                missing["missing"],

            "missing_reason":

                missing["reason"]

        },

        "timestamp":

            datetime.utcnow().isoformat()

    }

    return semantic_object


# =====================================================
# SAVE ANSWER OBJECT
# =====================================================

def save_answer_object(

    answer_object,

    filename="ats_engine/answer_result.json"

):

    with open(

        filename,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            answer_object,

            file,

            indent=4,

            ensure_ascii=False

        )

    return filename


# =====================================================
# TEST DATA
# =====================================================

TEST_CASES = [

    {

        "question_id": "SKILL_001",

        "question":
            "What are your strongest technical skills?",

        "category": "Skills",

        "answer":
            "I am strongest in Python, Django, React and SQL."

    },

    {

        "question_id": "EXP_001",

        "question":
            "How many years of experience do you have?",

        "category": "Experience",

        "answer":
            "I have three years of experience in software development."

    },

    {

        "question_id": "SALARY_001",

        "question":
            "What are your salary expectations?",

        "category": "Salary",

        "answer":
            "I am expecting around 6 LPA."

    },

    {

        "question_id": "NOTICE_001",

        "question":
            "What is your notice period?",

        "category": "Notice Period",

        "answer":
            "I can join immediately."

    },

    {

        "question_id": "SKILL_001",

        "question":
            "What are your strongest technical skills?",

        "category": "Skills",

        "answer":
            "I watched a movie yesterday."

    },

    {

        "question_id": "EXP_001",

        "question":
            "How many years of experience do you have?",

        "category": "Experience",

        "answer":
            "I don't know."

    }

]


# =====================================================
# RUN TESTS
# =====================================================

def run_tests():

    results = []

    for test in TEST_CASES:

        result = understand_answer(

            answer=test["answer"],

            question_id=test["question_id"],

            question=test["question"],

            expected_category=test["category"]

        )

        results.append(result)

    report = {

        "report_name":
            "Answer Understanding Engine Test Report",

        "total_tests":
            len(results),

        "results":
            results

    }

    with open(

        "answer_understanding_test.json",

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            report,

            file,

            indent=4,

            ensure_ascii=False

        )

    return report


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    result = understand_answer(

        answer=(
            "I have three years of experience "
            "working with Python and Django. "
            "I am expecting around 6 LPA "
            "and I can join immediately."
        ),

        question_id="EXP_001",

        question=(
            "Tell me about your experience."
        ),

        expected_category="Experience"

    )

    print(

        json.dumps(

            result,

            indent=4,

            ensure_ascii=False

        )

    )

    print(

        "\nRunning tests...\n"

    )

    report = run_tests()

    print(

        json.dumps(

            report,

            indent=4,

            ensure_ascii=False

        )

    )