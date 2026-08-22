import re

# ==========================================
# Master Skill Dictionary
# ==========================================

SKILL_DB = {

    # Programming
    "python": ["python", "py"],
    "java": ["java"],
    "c": ["c"],
    "c++": ["c++", "cpp"],
    "javascript": ["javascript", "js"],
    "php": ["php"],

    # Frameworks
    "django": ["django"],
    "flask": ["flask"],
    "react": ["react", "reactjs"],
    "angular": ["angular"],
    "vue": ["vue"],
    "node": ["node", "nodejs"],
    "express": ["express", "expressjs"],

    # Databases
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo"],
    "sqlite": ["sqlite"],

    # Cloud
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud"],

    # AI
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"],
    "nlp": ["nlp"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "openai": ["openai", "chatgpt"],
    "rag": ["rag"],

    # Office
    "excel": ["excel", "ms excel"],

    # Soft Skills
    "communication": ["communication", "communication skills"],
    "leadership": ["leadership", "team leadership"],
    "teamwork": ["teamwork"],
    "problem solving": ["problem solving"],
    "critical thinking": ["critical thinking"]
}

# ==========================================
# Skill Stack Mapping
# ==========================================

SKILL_STACKS = {

    "mern": [
        "mongodb",
        "express",
        "react",
        "node"
    ],

    "mean": [
        "mongodb",
        "express",
        "angular",
        "node"
    ],

    "lamp": [
        "linux",
        "apache",
        "mysql",
        "php"
    ]
}


# ==========================================
# Category Mapping
# ==========================================

CATEGORY = {

    "python": "Programming",
    "java": "Programming",
    "c": "Programming",
    "c++": "Programming",
    "javascript": "Programming",
    "php": "Programming",

    "django": "Backend",
    "flask": "Backend",

    "react": "Frontend",
    "angular": "Frontend",
    "vue": "Frontend",

    "node": "Backend",
    "express": "Backend",

    "mysql": "Database",
    "postgresql": "Database",
    "mongodb": "Database",

    "aws": "Cloud",
    "azure": "Cloud",
    "gcp": "Cloud",

    "machine learning": "AI",
    "deep learning": "AI",
    "nlp": "AI",
    "tensorflow": "AI",
    "pytorch": "AI",
    "openai": "AI",
    "rag": "AI",

    "communication": "Soft Skill",
    "leadership": "Soft Skill",
    "teamwork": "Soft Skill",
    "problem solving": "Soft Skill",
    "critical thinking": "Soft Skill"
}


# ==========================================
# Text Cleaning
# ==========================================

def clean_text(text):

    # Just convert to lowercase. We don't remove special characters 
    # so we can still match skills like "c++" or "c#".
    return text.lower()


# ==========================================
# Skill Extraction
# ==========================================

def extract_skills(text):

    text = clean_text(text)

    extracted = []

    # Individual Skills

    for skill, variants in SKILL_DB.items():

        for variant in variants:

            # Ensure we match whole words and prevent substring matching (e.g. "c" in "react")
            pattern = r'(?<![a-z0-9])' + re.escape(variant) + r'(?![a-z0-9])'

            if re.search(pattern, text):

                extracted.append(skill)

                break

    # Skill Stacks

    for stack, skills in SKILL_STACKS.items():

        pattern = r'(?<![a-z0-9])' + re.escape(stack) + r'(?![a-z0-9])'

        if re.search(pattern, text):

            extracted.extend(skills)

    return sorted(list(set(extracted)))


# ==========================================
# Confidence Score
# ==========================================

def calculate_confidence(skill, text):

    text = text.lower()

    occurrences = 0

    # Count exact matches of variants
    for variant in SKILL_DB.get(skill, [skill]):
        pattern = r'(?<![a-z0-9])' + re.escape(variant) + r'(?![a-z0-9])'
        occurrences += len(re.findall(pattern, text))

    # Also count if the stack this skill belongs to was mentioned
    for stack, skills in SKILL_STACKS.items():
        if skill in skills:
            pattern = r'(?<![a-z0-9])' + re.escape(stack) + r'(?![a-z0-9])'
            occurrences += len(re.findall(pattern, text))

    if occurrences >= 3:
        return 0.95

    elif occurrences == 2:
        return 0.85

    elif occurrences >= 1:
        return 0.75

    return 0.0


# ==========================================
# Structured Output
# ==========================================

def extract_skills_with_confidence(text, candidate_id="C001"):

    skills = extract_skills(text)

    output = {

        "candidate_id": candidate_id,

        "skills": []

    }

    for skill in skills:

        output["skills"].append({

            "skill_name": skill.title(),

            "category": CATEGORY.get(skill, "Other"),

            "confidence": round(calculate_confidence(skill, text), 2),

            "source": "resume"

        })

    return output