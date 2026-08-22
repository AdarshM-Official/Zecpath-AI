import json
import os
from datetime import datetime


# =====================================================
# HR DECISION THRESHOLDS
# =====================================================

THRESHOLDS = {

    "strong_pass": 80,

    "pass": 65,

    "review": 50
}


# =====================================================
# SIMULATED CANDIDATES
# =====================================================

TEST_CANDIDATES = [

    # =================================================
    # CONFIDENT CANDIDATE
    # =================================================

    {
        "candidate_id": "C101",

        "candidate_type": "Confident",

        "hr_score": 88,

        "communication_score": 91,

        "confidence_score": 90,

        "aptitude_score": 86,

        "consistency_score": 95,

        "manual_decision": "Pass",

        "manual_notes":
            "Strong communication, relevant answers "
            "and good problem-solving ability."
    },


    # =================================================
    # HESITANT CANDIDATE
    # =================================================

    {
        "candidate_id": "C102",

        "candidate_type": "Hesitant",

        "hr_score": 76,

        "communication_score": 68,

        "confidence_score": 52,

        "aptitude_score": 79,

        "consistency_score": 90,

        "manual_decision": "Pass",

        "manual_notes":
            "Candidate was nervous but provided relevant "
            "and technically sound responses."
    },


    # =================================================
    # INEXPERIENCED CANDIDATE
    # =================================================

    {
        "candidate_id": "C103",

        "candidate_type": "Inexperienced",

        "hr_score": 62,

        "communication_score": 72,

        "confidence_score": 70,

        "aptitude_score": 74,

        "consistency_score": 88,

        "manual_decision": "Review",

        "manual_notes":
            "Good potential but limited practical experience."
    },


    # =================================================
    # OVERQUALIFIED CANDIDATE
    # =================================================

    {
        "candidate_id": "C104",

        "candidate_type": "Overqualified",

        "hr_score": 82,

        "communication_score": 89,

        "confidence_score": 92,

        "aptitude_score": 90,

        "consistency_score": 94,

        "manual_decision": "Review",

        "manual_notes":
            "Strong candidate but role expectations and "
            "long-term fit require recruiter review."
    }

]


# =====================================================
# NORMALIZE SCORE
# =====================================================

def normalize_score(score):

    try:
        score = float(score)

    except (ValueError, TypeError):
        return 0

    return round(
        max(
            0,
            min(
                100,
                score
            )
        ),
        2
    )


# =====================================================
# CALCULATE SIMULATED AI SCORE
# =====================================================

def calculate_ai_score(candidate):

    # Confidence receives a lower weight so hesitation
    # does not dominate the candidate evaluation.

    weights = {

        "hr_score": 0.45,

        "communication_score": 0.20,

        "confidence_score": 0.10,

        "aptitude_score": 0.15,

        "consistency_score": 0.10
    }

    final_score = (

        candidate["hr_score"]
        * weights["hr_score"]

        +

        candidate["communication_score"]
        * weights["communication_score"]

        +

        candidate["confidence_score"]
        * weights["confidence_score"]

        +

        candidate["aptitude_score"]
        * weights["aptitude_score"]

        +

        candidate["consistency_score"]
        * weights["consistency_score"]
    )

    return (
        normalize_score(
            final_score
        ),
        weights
    )


# =====================================================
# AI DECISION
# =====================================================

def determine_ai_decision(
    score
):

    if score >= THRESHOLDS[
        "strong_pass"
    ]:

        return "Pass"

    elif score >= THRESHOLDS[
        "pass"
    ]:

        return "Pass"

    elif score >= THRESHOLDS[
        "review"
    ]:

        return "Review"

    return "Reject"


# =====================================================
# OVERQUALIFIED SAFEGUARD
# =====================================================

def apply_candidate_type_rules(
    candidate,
    ai_decision
):

    # Overqualification is not an automatic rejection.
    # Route to recruiter review for expectations/fit.

    if (
        candidate[
            "candidate_type"
        ]
        == "Overqualified"
    ):

        return "Review"

    return ai_decision


