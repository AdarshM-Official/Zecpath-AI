import re
import json

# ==========================================
# Personal Information Patterns
# ==========================================

EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
PHONE_PATTERN = r'\b(?:\+91[- ]?)?[6-9]\d{9}\b'
DOB_PATTERN = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'

# ==========================================
# Resume Normalization
# ==========================================

def normalize_resume(text):

    text = text.lower()

    text = re.sub(r'\s+', ' ', text)

    text = text.strip()

    return text


# ==========================================
# Mask Personal Information
# ==========================================

def mask_personal_info(text):

    text = re.sub(EMAIL_PATTERN, "[EMAIL]", text)

    text = re.sub(PHONE_PATTERN, "[PHONE]", text)

    text = re.sub(DOB_PATTERN, "[DOB]", text)

    return text


# ==========================================
# Keyword Normalization
# ==========================================

def normalize_keywords(text):

    replacements = {

        "reactjs": "react",

        "nodejs": "node",

        "js": "javascript",

        "py": "python",

        "ml": "machine learning"
    }

    for old, new in replacements.items():

        text = text.replace(old, new)

    return text


# ==========================================
# Score Normalization
# ==========================================

def normalize_score(score):

    if score < 0:
        score = 0

    if score > 100:
        score = 100

    return round(score, 2)


# ==========================================
# Reduce Keyword Dependency
# ==========================================

def adjusted_score(keyword_score,
                   semantic_score):

    return round(

        keyword_score * 0.40 +

        semantic_score * 0.60,

        2
    )


# ==========================================
# Bias Indicator Evaluation
# ==========================================

def evaluate_bias(text):

    indicators = []

    lower = text.lower()

    if "male" in lower or "female" in lower:

        indicators.append("Gender Mention")

    if "married" in lower:

        indicators.append("Marital Status")

    if "date of birth" in lower:

        indicators.append("Date of Birth")

    if "age" in lower:

        indicators.append("Age Mention")

    return indicators


# ==========================================
# Fairness Engine
# ==========================================

def fairness_engine(candidate_id,
                    resume_text,
                    keyword_score,
                    semantic_score):

    masked = mask_personal_info(resume_text)

    normalized = normalize_resume(masked)

    normalized = normalize_keywords(normalized)

    final_score = adjusted_score(

        keyword_score,

        semantic_score

    )

    final_score = normalize_score(final_score)

    bias = evaluate_bias(resume_text)

    output = {

        "candidate_id": candidate_id,

        "normalized_resume": normalized,

        "normalized_score": final_score,

        "bias_indicators": bias,

        "fairness_status":

            "Fair"

            if len(bias) == 0

            else "Review Required"

    }

    with open(

        "ats_engine/fairness_output.json",

        "w"

    ) as file:

        json.dump(output, file, indent=4)

    return output


# ==========================================
# Example
# ==========================================

if __name__ == "__main__":

    resume = """

    John Doe

    Email: john@gmail.com

    Phone: 9876543210

    Date of Birth: 12/05/2002

    Male

    Python Developer with ReactJS

    Machine Learning projects

    """

    result = fairness_engine(

        candidate_id="C123",

        resume_text=resume,

        keyword_score=82,

        semantic_score=90

    )

    print(json.dumps(result, indent=4))