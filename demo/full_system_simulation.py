import json
import os
import time
from datetime import datetime


# =====================================================
# SAMPLE CANDIDATE DATA
# =====================================================

CANDIDATES = [

    {
        "candidate_id": "C001",
        "name": "Candidate A",
        "role": "python_developer",
        "profile_type": "FRESHER",

        "resume_text": (
            "Python Django SQL REST API developer with "
            "academic project experience."
        ),

        "scores": {
            "ats": 82,
            "screening": 78,
            "hr_interview": 80,
            "technical_interview": 85,
            "machine_test": 83
        },

        "human_decision": "SELECTED"
    },

    {
        "candidate_id": "C002",
        "name": "Candidate B",
        "role": "python_developer",
        "profile_type": "FRESHER",

        "resume_text": (
            "Python developer with basic Django knowledge "
            "and limited project experience."
        ),

        "scores": {
            "ats": 70,
            "screening": 65,
            "hr_interview": 68,
            "technical_interview": 62,
            "machine_test": 58
        },

        "human_decision": "HOLD_REVIEW"
    },

    {
        "candidate_id": "C003",
        "name": "Candidate C",
        "role": "python_developer",
        "profile_type": "FRESHER",

        "resume_text": (
            "Basic Python knowledge with limited backend "
            "development experience."
        ),

        "scores": {
            "ats": 52,
            "screening": 48,
            "hr_interview": 55,
            "technical_interview": 40,
            "machine_test": 42
        },

        "human_decision": "REJECTED"
    },

    {
        "candidate_id": "C004",
        "name": "Candidate D",
        "role": "python_developer",
        "profile_type": "FRESHER",

        "resume_text": (
            "Strong Python Django profile with good academic "
            "projects but inconsistent technical interview performance."
        ),

        "scores": {
            "ats": 88,
            "screening": 84,
            "hr_interview": 82,
            "technical_interview": 45,
            "machine_test": 86
        },

        "human_decision": "HOLD_REVIEW"
    }
]


# =====================================================
# ROLE WEIGHTS
# =====================================================

ROLE_WEIGHTS = {

    "python_developer": {
        "ats": 0.15,
        "screening": 0.10,
        "hr_interview": 0.15,
        "technical_interview": 0.30,
        "machine_test": 0.30
    }
}


# =====================================================
# NORMALIZE SCORE
# =====================================================

def normalize_score(score):

    try:
        score = float(score)

    except (ValueError, TypeError):
        return 0.0

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
# RESUME UPLOAD SIMULATION
# =====================================================

def simulate_resume_upload(candidate):

    resume_text = candidate.get(
        "resume_text",
        ""
    )

    return {

        "status": "SUCCESS",

        "candidate_id":
            candidate[
                "candidate_id"
            ],

        "resume_received":
            bool(
                resume_text.strip()
            ),

        "characters":
            len(
                resume_text
            )
    }


# =====================================================
# ATS SIMULATION
# =====================================================

def simulate_ats(candidate):

    score = normalize_score(
        candidate[
            "scores"
        ][
            "ats"
        ]
    )

    return {

        "ats_score":
            score,

        "status":
            (
                "STRONG"
                if score >= 80

                else "MODERATE"
                if score >= 60

                else "WEAK"
            )
    }


# =====================================================
# SCREENING SIMULATION
# =====================================================

def simulate_screening(candidate):

    score = normalize_score(
        candidate[
            "scores"
        ][
            "screening"
        ]
    )

    return {

        "screening_score":
            score,

        "status":
            (
                "STRONG"
                if score >= 80

                else "MODERATE"
                if score >= 60

                else "WEAK"
            )
    }


# =====================================================
# HR INTERVIEW SIMULATION
# =====================================================

def simulate_hr_interview(candidate):

    score = normalize_score(
        candidate[
            "scores"
        ][
            "hr_interview"
        ]
    )

    return {

        "hr_score":
            score,

        "communication_signal":
            normalize_score(
                score + 2
            ),

        "status":
            (
                "STRONG"
                if score >= 80

                else "MODERATE"
                if score >= 60

                else "WEAK"
            )
    }


# =====================================================
# TECHNICAL INTERVIEW SIMULATION
# =====================================================

def simulate_technical_interview(
    candidate
):

    score = normalize_score(
        candidate[
            "scores"
        ][
            "technical_interview"
        ]
    )

    return {

        "technical_score":
            score,

        "status":
            (
                "STRONG"
                if score >= 80

                else "MODERATE"
                if score >= 60

                else "WEAK"
            )
    }


# =====================================================
# MACHINE TEST SIMULATION
# =====================================================

