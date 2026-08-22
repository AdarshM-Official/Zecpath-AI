import json
import os
import re
from datetime import datetime


# =====================================================
# TASK TYPES
# =====================================================

class TaskType:
    CODING = "CODING"
    DEBUGGING = "DEBUGGING"
    FILE_BASED = "FILE_BASED"
    SYSTEM_DESIGN = "SYSTEM_DESIGN"


# =====================================================
# DIFFICULTY
# =====================================================

class Difficulty:
    BASIC = "BASIC"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


# =====================================================
# SCORING CONFIGURATION
# =====================================================

SCORING_WEIGHTS = {

    TaskType.CODING: {
        "correctness": 0.45,
        "efficiency": 0.20,
        "code_quality": 0.20,
        "problem_solving": 0.15
    },

    TaskType.DEBUGGING: {
        "correctness": 0.40,
        "efficiency": 0.15,
        "code_quality": 0.20,
        "problem_solving": 0.25
    },

    TaskType.FILE_BASED: {
        "correctness": 0.40,
        "efficiency": 0.20,
        "code_quality": 0.20,
        "problem_solving": 0.20
    },

    TaskType.SYSTEM_DESIGN: {
        "correctness": 0.25,
        "efficiency": 0.20,
        "code_quality": 0.15,
        "problem_solving": 0.40
    }
}


# =====================================================
# DIFFICULTY FACTORS
# =====================================================

DIFFICULTY_FACTORS = {
    Difficulty.BASIC: 1.00,
    Difficulty.INTERMEDIATE: 1.05,
    Difficulty.ADVANCED: 1.10
}


# =====================================================
# TASK BANK
# =====================================================

TASK_BANK = {

    "PYTHON_001": {

        "task_id": "PYTHON_001",

        "title": "Remove Duplicate Elements",

        "task_type": TaskType.CODING,

        "skill": "python",

        "difficulty": Difficulty.BASIC,

        "description":
            "Write a Python function that removes duplicate "
            "elements from a list while preserving order.",

        "expected_time_minutes": 15,

        "total_tests": 5
    },


    "PYTHON_002": {

        "task_id": "PYTHON_002",

        "title": "Debug User Processing Function",

        "task_type": TaskType.DEBUGGING,

        "skill": "python",

        "difficulty": Difficulty.INTERMEDIATE,

        "description":
            "Identify and correct the bugs in the provided "
            "user processing function.",

        "expected_time_minutes": 20,

        "total_tests": 6
    },


    "DATA_001": {

        "task_id": "DATA_001",

        "title": "CSV Employee Analysis",

        "task_type": TaskType.FILE_BASED,

        "skill": "python",

        "difficulty": Difficulty.INTERMEDIATE,

        "description":
            "Read an employee CSV file, calculate department "
            "statistics and produce structured output.",

        "expected_time_minutes": 30,

        "total_tests": 8
    },


    "DESIGN_001": {

        "task_id": "DESIGN_001",

        "title": "Design URL Shortener",

        "task_type": TaskType.SYSTEM_DESIGN,

        "skill": "system_design",

        "difficulty": Difficulty.ADVANCED,

        "description":
            "Design a small URL shortening service including "
            "API, database and scalability considerations.",

        "expected_time_minutes": 40,

        "total_tests": 0
    }
}


# =====================================================
# SCORE NORMALIZATION
# =====================================================

def normalize_score(score):

    try:
        score = float(score)

    except (ValueError, TypeError):
        return 0.0

    return round(
        max(0, min(100, score)),
        2
    )


# =====================================================
# CORRECTNESS SCORE
# =====================================================

def calculate_correctness(
    passed_tests,
    total_tests
):

    if total_tests <= 0:
        return 0.0

    passed_tests = min(
        passed_tests,
        total_tests
    )

    score = (
        passed_tests
        /
        total_tests
    ) * 100

    return normalize_score(score)


# =====================================================
# EFFICIENCY SCORE
# =====================================================

def calculate_efficiency(
    execution_time_ms,
    benchmark_time_ms
):

    if (
        execution_time_ms is None
        or benchmark_time_ms is None
        or benchmark_time_ms <= 0
    ):
        return 50.0

    if execution_time_ms <= benchmark_time_ms:
        return 100.0

    ratio = (
        benchmark_time_ms
        /
        execution_time_ms
    )

    score = ratio * 100

    return normalize_score(
        max(score, 20)
    )


# =====================================================
# CODE QUALITY SCORE
# =====================================================