# =====================================================
# COMPARE AI VS MANUAL
# =====================================================

def compare_decisions(
    ai_decision,
    manual_decision
):

    return (
        ai_decision.lower()
        ==
        manual_decision.lower()
    )


# =====================================================
# IDENTIFY SCORING INCONSISTENCY
# =====================================================

def identify_inconsistency(
    candidate,
    ai_score,
    ai_decision
):

    issues = []

    # Hesitation should not dominate evaluation

    if (
        candidate[
            "candidate_type"
        ]
        == "Hesitant"

        and

        candidate[
            "confidence_score"
        ] < 60

        and

        candidate[
            "hr_score"
        ] >= 70

        and

        ai_decision == "Reject"
    ):

        issues.append(
            "Candidate may have been over-penalized "
            "for hesitation despite strong answer quality."
        )

    # Strong score but manual review

    if (
        ai_score >= 80

        and

        candidate[
            "manual_decision"
        ] == "Review"
    ):

        issues.append(
            "High AI score conflicts with manual review. "
            "Role expectations or contextual factors may "
            "require recruiter judgment."
        )

    # Low experience but strong aptitude

    if (
        candidate[
            "candidate_type"
        ] == "Inexperienced"

        and

        candidate[
            "aptitude_score"
        ] >= 70
    ):

        issues.append(
            "Candidate has limited experience but shows "
            "good aptitude; avoid automatic rejection."
        )

    return issues


# =====================================================
# SIMULATE SINGLE INTERVIEW
# =====================================================

def simulate_interview(
    candidate
):

    ai_score, weights = (
        calculate_ai_score(
            candidate
        )
    )

    initial_decision = (
        determine_ai_decision(
            ai_score
        )
    )

    final_decision = (
        apply_candidate_type_rules(

            candidate,

            initial_decision
        )
    )

    match = compare_decisions(

        final_decision,

        candidate[
            "manual_decision"
        ]
    )

    inconsistencies = (
        identify_inconsistency(

            candidate,

            ai_score,

            final_decision
        )
    )

    return {

        "candidate_id":
            candidate[
                "candidate_id"
            ],

        "candidate_type":
            candidate[
                "candidate_type"
            ],

        "component_scores": {

            "hr_score":
                candidate[
                    "hr_score"
                ],

            "communication":
                candidate[
                    "communication_score"
                ],

            "confidence":
                candidate[
                    "confidence_score"
                ],

            "aptitude":
                candidate[
                    "aptitude_score"
                ],

            "consistency":
                candidate[
                    "consistency_score"
                ]
        },

        "weights":
            weights,

        "final_ai_score":
            ai_score,

        "ai_decision":
            final_decision,

        "manual_decision":
            candidate[
                "manual_decision"
            ],

        "manual_notes":
            candidate[
                "manual_notes"
            ],

        "decision_match":
            match,

        "scoring_inconsistencies":
            inconsistencies
    }


# =====================================================
# ACCURACY CALCULATION
# =====================================================

def calculate_accuracy(
    results
):

    if not results:
        return 0

    correct = sum(

        1

        for result in results

        if result[
            "decision_match"
        ]
    )

    return round(

        (
            correct
            /
            len(results)
        )
        * 100,

        2
    )


# =====================================================
# MISMATCH ANALYSIS
# =====================================================

def get_mismatch_cases(
    results
):

    return [

        result

        for result in results

        if not result[
            "decision_match"
        ]
    ]


# =====================================================
# FALSE REJECTION ANALYSIS
# =====================================================

def calculate_false_rejections(
    results
):

    false_rejections = []

    for result in results:

        if (
            result[
                "ai_decision"
            ] == "Reject"

            and

            result[
                "manual_decision"
            ] in [
                "Pass",
                "Review"
            ]
        ):

            false_rejections.append(
                result[
                    "candidate_id"
                ]
            )

    return {

        "count":
            len(
                false_rejections
            ),

        "candidate_ids":
            false_rejections
    }


