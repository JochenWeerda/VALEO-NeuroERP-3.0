"""DOM-INV-005: kanonische Bewegungsrichtung fuer inventory_stock_movements.

Drei Ebenen:

1. die Richtungstabelle selbst,
2. ein Repository-Waechter, der anschlaegt, sobald irgendwo ein
   ``movement_type`` geschrieben wird, den die Tabelle nicht kennt,
3. Aggregationstests gegen eine laufende Datenbank mit je einer Zeile pro
   Richtungsklasse.
"""

import re
from pathlib import Path

import pytest
from sqlalchemy import text

from app.services.inventory_movement_direction import (
    INBOUND_TYPES,
    KNOWN_TYPES,
    MOVEMENT_DIRECTION,
    NEUTRAL_TYPES,
    OUTBOUND_TYPES,
    direction_of,
    direction_sql,
    signed_quantity,
    unknown_movement_types,
)

REPO = Path(__file__).resolve().parents[1]


# -- Ebene 1: die Richtungstabelle ------------------------------------------


@pytest.mark.unit
def test_jede_klasse_ist_disjunkt():
    assert not set(INBOUND_TYPES) & set(OUTBOUND_TYPES)
    assert not set(INBOUND_TYPES) & set(NEUTRAL_TYPES)
    assert not set(OUTBOUND_TYPES) & set(NEUTRAL_TYPES)
    assert len(KNOWN_TYPES) == len(INBOUND_TYPES) + len(OUTBOUND_TYPES) + len(NEUTRAL_TYPES)


@pytest.mark.unit
def test_alle_typen_sind_klein_geschrieben():
    """Die Auswertung normalisiert auf lower(); die Tabelle muss dazu passen."""
    for name in MOVEMENT_DIRECTION:
        assert name == name.lower(), f"{name!r} muss kleingeschrieben in der Tabelle stehen"


@pytest.mark.unit
@pytest.mark.parametrize(
    "movement_type,erwartet",
    [
        ("wareneingang", 1),
        ("ZUGANG", 1),
        ("zugang", 1),
        ("  Wareneingang  ", 1),
        ("EINLAGERUNG", 1),
        ("RETOURE", 1),
        ("opening_balance", 1),
        ("warenausgang", -1),
        ("ABGANG", -1),
        ("pick_out", -1),
        ("out", -1),
        ("reservation", 0),
        ("inventory_count", 0),
        ("voellig_unbekannt", 0),
        ("", 0),
        (None, 0),
    ],
)
def test_richtung_je_typ(movement_type, erwartet):
    assert direction_of(movement_type) == erwartet


@pytest.mark.unit
def test_unbekannter_typ_erbt_kein_vorzeichen():
    """Der eigentliche Fehler der alten CASE-Ausdruecke.

    Kein ELSE quantity (jeder Abgang zaehlt positiv), kein ELSE -quantity
    (jeder Zugang zaehlt negativ) - unbekannt heisst 0.
    """
    assert signed_quantity("gibt_es_nicht", 100) == 0


@pytest.mark.unit
def test_signierte_menge_uebernimmt_vorzeichen_bei_korrekturtypen():
    """inventur/adjustment tragen ihr Vorzeichen in der Menge selbst."""
    assert signed_quantity("inventur", -8) == -8
    assert signed_quantity("adjustment", -8) == -8
    # ein echter Abgangstyp dreht dagegen um
    assert signed_quantity("warenausgang", 8) == -8


@pytest.mark.unit
def test_sql_fragment_enthaelt_keinen_raten_zweig():
    fragment = direction_sql()
    assert "ELSE 0 END" in fragment
    assert "ELSE quantity" not in fragment
    assert "ELSE -quantity" not in fragment
    assert "lower(movement_type)" in fragment


# -- Ebene 2: Waechter gegen neue Vokabulare --------------------------------


# Netz 1: movement_type als Schluesselwort- oder Dict-Argument.
SCHREIB_MUSTER = [
    re.compile(r"movement_type\s*=\s*['\"]([A-Za-z_]+)['\"]"),
    re.compile(r"movement_type[\"']?\s*:\s*['\"]([A-Za-z_]+)['\"]"),
]

# Netz 2: der in diesem Repository haeufigere Stil - movement_type steckt
# positionsgleich in der Spaltenliste eines INSERT und im VALUES-Tupel. Ohne
# dieses Netz waeren 'wareneingang', 'RETOURE', 'opening_balance' und
# 'adjustment' fuer den Waechter unsichtbar, und genau so ist die
# Vokabular-Doppelung ueberhaupt erst entstanden.
INSERT_MUSTER = re.compile(
    r"INSERT\s+INTO\s+domain_inventory\.inventory_stock_movements\s*"
    r"\(([^)]*)\)\s*(?:VALUES|SELECT)\s*\(?(.{0,2000})",
    re.IGNORECASE | re.DOTALL,
)

