import re
import json
import os
from datetime import datetime


# =====================================================
# CONFIGURATION
# =====================================================

MAX_RETRIES = 2

MIN_STT_CONFIDENCE = 0.60

POOR_AUDIO_THRESHOLD = 0.40

HIGH_NOISE_THRESHOLD = 0.65

MIN_ANSWER_WORDS = 2


# =====================================================
# ERROR TYPES
# =====================================================

class ErrorType:

    POOR_AUDIO = "POOR_AUDIO"

    BACKGROUND_NOISE = "BACKGROUND_NOISE"

    MISSING_ANSWER = "MISSING_ANSWER"

    LOW_STT_CONFIDENCE = "LOW_STT_CONFIDENCE"

    LANGUAGE_MIXING = "LANGUAGE_MIXING"

    UNCLEAR_RESPONSE = "UNCLEAR_RESPONSE"

    SYSTEM_ERROR = "SYSTEM_ERROR"

    MAX_RETRIES = "MAX_RETRIES"


# =====================================================
# ACTION TYPES
# =====================================================

class ActionType:

    ACCEPT = "ACCEPT"

    RETRY = "RETRY"

    CLARIFY = "CLARIFY"

    SKIP = "SKIP"

    MANUAL_REVIEW = "MANUAL_REVIEW"

    SAFE_FALLBACK = "SAFE_FALLBACK"


# =====================================================
# NORMALIZE TEXT
# =====================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).strip()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# =====================================================
# HANDLE MISSING ANSWERS
# =====================================================

def detect_missing_answer(text):

    if text is None:
        return True

    text = normalize_text(text).lower()

    missing_patterns = [
        "",
        "...",
        "[silence]",
        "[no response]",
        "no response",
        "silence",
        "inaudible"
    ]

    if text in missing_patterns:
        return True

    return False


# =====================================================
# CHECK POOR AUDIO
# =====================================================

def detect_poor_audio(
    audio_quality=None,
    stt_confidence=None
):

    problems = []

    if audio_quality is not None:

        if audio_quality < POOR_AUDIO_THRESHOLD:

            problems.append(
                "Audio quality is below acceptable threshold."
            )

    if stt_confidence is not None:

        if stt_confidence < MIN_STT_CONFIDENCE:

            problems.append(
                "Speech-to-text confidence is low."
            )

    return {
        "detected": len(problems) > 0,
        "problems": problems
    }


# =====================================================
# DETECT BACKGROUND NOISE
# =====================================================

def detect_background_noise(noise_level=None):

    if noise_level is None:

        return {
            "detected": False,
            "noise_level": None,
            "severity": "Unknown"
        }

    if noise_level >= HIGH_NOISE_THRESHOLD:

        severity = "High"

        detected = True

    elif noise_level >= 0.40:

        severity = "Moderate"

        detected = True

    else:

        severity = "Low"

        detected = False

    return {
        "detected": detected,
        "noise_level": noise_level,
        "severity": severity
    }


# =====================================================
# DETECT LANGUAGE MIXING
# =====================================================

def detect_language_mixing(
    text,
    detected_languages=None
):

    text = normalize_text(text)

    if not text:

        return {
            "detected": False,
            "languages": []
        }

    # Preferred method:
    # receive language information from STT/language detector.

    if detected_languages:

        unique_languages = list(
            dict.fromkeys(detected_languages)
        )

        return {
            "detected": len(unique_languages) > 1,
            "languages": unique_languages
        }

    # Basic fallback heuristic.
    # Detects presence of Latin and non-Latin characters.

    has_latin = bool(
        re.search(
            r"[A-Za-z]",
            text
        )
    )

    has_non_latin = bool(
        re.search(
            r"[^\x00-\x7F]",
            text
        )
    )

    mixed = (
        has_latin
        and has_non_latin
    )

    return {
        "detected": mixed,
        "languages": (
            ["latin", "non_latin"]
            if mixed
            else []
        )
    }


# =====================================================
# DETECT UNCLEAR RESPONSE
# =====================================================

def detect_unclear_response(text):

    text = normalize_text(text)

    if not text:

        return True

    words = text.split()

    unclear_patterns = [
        "i don't know",
        "i dont know",
        "not sure",
        "maybe",
        "what",
        "anything",
        "no idea"
    ]

    if len(words) < MIN_ANSWER_WORDS:

        return True

    if text.lower() in unclear_patterns:

        return True

    return False


