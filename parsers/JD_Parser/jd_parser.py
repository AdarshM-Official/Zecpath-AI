import os
import re
import json


# =========================================================
# 1. SKILL DATABASE
# =========================================================
SKILLS_DB = [

    # Marine Core
    "marine engineering",
    "marine systems",
    "marine operations",
    "shipbuilding",
    "naval architecture",
    "ocean engineering",

    # Mechanical
    "mechanical troubleshooting",
    "maintenance planning",
    "propulsion systems",
    "hydraulics",
    "thermodynamics",
    "fluid mechanics",

    # Electrical
    "electrical systems",
    "power systems",
    "automation systems",
    "plc",
    "scada",
    "control systems",

    # Software / AI
    "python",
    "tensorflow",
    "pytorch",
    "machine learning",
    "artificial intelligence",
    "computer vision",
    "data analysis",

    # CAD / Design
    "autocad",
    "solidworks",
    "rhino",
    "maxsurf",
    "ansys",
    "catia",
    "aveva marine",

    # Offshore
    "subsea engineering",
    "rov systems",
    "pipeline engineering",
    "offshore safety",

    # Safety
    "risk assessment",
    "hazop",
    "fmea",
    "safety management",

    # Management
    "project management",
    "leadership",
    "budget management",
    "logistics planning",

    # Research
    "research methodology",
    "experimental design",
    "innovation",
    "critical thinking"
]


# =========================================================
# 2. ROLE DATABASE
# =========================================================
ROLE_DB = [

    "chief engineer",
    "second engineer",
    "third engineer",
    "fourth engineer",
    "junior engineer",
    "electro-technical officer",
    "naval architect",
    "marine design engineer",
    "hull structure engineer",
    "outfitting engineer",
    "marine cad engineer",
    "shipyard production engineer",
    "shipbuilding project engineer",
    "marine maintenance engineer",
    "dry dock engineer",
    "ship repair engineer",
    "inspection engineer",
    "marine service engineer",
    "technical superintendent",
    "offshore marine engineer",
    "subsea engineer",
    "fpso engineer",
    "drilling support engineer",
    "marine operations engineer",
    "rov engineer",
    "pipeline installation engineer",
    "marine electrical engineer",
    "marine automation engineer",
    "marine hvac engineer",
    "marine control systems engineer",
    "propulsion engineer",
    "marine corrosion engineer",
    "noise & vibration engineer",
    "marine surveyor",
    "classification society surveyor",
    "qa/qc engineer",
    "marine safety officer",
    "hse engineer",
    "risk & reliability engineer",
    "marine r&d engineer",
    "hydrodynamics engineer",
    "ocean engineering specialist",
    "marine simulation engineer",
    "green ship technology engineer",
    "autonomous ship engineer",
    "marine ai systems engineer",
    "electric & hybrid ship engineer",
    "smart port systems engineer",
    "ocean renewable energy engineer",
    "underwater robotics engineer",
    "digital twin engineer",
    "fleet manager",
    "marine project manager",
    "port engineer",
    "shipping operations manager",
    "logistics & maritime manager",
    "technical manager",
    "graduate marine engineer",
    "trainee marine engineer",
    "junior design engineer",
    "shipyard trainee",
    "offshore trainee engineer",
    "marine consultant",
    "ship design freelancer",
    "marine survey consultant",
    "simulation & cfd expert",
    "maritime safety consultant"
]


# =========================================================
# 3. CLEAN TEXT
# =========================================================
def clean_text(text):

    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    return text.strip()


# =========================================================
# 4. EXTRACT ROLE
# =========================================================
def extract_role(text):

    text_lower = text.lower()

    for role in ROLE_DB:

        if role in text_lower:
            return role.title()

    return "Unknown"


# =========================================================
# 5. EXTRACT SKILLS
# =========================================================
def extract_skills(text):

    text_lower = text.lower()

    found_skills = []

    for skill in SKILLS_DB:

        if skill in text_lower:
            found_skills.append(skill.title())

    return sorted(list(set(found_skills)))