def calculate_code_quality(code):

    if not code:
        return 0.0

    score = 40

    # ---------------------------------------------
    # Function usage
    # ---------------------------------------------

    if re.search(
        r"\bdef\s+\w+\(",
        code
    ):
        score += 15

    # ---------------------------------------------
    # Meaningful comments
    # ---------------------------------------------

    if "#" in code:
        score += 10

    # ---------------------------------------------
    # Documentation
    # ---------------------------------------------

    if '"""' in code or "'''" in code:
        score += 10

    # ---------------------------------------------
    # Exception handling
    # ---------------------------------------------

    if (
        "try:" in code
        and
        "except" in code
    ):
        score += 10

    # ---------------------------------------------
    # Excessively long lines
    # ---------------------------------------------

    lines = code.splitlines()

    long_lines = [
        line
        for line in lines
        if len(line) > 100
    ]

    if not long_lines:
        score += 10

    return normalize_score(score)


# =====================================================
# PROBLEM-SOLVING SCORE
# =====================================================

def calculate_problem_solving(
    explanation
):

    if not explanation:
        return 30.0

    text = explanation.lower()

    markers = [
        "first",
        "then",
        "because",
        "approach",
        "algorithm",
        "complexity",
        "edge case",
        "test",
        "validate",
        "alternative",
        "trade-off",
        "tradeoff",
        "optimize"
    ]

    matched = sum(
        1
        for marker in markers
        if marker in text
    )

    word_count = len(
        text.split()
    )

    score = 30

    score += min(
        matched * 6,
        48
    )

    if word_count >= 30:
        score += 10

    if word_count >= 60:
        score += 10

    return normalize_score(score)


# =====================================================
# TIME SCORE
# =====================================================

def calculate_time_score(
    expected_minutes,
    actual_minutes
):

    if (
        expected_minutes is None
        or actual_minutes is None
        or expected_minutes <= 0
    ):
        return 100.0

    # Completed within expected time
    if actual_minutes <= expected_minutes:

        return 100.0

    ratio = (
        expected_minutes
        /
        actual_minutes
    )

    score = ratio * 100

    # Avoid extreme punishment
    return normalize_score(
        max(score, 50)
    )


# =====================================================
# TIME ADJUSTMENT
# =====================================================

def apply_time_adjustment(
    technical_score,
    time_score
):

    # Time has only a small effect on the final result.
    # Technical correctness remains more important.

    factor = (
        0.90
        +
        (
            time_score / 100
        ) * 0.10
    )

    return normalize_score(
        technical_score * factor
    )


# =====================================================
# DIFFICULTY NORMALIZATION
# =====================================================

def apply_difficulty_factor(
    score,
    difficulty
):

    factor = DIFFICULTY_FACTORS.get(
        difficulty,
        1.0
    )

    return normalize_score(
        score * factor
    )


# =====================================================
# PERFORMANCE LEVEL
# =====================================================

def get_performance_level(score):

    if score >= 85:
        return "EXCELLENT"

    elif score >= 70:
        return "GOOD"

    elif score >= 55:
        return "MODERATE"

    elif score >= 40:
        return "BASIC"

    return "WEAK"


# =====================================================
# CODE SNAPSHOT
# =====================================================

def create_code_snapshot(
    code,
    snapshot_number
):

    return {

        "snapshot_number":
            snapshot_number,

        "timestamp":
            datetime.utcnow().isoformat(),

        "code":
            code
    }


# =====================================================
# EXECUTION RESULT
# =====================================================

def create_execution_result(
    passed_tests,
    total_tests,
    execution_time_ms=None,
    output=None,
    errors=None
):

    return {

        "timestamp":
            datetime.utcnow().isoformat(),

        "passed_tests":
            passed_tests,

        "total_tests":
            total_tests,

        "execution_time_ms":
            execution_time_ms,

        "output":
            output,

        "errors":
            errors or []
    }


# =====================================================
# EXPLAINABLE FEEDBACK
# =====================================================

def generate_explanation(
    scores
):

    explanation = []

    correctness = scores[
        "correctness"
    ]

    efficiency = scores[
        "efficiency"
    ]

    quality = scores[
        "code_quality"
    ]

    problem_solving = scores[
        "problem_solving"
    ]


    if correctness >= 90:

        explanation.append(
            "Solution passed nearly all required tests."
        )

    elif correctness >= 60:

        explanation.append(
            "Solution is partially correct but misses some cases."
        )

    else:

        explanation.append(
            "Solution has significant correctness issues."
        )


    if efficiency >= 80:

        explanation.append(
            "Execution performance is efficient."
        )

    elif efficiency < 50:

        explanation.append(
            "Solution may require performance optimization."
        )


    if quality >= 75:

        explanation.append(
            "Code demonstrates good structural quality."
        )

    elif quality < 50:

        explanation.append(
            "Code structure and maintainability can be improved."
        )


    if problem_solving >= 75:

        explanation.append(
            "Candidate demonstrates a structured problem-solving approach."
        )

    elif problem_solving < 50:

        explanation.append(
            "Problem-solving approach requires clearer reasoning."
        )


    return explanation


