import json
import os
from datetime import datetime, timedelta
from collections import defaultdict


# =====================================================
# INTEGRITY CONFIGURATION
# =====================================================

INTEGRITY_CONFIG = {

    # Tab switching
    "tab_switch_warning": 3,
    "tab_switch_high": 6,

    # Browser/window focus loss
    "focus_loss_warning": 3,
    "focus_loss_high": 6,

    # Multiple-speaker events
    "multi_speaker_warning": 2,
    "multi_speaker_high": 4,

    # Camera attention-loss events supplied by client.
    # Do not infer identity, emotion, health, or protected traits.
    "attention_loss_warning": 4,
    "attention_loss_high": 8,

    # Pattern detection
    "pattern_window_seconds": 60,
    "rapid_event_threshold": 4,

    # Maximum overall flag value
    "max_risk_score": 100
}


# =====================================================
# EVENT TYPES
# =====================================================

class IntegrityEvent:

    TAB_SWITCH = "TAB_SWITCH"

    FOCUS_LOSS = "FOCUS_LOSS"

    MULTIPLE_SPEAKERS = "MULTIPLE_SPEAKERS"

    ATTENTION_LOSS = "ATTENTION_LOSS"

    SCREEN_SHARE_STOPPED = "SCREEN_SHARE_STOPPED"

    CAMERA_UNAVAILABLE = "CAMERA_UNAVAILABLE"

    AUDIO_INTERRUPTION = "AUDIO_INTERRUPTION"


# =====================================================
# RISK LEVELS
# =====================================================

class RiskLevel:

    LOW = "LOW"

    MODERATE = "MODERATE"

    HIGH = "HIGH"

    REVIEW_REQUIRED = "REVIEW_REQUIRED"


# =====================================================
# ACTION TYPES
# =====================================================

class IntegrityAction:

    CONTINUE = "CONTINUE"

    WARNING = "WARNING"

    LOG_EVENT = "LOG_EVENT"

    REVIEW = "REVIEW"


# =====================================================
# CREATE EVENT
# =====================================================

def create_event(
    event_type,
    metadata=None,
    timestamp=None
):

    if timestamp is None:

        timestamp = (
            datetime.utcnow()
            .isoformat()
        )

    return {

        "event_type":
            event_type,

        "timestamp":
            timestamp,

        "metadata":
            metadata or {}
    }


# =====================================================
# COUNT EVENTS
# =====================================================

def count_events(
    events,
    event_type
):

    return sum(

        1

        for event in events

        if event.get(
            "event_type"
        ) == event_type
    )


# =====================================================
# EVENT SEVERITY
# =====================================================

def get_event_severity(
    event_type,
    count
):

    if event_type == IntegrityEvent.TAB_SWITCH:

        if count >= INTEGRITY_CONFIG[
            "tab_switch_high"
        ]:

            return "HIGH"

        elif count >= INTEGRITY_CONFIG[
            "tab_switch_warning"
        ]:

            return "MODERATE"


    elif event_type == IntegrityEvent.FOCUS_LOSS:

        if count >= INTEGRITY_CONFIG[
            "focus_loss_high"
        ]:

            return "HIGH"

        elif count >= INTEGRITY_CONFIG[
            "focus_loss_warning"
        ]:

            return "MODERATE"


    elif event_type == IntegrityEvent.MULTIPLE_SPEAKERS:

        if count >= INTEGRITY_CONFIG[
            "multi_speaker_high"
        ]:

            return "HIGH"

        elif count >= INTEGRITY_CONFIG[
            "multi_speaker_warning"
        ]:

            return "MODERATE"


    elif event_type == IntegrityEvent.ATTENTION_LOSS:

        if count >= INTEGRITY_CONFIG[
            "attention_loss_high"
        ]:

            return "HIGH"

        elif count >= INTEGRITY_CONFIG[
            "attention_loss_warning"
        ]:

            return "MODERATE"


    return "LOW"


