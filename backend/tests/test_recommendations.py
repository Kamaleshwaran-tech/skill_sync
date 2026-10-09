def test_recommendation_generation(client):
    payload = {
        "studentSkills": ["Python", "JavaScript", "Git"],
        "currentSkills": ["Python", "Git"],
        "missingSkills": ["Docker", "PostgreSQL", "React"],
        "targetRole": "Full Stack Developer",
        "preferredLocation": "New York",
        "remotePreference": "Hybrid",
        "experienceYears": 2.5,
        "skillPriorities": {"Docker": "HIGH", "PostgreSQL": "HIGH", "React": "MEDIUM"},
        "industryDemand": {"Docker": 0.88, "PostgreSQL": 0.82, "React": 0.73},
        "jobs": [
            {
                "title": "Full Stack Developer",
                "company": "Northstar Labs",
                "location": "New York",
                "required_skills": ["React", "Docker", "PostgreSQL"],
                "matchScore": 89,
                "skillCoverage": 82,
            }
        ],
    }

    response = client.post("/api/v1/recommendations/generate", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "jobs" in data
    assert "skills" in data
    assert "projects" in data
    assert "certifications" in data
    assert "learningResources" in data

    assert data["jobs"][0]["title"] == "Full Stack Developer"
    assert any(item["skill"] == "Docker" for item in data["skills"])
    assert any(item["title"] == "Docker Documentation" for item in data["learningResources"])
    assert all(item["url"] is None or item["url"].startswith("http") for item in data["learningResources"])
    assert any(item["title"] == "Docker Certified Associate" for item in data["certifications"])