def simulate_machine_test(candidate):

    score = normalize_score(
        candidate[
            "scores"
        ][
            "machine_test"
        ]
    )

    return {

        "machine_test_score":
            score,

        "status":
            (
                "STRONG"
                if score >= 80

                else "MODERATE"
                if score >= 60

                else "WEAK"
            )
    }


# =====================================================
# CROSS-ROUND AGGREGATION
# =====================================================

def calculate_hiring_fit(
    candidate
):

    role = candidate[
        "role"
    ]

    scores = candidate[
        "scores"
    ]

    weights = ROLE_WEIGHTS.get(

        role,

        {
            "ats": 0.20,
            "screening": 0.15,
            "hr_interview": 0.20,
            "technical_interview": 0.25,
            "machine_test": 0.20
        }
    )

    contributions = {}

    total = 0

    for round_name, weight in (
        weights.items()
    ):

        score = normalize_score(
            scores.get(
                round_name,
                0
            )
        )

        contribution = (
            score * weight
        )

        contributions[
            round_name
        ] = {

            "score":
                score,

            "weight":
                round(
                    weight * 100,
                    2
                ),

            "contribution":
                round(
                    contribution,
                    2
                )
        }

        total += contribution

    return {

        "hiring_fit_score":
            normalize_score(
                total
            ),

        "contributions":
            contributions
    }


# =====================================================
# CROSS-ROUND CONSISTENCY
# =====================================================

def detect_score_inconsistencies(
    scores
):

    values = [

        normalize_score(
            score
        )

        for score in scores.values()
    ]

    if not values:

        return {

            "consistent":
                True,

            "score_range":
                0,

            "issues":
                []
        }

    average = (
        sum(values)
        /
        len(values)
    )

    score_range = (
        max(values)
        -
        min(values)
    )

    issues = []

    for name, score in scores.items():

        score = normalize_score(
            score
        )

        difference = abs(
            score - average
        )

        if difference >= 25:

            issues.append({

                "round":
                    name,

                "score":
                    score,

                "difference_from_average":
                    round(
                        difference,
                        2
                    )
            })

    return {

        "consistent":
            len(
                issues
            ) == 0,

        "score_range":
            round(
                score_range,
                2
            ),

        "average":
            round(
                average,
                2
            ),

        "issues":
            issues
    }


# =====================================================
# FINAL AI DECISION
# =====================================================

def generate_ai_decision(
    hiring_fit_score,
    scores,
    consistency
):

    technical_score = (
        scores[
            "technical_interview"
        ]
    )

    machine_score = (
        scores[
            "machine_test"
        ]
    )


    # ---------------------------------------------
    # Major inconsistency safeguard
    # ---------------------------------------------

    if not consistency[
        "consistent"
    ]:

        return "HOLD_REVIEW"


    # ---------------------------------------------
    # Technical safeguard
    # ---------------------------------------------

    if (
        technical_score < 50
        or
        machine_score < 50
    ):

        if hiring_fit_score >= 60:

            return "HOLD_REVIEW"

        return "REJECTED"


    # ---------------------------------------------
    # Normal score classification
    # ---------------------------------------------

    if hiring_fit_score >= 80:

        return "SELECTED"

    elif hiring_fit_score >= 60:

        return "HOLD_REVIEW"

    return "REJECTED"


# =====================================================
# COMPARE AI WITH HUMAN
# =====================================================

def compare_with_human(
    ai_decision,
    human_decision
):

    match = (
        ai_decision
        ==
        human_decision
    )

    mismatch_type = None

    if not match:

        if (
            ai_decision == "SELECTED"
            and
            human_decision == "REJECTED"
        ):

            mismatch_type = (
                "FALSE_POSITIVE"
            )

        elif (
            ai_decision == "REJECTED"
            and
            human_decision == "SELECTED"
        ):

            mismatch_type = (
                "FALSE_NEGATIVE"
            )

        else:

            mismatch_type = (
                "DECISION_MISMATCH"
            )

    return {

        "match":
            match,

        "mismatch_type":
            mismatch_type
    }


# =====================================================
# SINGLE CANDIDATE SIMULATION
# =====================================================