# =====================================================
# IMPROVEMENT RECOMMENDATIONS
# =====================================================

def generate_improvement_recommendations(
    results
):

    recommendations = [

        {
            "priority": "High",

            "recommendation":
                "Keep substantive HR answer quality as the "
                "largest component of the final score."
        },

        {
            "priority": "High",

            "recommendation":
                "Do not automatically reject candidates "
                "because of hesitation or low confidence signals."
        },

        {
            "priority": "High",

            "recommendation":
                "Route overqualified candidates to recruiter "
                "review rather than automatically passing or rejecting them."
        },

        {
            "priority": "Medium",

            "recommendation":
                "Use aptitude and project performance to "
                "support evaluation of inexperienced candidates."
        },

        {
            "priority": "Medium",

            "recommendation":
                "Improve cross-answer contradiction detection "
                "using structured candidate claims."
        },

        {
            "priority": "Medium",

            "recommendation":
                "Validate HR scoring thresholds against a "
                "larger recruiter-reviewed interview dataset."
        },

        {
            "priority": "Low",

            "recommendation":
                "Add more candidate profiles and multilingual "
                "interview simulations."
        }
    ]

    return recommendations


# =====================================================
# GENERATE TEST REPORT
# =====================================================

def generate_test_report():

    results = []

    for candidate in TEST_CANDIDATES:

        result = simulate_interview(
            candidate
        )

        results.append(
            result
        )

    accuracy = (
        calculate_accuracy(
            results
        )
    )

    mismatches = (
        get_mismatch_cases(
            results
        )
    )

    false_rejections = (
        calculate_false_rejections(
            results
        )
    )

    inconsistency_count = sum(

        len(
            result[
                "scoring_inconsistencies"
            ]
        )

        for result in results
    )

    report = {

        "report_name":
            "Zecpath AI HR Interview Simulation Report",

        "generated_at":
            datetime.utcnow().isoformat(),

        "testing_summary": {

            "total_interviews":
                len(
                    results
                ),

            "candidate_types": [
                "Confident",
                "Hesitant",
                "Inexperienced",
                "Overqualified"
            ],

            "ai_vs_manual_accuracy":
                accuracy,

            "decision_mismatches":
                len(
                    mismatches
                ),

            "scoring_inconsistencies":
                inconsistency_count
        },

        "false_rejection_analysis":
            false_rejections,

        "interview_results":
            results,

        "mismatch_cases":
            mismatches,

        "improvement_recommendations":
            generate_improvement_recommendations(
                results
            )
    }

    return report


# =====================================================
# SAVE REPORT
# =====================================================

def save_report(
    report,
    filename="tests/hr_interview_test_report.json"
):

    directory = os.path.dirname(
        filename
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    return filename


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print(
        "=" * 65
    )

    print(
        "Zecpath AI - HR Interview Simulation"
    )

    print(
        "=" * 65
    )

    report = (
        generate_test_report()
    )

    filename = save_report(
        report
    )

    summary = report[
        "testing_summary"
    ]

    print(
        "\nTotal Interviews:",
        summary[
            "total_interviews"
        ]
    )

    print(
        "AI vs Manual Accuracy:",
        f"{summary['ai_vs_manual_accuracy']}%"
    )

    print(
        "Decision Mismatches:",
        summary[
            "decision_mismatches"
        ]
    )

    print(
        "Scoring Inconsistencies:",
        summary[
            "scoring_inconsistencies"
        ]
    )

    print(
        "False Rejections:",
        report[
            "false_rejection_analysis"
        ][
            "count"
        ]
    )

    print(
        "\nCandidate Results"
    )

    print(
        "-" * 65
    )

    for result in report[
        "interview_results"
    ]:

        print(
            f"{result['candidate_id']} | "
            f"{result['candidate_type']} | "
            f"Score: {result['final_ai_score']} | "
            f"AI: {result['ai_decision']} | "
            f"Human: {result['manual_decision']} | "
            f"Match: {result['decision_match']}"
        )

    print(
        "\nReport saved to:",
        filename
    )