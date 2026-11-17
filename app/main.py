
from datetime import date, time
from typing import Annotated, Literal

from fastapi import FastAPI, Query

from app.service import (
    LAGERSALDO,
    antal_arbetsdagar,
    leveransdatum,
)

app = FastAPI(title="Lovat & levererat", version="1.0.0")

APP_VERSION = "1.0.0"

VECKODAGAR = (
    "måndag",
    "tisdag",
    "onsdag",
    "torsdag",
    "fredag",
    "lördag",
    "söndag",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": APP_VERSION}


@app.get("/leveransdatum")
def hamta_leveransdatum(
    orderdatum: date,
    tid: time,
    alternativ: Literal["standard", "express"] = "standard",
    destination: Literal[
        "sverige", "norden", "eu", "ovrigt"
    ] = "sverige",
    storlek: Literal["brevlada", "paket"] = "brevlada",
    antal: Annotated[int, Query(ge=1)] = 1,
):
    datum = leveransdatum(
        orderdatum=orderdatum,
        tid=tid,
        alternativ=alternativ,
        destination=destination,
        storlek=storlek,
        antal=antal,
    )

    arbetsdagar = antal_arbetsdagar(
        alternativ=alternativ,
        destination=destination,
        storlek=storlek,
        antal=antal,
    )

    return {
        "leveransdatum": datum.isoformat(),
        "veckodag": VECKODAGAR[datum.weekday()],
        "produktionsorder": antal > LAGERSALDO,
        "arbetsdagar": arbetsdagar,
    }