# =====================================================
# EVENT RISK POINTS
# =====================================================

def calculate_event_points(
    event_type,
    count
):

    severity = get_event_severity(
        event_type,
        count
    )

    point_map = {

        "LOW": 0,

        "MODERATE": 10,

        "HIGH": 20
    }

    return point_map[
        severity
    ]


# =====================================================
# DETECT RAPID EVENT PATTERNS
# =====================================================

def detect_rapid_patterns(
    events
):

    if not events:

        return {
            "detected": False,
            "patterns": []
        }

    parsed_events = []

    for event in events:

        try:

            timestamp = (
                datetime.fromisoformat(
                    event[
                        "timestamp"
                    ]
                )
            )

            parsed_events.append(
                (
                    timestamp,
                    event
                )
            )

        except Exception:

            continue


    parsed_events.sort(
        key=lambda item: item[0]
    )


    patterns = []

    window_seconds = (
        INTEGRITY_CONFIG[
            "pattern_window_seconds"
        ]
    )

    threshold = (
        INTEGRITY_CONFIG[
            "rapid_event_threshold"
        ]
    )


    for index in range(
        len(parsed_events)
    ):

        start_time = (
            parsed_events[
                index
            ][0]
        )

        end_time = (
            start_time
            +
            timedelta(
                seconds=window_seconds
            )
        )

        window_events = [

            event

            for timestamp, event
            in parsed_events[index:]

            if timestamp <= end_time
        ]


        if len(
            window_events
        ) >= threshold:

            patterns.append({

                "start_time":
                    start_time.isoformat(),

                "event_count":
                    len(
                        window_events
                    ),

                "window_seconds":
                    window_seconds,

                "event_types":
                    list({
                        event[
                            "event_type"
                        ]

                        for event
                        in window_events
                    })
            })


    return {

        "detected":
            len(patterns) > 0,

        "patterns":
            patterns
    }


# =====================================================
# CROSS-SIGNAL PATTERN DETECTION
# =====================================================

def detect_combined_patterns(
    event_counts
):

    flags = []

    tab_switches = event_counts.get(
        IntegrityEvent.TAB_SWITCH,
        0
    )

    focus_losses = event_counts.get(
        IntegrityEvent.FOCUS_LOSS,
        0
    )

    multiple_speakers = event_counts.get(
        IntegrityEvent.MULTIPLE_SPEAKERS,
        0
    )

    attention_losses = event_counts.get(
        IntegrityEvent.ATTENTION_LOSS,
        0
    )


    # ---------------------------------------------
    # Tab switching + focus loss
    # ---------------------------------------------

    if (
        tab_switches >= 3
        and
        focus_losses >= 3
    ):

        flags.append({

            "pattern":
                "REPEATED_BROWSER_CONTEXT_CHANGE",

            "severity":
                "MODERATE",

            "description":
                (
                    "Repeated tab switching and "
                    "window focus loss were observed."
                )
        })


    # ---------------------------------------------
    # Multiple speakers + focus change
    # ---------------------------------------------

    if (
        multiple_speakers >= 2
        and
        focus_losses >= 2
    ):

        flags.append({

            "pattern":
                "MULTI_SIGNAL_REVIEW",

            "severity":
                "MODERATE",

            "description":
                (
                    "Multiple-speaker activity and "
                    "focus changes occurred during "
                    "the same interview session."
                )
        })


    # ---------------------------------------------
    # Repeated attention-loss events
    # ---------------------------------------------

    if attention_losses >= (
        INTEGRITY_CONFIG[
            "attention_loss_high"
        ]
    ):

        flags.append({

            "pattern":
                "REPEATED_ATTENTION_EVENT",

            "severity":
                "MODERATE",

            "description":
                (
                    "A high number of client-reported "
                    "attention-loss events was recorded."
                )
        })


    return flags


# =====================================================
# WARNING MESSAGE
# =====================================================

