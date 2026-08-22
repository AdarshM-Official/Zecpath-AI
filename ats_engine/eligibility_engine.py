import json
import os
from utils.config_loader import load_config

# Load configuration once
CONFIG = load_config()
OVERALL_THRESHOLDS = CONFIG.get('overall_score_thresholds', {'strong': 80, 'weak': 60})
WEAK_THRESHOLD = OVERALL_THRESHOLDS.get('weak', 60)
STRONG_THRESHOLD = OVERALL_THRESHOLDS.get('strong', 80)

# =====================================================
# Job Role Eligibility Configuration
# =====================================================

JOB_RULES = {

    "Software Engineer": {

        "minimum_ats_score": 70,

        "mandatory_skills": [
            "python",
            "django"
        ],

        "minimum_experience": 1,

        "maximum_experience": 5,

        "allowed_locations": [
            "kerala",
            "bangalore",
            "hyderabad",
            "remote"
        ],

        "review_score": 60
    },


    "Data Scientist": {

        "minimum_ats_score": 75,

        "mandatory_skills": [
            "python",
            "machine learning"
        ],

        "minimum_experience": 1,

        "maximum_experience": 6,

        "allowed_locations": [
            "kerala",
            "bangalore",
            "remote"
        ],

        "review_score": 65
    },


    "Frontend Developer": {

        "minimum_ats_score": 70,

        "mandatory_skills": [
            "javascript",
            "react"
        ],

        "minimum_experience": 1,

        "maximum_experience": 5,

        "allowed_locations": [
            "kerala",
            "bangalore",
            "remote"
        ],

        "review_score": 60
    },


    "Default": {

        "minimum_ats_score": 70,

        "mandatory_skills": [],

        "minimum_experience": 0,

        "maximum_experience": 100,

        "allowed_locations": [],

        "review_score": 60
    }
}


# =====================================================
# Normalize Text
# =====================================================

def normalize(value):

    if value is None:
        return ""

    return str(value).strip().lower()


# =====================================================
# Check Mandatory Skills
# =====================================================

def check_mandatory_skills(candidate_skills, required_skills):

    candidate_skills = [

        normalize(skill)

        for skill in candidate_skills

    ]

    required_skills = [

        normalize(skill)

        for skill in required_skills

    ]

    missing_skills = [

        skill

        for skill in required_skills

        if skill not in candidate_skills

    ]

    matched_skills = [

        skill

        for skill in required_skills

        if skill in candidate_skills

    ]

    return matched_skills, missing_skills


# =====================================================
# Check Experience
# =====================================================

def check_experience(

    experience,

    minimum_experience,

    maximum_experience

):

    try:

        experience = float(experience)

    except (ValueError, TypeError):

        return False

    return (

        minimum_experience

        <= experience

        <= maximum_experience

    )


# =====================================================
# Check Location
# =====================================================

def check_location(

    candidate_location,

    allowed_locations

):

    # Empty allowed_locations means location
    # is not a restriction.

    if not allowed_locations:

        return True

    candidate_location = normalize(
        candidate_location
    )

    allowed_locations = [

        normalize(location)

        for location in allowed_locations

    ]

    return candidate_location in allowed_locations


# =====================================================
# Eligibility Decision
# =====================================================

def determine_status(

    ats_score,

    skills_valid,

    experience_valid,

    location_valid,

    minimum_score,

    review_score

):

    # -----------------------------------------
    # Automatic Rejection
    # -----------------------------------------

    if not skills_valid:

        return "Rejected"

    if not experience_valid:

        return "Rejected"

    if not location_valid:

        return "Rejected"

    if ats_score < review_score:

        return "Rejected"

    # -----------------------------------------
    # Review Zone
    # -----------------------------------------

    if ats_score < minimum_score:

        return "Review"

    # -----------------------------------------
    # Eligible
    # -----------------------------------------

    return "Eligible"


# =====================================================
# Main Eligibility Engine
# =====================================================

