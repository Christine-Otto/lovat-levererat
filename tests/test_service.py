
from datetime import date, time

from app.service import leveransdatum, tillverkningsdagar

# Grundregler: leveransalternativ och helger

def test_express_vardag():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 11, 19)


def test_express_fredag():
    assert leveransdatum(
        date(2026, 11, 20),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 11, 23)


def test_efter_brytpunkt():
    assert leveransdatum(
        date(2026, 11, 20),
        time(15, 30),
        alternativ="express",
    ) == date(2026, 11, 24)


def test_exakt_brytpunkt():
    assert leveransdatum(
        date(2026, 11, 18),
        time(14, 0),
        alternativ="express",
    ) == date(2026, 11, 20)


def test_standard_over_helg():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="standard",
    ) == date(2026, 11, 23)


def test_order_pa_lordag():
    assert leveransdatum(
        date(2026, 11, 21),
        time(10, 0),
        alternativ="express",
    ) == date(2026, 11, 24)


def test_paket_till_ombud():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        storlek="paket",
    ) == date(2026, 11, 20)


# Lager och produktionsregler

def test_antal_ryms_i_lager():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        antal=100,
    ) == date(2026, 11, 19)


def test_antal_kraver_produktion():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        antal=101,
    ) == date(2026, 11, 25)


def test_antal_120():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        antal=120,
    ) == date(2026, 11, 25)


def test_50_st_att_tillverka():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        antal=150,
    ) == date(2026, 11, 25)


def test_51_st_att_tillverka():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        antal=151,
    ) == date(2026, 11, 26)


def test_stor_order():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        antal=300,
    ) == date(2026, 11, 30)


# Kombinationer och destinationer

def test_kombination_norden_paket():
    assert leveransdatum(
        date(2026, 11, 20),
        time(9, 0),
        alternativ="express",
        destination="norden",
        storlek="paket",
    ) == date(2026, 11, 26)


def test_utomlands():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="standard",
        destination="ovrigt",
        storlek="paket",
    ) == date(2026, 12, 3)


# Röda dagar och stängda aftnar

def test_jul():
    assert leveransdatum(
        date(2026, 12, 23),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 12, 28)

    assert leveransdatum(
        date(2026, 12, 24),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 12, 29)


def test_midsommar():
    assert leveransdatum(
        date(2026, 6, 18),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 6, 22)


def test_nyar():
    assert leveransdatum(
        date(2026, 12, 30),
        time(9, 0),
        alternativ="express",
    ) == date(2027, 1, 4)


def test_pask_2027():
    assert leveransdatum(
        date(2027, 3, 25),
        time(9, 0),
        alternativ="express",
    ) == date(2027, 3, 30)


def test_kristi_himmelsfard():
    assert leveransdatum(
        date(2026, 5, 13),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 5, 15)


# Sommartid och vintertid

def test_vintertid():
    assert leveransdatum(
        date(2026, 10, 23),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 10, 26)


def test_sommartid():
    assert leveransdatum(
        date(2026, 3, 27),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 3, 30)


# Direkt kontroll av hjälpfunktionen

def test_tillverkningsdagar_gransvarden():
    assert tillverkningsdagar(1) == 1
    assert tillverkningsdagar(50) == 1
    assert tillverkningsdagar(51) == 2

import os