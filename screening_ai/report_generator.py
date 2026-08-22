import json
from datetime import datetime
from typing import Dict, Any, List

class ScreeningReportGenerator:
    def __init__(self):
        pass

    def extract_highlights(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key highlights like salary, availability, and confirmed skills."""
        highlights = {
            "salary_expectation": "Not Disclosed",
            "availability": "Not Disclosed",
            "confirmed_skills": []
        }
        
        for qa in raw_data.get("qa_sessions", []):
            entities = qa.get("extracted_entities", {})
            
            # Extract Salary
            if "salary" in entities and entities["salary"].get("amount"):
                salary_data = entities["salary"]
                highlights["salary_expectation"] = f"{salary_data['amount']} {salary_data.get('unit', '')}".strip()
            
            # Extract Availability
            if "availability" in entities and entities["availability"].get("start_time"):
                avail_data = entities["availability"]
                highlights["availability"] = "Immediate" if avail_data.get("immediate") else avail_data["start_time"]
                
            # Extract Skills
            if "skills" in entities and entities["skills"]:
                for skill in entities["skills"]:
                    if skill not in highlights["confirmed_skills"]:
                        highlights["confirmed_skills"].append(skill)
                        
        return highlights

    def determine_strengths_and_risks(self, raw_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Identify strengths, risks, and missing data based on scores and flags."""
        strengths = []
        risks = []
        missing_data = []
        
        # Analyze overall score
        final_score = raw_data.get("overall_score", 0)
        if final_score >= 80:
            strengths.append(f"Strong overall screening performance ({final_score}/100)")
        elif final_score < 60:
            risks.append(f"Low overall screening performance ({final_score}/100)")
            
        # Analyze answers
        for qa in raw_data.get("qa_sessions", []):
            q_topic = qa.get("intent", "general")
            score = qa.get("score", 0)
            
            if score >= 85:
                strengths.append(f"Excellent response regarding {q_topic}.")
            elif score < 50:
                risks.append(f"Weak or concerning response regarding {q_topic}.")
                
            # Missing Info
            quality = qa.get("quality", {})
            if quality.get("missing_information"):
                reason = quality.get("missing_reason", f"Incomplete details in {q_topic}")
                missing_data.append(reason)
                
            if quality.get("off_topic"):
                risks.append(f"Off-topic response detected when asked about {q_topic}.")
                
        # Deduplicate
        return {
            "strengths": list(set(strengths)),
            "risks": list(set(risks)),
            "missing_data": list(set(missing_data))
        }

    def generate_report(self, candidate_id: str, job_role: str, raw_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Build the structured recruiter-ready screening report."""
        
        highlights = self.extract_highlights(raw_evaluation)
        analysis = self.determine_strengths_and_risks(raw_evaluation)
        
        # Summarize Key Answers
        key_answers = []
        for qa in raw_evaluation.get("qa_sessions", []):
            key_answers.append({
                "question": qa.get("question"),
                "answer_summary": qa.get("answer", {}).get("raw_text", "No answer provided"),
                "score": qa.get("score", 0)
            })
            
        report = {
            "report_metadata": {
                "candidate_id": candidate_id,
                "job_role": job_role,
                "generated_at": datetime.utcnow().isoformat(),
                "final_recommendation": raw_evaluation.get("recommendation", "Review")
            },
            "executive_summary": {
                "overall_score": raw_evaluation.get("overall_score", 0),
                "strengths": analysis["strengths"],
                "risks": analysis["risks"],
                "missing_information": analysis["missing_data"]
            },
            "recruiter_highlights": highlights,
            "detailed_qa_summary": key_answers
        }
        
        return report

    def export_report(self, report: Dict[str, Any], filepath: str) -> None:
        """Export the report to JSON format."""
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=4)
