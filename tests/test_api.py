# API-tester (integrationstester) för app/main.py (9 st).
# TestClient skickar riktiga HTTP-anrop till appen, som en webbläsare gör,
# men utan att starta någon server. Här testas det andra system ser:
# svaret från appen och felkoderna.

from fastapi.testclient import TestClient

from app.main import app

# En "låtsas-webbläsare" som pratar direkt med appen.
client = TestClient(app)


# /health ska svara 200 och {"status": "ok"}. Samma kontroll gör verify.sh.
def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# /version ska svara 1.0.0. verify.sh kontrollerar också att rätt version körs.
def test_version():
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "1.0.0"}


# Ett riktigt anrop: fredag kl. 9 med express ska ge måndag 23/11 i svaret.
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


# 120 st räcker inte i lagret -> svaret ska visa produktionsorder: true.
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


# Kontraktstest: svaret ska ha exakt de här fyra fälten med rätt typ.
# Andra system (till exempel transport) läser svaret. Döps ett fält om
# eller ändrar typ ska testet bli rött innan det når dem.
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


# Felaktig indata ska stoppas med felkod 422 (FastAPI validerar parametrarna).

# "flyg" finns inte som alternativ (bara standard och express) -> 422.
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


# "mars" finns inte som destination -> 422.
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


# Antal måste vara minst 1 -> 0 ger 422.
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


# Månad 13 och dag 40 finns inte -> 422.
def test_felaktigt_datum():
    response = client.get(
        "/leveransdatum",
        params={
            "orderdatum": "2026-13-40",
            "tid": "09:00",
        },
    )

    assert response.status_code == 422
