import json

# ==========================================
# Sample Test Cases
# ==========================================

TEST_CASES = [

    {
        "candidate_id": "C101",
        "role": "Software Engineer",
        "profile": "Tech - Fresher",
        "manual_decision": "Shortlisted",
        "ai_decision": "Shortlisted"
    },

    {
        "candidate_id": "C102",
        "role": "Data Scientist",
        "profile": "Tech - Senior",
        "manual_decision": "Shortlisted",
        "ai_decision": "Review"
    },

    {
        "candidate_id": "C103",
        "role": "HR Executive",
        "profile": "Non-Tech",
        "manual_decision": "Review",
        "ai_decision": "Review"
    },

    {
        "candidate_id": "C104",
        "role": "Marketing Executive",
        "profile": "Non-Tech",
        "manual_decision": "Rejected",
        "ai_decision": "Rejected"
    },

    {
        "candidate_id": "C105",
        "role": "Backend Developer",
        "profile": "Tech - Senior",
        "manual_decision": "Shortlisted",
        "ai_decision": "Shortlisted"
    },

    {
        "candidate_id": "C106",
        "role": "Software Engineer",
        "profile": "Tech - Fresher",
        "manual_decision": "Rejected",
        "ai_decision": "Review"
    }

]

# ==========================================
# Accuracy Metrics
# ==========================================

def calculate_metrics(test_cases):

    total = len(test_cases)

    correct = 0

    false_positive = 0

    false_negative = 0

    mismatches = []

    for case in test_cases:

        if case["manual_decision"] == case["ai_decision"]:

            correct += 1

        else:

            mismatches.append(case)

            if case["ai_decision"] == "Shortlisted":

                false_positive += 1

            else:

                false_negative += 1

    accuracy = round(correct / total, 2)

    precision = round(

        correct /

        (correct + false_positive)

        if (correct + false_positive) > 0

        else 0,

        2

    )

    recall = round(

        correct /

        (correct + false_negative)

        if (correct + false_negative) > 0

        else 0,

        2

    )

    return accuracy, precision, recall, mismatches


# ==========================================
# ATS Testing Report
# ==========================================

def generate_testing_report():

    accuracy, precision, recall, mismatches = calculate_metrics(TEST_CASES)

    report = {

        "testing_summary": {

            "total_test_cases": len(TEST_CASES),

            "tech_roles": 4,

            "non_tech_roles": 2,

            "fresher_profiles": 2,

            "senior_profiles": 2

        },

        "accuracy_metrics": {

            "accuracy": accuracy,

            "precision": precision,

            "recall": recall

        },

        "mismatch_cases": mismatches,

        "improvement_backlog": [

            "Improve semantic similarity for non-technical roles.",

            "Enhance experience relevance scoring.",

            "Expand skill dictionary for niche technologies.",

            "Improve handling of fresher resumes with academic projects.",

            "Fine-tune ATS scoring thresholds for different job roles."

        ]

    }

    with open("ats_engine/ats_testing_report.json", "w") as file:

        json.dump(report, file, indent=4)

    return report


# ==========================================
# Example
# ==========================================

if __name__ == "__main__":

    report = generate_testing_report()

    print(json.dumps(report, indent=4))