# =====================================================
# RETRY MESSAGE
# =====================================================

def get_retry_message(
    error_type,
    retry_count
):

    if error_type == ErrorType.POOR_AUDIO:

        return (
            "I had difficulty hearing your response. "
            "Please speak clearly and try again."
        )

    if error_type == ErrorType.BACKGROUND_NOISE:

        return (
            "There seems to be significant background noise. "
            "If possible, please move to a quieter place "
            "and repeat your answer."
        )

    if error_type == ErrorType.MISSING_ANSWER:

        return (
            "I did not receive an answer. "
            "Please take your time and respond when ready."
        )

    if error_type == ErrorType.LOW_STT_CONFIDENCE:

        return (
            "I may not have captured your response correctly. "
            "Could you please repeat it?"
        )

    if error_type == ErrorType.LANGUAGE_MIXING:

        return (
            "I detected more than one language in the response. "
            "I will try to continue using the available transcript. "
            "Please repeat the answer if it was not captured correctly."
        )

    if error_type == ErrorType.UNCLEAR_RESPONSE:

        return (
            "I need a little more information to understand "
            "your answer. Could you please provide more details?"
        )

    return (
        "I could not process the response correctly. "
        "Please try again."
    )


# =====================================================
# CLARIFICATION QUESTION
# =====================================================

def get_clarification_question(
    original_question,
    category=None
):

    fallback_questions = {

        "skills":
            "Please mention the skills or technologies "
            "you are comfortable working with.",

        "experience":
            "Could you describe your work, internship, "
            "or project experience?",

        "salary":
            "Could you provide your expected salary "
            "or an approximate salary range?",

        "availability":
            "When would you be available to join?",

        "education":
            "Could you briefly describe your "
            "educational qualification?",

        "location":
            "Are you comfortable working from "
            "the required job location?"
    }

    if category in fallback_questions:

        return fallback_questions[
            category
        ]

    return (
        "Let me rephrase the question: "
        + original_question
    )


# =====================================================
# SAFE FALLBACK
# =====================================================

def safe_fallback(
    question_id,
    reason
):

    return {

        "question_id":
            question_id,

        "status":
            "UNRESOLVED",

        "action":
            ActionType.MANUAL_REVIEW,

        "score_action":
            "DO_NOT_AUTO_REJECT",

        "reason":
            reason,

        "message":
            (
                "The response could not be reliably processed. "
                "This item should be reviewed manually."
            )
    }


# =====================================================
# ERROR LOG
# =====================================================

def create_error_log(
    question_id,
    error_type,
    details=None
):

    return {

        "timestamp":
            datetime.utcnow().isoformat(),

        "question_id":
            question_id,

        "error_type":
            error_type,

        "details":
            details or {}
    }


# =====================================================
# EDGE CASE HANDLER
# =====================================================