def simulate_candidate(candidate):

    start = time.perf_counter()


    # ---------------------------------------------
    # Step 1 - Resume Upload
    # ---------------------------------------------

    resume_result = (
        simulate_resume_upload(
            candidate
        )
    )


    # ---------------------------------------------
    # Step 2 - ATS
    # ---------------------------------------------

    ats_result = (
        simulate_ats(
            candidate
        )
    )


    # ---------------------------------------------
    # Step 3 - Screening
    # ---------------------------------------------

    screening_result = (
        simulate_screening(
            candidate
        )
    )


    # ---------------------------------------------
    # Step 4 - HR Interview
    # ---------------------------------------------

    hr_result = (
        simulate_hr_interview(
            candidate
        )
    )


    # ---------------------------------------------
    # Step 5 - Technical Interview
    # ---------------------------------------------

    technical_result = (
        simulate_technical_interview(
            candidate
        )
    )


    # ---------------------------------------------
    # Step 6 - Machine Test
    # ---------------------------------------------

    machine_result = (
        simulate_machine_test(
            candidate
        )
    )


    # ---------------------------------------------
    # Step 7 - Aggregation
    # ---------------------------------------------

    aggregation = (
        calculate_hiring_fit(
            candidate
        )
    )


    # ---------------------------------------------
    # Step 8 - Consistency
    # ---------------------------------------------

    consistency = (
        detect_score_inconsistencies(
            candidate[
                "scores"
            ]
        )
    )


    # ---------------------------------------------
    # Step 9 - Final Decision
    # ---------------------------------------------

    ai_decision = (
        generate_ai_decision(

            hiring_fit_score=
                aggregation[
                    "hiring_fit_score"
                ],

            scores=
                candidate[
                    "scores"
                ],

            consistency=
                consistency
        )
    )


    # ---------------------------------------------
    # Step 10 - Human Comparison
    # ---------------------------------------------

    comparison = (
        compare_with_human(

            ai_decision,

            candidate[
                "human_decision"
            ]
        )
    )


    end = time.perf_counter()


    return {

        "candidate_id":
            candidate[
                "candidate_id"
            ],

        "candidate_name":
            candidate[
                "name"
            ],

        "role":
            candidate[
                "role"
            ],

        "pipeline": {

            "resume_upload":
                resume_result,

            "ats":
                ats_result,

            "screening":
                screening_result,

            "hr_interview":
                hr_result,

            "technical_interview":
                technical_result,

            "machine_test":
                machine_result
        },

        "round_scores":
            candidate[
                "scores"
            ],

        "aggregation":
            aggregation,

        "consistency_analysis":
            consistency,

        "ai_decision":
            ai_decision,

        "human_decision":
            candidate[
                "human_decision"
            ],

        "comparison":
            comparison,

        "processing_time_ms":
            round(
                (
                    end - start
                ) * 1000,
                4
            )
    }


# =====================================================
# SYSTEM ACCURACY
# =====================================================

