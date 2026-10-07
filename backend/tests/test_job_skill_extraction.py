from app.services.job_skill_extraction import JobSkillExtractionService


def test_extract_required_preferred_and_soft_skills():
    extractor = JobSkillExtractionService()
    content = (
        "Senior Full Stack Developer. Required: ReactJS, Node, PostgreSQL and Docker. "
        "Preferred: Kubernetes, AWS. Nice to have: leadership and communication."
    )
    extracted = extractor.extract("Full Stack Developer", content)

    assert "React" in extracted["required"]
    assert "Node.js" in extracted["required"]
    assert "PostgreSQL" in extracted["required"]
    assert "Docker" in extracted["required"]
    assert "Kubernetes" in extracted["preferred"]
    assert "AWS" in extracted["preferred"]
    assert "Leadership" in extracted["soft_skills"]
    assert "Communication" in extracted["soft_skills"]


def test_extract_detects_soft_skill_by_name():
    extractor = JobSkillExtractionService()
    extracted = extractor.extract("Engineering Manager", "We value teamwork, problem solving, and communication.")
    assert "Teamwork" in extracted["soft_skills"]
    assert "Problem Solving" in extracted["soft_skills"]
    assert "Communication" in extracted["soft_skills"]
