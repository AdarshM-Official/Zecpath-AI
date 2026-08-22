import json
import os
from datetime import datetime


# =====================================================
# DECISION CATEGORIES
# =====================================================

class DecisionCategory:

    SELECTED = "SELECTED"

    HOLD_REVIEW = "HOLD_REVIEW"

    REJECTED = "REJECTED"


# =====================================================
# CONFIGURATION
# =====================================================

DECISION_CONFIG = {

    "selected_threshold": 80,

    "review_threshold": 60,

    "rejection_threshold": 45,

    # Minimum critical-round scores
    "minimum_technical_score": 50,

    "minimum_machine_test_score": 50,

    "minimum_hr_score": 50,

    # Confidence limits
    "high_confidence": 85,

    "medium_confidence": 65
}


# =====================================================
# NORMALIZE SCORE
# =====================================================

def normalize_score(score):

    if score is None:
        return None

    try:
        score = float(score)

    except (ValueError, TypeError):
        return None

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
# MISSING ROUND CHECK
# =====================================================

def get_missing_rounds(
    round_scores
):

    return [

        name

        for name, score
        in round_scores.items()

        if score is None
    ]


# =====================================================
# CRITICAL SCORE CHECK
# =====================================================

def evaluate_critical_scores(
    round_scores
):

    issues = []

    technical = normalize_score(
        round_scores.get(
            "technical_interview"
        )
    )

    machine = normalize_score(
        round_scores.get(
            "machine_test"
        )
    )

    hr = normalize_score(
        round_scores.get(
            "hr_interview"
        )
    )


    if (
        technical is not None
        and
        technical
        <
        DECISION_CONFIG[
            "minimum_technical_score"
        ]
    ):

        issues.append({
            "type":
                "TECHNICAL_SCORE",

            "severity":
                "HIGH",

            "message":
                "Technical interview performance is below the configured minimum."
        })


    if (
        machine is not None
        and
        machine
        <
        DECISION_CONFIG[
            "minimum_machine_test_score"
        ]
    ):

        issues.append({
            "type":
                "MACHINE_TEST_SCORE",

            "severity":
                "HIGH",

            "message":
                "Machine test performance is below the configured minimum."
        })


    if (
        hr is not None
        and
        hr
        <
        DECISION_CONFIG[
            "minimum_hr_score"
        ]
    ):

        issues.append({
            "type":
                "HR_SCORE",

            "severity":
                "MODERATE",

            "message":
                "HR interview performance is below the preferred minimum."
        })


    return issues


# =====================================================
# INTEGRITY RISK ANALYSIS
# =====================================================

def analyze_integrity_risk(
    integrity_data
):

    if not integrity_data:

        return {
            "level": "UNKNOWN",
            "requires_review": False,
            "reason": None
        }

    risk_level = str(
        integrity_data.get(
            "risk_level",
            "LOW"
        )
    ).upper()


    if risk_level in [
        "HIGH",
        "REVIEW_REQUIRED"
    ]:

        return {

            "level":
                risk_level,

            "requires_review":
                True,

            "reason":
                (
                    "Integrity monitoring produced signals "
                    "that require manual review."
                )
        }


    return {

        "level":
            risk_level,

        "requires_review":
            False,

        "reason":
            None
    }


# =====================================================
# BEHAVIORAL RISK ANALYSIS
# =====================================================

def analyze_behavioral_risk(
    behavioral_data
):

    if not behavioral_data:

        return {

            "level":
                "UNKNOWN",

            "requires_review":
                False,

            "reason":
                None
        }


    stress_score = normalize_score(

        behavioral_data.get(
            "stress_signals",
            {}
        ).get(
            "score"
        )
    )


    contradiction_count = (

        behavioral_data.get(
            "contradiction_analysis",
            {}
        ).get(
            "count",
            0
        )
    )


    if contradiction_count >= 2:

        return {

            "level":
                "HIGH",

            "requires_review":
                True,

            "reason":
                (
                    "Multiple contradictory statements "
                    "were detected."
                )
        }


    if (
        stress_score is not None
        and
        stress_score >= 70
    ):

        return {

            "level":
                "MODERATE",

            "requires_review":
                True,

            "reason":
                (
                    "Multiple communication-related signals "
                    "were detected and should be reviewed in context."
                )
        }


    return {

        "level":
            "LOW",

        "requires_review":
            False,

        "reason":
            None
    }


# =====================================================
# SCORE-BASED DECISION
# =====================================================

def get_score_based_decision(
    hiring_fit_score
):

    score = normalize_score(
        hiring_fit_score
    )

    if score is None:

        return DecisionCategory.HOLD_REVIEW


    if score >= DECISION_CONFIG[
        "selected_threshold"
    ]:

        return DecisionCategory.SELECTED


    elif score >= DECISION_CONFIG[
        "review_threshold"
    ]:

        return DecisionCategory.HOLD_REVIEW


    return DecisionCategory.REJECTED


# =====================================================
# HYBRID DECISION LOGIC
# =====================================================

