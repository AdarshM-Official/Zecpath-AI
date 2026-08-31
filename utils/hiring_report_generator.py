import os
from typing import Dict, Any
from datetime import datetime

class HiringReportGenerator:
    """
    Synthesizes raw data from all AI evaluation modules into a single, 
    recruiter-friendly Markdown report.
    """

    def __init__(self, output_dir: str = "reports"):
        # Resolve relative to project root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(base_dir, output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_report(self, candidate_id: str, role: str, master_data: Dict[str, Any]) -> str:
        """
        Generates the Markdown string for the report.
        """
        # 1. Extract data safely
        decision_data = master_data.get("final_decision", {})
        recommendation = decision_data.get("final_decision", "UNKNOWN")
        confidence = decision_data.get("decision_confidence", {}).get("score", 0.0)
        hiring_fit = decision_data.get("hiring_fit_score", 0.0)
        explanation = "\n".join(decision_data.get("explanation", []))

        integrity_risk = master_data.get("integrity_report", {}).get("integrity_risk_tag", "UNKNOWN")
        behavioral_risk = master_data.get("behavioral_report", {}).get("behavioral_context", {}).get("stress_indicator", 0.0)
        beh_risk_label = "HIGH" if behavioral_risk > 60 else "MODERATE" if behavioral_risk > 30 else "LOW"

        round_scores = master_data.get("round_scores", {})
        
        strengths = master_data.get("strengths", ["No strengths documented."])
        weaknesses = master_data.get("weaknesses", ["No weaknesses documented."])

        # 2. Build Markdown
        md = []
        md.append(f"# Zecpath-AI Candidate Evaluation Report")
        md.append(f"**Candidate ID:** {candidate_id}  ")
        md.append(f"**Role:** {role}  ")
        md.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
        md.append("\n---\n")

        # Executive Summary
        md.append("## 1. Executive Summary\n")
        
        # Color coding/emoji based on decision
        decision_badge = "🟢 **SELECTED**" if recommendation == "SELECTED" else "🟡 **HOLD REVIEW**" if recommendation == "HOLD_REVIEW" else "🔴 **REJECTED**"
        
        md.append(f"> [!IMPORTANT]")
        md.append(f"> **Final Recommendation:** {decision_badge} (Confidence: {confidence}%)")
        md.append(f"> **Hiring Fit Score:** {hiring_fit} / 100\n")
        
        md.append(f"- **Integrity Risk:** `{integrity_risk}`")
        md.append(f"- **Behavioral Stress:** `{beh_risk_label}` ({behavioral_risk}/100)")
        md.append(f"\n*AI Explanation:*\n> {explanation.replace(chr(10), chr(10)+'> ')}")
        md.append("\n---\n")

        # Strengths & Weaknesses
        md.append("## 2. Strengths & Weaknesses\n")
        md.append("### 💪 Key Strengths")
        for s in strengths:
            md.append(f"- {s}")
        
        md.append("\n### ⚠️ Key Weaknesses")
        for w in weaknesses:
            md.append(f"- {w}")
        md.append("\n---\n")

        # Stage-by-Stage
        md.append("## 3. Stage-by-Stage Breakdown\n")
        md.append("| Stage | Normalized Score (0-100) |")
        md.append("|:---|:---:|")
        for stage, score in round_scores.items():
            fmt_stage = stage.replace('_', ' ').title()
            md.append(f"| **{fmt_stage}** | `{score}` |")
        md.append("\n---\n")

        # Risk & Anomaly Indicators
        md.append("## 4. Risk & Anomaly Indicators\n")
        
        flags = master_data.get("integrity_report", {}).get("flags", [])
        if flags:
            md.append("> [!WARNING]")
            md.append("> **Integrity Alerts:**")
            for f in flags:
                sev = f.get('severity', 'UNK')
                emoji = "🚨" if sev == "HIGH" else "⚠️" if sev == "MEDIUM" else "ℹ️"
                md.append(f"> - {emoji} **[{sev}]** {f.get('description', '')}")
        else:
            md.append("> [!NOTE]")
            md.append("> **Integrity Alerts:** None detected.")

        md.append("\n**Behavioral Alerts:**")
        beh_note = master_data.get("behavioral_report", {}).get("behavioral_context", {}).get("recruiter_note", "")
        if beh_note:
            md.append(f"- {beh_note}")
        else:
            md.append("- *No notable behavioral anomalies.*")

        return "\n".join(md)

    def export_report(self, candidate_id: str, markdown_content: str) -> str:
        """
        Saves the markdown report to disk.
        """
        filename = f"{candidate_id}_evaluation_report.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        return filepath

__all__ = ["HiringReportGenerator"]
