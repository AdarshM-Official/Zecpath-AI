import re
import json
import spacy
from collections import defaultdict

# =========================================================
# LOAD NLP MODEL
# =========================================================
nlp = spacy.load("en_core_web_sm")


# =========================================================
# MASTER SKILL DATABASE
# =========================================================
TECH_SKILLS = [
    "python",
    "java",
    "sql",
    "aws",
    "docker",
    "kubernetes",
    "react",
    "node.js",
    "mongodb",
    "express",
    "tensorflow",
    "pandas",
    "numpy",
    "machine learning",
    "deep learning",
    "django",
    "flask",
    "git"
]

BUSINESS_SKILLS = [
    "project management",
    "leadership",
    "communication",
    "agile",
    "scrum",
    "business analysis",
    "sales",
    "marketing"
]

CREATIVE_SKILLS = [
    "photoshop",
    "figma",
    "illustrator",
    "video editing",
    "ui/ux design",
    "content writing"
]

# Combine all skills
MASTER_SKILLS = set(
    TECH_SKILLS +
    BUSINESS_SKILLS +
    CREATIVE_SKILLS
)


# =========================================================
# SKILL SYNONYMS
# =========================================================
SKILL_SYNONYMS = {
    "py": "python",
    "js": "javascript",
    "ml": "machine learning",
    "ai": "artificial intelligence"
}


# =========================================================
# SKILL STACKS
# =========================================================
SKILL_STACKS = {
    "mern": [
        "mongodb",
        "express",
        "react",
        "node.js"
    ],

    "mean": [
        "mongodb",
        "express",
        "angular",
        "node.js"
    ]
}


# =========================================================
# CLEAN TEXT
# =========================================================
def clean_text(text):

    text = text.lower()

    # Remove weird symbols
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# =========================================================
# NORMALIZE SKILL
# =========================================================
def normalize_skill(skill):

    skill = skill.lower().strip()

    # Synonym normalization
    if skill in SKILL_SYNONYMS:
        skill = SKILL_SYNONYMS[skill]

    return skill


# =========================================================
# CONFIDENCE BOOSTER
# =========================================================
def boost_confidence(existing, value):

    updated = existing + value

    # Cap confidence at 1.0
    return round(min(updated, 1.0), 2)


# =========================================================
# EXTRACT SKILLS
# =========================================================
def extract_skills(text):

    cleaned_text = clean_text(text)

    extracted_skills = defaultdict(float)

    doc = nlp(cleaned_text)

    # -----------------------------------------------------
    # 1. DIRECT FULL-TEXT MATCHING
    # -----------------------------------------------------
    for skill in MASTER_SKILLS:

        if skill in cleaned_text:

            extracted_skills[skill] = boost_confidence(
                extracted_skills[skill],
                0.9
            )

    # -----------------------------------------------------
    # 2. TOKEN-LEVEL NLP MATCHING
    # -----------------------------------------------------
    for token in doc:

        token_text = normalize_skill(token.text)

        if token_text in MASTER_SKILLS:

            extracted_skills[token_text] = boost_confidence(
                extracted_skills[token_text],
                0.7
            )

    # -----------------------------------------------------
    # 3. HANDLE SKILL STACKS
    # -----------------------------------------------------
    for stack_name, stack_skills in SKILL_STACKS.items():

        if stack_name in cleaned_text:

            for skill in stack_skills:

                extracted_skills[skill] = boost_confidence(
                    extracted_skills[skill],
                    0.85
                )

    # -----------------------------------------------------
    # 4. BUILD FINAL STRUCTURED OUTPUT
    # -----------------------------------------------------
    final_output = []

    for skill, confidence in extracted_skills.items():

        # Skill category detection
        if skill in TECH_SKILLS:
            category = "Technical"

        elif skill in BUSINESS_SKILLS:
            category = "Business"

        elif skill in CREATIVE_SKILLS:
            category = "Creative"

        else:
            category = "Other"

        final_output.append({
            "skill": skill.title(),
            "category": category,
            "confidence": confidence
        })

    # -----------------------------------------------------
    # 5. SORT BY CONFIDENCE
    # -----------------------------------------------------
    final_output = sorted(
        final_output,
        key=lambda x: x["confidence"],
        reverse=True
    )

    return final_output


# =========================================================
# SAVE OUTPUT
# =========================================================
def save_output(skills, output_file="aiproject/parsers/skills/skills_output.json"):

    with open(output_file, "w", encoding="utf-8") as file:

        json.dump(skills, file, indent=4)

    print(f"\n✅ Skill output saved: {output_file}")


# =========================================================
# SAMPLE RESUME
# =========================================================
SAMPLE_RESUME = """
Python Developer with experience in AWS, Docker,
Machine Learning, MERN stack, and Agile methodology.

Worked with React and Node.js applications.
Excellent communication and leadership skills.

Experience with Django, Flask, Git, SQL,
and cloud deployment systems.
"""


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":

    print("\n🧠 Running Skill Extraction Engine...\n")

    extracted_skills = extract_skills(SAMPLE_RESUME)

    print(json.dumps(extracted_skills, indent=4))

    save_output(extracted_skills)