def apply_hybrid_rules(
    score_decision,
    hiring_fit_score,
    critical_issues,
    integrity_review,
    behavioral_review,
    missing_rounds
):

    reasons = []


    # -------------------------------------------------
    # Missing assessment data
    # -------------------------------------------------

    if missing_rounds:

        reasons.append(
            "One or more evaluation rounds are unavailable."
        )

        return (
            DecisionCategory.HOLD_REVIEW,
            reasons
        )


    # -------------------------------------------------
    # Integrity signals -> manual review
    # -------------------------------------------------

    if integrity_review[
        "requires_review"
    ]:

        reasons.append(
            integrity_review[
                "reason"
            ]
        )

        return (
            DecisionCategory.HOLD_REVIEW,
            reasons
        )


    # -------------------------------------------------
    # Behavioral signals -> review, not auto-reject
    # -------------------------------------------------

    if behavioral_review[
        "requires_review"
    ]:

        reasons.append(
            behavioral_review[
                "reason"
            ]
        )

        return (
            DecisionCategory.HOLD_REVIEW,
            reasons
        )


    # -------------------------------------------------
    # Critical score issues
    # -------------------------------------------------

    high_issues = [

        issue

        for issue
        in critical_issues

        if issue[
            "severity"
        ] == "HIGH"
    ]


    if high_issues:

        reasons.extend(

            issue["message"]

            for issue
            in high_issues
        )


        if hiring_fit_score < 60:

            return (
                DecisionCategory.REJECTED,
                reasons
            )


        return (
            DecisionCategory.HOLD_REVIEW,
            reasons
        )


    # -------------------------------------------------
    # Normal score decision
    # -------------------------------------------------

    if score_decision == (
        DecisionCategory.SELECTED
    ):

        reasons.append(
            "Candidate achieved a strong overall hiring-fit score."
        )


    elif score_decision == (
        DecisionCategory.HOLD_REVIEW
    ):

        reasons.append(
            "Candidate performance is within the recruiter-review range."
        )


    else:

        reasons.append(
            "Overall hiring-fit score is below the configured threshold."
        )


    return (
        score_decision,
        reasons
    )


# =====================================================
# DECISION CONFIDENCE
# =====================================================

def calculate_decision_confidence(
    hiring_fit_score,
    round_scores,
    missing_rounds,
    integrity_review,
    behavioral_review
):

    score = 100


    # -------------------------------------------------
    # Missing information
    # -------------------------------------------------

    score -= min(
        len(
            missing_rounds
        ) * 15,
        45
    )


    # -------------------------------------------------
    # Integrity uncertainty
    # -------------------------------------------------

    if integrity_review[
        "requires_review"
    ]:

        score -= 25


    # -------------------------------------------------
    # Behavioral uncertainty
    # -------------------------------------------------

    if behavioral_review[
        "requires_review"
    ]:

        score -= 15


    # -------------------------------------------------
    # Round score variance
    # -------------------------------------------------

    available_scores = [

        normalize_score(
            value
        )

        for value
        in round_scores.values()

        if normalize_score(
            value
        ) is not None
    ]


    if len(available_scores) >= 2:
        difference = max(available_scores) - min(available_scores)

        # Relaxed variance penalty (Day 54 optimization)
        # Previous thresholds were >40 (penalty 20) and >25 (penalty 10)
        if difference > 45:
            score -= 20
        elif difference > 30:
            score -= 10


    # -------------------------------------------------
    # Borderline final score
    # -------------------------------------------------

    final_score = normalize_score(
        hiring_fit_score
    )


    if final_score is not None:

        boundaries = [
            DECISION_CONFIG[
                "selected_threshold"
            ],

            DECISION_CONFIG[
                "review_threshold"
            ]
        ]


        distance = min(

            abs(
                final_score - boundary
            )

            for boundary
            in boundaries
        )


        if distance <= 3:

            score -= 15


    return normalize_score(
        score
    )


# =====================================================
# CONFIDENCE LEVEL
# =====================================================

def get_confidence_level(
    score
):

    if score >= DECISION_CONFIG[
        "high_confidence"
    ]:

        return "HIGH"

    elif score >= DECISION_CONFIG[
        "medium_confidence"
    ]:

        return "MEDIUM"

    return "LOW"


# =====================================================
# EXPLAIN DECISION
# =====================================================

def generate_explanation(
    decision,
    hiring_fit_score,
    confidence_score,
    reasons,
    critical_issues,
    integrity_review,
    behavioral_review
):

    explanation = [

        (
            f"Final Hiring Fit Score: "
            f"{hiring_fit_score}%."
        ),

        (
            f"Decision confidence: "
            f"{confidence_score}%."
        )
    ]


    explanation.extend(
        reasons
    )


    if critical_issues:

        explanation.append(
            (
                f"{len(critical_issues)} "
                f"critical or review-level score issue(s) "
                f"were identified."
            )
        )


    if integrity_review[
        "requires_review"
    ]:

        explanation.append(
            (
                "Integrity signals were not used as "
                "automatic proof of malpractice."
            )
        )


    if behavioral_review[
        "requires_review"
    ]:

        explanation.append(
            (
                "Behavioral communication signals were "
                "used only to trigger review."
            )
        )


    if decision == DecisionCategory.SELECTED:

        explanation.append(
            "No blocking review conditions were identified."
        )


    return explanation