class EdgeCaseHandler:

    def __init__(self):

        self.retry_counts = {}

        self.error_logs = []


    # =================================================
    # GET RETRY COUNT
    # =================================================

    def get_retry_count(
        self,
        question_id
    ):

        return self.retry_counts.get(
            question_id,
            0
        )


    # =================================================
    # ADD RETRY
    # =================================================

    def add_retry(
        self,
        question_id
    ):

        self.retry_counts[
            question_id
        ] = (
            self.get_retry_count(
                question_id
            ) + 1
        )

        return self.retry_counts[
            question_id
        ]


    # =================================================
    # RESET RETRIES
    # =================================================

    def reset_retry(
        self,
        question_id
    ):

        self.retry_counts[
            question_id
        ] = 0


    # =================================================
    # REGISTER ERROR
    # =================================================

    def register_error(
        self,
        question_id,
        error_type,
        details=None
    ):

        log = create_error_log(
            question_id,
            error_type,
            details
        )

        self.error_logs.append(
            log
        )


    # =================================================
    # HANDLE FAILURE
    # =================================================

    def handle_failure(
        self,
        question_id,
        error_type,
        original_question,
        category=None,
        details=None
    ):

        self.register_error(
            question_id,
            error_type,
            details
        )

        retry_count = self.add_retry(
            question_id
        )

        if retry_count <= MAX_RETRIES:

            return {

                "question_id":
                    question_id,

                "status":
                    "RETRY_REQUIRED",

                "error_type":
                    error_type,

                "retry_count":
                    retry_count,

                "action":
                    ActionType.RETRY,

                "message":
                    get_retry_message(
                        error_type,
                        retry_count
                    ),

                "clarification":
                    get_clarification_question(
                        original_question,
                        category
                    )
            }

        self.register_error(
            question_id,
            ErrorType.MAX_RETRIES,
            {
                "original_error":
                    error_type
            }
        )

        return safe_fallback(
            question_id,
            (
                f"Maximum retries reached "
                f"for {error_type}."
            )
        )


    # =================================================
    # PROCESS RESPONSE
    # =================================================

    def process_response(
        self,
        question_id,
        question,
        answer,
        category=None,
        stt_confidence=None,
        audio_quality=None,
        noise_level=None,
        detected_languages=None
    ):

        # ---------------------------------------------
        # 1. Missing Answer
        # ---------------------------------------------

        if detect_missing_answer(
            answer
        ):

            return self.handle_failure(

                question_id,

                ErrorType.MISSING_ANSWER,

                question,

                category,

                {
                    "answer":
                        answer
                }
            )


        # ---------------------------------------------
        # 2. Poor Audio
        # ---------------------------------------------

        audio_result = detect_poor_audio(

            audio_quality,

            stt_confidence

        )

        if audio_result[
            "detected"
        ]:

            error_type = (
                ErrorType.LOW_STT_CONFIDENCE
                if (
                    stt_confidence is not None
                    and
                    stt_confidence
                    < MIN_STT_CONFIDENCE
                )
                else ErrorType.POOR_AUDIO
            )

            return self.handle_failure(

                question_id,

                error_type,

                question,

                category,

                audio_result
            )


        # ---------------------------------------------
        # 3. Background Noise
        # ---------------------------------------------

        noise_result = (
            detect_background_noise(
                noise_level
            )
        )

        if (
            noise_result["detected"]
            and
            noise_result["severity"]
            == "High"
        ):

            return self.handle_failure(

                question_id,

                ErrorType.BACKGROUND_NOISE,

                question,

                category,

                noise_result
            )


        # ---------------------------------------------
        # 4. Language Mixing
        # ---------------------------------------------

        language_result = (
            detect_language_mixing(
                answer,
                detected_languages
            )
        )

        # Language mixing itself is NOT considered
        # an invalid answer.
        # Only request clarification if the transcript
        # is also unclear.

        if (
            language_result["detected"]
            and
            detect_unclear_response(
                answer
            )
        ):

            return self.handle_failure(

                question_id,

                ErrorType.LANGUAGE_MIXING,

                question,

                category,

                language_result
            )


        # ---------------------------------------------
        # 5. Unclear Response
        # ---------------------------------------------

        if detect_unclear_response(
            answer
        ):

            return self.handle_failure(

                question_id,

                ErrorType.UNCLEAR_RESPONSE,

                question,

                category,

                {
                    "answer":
                        answer
                }
            )


        # ---------------------------------------------
        # VALID RESPONSE
        # ---------------------------------------------

        self.reset_retry(
            question_id
        )

        return {

            "question_id":
                question_id,

            "status":
                "SUCCESS",

            "action":
                ActionType.ACCEPT,

            "answer":
                normalize_text(
                    answer
                ),

            "audio_quality":
                audio_quality,

            "stt_confidence":
                stt_confidence,

            "noise":
                noise_result,

            "language_analysis":
                language_result,

            "message":
                "Response accepted successfully."
        }


    # =================================================
    # GET ERROR REPORT
    # =================================================

    def get_error_report(self):

        return {

            "generated_at":
                datetime.utcnow().isoformat(),

            "total_errors":
                len(
                    self.error_logs
                ),

            "retry_counts":
                self.retry_counts,

            "errors":
                self.error_logs
        }


# =====================================================
# SAFE SYSTEM WRAPPER
# =====================================================

def safely_process_response(
    handler,
    **kwargs
):

    try:

        return handler.process_response(
            **kwargs
        )

    except Exception as error:

        question_id = kwargs.get(
            "question_id",
            "UNKNOWN"
        )

        handler.register_error(

            question_id,

            ErrorType.SYSTEM_ERROR,

            {
                "error":
                    str(error)
            }
        )

        return {

            "question_id":
                question_id,

            "status":
                "SYSTEM_FALLBACK",

            "action":
                ActionType.SAFE_FALLBACK,

            "score_action":
                "DO_NOT_AUTO_REJECT",

            "message":
                (
                    "The response could not be processed "
                    "because of a system error. "
                    "The item has been marked for review."
                )
        }