def calculate_system_accuracy(
    results
):

    if not results:
        return 0.0

    correct = sum(

        1

        for result in results

        if result[
            "comparison"
        ][
            "match"
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
# MISMATCH SUMMARY
# =====================================================

def collect_mismatches(results):

    return [

        {
            "candidate_id":
                result[
                    "candidate_id"
                ],

            "ai_decision":
                result[
                    "ai_decision"
                ],

            "human_decision":
                result[
                    "human_decision"
                ],

            "mismatch_type":
                result[
                    "comparison"
                ][
                    "mismatch_type"
                ]
        }

        for result in results

        if not result[
            "comparison"
        ][
            "match"
        ]
    ]


# =====================================================
# SYSTEM PERFORMANCE
# =====================================================

def analyze_system_performance(
    results
):

    processing_times = [

        result[
            "processing_time_ms"
        ]

        for result in results
    ]

    consistency_issues = sum(

        1

        for result in results

        if not result[
            "consistency_analysis"
        ][
            "consistent"
        ]
    )

    return {

        "average_processing_time_ms":
            round(
                sum(
                    processing_times
                )
                /
                len(
                    processing_times
                ),
                4
            )
            if processing_times
            else 0,

        "fastest_processing_ms":
            round(
                min(
                    processing_times
                ),
                4
            )
            if processing_times
            else 0,

        "slowest_processing_ms":
            round(
                max(
                    processing_times
                ),
                4
            )
            if processing_times
            else 0,

        "cross_round_inconsistency_cases":
            consistency_issues
    }


# =====================================================
# IMPROVEMENT RECOMMENDATIONS
# =====================================================

def generate_improvement_recommendations(
    accuracy,
    mismatches,
    performance
):

    recommendations = []


    if accuracy < 90:

        recommendations.append(
            (
                "Increase the validation dataset and "
                "recalibrate decision thresholds using "
                "recruiter-reviewed outcomes."
            )
        )


    if mismatches:

        recommendations.append(
            (
                "Review mismatch cases individually to "
                "identify whether scoring weights, thresholds, "
                "or round-specific rules caused the disagreement."
            )
        )


    if (
        performance[
            "cross_round_inconsistency_cases"
        ] > 0
    ):

        recommendations.append(
            (
                "Improve cross-round consistency handling "
                "and route large score discrepancies to manual review."
            )
        )


    recommendations.extend([

        (
            "Replace simulated round scores with outputs "
            "from the actual ATS, screening, HR, technical, "
            "and machine-test modules."
        ),

        (
            "Measure each AI component independently to identify "
            "the largest source of false positives and false negatives."
        ),

        (
            "Cache reusable NLP models, embeddings, and parsed "
            "candidate data to improve end-to-end processing speed."
        ),

        (
            "Maintain audit logs for every score and final "
            "recommendation to support troubleshooting."
        ),

        (
            "Validate the final system using candidates from "
            "different roles and experience levels."
        )
    ])


    return recommendations


# =====================================================
# FULL SYSTEM SIMULATION
# =====================================================

def run_full_simulation():

    results = []


    print(
        "=" * 70
    )

    print(
        "       Zecpath AI - Full System Simulation"
    )

    print(
        "=" * 70
    )


    for candidate in CANDIDATES:

        print(
            f"\nProcessing Candidate: "
            f"{candidate['candidate_id']} "
            f"- {candidate['name']}"
        )


        result = (
            simulate_candidate(
                candidate
            )
        )


        results.append(
            result
        )


        print(
            "  Resume Upload     :",
            result[
                "pipeline"
            ][
                "resume_upload"
            ][
                "status"
            ]
        )


        print(
            "  ATS Score         :",
            result[
                "round_scores"
            ][
                "ats"
            ]
        )


        print(
            "  Screening Score   :",
            result[
                "round_scores"
            ][
                "screening"
            ]
        )


        print(
            "  HR Score          :",
            result[
                "round_scores"
            ][
                "hr_interview"
            ]
        )


        print(
            "  Technical Score   :",
            result[
                "round_scores"
            ][
                "technical_interview"
            ]
        )


        print(
            "  Machine Test      :",
            result[
                "round_scores"
            ][
                "machine_test"
            ]
        )


        print(
            "  Hiring Fit        :",
            f"{result['aggregation']['hiring_fit_score']}%"
        )


        print(
            "  AI Decision       :",
            result[
                "ai_decision"
            ]
        )


        print(
            "  Human Decision    :",
            result[
                "human_decision"
            ]
        )


        print(
            "  Decision Match    :",
            result[
                "comparison"
            ][
                "match"
            ]
        )


    # =================================================
    # FINAL METRICS
    # =================================================

    accuracy = (
        calculate_system_accuracy(
            results
        )
    )


    mismatches = (
        collect_mismatches(
            results
        )
    )


    performance = (
        analyze_system_performance(
            results
        )
    )


    recommendations = (
        generate_improvement_recommendations(

            accuracy,
            mismatches,
            performance
        )
    )


    report = {

        "report_name":
            "Zecpath AI End-to-End System Test Report",

        "generated_at":
            datetime.utcnow()
            .isoformat(),

        "test_summary": {

            "total_candidates":
                len(
                    results
                ),

            "ai_human_decision_accuracy":
                accuracy,

            "decision_matches":
                len(
                    results
                )
                -
                len(
                    mismatches
                ),

            "decision_mismatches":
                len(
                    mismatches
                )
        },

        "candidate_results":
            results,

        "mismatch_analysis":
            mismatches,

        "system_performance":
            performance,

        "improvement_recommendations":
            recommendations,

        "validation_note":
            (
                "Reported accuracy measures agreement on the "
                "simulated validation dataset only and should "
                "not be interpreted as production hiring accuracy."
            )
    }


    return report


# =====================================================
# SAVE REPORT
# =====================================================

def save_report(
    report,
    filename=
        "demo/full_system_test_report.json"
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

    report = run_full_simulation()


    filename = save_report(
        report
    )


    print(
        "\n" + "=" * 70
    )

    print(
        "SYSTEM TEST SUMMARY"
    )

    print(
        "=" * 70
    )


    print(
        "Candidates Tested:",
        report[
            "test_summary"
        ][
            "total_candidates"
        ]
    )


    print(
        "AI vs Human Accuracy:",
        f"{report['test_summary']['ai_human_decision_accuracy']}%"
    )


    print(
        "Decision Matches:",
        report[
            "test_summary"
        ][
            "decision_matches"
        ]
    )


    print(
        "Decision Mismatches:",
        report[
            "test_summary"
        ][
            "decision_mismatches"
        ]
    )


    print(
        "Cross-Round Inconsistencies:",
        report[
            "system_performance"
        ][
            "cross_round_inconsistency_cases"
        ]
    )


    print(
        "\nReport saved to:",
        filename
    )