# =========================================================
# 6. EXTRACT EXPERIENCE
# =========================================================
def extract_experience(text):

    patterns = [

        r'(\d+\s*[–-]\s*\d+\+?\s*years)',
        r'(\d+\+?\s*years)',
        r'(\d+\s*[–-]\s*\d+\+?\s*yrs)',
        r'(\d+\+?\s*yrs)'
    ]

    for pattern in patterns:

        match = re.search(pattern, text.lower())

        if match:
            return match.group()

    return "Not Mentioned"


# =========================================================
# 7. EXTRACT EDUCATION
# =========================================================
def extract_education(text):

    education_keywords = [

        "b.tech",
        "b.e",
        "m.tech",
        "phd",
        "marine engineering",
        "naval architecture",
        "ocean engineering",
        "mechanical engineering",
        "electrical engineering",
        "robotics",
        "mechatronics"
    ]

    text_lower = text.lower()

    found_education = []

    for edu in education_keywords:

        if edu in text_lower:
            found_education.append(edu.title())

    return list(set(found_education))


# =========================================================
# 8. EXTRACT SALARY
# =========================================================
def extract_salary(text):

    pattern = r'(\$[\d,]+\s*[–-]\s*\$?[\d,]+(?:\+)?\/month)'

    match = re.search(pattern, text)

    if match:
        return match.group()

    return "Not Mentioned"


# =========================================================
# 9. EXTRACT RESPONSIBILITIES
# =========================================================
def extract_responsibilities(text):

    responsibilities = []

    lines = text.split("\n")

    capture = False

    for line in lines:

        line_lower = line.lower().strip()

        if "responsibilities" in line_lower:
            capture = True
            continue

        if capture:

            if (
                "skills" in line_lower or
                "qualifications" in line_lower or
                "salary" in line_lower
            ):
                break

            if line.strip().startswith("•"):
                responsibilities.append(
                    line.replace("•", "").strip()
                )

    return responsibilities


# =========================================================
# 10. BUILD JD OBJECT
# =========================================================
def parse_job_description(text):

    cleaned_text = clean_text(text)

    jd_data = {

        "role": extract_role(cleaned_text),

        "skills": extract_skills(cleaned_text),

        "experience": extract_experience(cleaned_text),

        "education": extract_education(cleaned_text),

        "salary_range": extract_salary(cleaned_text),

        "responsibilities": extract_responsibilities(text)
    }

    return jd_data


# =========================================================
# 11. PROCESS SINGLE JD FILE
# =========================================================
def process_jd_file(input_path, output_path):

    with open(input_path, "r", encoding="utf-8") as file:

        jd_text = file.read()

    parsed_data = parse_job_description(jd_text)

    with open(output_path, "w", encoding="utf-8") as output:

        json.dump(parsed_data, output, indent=4)

    print(f"✅ Parsed: {os.path.basename(input_path)}")


# =========================================================
# 12. PROCESS ALL JDs
# =========================================================
def process_all_jds(input_folder, output_folder):

    os.makedirs(output_folder, exist_ok=True)

    logs = []

    for file_name in os.listdir(input_folder):

        input_path = os.path.join(input_folder, file_name)

        output_path = os.path.join(

            output_folder,

            file_name.split(".")[0] + ".json"
        )

        try:

            process_jd_file(input_path, output_path)

            logs.append(f"{file_name} --> SUCCESS")

        except Exception as e:

            logs.append(f"{file_name} --> FAILED ({str(e)})")

    # Save Logs
    with open("jd_testlogs.txt", "w", encoding="utf-8") as log_file:

        for log in logs:
            log_file.write(log + "\n")

    print("\n✅ JD Parsing Completed")
    print("📄 Logs saved: jd_testlogs.txt")


# =========================================================
# 13. RUN
# =========================================================
if __name__ == "__main__":

    INPUT_FOLDER = "aiproject/data/JD"

    OUTPUT_FOLDER = "aiproject/data/cleaned_jd"

    process_all_jds(INPUT_FOLDER, OUTPUT_FOLDER)