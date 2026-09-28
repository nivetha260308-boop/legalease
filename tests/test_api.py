import os

os.environ["DEMO_MODE"] = "true"
os.environ["GEMINI_API_KEY"] = ""

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "ok"
    )


def test_generate():

    response = client.post(
        "/generate",
        json={
            "document_type":
                "Freelance Work Contract",

            "parties":
                "Jane Doe (Provider), "
                "ABC Corp (Client)",

            "terms":
                "Payment within 30 days; "
                "Confidentiality applies",

            "effective_date":
                "2026-09-27",

            "jurisdiction":
                "Tamil Nadu, India",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document"]

    assert (
        data["demo_mode"]
        is True
    )