# =====================================================
# FINAL RECOMMENDATION ENGINE
# =====================================================

class FinalRecommendationEngine:

    def __init__(
        self,
        candidate_id,
        job_id
    ):

        self.candidate_id = (
            candidate_id
        )

        self.job_id = (
            job_id
        )


    # =================================================
    # GENERATE DECISION
    # =================================================

    def generate_decision(
        self,
        hiring_fit_score,
        round_scores,
        integrity_data=None,
        behavioral_data=None
    ):

        hiring_fit_score = (
            normalize_score(
                hiring_fit_score
            )
        )


        normalized_round_scores = {

            key:
                normalize_score(
                    value
                )

            for key, value
            in round_scores.items()
        }


        missing_rounds = (
            get_missing_rounds(
                normalized_round_scores
            )
        )


        critical_issues = (
            evaluate_critical_scores(
                normalized_round_scores
            )
        )


        integrity_review = (
            analyze_integrity_risk(
                integrity_data
            )
        )


        behavioral_review = (
            analyze_behavioral_risk(
                behavioral_data
            )
        )


        score_decision = (
            get_score_based_decision(
                hiring_fit_score
            )
        )


        (
            final_decision,
            reasons

        ) = apply_hybrid_rules(

            score_decision=
                score_decision,

            hiring_fit_score=
                hiring_fit_score,

            critical_issues=
                critical_issues,

            integrity_review=
                integrity_review,

            behavioral_review=
                behavioral_review,

            missing_rounds=
                missing_rounds
        )


        confidence_score = (
            calculate_decision_confidence(

                hiring_fit_score=
                    hiring_fit_score,

                round_scores=
                    normalized_round_scores,

                missing_rounds=
                    missing_rounds,

                integrity_review=
                    integrity_review,

                behavioral_review=
                    behavioral_review
            )
        )


        confidence_level = (
            get_confidence_level(
                confidence_score
            )
        )


        return {

            "candidate_id":
                self.candidate_id,

            "job_id":
                self.job_id,

            "generated_at":
                datetime.utcnow()
                .isoformat(),

            "hiring_fit_score":
                hiring_fit_score,

            "round_scores":
                normalized_round_scores,

            "score_based_decision":
                score_decision,

            "final_decision":
                final_decision,

            "decision_confidence": {

                "score":
                    confidence_score,

                "level":
                    confidence_level
            },

            "critical_score_issues":
                critical_issues,

            "integrity_review":
                integrity_review,

            "behavioral_review":
                behavioral_review,

            "missing_rounds":
                missing_rounds,

            "reasons":
                reasons,

            "explanation":
                generate_explanation(

                    decision=
                        final_decision,

                    hiring_fit_score=
                        hiring_fit_score,

                    confidence_score=
                        confidence_score,

                    reasons=
                        reasons,

                    critical_issues=
                        critical_issues,

                    integrity_review=
                        integrity_review,

                    behavioral_review=
                        behavioral_review
                ),

            "human_review_required":
                (
                    final_decision
                    ==
                    DecisionCategory.HOLD_REVIEW
                ),

            "decision_note":
                (
                    "The recommendation is a decision-support "
                    "output. Final employment decisions should "
                    "remain subject to authorized human review."
                )
        }


# =====================================================
# SAVE OUTPUT
# =====================================================

def save_decision(
    decision,
    filename=
        "decision_engine/final_candidate_decision.json"
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
            decision,
            file,
            indent=4,
            ensure_ascii=False
        )


    return filename


# =====================================================
# DEMO
# =====================================================

def run_demo():

    engine = FinalRecommendationEngine(

        candidate_id=
            "C_FINAL_01",

        job_id=
            "JOB_PYTHON_001"
    )


    round_scores = {

        "ats":
            82,

        "screening":
            78,

        "hr_interview":
            80,

        "technical_interview":
            85,

        "machine_test":
            83
    }


    integrity_data = {

        "risk_level":
            "LOW"
    }


    behavioral_data = {

        "stress_signals": {
            "score":
                22
        },

        "contradiction_analysis": {
            "count":
                0
        }
    }


    decision = (
        engine.generate_decision(

            hiring_fit_score=
                82.5,

            round_scores=
                round_scores,

            integrity_data=
                integrity_data,

            behavioral_data=
                behavioral_data
        )
    )


    print(
        "=" * 70
    )

    print(
        "Zecpath AI - Final Recommendation Engine"
    )

    print(
        "=" * 70
    )


    print(
        json.dumps(
            decision,
            indent=4
        )
    )


    filename = (
        save_decision(
            decision
        )
    )


    print(
        "\nDecision saved to:",
        filename
    )


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    run_demo()