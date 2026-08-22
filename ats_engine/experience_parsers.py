import re
import json
from datetime import datetime
from difflib import SequenceMatcher

# ==========================================
# Job Titles Database
# ==========================================

JOB_TITLES = [
    "software engineer",
    "software developer",
    "python developer",
    "java developer",
    "backend developer",
    "frontend developer",
    "full stack developer",
    "web developer",
    "data analyst",
    "data scientist",
    "machine learning engineer",
    "project manager",
    "intern"
]

# ==========================================
# Company Extraction
# ==========================================

def extract_companies(text):
    """
    Extract company names using simple regex.
    Example:
    Software Engineer at Infosys
    Python Developer with TCS
    """

    pattern = r"(?:at|with)\s+([A-Z][A-Za-z0-9& ]+)"

    companies = re.findall(pattern, text)

    return list(set(companies))


# ==========================================
# Job Title Extraction
# ==========================================

def extract_job_titles(text):

    text = text.lower()

    titles = []

    for title in JOB_TITLES:

        if title in text:
            titles.append(title.title())

    return list(set(titles))


# ==========================================
# Employment Duration Extraction
# ==========================================

def extract_dates(text):

    pattern = r"([A-Za-z]{3,9}\s+\d{4})\s*[-–]\s*(Present|[A-Za-z]{3,9}\s+\d{4})"

    return re.findall(pattern, text)


# ==========================================
# Total Experience
# ==========================================

def calculate_total_experience(date_ranges):

    total_months = 0

    for start, end in date_ranges:

        try:

            start_date = datetime.strptime(start, "%b %Y")

        except:

            start_date = datetime.strptime(start, "%B %Y")

        if end.lower() == "present":

            end_date = datetime.today()

        else:

            try:

                end_date = datetime.strptime(end, "%b %Y")

            except:

                end_date = datetime.strptime(end, "%B %Y")

        months = (
            (end_date.year - start_date.year) * 12
            + end_date.month
            - start_date.month
        )

        total_months += months

    return round(total_months / 12, 2)


# ==========================================
# Gap Detection
# ==========================================

def detect_gaps(date_ranges):

    parsed = []

    for start, end in date_ranges:

        try:
            s = datetime.strptime(start, "%b %Y")
        except:
            s = datetime.strptime(start, "%B %Y")

        if end.lower() == "present":
            e = datetime.today()
        else:
            try:
                e = datetime.strptime(end, "%b %Y")
            except:
                e = datetime.strptime(end, "%B %Y")

        parsed.append((s, e))

    parsed.sort()

    gaps = []

    for i in range(len(parsed) - 1):

        end1 = parsed[i][1]

        start2 = parsed[i + 1][0]

        months = (
            (start2.year - end1.year) * 12
            + start2.month
            - end1.month
        )

        if months > 1:
            gaps.append(f"{months} month(s)")

    return gaps


# ==========================================
# Overlap Detection
# ==========================================

def detect_overlaps(date_ranges):

    parsed = []

    for start, end in date_ranges:

        try:
            s = datetime.strptime(start, "%b %Y")
        except:
            s = datetime.strptime(start, "%B %Y")

        if end.lower() == "present":
            e = datetime.today()
        else:
            try:
                e = datetime.strptime(end, "%b %Y")
            except:
                e = datetime.strptime(end, "%B %Y")

        parsed.append((s, e))

    parsed.sort()

    overlaps = 0

    for i in range(len(parsed) - 1):

        if parsed[i][1] > parsed[i + 1][0]:
            overlaps += 1

    return overlaps


# ==========================================
# Role Similarity
# ==========================================

def role_similarity(candidate_roles, required_role):

    best = 0

    for role in candidate_roles:

        score = SequenceMatcher(
            None,
            role.lower(),
            required_role.lower()
        ).ratio()

        best = max(best, score)

    return round(best, 2)


# ==========================================
# Experience Relevance
# ==========================================

def relevance_score(candidate_roles, required_role):

    score = role_similarity(candidate_roles, required_role)

    if score >= 0.80:
        return score, "Highly Relevant"

    elif score >= 0.60:
        return score, "Moderately Relevant"

    return score, "Low Relevance"


# ==========================================
# Main Experience Parser
# ==========================================

def parse_experience(text, candidate_id="C001", required_role="Software Engineer"):

    companies = extract_companies(text)

    titles = extract_job_titles(text)

    dates = extract_dates(text)

    total_exp = calculate_total_experience(dates)

    gaps = detect_gaps(dates)

    overlaps = detect_overlaps(dates)

    similarity, relevance = relevance_score(
        titles,
        required_role
    )

    output = {

        "candidate_id": candidate_id,

        "experience": {

            "companies": companies,

            "job_titles": titles,

            "employment_periods": dates,

            "total_experience_years": total_exp,

            "gaps": gaps,

            "overlaps": overlaps,

            "role_similarity": similarity,

            "relevance": relevance

        }

    }

    with open("aiproject/data/outputs/experience_output.json", "w") as f:
        json.dump(output, f, indent=4)

    return output


# ==========================================
# Example
# ==========================================

if __name__ == "__main__":

    resume = """

    Software Engineer at Infosys

    Jan 2021 - Mar 2023

    Python Developer at TCS

    Apr 2023 - Present

    """

    result = parse_experience(
        resume,
        candidate_id="C123",
        required_role="Backend Developer"
    )

    print(json.dumps(result, indent=4))