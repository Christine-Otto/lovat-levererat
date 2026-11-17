
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version():
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "1.0.0"}


def test_riktigt_anrop():
    response = client.get(
        "/leveransdatum",
        params={
            "orderdatum": "2026-11-20",
            "tid": "09:00",
            "alternativ": "express",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "leveransdatum": "2026-11-23",
        "veckodag": "måndag",
        "produktionsorder": False,
        "arbetsdagar": 1,
    }


def test_produktionsorder_i_svaret():
    response = client.get(
        "/leveransdatum",
        params={
            "orderdatum": "2026-11-18",
            "tid": "09:00",
            "alternativ": "express",
            "antal": 120,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "leveransdatum": "2026-11-25",
        "veckodag": "onsdag",
        "produktionsorder": True,
        "arbetsdagar": 5,
    }


def test_kontrakt_svarets_falt():
    response = client.get(
        "/leveransdatum",
        params={
            "orderdatum": "2026-11-20",
            "tid": "09:00",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {
        "leveransdatum",
        "veckodag",
        "produktionsorder",
        "arbetsdagar",
    }

    assert type(data["leveransdatum"]) is str
    assert type(data["veckodag"]) is str
    assert type(data["produktionsorder"]) is bool
    assert type(data["arbetsdagar"]) is int


def test_okant_alternativ():
    response = client.get(
        "/leveransdatum",
        params={
            "orderdatum": "2026-11-20",
            "tid": "09:00",
            "alternativ": "flyg",
        },
    )

    assert response.status_code == 422


def test_okand_destination():
    response = client.get(
        "/leveransdatum",
        params={
            "orderdatum": "2026-11-20",
            "tid": "09:00",
            "destination": "mars",
        },
    )

    assert response.status_code == 422


def test_antal_noll():
    response = client.get(
        "/leveransdatum",
        params={
            "orderdatum": "2026-11-20",
            "tid": "09:00",
            "antal": 0,
        },
    )

    assert response.status_code == 422


def test_felaktigt_datum():
    response = client.get(
        "/leveransdatum",
        params={
            "orderdatum": "2026-13-40",
            "tid": "09:00",
        },
    )

    assert response.status_code == 422