LITERAL_MUSTER = re.compile(r"^'([A-Za-z_]+)'$")


def _positionale_werte(inhalt: str) -> set[str]:
    """movement_type-Literale aus INSERT-Spaltenliste plus VALUES-Tupel."""
    werte: set[str] = set()
    for spalten_roh, werte_roh in INSERT_MUSTER.findall(inhalt):
        spalten = [teil.strip() for teil in spalten_roh.split(",")]
        if "movement_type" not in spalten:
            continue
        index = spalten.index("movement_type")
        stuecke = _tupel_teilen(werte_roh)
        if index >= len(stuecke):
            continue
        treffer = LITERAL_MUSTER.match(stuecke[index].strip())
        if treffer:
            werte.add(treffer.group(1))
    return werte


def _tupel_teilen(roh: str) -> list[str]:
    """Kommas auf oberster Klammerebene trennen, Kommas in COALESCE(...) nicht."""
    stuecke: list[str] = []
    tiefe = 0
    aktuell: list[str] = []
    in_string = False
    for zeichen in roh:
        if zeichen == "'":
            in_string = not in_string
        if not in_string:
            if zeichen in "([":
                tiefe += 1
            elif zeichen in ")]":
                if tiefe == 0:
                    break
                tiefe -= 1
            elif zeichen == "," and tiefe == 0:
                stuecke.append("".join(aktuell))
                aktuell = []
                continue
        aktuell.append(zeichen)
    stuecke.append("".join(aktuell))
    return stuecke

# Werte, die im Repository als movement_type-Literal vorkommen, aber keine
# Bewegungstypen sind (Spaltennamen, Referenzsuffixe, Einheiten).
NICHT_BEWEGUNGSTYPEN = {"movement_type", "movements_by_type", "t", "i"}


def _python_dateien():
    for basis in ("app", "modules"):
        wurzel = REPO / basis
        if wurzel.exists():
            yield from wurzel.rglob("*.py")


@pytest.mark.unit
def test_kein_schreibpfad_erfindet_ein_neues_vokabular():
    """Der eigentliche Schutz gegen die Vokabular-Doppelung.

    Wer einen neuen movement_type einfuehrt, ohne ihn in die Richtungstabelle
    einzutragen, faellt hier auf - statt erst dann, wenn irgendein Bestand
    still falsch wird.
    """
    unbekannt: dict[str, set[str]] = {}
    for pfad in _python_dateien():
        try:
            inhalt = pfad.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "inventory_stock_movements" not in inhalt:
            continue
        treffer_der_datei = set()
        for muster in SCHREIB_MUSTER:
            treffer_der_datei.update(muster.findall(inhalt))
        treffer_der_datei.update(_positionale_werte(inhalt))
        for treffer in treffer_der_datei:
            wert = treffer.strip().lower()
            if not wert or wert in NICHT_BEWEGUNGSTYPEN:
                continue
            if wert not in KNOWN_TYPES:
                unbekannt.setdefault(wert, set()).add(str(pfad.relative_to(REPO)))

    assert not unbekannt, (
        "movement_type-Werte ohne Eintrag in MOVEMENT_DIRECTION: "
        + ", ".join(f"{wert} ({', '.join(sorted(dateien))})" for wert, dateien in sorted(unbekannt.items()))
    )


@pytest.mark.unit
def test_die_api_erlaubt_keinen_typ_ohne_richtung():
    """Payload-Seite des Waechters.

    POST /lager/bewegungen nimmt movement_type aus dem Request und prueft ihn
    gegen eine eigene Whitelist. Diese Werte stehen nirgends als
    SQL-Literal - die statischen Netze oben sehen sie nicht. Sie muessen
    trotzdem eine Richtung haben, sonst buchen sie ins Leere.
    """
    quelle = (REPO / "app" / "api" / "v1" / "endpoints" / "inventory_operations.py").read_text(
        encoding="utf-8"
    )
    treffer = re.search(r"allowed_types\s*=\s*\{([^}]*)\}", quelle)
    assert treffer, "allowed_types in create_lagerbewegung nicht gefunden"
    erlaubte = {
        wert.strip().strip("\"'").lower()
        for wert in treffer.group(1).split(",")
        if wert.strip()
    }
    assert erlaubte, "allowed_types ist leer - der Test wuerde sonst nichts pruefen"
    ohne_richtung = sorted(erlaubte - KNOWN_TYPES)
    assert not ohne_richtung, (
        "POST /lager/bewegungen erlaubt movement_type ohne Eintrag in "
        f"MOVEMENT_DIRECTION: {ohne_richtung}"
    )


