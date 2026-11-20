# Lovat & levererat

Det här är mitt slutprojekt i kursen Continuous integration och continuous delivery (DEVOPS25, Nackademin).

Idén är att det man lovar kunden också ska vara det som levereras. Appen räknar ut ett leveransdatum för en order, och pipelinen ska se till att varje ändring testas, byggs och kontrolleras innan den kommer in på `main`.

Repo: https://github.com/Christine-Otto/lovat-levererat

## Appen

Jag har byggt appen med FastAPI. Reglerna finns i `app/service.py` och API:t i `app/main.py`.

| Endpoint | Svar |
|---|---|
| `/health` | `{"status": "ok"}` |
| `/version` | `{"version": "1.0.0"}` |
| `/leveransdatum` | Leveransdatum för en order |

Till `/leveransdatum` skickar man `orderdatum`, `tid`, `alternativ` (standard eller express), `destination` (sverige, norden, eu, ovrigt), `storlek` (brevlada eller paket) och `antal` (minst 1).

Reglerna är ungefär så här:
- Standard tar 3 arbetsdagar och express 1. Norden ger +2 dagar, EU +4 och övriga världen +7. Ett paket tar en dag extra.
- Brytpunkten är kl. 14:00. Kommer ordern 14:00 eller senare räknas den från nästa arbetsdag.
- Helger, röda dagar 2026–2027 och midsommar-, jul- och nyårsafton räknas inte som arbetsdagar.
- Det finns 100 st i lager. Beställer man fler blir det en produktionsorder: 2 dagar för material, 1 dag tillverkning per påbörjade 50 st och 1 dag kvalitetskontroll.

Exempel: `/leveransdatum?orderdatum=2026-11-20&tid=09:00&alternativ=express`

```json
{"leveransdatum": "2026-11-23", "veckodag": "måndag", "produktionsorder": false, "arbetsdagar": 1}
```

## Köra lokalt

Jag kör allt i Git Bash från mappen där repot ligger.

```bash
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt

ruff check app tests
python -m pytest -v
python -m uvicorn app.main:app --reload
```

Sedan går det att testa appen på http://127.0.0.1:8000/docs.

Obs: bara `pytest` fungerade inte i min venv, så jag kör `python -m pytest`.

## Tester

- `tests/test_service.py` har 23 enhetstester för reglerna, till exempel helger, röda dagar, brytpunkten, ledtider och produktion.
- `tests/test_api.py` har 9 API-tester med TestClient. Där testar jag bland annat felaktig indata (422), och så finns ett kontraktstest som kollar att svaret har precis de fyra fälten.

## Docker och skript

| Skript | Vad det gör |
|---|---|
| `scripts/deploy_local.sh 1.0.0` | Bygger imagen `leveransdatum:1.0.0` och startar containern på port 8000 |
| `scripts/verify.sh 1.0.0` | Kollar `/health`, att rätt version körs och att ett riktigt leveransdatum kommer tillbaka |
| `scripts/rollback_local.sh` | Startar `leveransdatum:1.0.0` igen och kör verify |

## Pipeline

Pipelinen ligger i `.github/workflows/ci.yml`. Den körs när man pushar till `main` och när man gör en pull request mot `main`. Den har två jobb:

1. **Test and lint** installerar det som behövs (med pip-cache), kör Ruff och testerna och sparar testrapporten som en artifact.
2. **Build and verify** startar bara om första jobbet är grönt (`needs: test-and-lint`). Det bygger Docker-imagen med commit-SHA som tagg, startar en container och kör `verify.sh`. Om något går fel skrivs containerns logg ut, så att man ser varför.

När en ändring har kommit in på `main` publiceras imagen också i GitHub Container Registry (GHCR) som `ghcr.io/christine-otto/leveransdatum:<commit-SHA>`. Det sker bara efter att verify har gått igenom. Vid en pull request hoppas det steget över.

Pipelinen får bara läsa repot (`permissions: contents: read`). Undantaget är att Build and verify också får skriva paket (`packages: write`), annars går det inte att publicera imagen. Versionerna av alla paket är låsta i `requirements.txt`.

## Hämta imagen från GHCR

Byt `<commit-SHA>` mot hela SHA:n, som finns i Actions eller under Packages:

```bash
docker pull ghcr.io/christine-otto/leveransdatum:<commit-SHA>
docker run -d --name leveransdatum -p 8000:8000 ghcr.io/christine-otto/leveransdatum:<commit-SHA>
bash scripts/verify.sh 1.0.0
```

Jag har testat att hämta och köra imagen från GHCR på min egen dator, och verify.sh gick igenom.

## Hur jag jobbar

`main` är skyddad med ett ruleset, så det går inte att pusha direkt dit. Jag gör ändringar på en egen gren och skapar en pull request. Den går bara att merga när både Test and lint och Build and verify är gröna. Den första versionen som fungerade har taggen `v1.0.0`.

## Struktur

```
.github/workflows/ci.yml   pipelinen
app/service.py             reglerna
app/main.py                API:t
tests/                     enhets- och API-tester
scripts/                   deploy, verify och rollback
Dockerfile                 hur imagen byggs
requirements.txt           låsta versioner
```