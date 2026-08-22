import json
import os
from typing import List, Dict

class InterviewSummaryGenerator:
    """Generate a recruiter‑ready summary from answer history and HR report.

    The generator loads a JSON template that defines thresholds, cultural‑fit
    keywords and risk‑flag expressions.  The implementation is intentionally
    lightweight – it uses simple keyword matching and the numeric scores that
    are already present in the HR report.
    """

    DEFAULT_TEMPLATE = {
        "strength_threshold": 0.75,
        "weakness_threshold": 0.4,
        "cultural_fit_keywords": ["teamwork", "collaboration", "leadership", "adaptability"],
        "risk_categories": {
            "overconfidence": "confidence_score > 0.9",
            "contradiction": "consistency_score < 0.5",
            "hesitation": "detected_hesitation == true"
        }
    }

    def __init__(self, template_path: str = "config/summary_template.json"):
        self.template_path = template_path
        self.config = self._load_template(template_path)

    def _load_template(self, path: str) -> Dict:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                # Fallback to defaults if loading fails
                return self.DEFAULT_TEMPLATE
        else:
            return self.DEFAULT_TEMPLATE

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def generate_summary(self, answer_history: List[Dict], hr_report: Dict) -> Dict:
        """Create a structured summary.

        Parameters
        ----------
        answer_history: List of answer objects as stored in the conversation flow.
        hr_report: The latest HR report dict produced by ``HRScoringEngine``.
        """
        # Extract scores from the HR report
        metrics = hr_report.get("metrics", {})
        relevance = metrics.get("relevance", 0)
        communication = metrics.get("communication", 0)
        confidence = metrics.get("confidence", 0)
        consistency = metrics.get("consistency", 0)

        # Strengths / Weaknesses based on thresholds
        thresh_str = self.config.get("strength_threshold", 0.75)
        thresh_weak = self.config.get("weakness_threshold", 0.4)

        strengths = []
        weaknesses = []
        if relevance >= thresh_str:
            strengths.append("Relevant answers (high relevance score)")
        else:
            weaknesses.append("Low relevance in answers")
        if communication >= thresh_str:
            strengths.append("Clear communication")
        else:
            weaknesses.append("Communication could be clearer")
        if confidence >= thresh_str:
            strengths.append("Confident responses")
        else:
            weaknesses.append("Lack of confidence in some answers")
        if consistency >= thresh_str:
            strengths.append("Consistent narrative across answers")
        else:
            weaknesses.append("Inconsistent statements detected")

        # Cultural‑fit detection – simple keyword search in raw texts
        cultural_fit = []
        keywords = self.config.get("cultural_fit_keywords", [])
        for ans in answer_history:
            raw = ans.get("answer", {}).get("raw_text", "").lower()
            for kw in keywords:
                if kw.lower() in raw:
                    cultural_fit.append(kw)
        # Deduplicate while preserving order
        cultural_fit = list(dict.fromkeys(cultural_fit))

        # Risk flags – evaluate expressions from config
        risk_flags = []
        risk_cfg = self.config.get("risk_categories", {})
        # Provide a safe evaluation context
        ctx = {
            "confidence_score": confidence,
            "consistency_score": consistency,
            "detected_hesitation": any(ans.get("metadata", {}).get("hesitation", False) for ans in answer_history)
        }
        for name, expr in risk_cfg.items():
            try:
                if eval(expr, {}, ctx):
                    risk_flags.append(name)
            except Exception:
                continue

        # Inconsistencies – we already have a consistency score
        inconsistencies = []
        if consistency < thresh_weak:
            inconsistencies.append("Low consistency score indicates possible contradictions.")

        # Overall performance – reuse the final HR score if present
        overall_performance = hr_report.get("final_score", 0)

        summary = {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "cultural_fit": cultural_fit,
            "risk_flags": risk_flags,
            "inconsistencies": inconsistencies,
            "overall_performance": overall_performance,
            "metrics": metrics
        }
        return summary

    def render_report(self, summary: Dict) -> str:
        """Render the structured summary as a markdown narrative."""
        lines = []
        lines.append("# Candidate Interview Summary")
        lines.append("")
        lines.append(f"**Overall Performance:** {summary.get('overall_performance', 0):.1f}/100")
        lines.append("")
        def bullet(section, items):
            if not items:
                return
            lines.append(f"## {section}")
            lines.append("")
            for it in items:
                lines.append(f"- {it}")
            lines.append("")
        bullet("Strengths", summary.get("strengths", []))
        bullet("Weaknesses", summary.get("weaknesses", []))
        bullet("Cultural Fit Indicators", summary.get("cultural_fit", []))
        bullet("Risk Flags", summary.get("risk_flags", []))
        bullet("Inconsistencies", summary.get("inconsistencies", []))
        return "\n".join(lines)