# -- Ebene 3: Aggregation gegen die Datenbank -------------------------------


@pytest.fixture(scope="module")
def db_session():
    from app.core.database import SessionLocal

    try:
        session = SessionLocal()
        session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - ohne DB ist die Aggregation nicht pruefbar
        pytest.skip(f"keine Datenbank erreichbar: {exc.__class__.__name__}")
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def bewegungsprobe(db_session):
    """Je eine Zeile pro Richtungsklasse auf einer eigenen Artikel-/Lagerkombination."""
    import uuid

    referenz = db_session.execute(
        text(
            "SELECT article_id, warehouse_id, tenant_id "
            "FROM domain_inventory.inventory_stock_movements LIMIT 1"
        )
    ).first()
    if referenz is None:
        referenz = db_session.execute(
            text(
                "SELECT a.id, w.id, a.tenant_id "
                "FROM domain_inventory.articles a "
                "JOIN domain_inventory.warehouses w ON w.tenant_id = a.tenant_id LIMIT 1"
            )
        ).first()
    if referenz is None:
        pytest.skip("keine Artikel-/Lagerstammdaten fuer eine Bewegungsprobe vorhanden")

    article_id, warehouse_id, tenant_id = referenz
    marke = f"DOM-INV-005-{uuid.uuid4()}"

    zeilen = [
        ("wareneingang", 100),
        ("ZUGANG", 50),
        ("warenausgang", 30),
        ("ABGANG", 20),
        ("reservation", 999),
        ("inventory_count", 777),
    ]
    for movement_type, menge in zeilen:
        db_session.execute(
            text(
                """
                INSERT INTO domain_inventory.inventory_stock_movements
                    (id, tenant_id, article_id, warehouse_id, movement_type,
                     quantity, unit, notes, previous_stock, new_stock,
                     auto_created, ownership_type, storage_fee_relevant)
                VALUES (:id, :tid, :aid, :wid, :mt, :qty, 'kg', :notes,
                        0, 0, true, 'owned', false)
                """
            ),
            {
                "id": str(uuid.uuid4()),
                "tid": tenant_id,
                "aid": article_id,
                "wid": warehouse_id,
                "mt": movement_type,
                "qty": menge,
                "notes": marke,
            },
        )
    db_session.commit()
    try:
        yield {"article_id": article_id, "warehouse_id": warehouse_id, "tenant_id": tenant_id}
    finally:
        db_session.rollback()
        db_session.execute(
            text("DELETE FROM domain_inventory.inventory_stock_movements WHERE notes = :m"),
            {"m": marke},
        )
        db_session.commit()


@pytest.mark.integration
def test_saldo_zaehlt_abgang_negativ_und_zaehlwerte_gar_nicht(db_session, bewegungsprobe):
    """100 + 50 - 30 - 20 = 100; Reservierung und Zaehlwert bleiben draussen.

    Vor DOM-INV-005 kam hier 100 + 50 + 30 + 20 + 999 + 777 heraus, weil der
    ELSE-Zweig jeden nicht aufgezaehlten Typ positiv gezaehlt hat.
    """
    from app.services.inventory_stock_balance import current_stock

    saldo = current_stock(
        db_session,
        tenant_id=bewegungsprobe["tenant_id"],
        article_id=bewegungsprobe["article_id"],
        warehouse_id=bewegungsprobe["warehouse_id"],
    )
    # Der Bestand kann Altzeilen enthalten; entscheidend ist der Beitrag der Probe.
    beitrag = db_session.execute(
        text(
            f"SELECT COALESCE(SUM({direction_sql()}), 0) "  # nosec B608 - Fragment aus Modulkonstanten
            "FROM domain_inventory.inventory_stock_movements "
            "WHERE notes LIKE 'DOM-INV-005-%'"
        )
    ).scalar()
    assert float(beitrag) == 100.0
    assert isinstance(saldo, float)


@pytest.mark.integration
def test_keine_unbekannten_bewegungstypen_in_der_datenbank(db_session):
    """Laufzeit-Gegenstueck zum Repository-Waechter.

    Faengt Werte, die nicht als Literal im Code stehen, sondern aus Import oder
    Konfiguration kommen.
    """
    unbekannt = unknown_movement_types(db_session)
    assert not unbekannt, f"movement_type ohne bekannte Richtung in der Datenbank: {unbekannt}"