def evaluate_candidate(

    candidate,

    job_role

):

    rules = JOB_RULES.get(

        job_role,

        JOB_RULES["Default"]

    )

    candidate_id = candidate.get(
        "candidate_id",
        "UNKNOWN"
    )

    candidate_name = candidate.get(
        "candidate_name",
        "Unknown"
    )

    ats_score = candidate.get(
        "ats_score",
        0
    )

    candidate_skills = candidate.get(
        "skills",
        []
    )

    experience = candidate.get(
        "experience",
        0
    )

    location = candidate.get(
        "location",
        ""
    )

    # -----------------------------------------
    # Skill Evaluation
    # -----------------------------------------

    matched_skills, missing_skills = (

        check_mandatory_skills(

            candidate_skills,

            rules["mandatory_skills"]

        )

    )

    skills_valid = len(missing_skills) == 0

    # -----------------------------------------
    # Experience Evaluation
    # -----------------------------------------

    experience_valid = check_experience(

        experience,

        rules["minimum_experience"],

        rules["maximum_experience"]

    )

    # -----------------------------------------
    # Location Evaluation
    # -----------------------------------------

    location_valid = check_location(

        location,

        rules["allowed_locations"]

    )

    # -----------------------------------------
    # Final Decision
    # -----------------------------------------

    status = determine_status(

        ats_score,

        skills_valid,

        experience_valid,

        location_valid,

        rules["minimum_ats_score"],

        rules["review_score"]

    )

    # -----------------------------------------
    # Reasons
    # -----------------------------------------

    reasons = []

    if missing_skills:

        reasons.append(

            "Missing mandatory skills: "

            + ", ".join(missing_skills)

        )

    if not experience_valid:

        reasons.append(

            "Experience is outside the required range"

        )

    if not location_valid:

        reasons.append(

            "Location is not within the allowed locations"

        )

    if (

        ats_score < rules["minimum_ats_score"]

        and ats_score >= rules["review_score"]

    ):

        reasons.append(

            "ATS score is below the eligibility cutoff"

        )

    if not reasons:

        reasons.append(

            "Candidate satisfies all eligibility requirements"

        )

    # -----------------------------------------
    # Structured Result
    # -----------------------------------------

    result = {

        "candidate_id": candidate_id,

        "candidate_name": candidate_name,

        "job_role": job_role,

        "eligibility": {

            "status": status,

            "ats_score": ats_score,

            "minimum_ats_score":
                rules["minimum_ats_score"],

            "mandatory_skills": {

                "required":
                    rules["mandatory_skills"],

                "matched":
                    matched_skills,

                "missing":
                    missing_skills

            },

            "experience": {

                "candidate":
                    experience,

                "minimum":
                    rules["minimum_experience"],

                "maximum":
                    rules["maximum_experience"],

                "valid":
                    experience_valid

            },

            "location": {

                "candidate":
                    location,

                "allowed":
                    rules["allowed_locations"],

                "valid":
                    location_valid

            },

            "reasons":
                reasons

        }

    }

    return result


# =====================================================
# Evaluate Multiple Candidates
# =====================================================

def evaluate_candidates(

    candidates,

    job_role

):

    results = []

    for candidate in candidates:

        result = evaluate_candidate(

            candidate,

            job_role

        )

        results.append(result)

    output = {

        "job_role": job_role,

        "total_candidates":
            len(results),

        "summary": {

            "eligible": len([

                r for r in results

                if r["eligibility"]["status"]
                == "Eligible"

            ]),

            "review": len([

                r for r in results

                if r["eligibility"]["status"]
                == "Review"

            ]),

            "rejected": len([

                r for r in results

                if r["eligibility"]["status"]
                == "Rejected"

            ])

        },

        "candidates": results

    }

    with open(

        "ats_engine/eligibility_output.json",

        "w"

    ) as file:

        json.dump(

            output,

            file,

            indent=4

        )

    return output


# =====================================================
# Example
# =====================================================

if __name__ == "__main__":

    candidates = [

        {

            "candidate_id": "C101",

            "candidate_name": "Rahul",

            "ats_score": 88,

            "skills": [

                "Python",

                "Django",

                "React"

            ],

            "experience": 2,

            "location": "Kerala"

        },


        {

            "candidate_id": "C102",

            "candidate_name": "Anjali",

            "ats_score": 66,

            "skills": [

                "Python",

                "Django"

            ],

            "experience": 2,

            "location": "Kerala"

        },


        {

            "candidate_id": "C103",

            "candidate_name": "John",

            "ats_score": 85,

            "skills": [

                "Java",

                "Spring"

            ],

            "experience": 3,

            "location": "Kerala"

        },


        {

            "candidate_id": "C104",

            "candidate_name": "Priya",

            "ats_score": 90,

            "skills": [

                "Python",

                "Django"

            ],

            "experience": 7,

            "location": "Kerala"

        }

    ]


    result = evaluate_candidates(

        candidates,

        "Software Engineer"

    )


    print(

        json.dumps(

            result,

            indent=4

        )

    )