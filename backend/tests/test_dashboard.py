def test_dashboard_endpoint_matches_frontend_contract(client):
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "dashboard@example.com", "password": "s3cureP@ssword", "full_name": "Dashboard User"},
    )
    assert register.status_code == 200, register.text

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "dashboard@example.com", "password": "s3cureP@ssword"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    response = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()

    for key in [
        "profile",
        "readiness",
        "careerMatches",
        "skillOverview",
        "recommendedJobs",
        "skillDemand",
        "learningProgress",
        "recommendedProjects",
        "certifications",
        "recentActivity",
    ]:
        assert key in data, data

    assert "resumeScore" in data and "careerReadinessScore" in data
    assert data["profile"]["name"] == "Dashboard User"
    assert data["readiness"]["overall"] >= 0
    assert data["careerMatches"] == []
    assert data["skillOverview"]["current"] == []
