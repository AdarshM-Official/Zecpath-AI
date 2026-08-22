import json

# ==========================================
# Dynamic Weight Configuration
# ==========================================

ROLE_WEIGHTS = {

    "Software Engineer": {
        "skills": 35,
        "experience": 30,
        "education": 15,
        "semantic": 20
    },

    "Data Scientist": {
        "skills": 30,
        "experience": 25,
        "education": 20,
        "semantic": 25
    },

    "Frontend Developer": {
        "skills": 40,
        "experience": 25,
        "education": 10,
        "semantic": 25
    },

    "Default": {
        "skills": 30,
        "experience": 30,
        "education": 20,
        "semantic": 20
    }
}


# ==========================================
# Safe Score Extraction
# ==========================================

def safe_score(value):

    if value is None:
        return 0

    try:
        return float(value)

    except:
        return 0


# ==========================================
# ATS Score Generator
# ==========================================

def generate_ats_score(candidate_id,
                       role,
                       skill_score,
                       experience_score,
                       education_score,
                       semantic_score):

    weights = ROLE_WEIGHTS.get(role,
                               ROLE_WEIGHTS["Default"])

    skill_score = safe_score(skill_score)

    experience_score = safe_score(experience_score)

    education_score = safe_score(education_score)

    semantic_score = safe_score(semantic_score)

    final_score = (

        skill_score *
        weights["skills"]

        +

        experience_score *
        weights["experience"]

        +

        education_score *
        weights["education"]

        +

        semantic_score *
        weights["semantic"]

    ) / 100

    explanation = []

    explanation.append(

        f"Skill Match : {skill_score:.2f} × {weights['skills']}%"
    )

    explanation.append(

        f"Experience : {experience_score:.2f} × {weights['experience']}%"
    )

    explanation.append(

        f"Education : {education_score:.2f} × {weights['education']}%"
    )

    explanation.append(

        f"Semantic Match : {semantic_score:.2f} × {weights['semantic']}%"
    )

    if final_score >= 0.85:

        recommendation = "Excellent Candidate"

    elif final_score >= 0.70:

        recommendation = "Strong Candidate"

    elif final_score >= 0.50:

        recommendation = "Average Candidate"

    else:

        recommendation = "Needs Improvement"

    result = {

        "candidate_id": candidate_id,

        "job_role": role,

        "weights": weights,

        "scores": {

            "skill_match": skill_score,

            "experience_relevance": experience_score,

            "education_alignment": education_score,

            "semantic_similarity": semantic_score

        },

        "final_ats_score": round(final_score * 100, 2),

        "recommendation": recommendation,

        "explanation": explanation

    }

    with open("ats_engine/ats_score_output.json", "w") as file:

        json.dump(result,
                  file,
                  indent=4)

    return result


# ==========================================
# Example
# ==========================================

if __name__ == "__main__":

    output = generate_ats_score(

        candidate_id="C123",

        role="Software Engineer",

        skill_score=0.90,

        experience_score=0.80,

        education_score=0.85,

        semantic_score=0.88

    )

    print(json.dumps(output, indent=4))