# =====================================================
# MACHINE TEST TASK EVALUATOR
# =====================================================

def evaluate_task(
    task,
    code,
    passed_tests,
    execution_time_ms,
    benchmark_time_ms,
    actual_time_minutes,
    explanation
):

    task_type = task[
        "task_type"
    ]

    # ---------------------------------------------
    # Individual scores
    # ---------------------------------------------

    correctness = calculate_correctness(

        passed_tests,

        task[
            "total_tests"
        ]
    )


    efficiency = calculate_efficiency(

        execution_time_ms,

        benchmark_time_ms
    )


    code_quality = calculate_code_quality(
        code
    )


    problem_solving = calculate_problem_solving(
        explanation
    )


    scores = {

        "correctness":
            correctness,

        "efficiency":
            efficiency,

        "code_quality":
            code_quality,

        "problem_solving":
            problem_solving
    }


    # ---------------------------------------------
    # Select task-specific rubric
    # ---------------------------------------------

    weights = SCORING_WEIGHTS[
        task_type
    ]


    raw_score = sum(

        scores[
            parameter
        ]
        *
        weights[
            parameter
        ]

        for parameter
        in weights
    )


    raw_score = normalize_score(
        raw_score
    )


    # ---------------------------------------------
    # Time score
    # ---------------------------------------------

    time_score = calculate_time_score(

        task[
            "expected_time_minutes"
        ],

        actual_time_minutes
    )


    time_adjusted_score = (
        apply_time_adjustment(
            raw_score,
            time_score
        )
    )


    # ---------------------------------------------
    # Difficulty normalization
    # ---------------------------------------------

    final_score = (
        apply_difficulty_factor(

            time_adjusted_score,

            task[
                "difficulty"
            ]
        )
    )


    return {

        "task_id":
            task[
                "task_id"
            ],

        "title":
            task[
                "title"
            ],

        "task_type":
            task_type,

        "skill":
            task[
                "skill"
            ],

        "difficulty":
            task[
                "difficulty"
            ],

        "parameter_scores":
            scores,

        "weights":
            weights,

        "raw_score":
            raw_score,

        "time_score":
            time_score,

        "time_adjusted_score":
            time_adjusted_score,

        "final_score":
            final_score,

        "performance_level":
            get_performance_level(
                final_score
            ),

        "explanation":
            generate_explanation(
                scores
            )
    }


# =====================================================
# SKILL-WISE BREAKDOWN
# =====================================================

def calculate_skill_breakdown(
    task_results
):

    skills = {}

    for result in task_results:

        skill = result[
            "skill"
        ]

        if skill not in skills:

            skills[skill] = {
                "scores": [],
                "tasks_completed": 0
            }

        skills[
            skill
        ][
            "scores"
        ].append(
            result[
                "final_score"
            ]
        )

        skills[
            skill
        ][
            "tasks_completed"
        ] += 1


    output = {}

    for skill, data in skills.items():

        average = (
            sum(
                data[
                    "scores"
                ]
            )
            /
            len(
                data[
                    "scores"
                ]
            )
        )

        average = normalize_score(
            average
        )

        output[
            skill
        ] = {

            "score":
                average,

            "tasks_completed":
                data[
                    "tasks_completed"
                ],

            "level":
                get_performance_level(
                    average
                )
        }

    return output


# =====================================================
# OVERALL SCORE
# =====================================================

def calculate_overall_score(
    task_results
):

    if not task_results:
        return 0.0

    scores = [

        result[
            "final_score"
        ]

        for result
        in task_results
    ]

    return normalize_score(

        sum(scores)
        /
        len(scores)
    )


# =====================================================
# MACHINE TEST ENGINE
# =====================================================

