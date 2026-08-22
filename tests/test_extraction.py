from ats_engine.skill_extractor import extract_skills_with_confidence


def test_skill_extraction():

    resume = """

    Python Developer

    Django Developer

    Worked on MERN stack.

    Excellent communication skills.

    Leadership experience.

    """

    result = extract_skills_with_confidence(resume)

    assert len(result["skills"]) > 0

    assert any(
        s["skill_name"] == "Python"
        for s in result["skills"]
    )

    print(result)