"""Die Rollen-Projektion der Maskenaktionen entspricht den Abhaengigkeiten der Kommandowege (eine Quelle)."""
from scripts.generate_action_permission_projection import OUT, render


def test_projektion_ist_aktuell():
    assert OUT.read_text(encoding="utf-8") == render(), \
        "Neu erzeugen: python scripts/generate_action_permission_projection.py"


def test_bearbeiten_folgt_dem_aenderungsweg():
    import json

    screens = json.loads(render())["screens"]
    assert screens["agrar/kontrakte"]["kontrakt.update"] == [["KONTRAKT_ADMIN", "KONTRAKT_BEARBEITEN"]]
    assert screens["crm/lead"]["crm.lead.update"] == [["CRM_ADMIN", "CRM_BEARBEITEN", "admin"]]