def generate_warning(
    event_type
):

    messages = {

        IntegrityEvent.TAB_SWITCH:
            (
                "Please keep the interview tab active "
                "unless you need to access a resource "
                "explicitly permitted by the interviewer."
            ),

        IntegrityEvent.FOCUS_LOSS:
            (
                "The interview window has repeatedly "
                "lost focus. Please return to the "
                "interview when ready."
            ),

        IntegrityEvent.MULTIPLE_SPEAKERS:
            (
                "Additional speech activity was detected. "
                "Please ensure your response represents "
                "your own answer unless collaboration "
                "has been permitted."
            ),

        IntegrityEvent.ATTENTION_LOSS:
            (
                "Repeated attention events were recorded. "
                "Please continue focusing on the interview "
                "where possible."
            ),

        IntegrityEvent.SCREEN_SHARE_STOPPED:
            (
                "Screen sharing appears to have stopped. "
                "Please restore it if required for this interview."
            )
    }

    return messages.get(

        event_type,

        (
            "An interview integrity event was detected "
            "and has been recorded."
        )
    )


# =====================================================
# INTEGRITY MONITOR
# =====================================================

class IntegrityMonitor:

    def __init__(
        self,
        candidate_id,
        session_id
    ):

        self.candidate_id = (
            candidate_id
        )

        self.session_id = (
            session_id
        )

        self.events = []

        self.warnings = []

        self.started_at = (
            datetime.utcnow()
            .isoformat()
        )


    # =================================================
    # RECORD EVENT
    # =================================================

    def record_event(
        self,
        event_type,
        metadata=None,
        timestamp=None
    ):

        event = create_event(

            event_type=
                event_type,

            metadata=
                metadata,

            timestamp=
                timestamp
        )

        self.events.append(
            event
        )

        count = count_events(

            self.events,

            event_type
        )

        severity = (
            get_event_severity(
                event_type,
                count
            )
        )


        # ---------------------------------------------
        # Warning generation
        # ---------------------------------------------

        warning = None

        if severity in [
            "MODERATE",
            "HIGH"
        ]:

            warning = {

                "event_type":
                    event_type,

                "severity":
                    severity,

                "message":
                    generate_warning(
                        event_type
                    ),

                "timestamp":
                    datetime.utcnow()
                    .isoformat()
            }

            self.warnings.append(
                warning
            )


        return {

            "event":
                event,

            "event_count":
                count,

            "severity":
                severity,

            "warning":
                warning
        }


    # =================================================
    # EVENT SUMMARY
    # =================================================

    def get_event_counts(self):

        counts = defaultdict(
            int
        )

        for event in self.events:

            counts[
                event[
                    "event_type"
                ]
            ] += 1

        return dict(
            counts
        )


    # =================================================
    # RISK SCORE
    # =================================================

    def calculate_risk_score(self):

        event_counts = (
            self.get_event_counts()
        )

        score = 0

        monitored_types = [

            IntegrityEvent.TAB_SWITCH,

            IntegrityEvent.FOCUS_LOSS,

            IntegrityEvent.MULTIPLE_SPEAKERS,

            IntegrityEvent.ATTENTION_LOSS
        ]


        for event_type in monitored_types:

            count = event_counts.get(
                event_type,
                0
            )

            score += (
                calculate_event_points(
                    event_type,
                    count
                )
            )


        # ---------------------------------------------
        # Rapid event pattern
        # ---------------------------------------------

        rapid_pattern = (
            detect_rapid_patterns(
                self.events
            )
        )

        if rapid_pattern[
            "detected"
        ]:

            score += 10


        # ---------------------------------------------
        # Combined patterns
        # ---------------------------------------------

        combined = (
            detect_combined_patterns(
                event_counts
            )
        )

        score += min(
            len(combined) * 10,
            20
        )


        return min(

            score,

            INTEGRITY_CONFIG[
                "max_risk_score"
            ]
        )


    # =================================================
    # RISK LEVEL
    # =================================================

    def get_risk_level(self):

        score = (
            self.calculate_risk_score()
        )

        if score >= 60:

            return RiskLevel.REVIEW_REQUIRED

        elif score >= 40:

            return RiskLevel.HIGH

        elif score >= 20:

            return RiskLevel.MODERATE

        return RiskLevel.LOW


    # =================================================
    # REPORT
    # =================================================

    def generate_report(self):

        event_counts = (
            self.get_event_counts()
        )

        rapid_patterns = (
            detect_rapid_patterns(
                self.events
            )
        )

        combined_patterns = (
            detect_combined_patterns(
                event_counts
            )
        )

        risk_score = (
            self.calculate_risk_score()
        )

        risk_level = (
            self.get_risk_level()
        )


        return {

            "report_type":
                "Interview Integrity Review",

            "candidate_id":
                self.candidate_id,

            "session_id":
                self.session_id,

            "generated_at":
                datetime.utcnow()
                .isoformat(),

            "event_counts":
                event_counts,

            "total_events":
                len(
                    self.events
                ),

            "risk_score":
                risk_score,

            "risk_level":
                risk_level,

            "rapid_event_patterns":
                rapid_patterns,

            "combined_patterns":
                combined_patterns,

            "warnings":
                self.warnings,

            "events":
                self.events,

            "recommended_action":
                self.get_recommended_action(
                    risk_level
                ),

            "review_note":
                (
                    "Integrity signals are indicators only. "
                    "They do not prove malpractice and must "
                    "be reviewed in context before any "
                    "employment decision is made."
                )
        }


    # =================================================
    # RECOMMENDED ACTION
    # =================================================

    def get_recommended_action(
        self,
        risk_level
    ):

        if risk_level == RiskLevel.LOW:

            return {

                "action":
                    IntegrityAction.CONTINUE,

                "message":
                    "No significant integrity pattern detected."
            }


        elif risk_level == RiskLevel.MODERATE:

            return {

                "action":
                    IntegrityAction.LOG_EVENT,

                "message":
                    (
                        "Integrity events were recorded. "
                        "Continue the interview and retain "
                        "the events for review."
                    )
            }


        elif risk_level == RiskLevel.HIGH:

            return {

                "action":
                    IntegrityAction.WARNING,

                "message":
                    (
                        "Repeated integrity events were "
                        "detected. A recruiter should "
                        "review the interview evidence."
                    )
            }


        return {

            "action":
                IntegrityAction.REVIEW,

            "message":
                (
                    "Multiple integrity signals were observed. "
                    "Manual review is required. Do not make "
                    "an automatic candidate rejection."
                )
        }


# =====================================================
# SAVE REPORT
# =====================================================

def save_integrity_report(
    report,
    filename=
        "technical_interview/integrity_report.json"
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

    monitor = IntegrityMonitor(

        candidate_id=
            "C101",

        session_id=
            "TECH_SESSION_001"
    )


    # ---------------------------------------------
    # Simulated interview events
    # ---------------------------------------------

    monitor.record_event(
        IntegrityEvent.TAB_SWITCH
    )

    monitor.record_event(
        IntegrityEvent.TAB_SWITCH
    )

    monitor.record_event(
        IntegrityEvent.TAB_SWITCH
    )

    monitor.record_event(
        IntegrityEvent.FOCUS_LOSS
    )

    monitor.record_event(
        IntegrityEvent.FOCUS_LOSS
    )

    monitor.record_event(
        IntegrityEvent.MULTIPLE_SPEAKERS,
        metadata={
            "speaker_activity_count": 2
        }
    )


    report = (
        monitor.generate_report()
    )

    filename = (
        save_integrity_report(
            report
        )
    )


    print(
        "=" * 65
    )

    print(
        "Zecpath AI - Integrity Detection Framework"
    )

    print(
        "=" * 65
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