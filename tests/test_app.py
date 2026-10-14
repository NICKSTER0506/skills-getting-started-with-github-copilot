import copy

import pytest
from fastapi.testclient import TestClient

import src.app as activity_app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        activity_app, "activities", copy.deepcopy(activity_app.activities)
    )
    return TestClient(activity_app.app)


def test_root_redirects_to_frontend(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    email = "student@example.com"

    response = client.post(
        "/activities/Basketball Team/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Basketball Team"
    }
    assert email in activity_app.activities["Basketball Team"]["participants"]


def test_signup_for_unknown_activity_returns_404(client):
    response = client.post(
        "/activities/Unknown/signup", params={"email": "student@example.com"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_duplicate_signup_returns_400_without_adding_participant(client):
    email = "michael@mergington.edu"

    response = client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activity_app.activities["Chess Club"]["participants"].count(email) == 1


def test_unregister_removes_participant(client):
    email = "michael@mergington.edu"

    response = client.delete(
        "/activities/Chess Club/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    assert email not in activity_app.activities["Chess Club"]["participants"]


def test_unregister_from_unknown_activity_returns_404(client):
    response = client.delete(
        "/activities/Unknown/signup", params={"email": "student@example.com"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_unregistered_participant_returns_404(client):
    response = client.delete(
        "/activities/Chess Club/signup", params={"email": "student@example.com"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up for this activity"