class MachineTestEngine:

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

        self.started_at = (
            datetime.utcnow()
            .isoformat()
        )

        self.snapshots = {}

        self.execution_results = {}

        self.task_results = []


    # =================================================
    # CAPTURE SNAPSHOT
    # =================================================

    def capture_snapshot(
        self,
        task_id,
        code
    ):

        if task_id not in self.snapshots:

            self.snapshots[
                task_id
            ] = []

        snapshot_number = (
            len(
                self.snapshots[
                    task_id
                ]
            )
            + 1
        )

        snapshot = (
            create_code_snapshot(

                code,

                snapshot_number
            )
        )

        self.snapshots[
            task_id
        ].append(
            snapshot
        )

        return snapshot


    # =================================================
    # CAPTURE EXECUTION
    # =================================================

    def capture_execution(
        self,
        task_id,
        passed_tests,
        total_tests,
        execution_time_ms=None,
        output=None,
        errors=None
    ):

        result = (
            create_execution_result(

                passed_tests,
                total_tests,
                execution_time_ms,
                output,
                errors
            )
        )

        if task_id not in (
            self.execution_results
        ):

            self.execution_results[
                task_id
            ] = []

        self.execution_results[
            task_id
        ].append(
            result
        )

        return result


    # =================================================
    # EVALUATE SUBMISSION
    # =================================================

    def evaluate_submission(
        self,
        task_id,
        code,
        passed_tests,
        execution_time_ms,
        benchmark_time_ms,
        actual_time_minutes,
        explanation
    ):

        task = TASK_BANK.get(
            task_id
        )

        if not task:

            raise ValueError(
                "Invalid task ID"
            )


        # ---------------------------------------------
        # Final code snapshot
        # ---------------------------------------------

        self.capture_snapshot(
            task_id,
            code
        )


        # ---------------------------------------------
        # Execution capture
        # ---------------------------------------------

        self.capture_execution(

            task_id=

                task_id,

            passed_tests=
                passed_tests,

            total_tests=
                task[
                    "total_tests"
                ],

            execution_time_ms=
                execution_time_ms
        )


        # ---------------------------------------------
        # Evaluation
        # ---------------------------------------------

        result = evaluate_task(

            task=
                task,

            code=
                code,

            passed_tests=
                passed_tests,

            execution_time_ms=
                execution_time_ms,

            benchmark_time_ms=
                benchmark_time_ms,

            actual_time_minutes=
                actual_time_minutes,

            explanation=
                explanation
        )


        self.task_results.append(
            result
        )

        return result


    # =================================================
    # GENERATE FINAL REPORT
    # =================================================

    def generate_report(self):

        overall_score = (
            calculate_overall_score(
                self.task_results
            )
        )

        skill_breakdown = (
            calculate_skill_breakdown(
                self.task_results
            )
        )

        return {

            "report_type":
                "Machine Test Evaluation",

            "candidate_id":
                self.candidate_id,

            "job_id":
                self.job_id,

            "generated_at":
                datetime.utcnow()
                .isoformat(),

            "tasks_completed":
                len(
                    self.task_results
                ),

            "task_results":
                self.task_results,

            "skill_breakdown":
                skill_breakdown,

            "machine_test_score":
                overall_score,

            "performance_level":
                get_performance_level(
                    overall_score
                ),

            "code_snapshots":
                self.snapshots,

            "execution_results":
                self.execution_results,

            "recommendation":
                generate_recommendation(
                    overall_score
                )
        }


# =====================================================
# RECOMMENDATION
# =====================================================

def generate_recommendation(
    score
):

    if score >= 85:

        return {
            "status": "STRONG",
            "message":
                "Candidate demonstrated strong practical technical skills."
        }

    elif score >= 70:

        return {
            "status": "SUITABLE",
            "message":
                "Candidate demonstrated good practical technical ability."
        }

    elif score >= 55:

        return {
            "status": "REVIEW",
            "message":
                "Candidate demonstrated moderate practical ability."
        }

    return {
        "status": "FURTHER_ASSESSMENT",
        "message":
            "Additional practical technical assessment is recommended."
    }


# =====================================================
# SAVE REPORT
# =====================================================

def save_report(
    report,
    filename=
        "machine_test/machine_test_report.json"
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
# DEMO
# =====================================================

def run_demo():

    engine = MachineTestEngine(

        candidate_id=
            "C101",

        job_id=
            "JOB_PYTHON_001"
    )


    code = """
def remove_duplicates(items):
    # Track previously seen values
    seen = set()
    result = []

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result
"""


    explanation = """
First I create a set to track elements that have already
been encountered. Then I iterate through the input list.

If an item has not been seen, I add it to both the set and
the result list. This preserves the original order.

The approach avoids repeatedly scanning the result list,
so membership checking is efficient for normal hashable
values. I would also test empty input, repeated values and
already unique lists.
"""


    # ---------------------------------------------
    # Intermediate snapshot
    # ---------------------------------------------

    engine.capture_snapshot(

        task_id=
            "PYTHON_001",

        code=
            "def remove_duplicates(items):\n    pass"
    )


    # ---------------------------------------------
    # Evaluate final submission
    # ---------------------------------------------

    result = engine.evaluate_submission(

        task_id=
            "PYTHON_001",

        code=
            code,

        passed_tests=
            5,

        execution_time_ms=
            8,

        benchmark_time_ms=
            10,

        actual_time_minutes=
            12,

        explanation=
            explanation
    )


    print(
        "\nTASK RESULT"
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )


    report = (
        engine.generate_report()
    )


    filename = (
        save_report(
            report
        )
    )


    print(
        "\nFINAL MACHINE TEST REPORT"
    )

    print(
        json.dumps(
            report,
            indent=4
        )
    )


    print(
        "\nReport saved to:",
        filename
    )


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    run_demo()