# =====================================================
# SAVE REPORT
# =====================================================

def save_error_report(
    report,
    filename="ats_engine/edge_case_report.json"
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
# TEST CASES
# =====================================================

TEST_CASES = [

    # ---------------------------------------------
    # Normal Response
    # ---------------------------------------------

    {
        "name":
            "Normal Response",

        "question_id":
            "SKILL_001",

        "question":
            "What are your strongest technical skills?",

        "category":
            "skills",

        "answer":
            "My strongest skills are Python, Django and SQL.",

        "stt_confidence":
            0.95,

        "audio_quality":
            0.90,

        "noise_level":
            0.10,

        "detected_languages":
            ["English"]
    },

    # ---------------------------------------------
    # Poor Audio
    # ---------------------------------------------

    {
        "name":
            "Poor Audio",

        "question_id":
            "EXP_001",

        "question":
            "Tell me about your work experience.",

        "category":
            "experience",

        "answer":
            "I worked as a software developer.",

        "stt_confidence":
            0.35,

        "audio_quality":
            0.30,

        "noise_level":
            0.20,

        "detected_languages":
            ["English"]
    },

    # ---------------------------------------------
    # Missing Answer
    # ---------------------------------------------

    {
        "name":
            "Missing Answer",

        "question_id":
            "SALARY_001",

        "question":
            "What are your salary expectations?",

        "category":
            "salary",

        "answer":
            "",

        "stt_confidence":
            None,

        "audio_quality":
            None,

        "noise_level":
            None,

        "detected_languages":
            []
    },

    # ---------------------------------------------
    # Background Noise
    # ---------------------------------------------

    {
        "name":
            "Background Noise",

        "question_id":
            "NOTICE_001",

        "question":
            "When can you join?",

        "category":
            "availability",

        "answer":
            "I can join immediately.",

        "stt_confidence":
            0.80,

        "audio_quality":
            0.70,

        "noise_level":
            0.85,

        "detected_languages":
            ["English"]
    },

    # ---------------------------------------------
    # Language Mixing
    # ---------------------------------------------

    {
        "name":
            "Language Mixing",

        "question_id":
            "SKILL_002",

        "question":
            "Describe your technical experience.",

        "category":
            "skills",

        "answer":
            (
                "I have experience in Python and Django "
                "and ഞാൻ academic projects ചെയ്തിട്ടുണ്ട്."
            ),

        "stt_confidence":
            0.82,

        "audio_quality":
            0.80,

        "noise_level":
            0.15,

        "detected_languages":
            [
                "English",
                "Malayalam"
            ]
    }

]


# =====================================================
# RUN EDGE CASE TESTS
# =====================================================

def run_edge_case_tests():

    handler = EdgeCaseHandler()

    results = []

    for test in TEST_CASES:

        result = safely_process_response(

            handler,

            question_id=
                test["question_id"],

            question=
                test["question"],

            answer=
                test["answer"],

            category=
                test["category"],

            stt_confidence=
                test["stt_confidence"],

            audio_quality=
                test["audio_quality"],

            noise_level=
                test["noise_level"],

            detected_languages=
                test["detected_languages"]
        )

        results.append({

            "test_name":
                test["name"],

            "result":
                result
        })

    report = {

        "report_name":
            "Zecpath AI Edge Case "
            "and Failure Handling Report",

        "generated_at":
            datetime.utcnow().isoformat(),

        "total_tests":
            len(TEST_CASES),

        "test_results":
            results,

        "error_summary":
            handler.get_error_report()
    }

    return report


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print(
        "=" * 60
    )

    print(
        "Zecpath AI - Edge Case & Failure Handling"
    )

    print(
        "=" * 60
    )

    report = run_edge_case_tests()

    filename = save_error_report(
        report
    )

    for test in report[
        "test_results"
    ]:

        print(
            "\nTest:",
            test["test_name"]
        )

        print(
            "Status:",
            test[
                "result"
            ].get(
                "status"
            )
        )

        print(
            "Action:",
            test[
                "result"
            ].get(
                "action"
            )
        )

        print(
            "Message:",
            test[
                "result"
            ].get(
                "message"
            )
        )

    print(
        "\nReport generated successfully."
    )

    print(
        f"Saved to: {filename}"
    )