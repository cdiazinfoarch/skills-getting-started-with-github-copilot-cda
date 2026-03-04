import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Helper to reset activities state if needed (for stateless tests)
def reset_activities():
    # If activities are global, you may need to clear or reset them here
    pass


def test_get_activities():
    # Arrange: nothing needed

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert all(isinstance(v, dict) for v in data.values())


def test_signup_success():
    # Arrange
    activities = client.get("/activities").json()
    activity_name = next(iter(activities))
    email = "testuser@mergington.edu"
    client.post(f"/activities/{activity_name}/unregister?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    result = response.json()

    # Assert
    assert response.status_code == 200
    assert "message" in result


def test_signup_duplicate():
    # Arrange
    activities = client.get("/activities").json()
    activity_name = next(iter(activities))
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    result = response.json()

    # Assert
    assert response.status_code == 400
    assert "detail" in result


def test_signup_activity_not_found():
    # Arrange: nothing needed

    # Act
    response = client.post("/activities/NonExistentActivity/signup?email=nouser@mergington.edu")
    result = response.json()

    # Assert
    assert response.status_code == 404
    assert "detail" in result


def test_signup_max_participants():
    # Arrange
    activities = client.get("/activities").json()
    for name, details in activities.items():
        if details["max_participants"] == 1:
            activity_name = name
            break
    else:
        activity_name = next(iter(activities))
        from src.app import activities as activities_dict
        activities_dict[activity_name]["max_participants"] = 1
    email1 = "max1@mergington.edu"
    email2 = "max2@mergington.edu"
    client.post(f"/activities/{activity_name}/unregister?email={email1}")
    client.post(f"/activities/{activity_name}/unregister?email={email2}")
    client.post(f"/activities/{activity_name}/signup?email={email1}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email2}")
    result = response.json()

    # Assert
    assert response.status_code == 400
    assert "detail" in result


def test_unregister_success():
    # Arrange
    activities = client.get("/activities").json()
    activity_name = next(iter(activities))
    email = "unregister@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    result = response.json()

    # Assert
    assert response.status_code == 200
    assert "message" in result


def test_unregister_not_found():
    # Arrange
    activities = client.get("/activities").json()
    activity_name = next(iter(activities))
    email = "notfound@mergington.edu"
    client.post(f"/activities/{activity_name}/unregister?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    result = response.json()

    # Assert
    assert response.status_code == 404
    assert "detail" in result

