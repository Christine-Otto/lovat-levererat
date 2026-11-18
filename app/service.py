
from datetime import date, time, timedelta

# Lagstadgade svenska helgdagar
RODA_DAGAR = {
    # 2026
    date(2026, 1, 1),
    date(2026, 1, 6),
    date(2026, 4, 3),
    date(2026, 4, 5),
    date(2026, 4, 6),
    date(2026, 5, 1),
    date(2026, 5, 14),
    date(2026, 5, 24),
    date(2026, 6, 6),
    date(2026, 6, 20),
    date(2026, 10, 31),
    date(2026, 12, 25),
    date(2026, 12, 26),

    # 2027
    date(2027, 1, 1),
    date(2027, 1, 6),
    date(2027, 3, 26),
    date(2027, 3, 28),
    date(2027, 3, 29),
    date(2027, 5, 1),
    date(2027, 5, 6),
    date(2027, 5, 16),
    date(2027, 6, 6),
    date(2027, 6, 26),
    date(2027, 11, 6),
    date(2027, 12, 25),
    date(2027, 12, 26),
}

# Egna affärsregler: stängda aftnar
STANGDA_AFTNAR = {
    # 2026
    date(2026, 6, 19),
    date(2026, 12, 24),
    date(2026, 12, 31),

    # 2027
    date(2027, 6, 25),
    date(2027, 12, 24),
    date(2027, 12, 31),
}

# Lagersaldo och fasta ledtider
LAGERSALDO = 100

LEVERANSALTERNATIV = {
    "standard": 3,
    "express": 1,
}

DESTINATIONER = {
    "sverige": 0,
    "norden": 2,
    "eu": 4,
    "ovrigt": 7,
}

STORLEKAR = {
    "brevlada": 0,
    "paket": 1,
}


def ar_arbetsdag(dag: date) -> bool:
    """Kontrollera om datumet är en arbetsdag."""
    return (
        dag.weekday() < 5
        and dag not in RODA_DAGAR
        and dag not in STANGDA_AFTNAR
    )


def nasta_arbetsdag(dag: date) -> date:
    """Hitta nästa arbetsdag efter angivet datum."""
    dag += timedelta(days=1)

    while not ar_arbetsdag(dag):
        dag += timedelta(days=1)

    return dag


def raknedag(orderdatum: date, tid: time) -> date:
    """Bestäm räknedag utifrån orderdatum och brytpunkt kl. 14."""
    brytpunkt = time(14, 0)

    if ar_arbetsdag(orderdatum) and tid < brytpunkt:
        return orderdatum

    return nasta_arbetsdag(orderdatum)


def tillverkningsdagar(antal_att_tillverka: int) -> int:
    """En arbetsdag per påbörjade 50 exemplar."""
    if antal_att_tillverka <= 0:
        return 0

    return (antal_att_tillverka + 49) // 50


def produktionstid(antal: int) -> int:
    """Beräkna extra ledtid när lagersaldot inte räcker."""
    if antal <= LAGERSALDO:
        return 0

    antal_att_tillverka = antal - LAGERSALDO

    material = 2
    tillverkning = tillverkningsdagar(antal_att_tillverka)
    kvalitetskontroll = 1

    return material + tillverkning + kvalitetskontroll


def antal_arbetsdagar(
    alternativ: str = "standard",
    destination: str = "sverige",
    storlek: str = "brevlada",
    antal: int = 1,
) -> int:
    """Beräkna den totala ledtiden i arbetsdagar."""
    if antal < 1:
        raise ValueError("Antal måste vara minst 1")

    return (
        LEVERANSALTERNATIV[alternativ]
        + DESTINATIONER[destination]
        + STORLEKAR[storlek]
        + produktionstid(antal)
    )


def leveransdatum(
    orderdatum: date,
    tid: time,
    alternativ: str = "standard",
    destination: str = "sverige",
    storlek: str = "brevlada",
    antal: int = 1,
) -> date:
    """Beräkna leveransdatum genom att räkna arbetsdagar."""
    start = raknedag(orderdatum, tid)

    dagar = antal_arbetsdagar(
        alternativ=alternativ,
        destination=destination,
        storlek=storlek,
        antal=antal,
    )

    leverans = start

    for _ in range(dagar):
        leverans = leverans + timedelta(days=1) if alternativ == "express" else nasta_arbetsdag(leverans)

    return leverans
