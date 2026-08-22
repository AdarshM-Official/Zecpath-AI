import re
import json
from collections import defaultdict
import spacy

nlp = spacy.load("en_core_web_sm")

SECTION_KEYWORDS = {
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "technologies"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history"
    ],

    "education": [
        "education",
        "academic background",
        "qualifications"
    ],

    "projects": [
        "projects",
        "personal projects",
        "academic projects"
    ],

    "certifications": [
        "certifications",
        "licenses",
        "certificates"
    ],

    "summary": [
        "summary",
        "professional summary",
        "profile"
    ],

    "achievements": [
        "achievements",
        "awards",
        "accomplishments"
    ]
}


def clean_line(line):

    line = line.strip()

    line = re.sub(r"\s+", " ", line)

    line = re.sub(r"[^\x00-\x7F]+", " ", line)

    return line


def fix_layout(text):

    text = re.sub(r"\s{3,}", " ", text)

    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    return text


def detect_heading(line):

    line_lower = line.lower()

    for section, keywords in SECTION_KEYWORDS.items():

        for keyword in keywords:

            if keyword == line_lower:
                return section

    return None


def classify_line_nlp(line):

    text = line.lower()

    doc = nlp(text)

    if any(word in text for word in [
        "python",
        "java",
        "sql",
        "aws",
        "docker",
        "tensorflow",
        "machine learning",
        "react",
        "node.js"
    ]):
        return "skills"

    if any(word in text for word in [
        "university",
        "college",
        "school",
        "b.tech",
        "m.tech",
        "bachelor",
        "master",
        "degree"
    ]):
        return "education"

    if any(word in text for word in [
        "worked",
        "developed",
        "intern",
        "engineer",
        "company",
        "team",
        "responsible"
    ]):
        return "experience"

    if any(word in text for word in [
        "project",
        "built",
        "created",
        "designed",
        "implemented"
    ]):
        return "projects"

    if any(word in text for word in [
        "certified",
        "certificate",
        "certification"
    ]):
        return "certifications"

    return "unknown"


def segment_resume(text):

    sections = defaultdict(list)

    current_section = "unknown"

    text = fix_layout(text)

    lines = text.split("\n")

    for raw_line in lines:

        line = clean_line(raw_line)

        if not line:
            continue

        detected_section = detect_heading(line)

        if detected_section:
            current_section = detected_section
            continue

        predicted_section = classify_line_nlp(line)

        if current_section == "unknown":
            current_section = predicted_section

        sections[current_section].append(line)

    return dict(sections)


def save_output(data, output_file="segmented_resume.json"):

    with open(output_file, "w", encoding="utf-8") as file:

        json.dump(data, file, indent=4)

    print(f"\n✅ Segmented resume saved: {output_file}")


SAMPLE_RESUME = """
John Doe
Email: johndoe@gmail.com

Professional Summary
Backend Developer with 3 years experience in Python and Django.

Skills
Python
SQL
AWS
Docker
React

Experience
Software Engineer at ABC Company
Developed REST APIs using Django.
Worked with cloud deployment systems.

Education
B.Tech in Computer Science
XYZ University

Projects
Built ATS Resume Parser
Created AI Screening System

Certifications
AWS Certified Cloud Practitioner
"""
if __name__ == "__main__":

    print("\n🧠 Running Resume Section Segmenter...\n")

    segmented_data = segment_resume(SAMPLE_RESUME)

    print(json.dumps(segmented_data, indent=4))

    save_output(segmented_data)
