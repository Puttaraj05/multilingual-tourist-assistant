from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from backend.utils.distance import calculate_distance


client = TestClient(app)


MOCK_RESTAURANTS = [
    {
        "name": "Test Restaurant One",
        "source_url": "https://maps.google.com/test1"
    },
    {
        "name": "Test Restaurant Two",
        "source_url": "https://maps.google.com/test2"
    }
]


MOCK_ATTRACTIONS = [
    {
        "name": "Test Attraction One",
        "source_url": "https://maps.google.com/attraction1"
    },
    {
        "name": "Test Attraction Two",
        "source_url": "https://maps.google.com/attraction2"
    }
]


# REC-01
@patch(
    "backend.services.recommendation_service.find_nearby_places_with_gemini"
)
def test_rec_01_restaurant_recommendation(mock_gemini):

    mock_gemini.return_value = {
        "category": "restaurant",
        "text": "Nearby restaurants found",
        "places": MOCK_RESTAURANTS
    }

    response = client.post(
        "/api/recommendations",
        json={
            "latitude": 17.405,
            "longitude": 78.489,
            "category": "restaurant"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["recommendations"]) > 0

    for place in data["recommendations"]:
        assert place["category"] == "restaurant"


# REC-02
@patch(
    "backend.services.recommendation_service.find_nearby_places_with_gemini"
)
def test_rec_02_attraction_recommendation(mock_gemini):

    mock_gemini.return_value = {
        "category": "tourist attraction",
        "text": "Nearby attractions found",
        "places": MOCK_ATTRACTIONS
    }

    response = client.post(
        "/api/recommendations",
        json={
            "latitude": 17.385,
            "longitude": 78.486,
            "category": "attraction"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["recommendations"]) > 0

    for place in data["recommendations"]:
        assert (
            place["category"]
            == "tourist attraction"
        )


# REC-03
@patch(
    "backend.services.recommendation_service.find_nearby_places_with_gemini"
)
def test_rec_03_radius_filtering(mock_gemini):

    mock_gemini.return_value = {
        "category": "restaurant",
        "text": "Results",
        "places": MOCK_RESTAURANTS
    }

    response = client.post(
        "/api/recommendations",
        json={
            "latitude": 17.405,
            "longitude": 78.489,
            "category": "restaurant",
            "radius": 5
        }
    )

    assert response.status_code == 200


# REC-04
@patch(
    "backend.services.recommendation_service.find_nearby_places_with_gemini"
)
def test_rec_04_maximum_results(mock_gemini):

    mock_places = [
        {
            "name": f"Restaurant {i}",
            "source_url": (
                f"https://maps.google.com/{i}"
            )
        }
        for i in range(10)
    ]

    mock_gemini.return_value = {
        "category": "restaurant",
        "text": "Results",
        "places": mock_places
    }

    response = client.post(
        "/api/recommendations",
        json={
            "latitude": 17.405,
            "longitude": 78.489,
            "category": "restaurant",
            "max_results": 5
        }
    )

    assert response.status_code == 200

    assert (
        len(
            response.json()["recommendations"]
        )
        <= 5
    )


# REC-05
def test_rec_05_invalid_latitude():

    response = client.post(
        "/api/recommendations",
        json={
            "latitude": 100,
            "longitude": 78.489,
            "category": "restaurant"
        }
    )

    assert response.status_code == 422


# REC-06
def test_rec_06_invalid_longitude():

    response = client.post(
        "/api/recommendations",
        json={
            "latitude": 17.405,
            "longitude": 200,
            "category": "restaurant"
        }
    )

    assert response.status_code == 422


# REC-07
@patch(
    "backend.services.recommendation_service.find_nearby_places_with_gemini"
)
def test_rec_07_missing_category(mock_gemini):

    mock_gemini.return_value = {
        "category": "restaurant",
        "text": "Results",
        "places": MOCK_RESTAURANTS
    }

    response = client.post(
        "/api/recommendations",
        json={
            "latitude": 17.405,
            "longitude": 78.489
        }
    )

    assert response.status_code == 200

    for place in response.json()["recommendations"]:
        assert place["category"] == "restaurant"


# REC-08
@patch(
    "backend.services.recommendation_service.find_nearby_places_with_gemini"
)
def test_rec_08_no_matching_places(mock_gemini):

    mock_gemini.return_value = {
        "category": "beach",
        "text": "No places found",
        "places": []
    }

    response = client.post(
        "/api/recommendations",
        json={
            "latitude": 17.405,
            "longitude": 78.489,
            "category": "beach"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["recommendations"] == []
    assert data["count"] == 0


# REC-09
def test_rec_09_same_coordinates():

    distance = calculate_distance(
        17.405,
        78.489,
        17.405,
        78.489
    )

    assert distance == 0


def test_rec_09_known_distance():

    distance = calculate_distance(
        0,
        0,
        0,
        1
    )

    assert 111 <= distance <= 112


# REC-10
@patch(
    "backend.services.recommendation_service.find_nearby_places_with_gemini"
)
def test_rec_10_api_response(mock_gemini):

    mock_gemini.return_value = {
        "category": "restaurant",
        "text": "Results",
        "places": MOCK_RESTAURANTS
    }

    response = client.post(
        "/api/recommendations",
        json={
            "latitude": 17.405,
            "longitude": 78.489,
            "category": "restaurant",
            "radius": 5,
            "max_results": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert "recommendations" in data
    assert "count" in data
    assert isinstance(
        data["recommendations"],
        list
    )