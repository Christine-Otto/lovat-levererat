# Enhetstester för reglerna i app/service.py (23 st).
# Här testas funktionerna direkt, utan webbserver och utan Docker.
# Varje test skickar in en order och kontrollerar att rätt leveransdatum kommer tillbaka.
# Alla datum i november 2026: ons 18, tor 19, fre 20, lör 21, sön 22, mån 23.

from datetime import date, time

from app.service import leveransdatum, tillverkningsdagar

# Grundregler: leveransalternativ och helger


# Express = 1 arbetsdag. Onsdag före kl. 14 räknas från onsdag -> torsdag.
def test_express_vardag():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 11, 19)


# Fredag före kl. 14 -> nästa arbetsdag är måndag, inte lördag.
# Det här testet blev rött vid fel 1 (kalenderdagar i stället för arbetsdagar).
def test_express_fredag():
    assert leveransdatum(
        date(2026, 11, 20),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 11, 23)


# Efter brytpunkten kl. 14 räknas ordern från nästa arbetsdag (måndag) -> tisdag.
def test_efter_brytpunkt():
    assert leveransdatum(
        date(2026, 11, 20),
        time(15, 30),
        alternativ="express",
    ) == date(2026, 11, 24)


# Gränsvärde: kl. 14:00 prick räknas som EFTER brytpunkten.
# Onsdag 14:00 räknas från torsdag -> fredag.
def test_exakt_brytpunkt():
    assert leveransdatum(
        date(2026, 11, 18),
        time(14, 0),
        alternativ="express",
    ) == date(2026, 11, 20)


# Standard = 3 arbetsdagar. Från onsdag: tor, fre, (helg), mån.
def test_standard_over_helg():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="standard",
    ) == date(2026, 11, 23)


# En order på en lördag räknas från måndag -> leverans tisdag.
def test_order_pa_lordag():
    assert leveransdatum(
        date(2026, 11, 21),
        time(10, 0),
        alternativ="express",
    ) == date(2026, 11, 24)


# Storlek paket ger en extra arbetsdag jämfört med brevlåda.
def test_paket_till_ombud():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        storlek="paket",
    ) == date(2026, 11, 20)


# Lager och produktionsregler
# Lagret har 100 st. Beställer man fler blir det en produktionsorder:
# 2 dagar material + 1 dag tillverkning per påbörjade 50 st + 1 dag kvalitetskontroll.


# Gränsvärde: exakt 100 st finns i lager -> ingen produktion.
def test_antal_ryms_i_lager():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        antal=100,
    ) == date(2026, 11, 19)


# Gränsvärde: 101 st räcker inte -> produktionsorder (+4 arbetsdagar).
def test_antal_kraver_produktion():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        antal=101,
    ) == date(2026, 11, 25)


# Samma fall som jag visar i demon: 120 st -> 25 november.
def test_antal_120():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        antal=120,
    ) == date(2026, 11, 25)


# 150 st = 50 st att tillverka -> fortfarande bara 1 tillverkningsdag.
def test_50_st_att_tillverka():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        antal=150,
    ) == date(2026, 11, 25)


# 151 st = 51 st att tillverka -> 2 tillverkningsdagar, en dag senare.
def test_51_st_att_tillverka():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        antal=151,
    ) == date(2026, 11, 26)


# Stor order: 300 st = 200 st att tillverka -> 4 tillverkningsdagar.
def test_stor_order():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="express",
        antal=300,
    ) == date(2026, 11, 30)


# Kombinationer och destinationer


# Express (1) + Norden (+2) + paket (+1) = 4 arbetsdagar från fredag -> torsdag.
def test_kombination_norden_paket():
    assert leveransdatum(
        date(2026, 11, 20),
        time(9, 0),
        alternativ="express",
        destination="norden",
        storlek="paket",
    ) == date(2026, 11, 26)


# Standard (3) + övriga världen (+7) + paket (+1) = 11 arbetsdagar.
def test_utomlands():
    assert leveransdatum(
        date(2026, 11, 18),
        time(9, 0),
        alternativ="standard",
        destination="ovrigt",
        storlek="paket",
    ) == date(2026, 12, 3)


# Röda dagar och stängda aftnar
# Röda dagar 2026–2027 och stängda aftnar räknas inte som arbetsdagar.


# Julafton, juldagen och annandag jul hoppas över (två fall i samma test).
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


# Midsommarafton (fredag 19 juni) är stängd -> måndag 22 juni.
def test_midsommar():
    assert leveransdatum(
        date(2026, 6, 18),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 6, 22)


# Nyårsafton och nyårsdagen hoppas över -> måndag 4 januari 2027.
def test_nyar():
    assert leveransdatum(
        date(2026, 12, 30),
        time(9, 0),
        alternativ="express",
    ) == date(2027, 1, 4)


# Påsken 2027: långfredag och annandag påsk hoppas över -> tisdag 30 mars.
def test_pask_2027():
    assert leveransdatum(
        date(2027, 3, 25),
        time(9, 0),
        alternativ="express",
    ) == date(2027, 3, 30)


# Kristi himmelsfärds dag (torsdag 14 maj) hoppas över -> fredag 15 maj.
def test_kristi_himmelsfard():
    assert leveransdatum(
        date(2026, 5, 13),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 5, 15)


# Sommartid och vintertid
# Appen räknar med datum, inte timmar, så helgen då klockan ställs om ska inte ge fel.


# Helgen då vintertid börjar (25 oktober) -> fredag till måndag som vanligt.
def test_vintertid():
    assert leveransdatum(
        date(2026, 10, 23),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 10, 26)


# Helgen då sommartid börjar (29 mars) -> fredag till måndag som vanligt.
def test_sommartid():
    assert leveransdatum(
        date(2026, 3, 27),
        time(9, 0),
        alternativ="express",
    ) == date(2026, 3, 30)


# Direkt kontroll av hjälpfunktionen


# tillverkningsdagar räknar 1 dag per påbörjade 50 st: 1 och 50 st -> 1 dag, 51 st -> 2 dagar.
def test_tillverkningsdagar_gransvarden():
    assert tillverkningsdagar(1) == 1
    assert tillverkningsdagar(50) == 1
    assert tillverkningsdagar(51) == 2
