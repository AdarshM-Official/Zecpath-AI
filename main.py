import json
from aiproject.ats_engine.skill_extractor import extract_skills_with_confidence

resume = """
Python Developer with Django experience.

Worked on MERN stack projects.

Good communication and leadership skills.
"""

result = extract_skills_with_confidence(resume, "C123")

# Save to JSON file
with open("aiproject/data/outputs/skills_output.json", "w") as f:
    json.dump(result, f, indent=4)

print("Output saved to skills_output.json")