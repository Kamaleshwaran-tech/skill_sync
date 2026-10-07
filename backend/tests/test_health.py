def test_health_endpoint(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "SkillSync AI"
    assert payload["version"] == "0.1.0"
    assert payload["database"]["status"] in {"connected", "unavailable"}
    assert "message" in payload["database"]


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "SkillSync AI API is running."
