from fastapi.testclient import TestClient

from app.services.location_helper import build_location_guidance


def create_session(client: TestClient) -> str:
    response = client.post(
        "/api/sessions",
        json={"form_id": "income_certificate", "language": "auto"},
    )
    assert response.status_code == 201
    return response.json()["session_id"]


def ask(client: TestClient, session_id: str, message: str) -> dict:
    response = client.post(
        "/api/assistant/ask",
        json={
            "session_id": session_id,
            "message": message,
            "language": "auto",
        },
    )
    assert response.status_code == 200
    return response.json()


def test_location_search_by_pincode(client: TestClient) -> None:
    response = client.get("/api/location/search?pincode=500032")
    assert response.status_code == 200
    matches = response.json()["matches"]
    assert matches == [
        {
            "state": "Telangana",
            "district": "Rangareddy",
            "mandal": "Serilingampally",
            "village_or_locality": "Gachibowli",
            "pincode": "500032",
        }
    ]


def test_location_search_by_name(client: TestClient) -> None:
    response = client.get("/api/location/search?query=gachibowli")
    assert response.status_code == 200
    assert response.json()["matches"][0]["mandal"] == "Serilingampally"


def test_location_dataset_includes_requested_demo_districts(client: TestClient) -> None:
    for query, expected_district in [
        ("siddipet", "Siddipet"),
        ("suryapet", "Suryapet"),
        ("adilabad", "Adilabad"),
        ("mancherial", "Mancherial"),
    ]:
        response = client.get(f"/api/location/search?query={query}")
        assert response.status_code == 200
        assert any(
            match["district"] == expected_district
            for match in response.json()["matches"]
        )


def test_telugu_mandal_unknown_asks_for_details(client: TestClient) -> None:
    body = ask(client, create_session(client), "na mandal teliyadu")
    assert body["detected_language"] == "telugu"
    assert body["language_code"] == "te-IN"
    assert "గ్రామం" in body["reply"]
    assert "pincode" in body["reply"]
    assert body["location_matches"] == []
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_telugu_pincode_lookup_suggests_without_filling(client: TestClient) -> None:
    body = ask(
        client,
        create_session(client),
        "na mandal teliyadu pincode 500032",
    )
    assert body["detected_language"] == "telugu"
    assert "Rangareddy" in body["reply"]
    assert "Serilingampally" in body["reply"]
    assert "ఉండవచ్చు" in body["reply"]
    assert body["related_values"]["district"] == "Rangareddy"
    assert body["related_values"]["mandal"] == "Serilingampally"
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_follow_up_pincode_uses_last_telugu_location_context(
    client: TestClient,
) -> None:
    session_id = create_session(client)
    ask(client, session_id, "na mandal teliyadu")
    body = ask(client, session_id, "na pincode 500032")
    assert body["detected_language"] == "telugu"
    assert "Serilingampally" in body["reply"]


def test_hindi_mandal_unknown_asks_for_details(client: TestClient) -> None:
    body = ask(client, create_session(client), "mujhe mandal nahi pata")
    assert body["detected_language"] == "hindi"
    assert body["language_code"] == "hi-IN"
    assert "गाँव" in body["reply"]
    assert "pincode" in body["reply"]


def test_hindi_pincode_lookup(client: TestClient) -> None:
    body = ask(
        client,
        create_session(client),
        "mujhe mandal nahi pata pincode 500032",
    )
    assert body["detected_language"] == "hindi"
    assert "Rangareddy" in body["reply"]
    assert "Serilingampally" in body["reply"]
    assert "हो सकता है" in body["reply"]
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_location_no_match_requests_more_details(client: TestClient) -> None:
    response = client.post(
        "/api/location/help",
        json={
            "message": "na mandal teliyadu pincode 599999",
            "language": "auto",
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["detected_language"] == "telugu"
    assert body["matches"] == []
    assert "మళ్లీ చెప్పండి" in body["reply"]
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_reverse_location_is_honest_placeholder(client: TestClient) -> None:
    response = client.post(
        "/api/location/reverse",
        json={
            "latitude": 17.444,
            "longitude": 78.377,
            "language": "english",
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert "exact mandal lookup is not available" in body["reply"]
    assert body["matches"] == []
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_multiple_location_matches_require_citizen_confirmation() -> None:
    matches = [
        {
            "district": "Rangareddy",
            "mandal": "Serilingampally",
            "village_or_locality": "Gachibowli",
            "pincode": "500032",
        },
        {
            "district": "Rangareddy",
            "mandal": "Serilingampally",
            "village_or_locality": "Nanakramguda",
            "pincode": "500032",
        },
    ]
    guidance = build_location_guidance(matches, "telugu")
    assert "ఒకటి కంటే ఎక్కువ" in guidance["reply"]
    assert "Gachibowli" in guidance["reply"]
    assert "Nanakramguda" in guidance["reply"]
    assert guidance["auto_fill"] is False
    assert guidance["should_submit"] is False
