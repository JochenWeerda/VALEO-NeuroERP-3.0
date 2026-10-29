"""Eine Belegmaske, neun Varianten (BELEG-020).

Entscheidung des Auftraggebers vom 13.10.2026: Fuer jeden Schritt einer Belegfolge keine eigene Maske, sondern
die Variante einer Belegmaske — oft aendert sich nur die Bezeichnung, mal mit Preisen (Rechnung), mal nur mit
Mengen (Lieferschein).

``build_beleg_screen_definition(belegart)`` erzeugt aus einem Grundgeruest und der Variante des Belegvertrags
(``app/core/belegvertrag.py``) eine ScreenDefinition. Es gibt keine ausgeschriebene Definition je Belegart:

* Titel und Beschriftungen kommen aus der Variante (Bezeichnung, Partnerrolle).
* Preisspalten und Summenfelder gibt es nur in Varianten mit Preisen.
* Aktionen kommen aus dem Verzeichnis der Belegkommandos, Folgebelege aus der Variante.
* Gelesen wird ueber den Belegweg (``/api/v1/belege/…``); die Maske kennt keinen Speicher.

Die Definition beschreibt, was die Maske zeigen *kann*. Was der Leser sieht und darf, entscheidet der Server je
Beleg: ohne Preisrecht kommen die Preisfelder leer, und welche Aktion im Zustand des Belegs moeglich ist, sagt
``aktionen`` des Belegvertrags. Jede Aktion der Definition haengt ueber ``enabledWhen`` an einem Kopffeld
``aktion_<schluessel>``, das der Kopfweg aus ``aktionen`` setzt; die Sperrgruende stehen in ``aktionshinweis``.

Stand: Die Definitionen sind erzeugbar und geprueft, aber noch nicht in der Registry der Masken eingetragen —
der Eintrag folgt mit der Sichtpruefung im Browser (Entscheidung E4: keine Maskenmigration ohne sie).
"""
from __future__ import annotations

from typing import Any

from app.core import beleg_maske_parent as bmp
from app.core.beleg_maske_parent import beleg_meridian_layout_extras
from app.core.belegvertrag import BELEGARTEN, Belegvariante

REITER = bmp.REITER
screen_id = bmp.screen_id
zustandsfeld = bmp.zustandsfeld
positionsspalten = bmp.beleg_positionsspalten
kopffelder = bmp.beleg_kopffelder
aktionen = bmp.beleg_aktionen

_PARTNER = {"kunde": "Kunde", "lieferant": "Lieferant"}


def _build_via_parent(belegart: str) -> dict[str, Any]:
    from app.core.beleg_maske_parent import _PRODUCTION_NO_WORKFLOW_REASON

    variante = BELEGARTEN[belegart]
    partner = _PARTNER[variante.partnerrolle]
    slug = belegart.replace("_", "-")
    return bmp.build_beleg_maske_parent(
        belegart,
        business_purpose=(
            f"{variante.bezeichnung} lesen: Kopf, {partner}, Positionen"
            f"{' mit Preisen und Summen' if variante.mit_preisen else ' (nur Mengen)'}, Belegkette, Dokumente und Verlauf. "
            "Dieselben Daten liefert das MCP-Werkzeug beleg.lesen."
        ),
        example_prompts=[
            f"Zeige die Positionen von {variante.bezeichnung} {{entity_id}}.",
            f"Aus welchem Beleg ist {variante.bezeichnung} {{entity_id}} entstanden?",
            f"Was ist der Stand von {variante.bezeichnung} {{entity_id}}, und was geht als Nächstes?",
        ],
        test_id=f"beleg-{slug}",
        sensitive_fields=(
            ["netto", "steuer", "brutto", "einzelpreis", "rabatt_prozent"] if variante.mit_preisen else []
        ),
        meridian_profile=True,
        register_tabs=True,
        no_process_chain_reason=(
            "BELEG-020: Die Belegfolge laeuft ueber Reiter Kette, Folgebeleg-Aktionen und "
            "ProcessRibbon — nicht ueber process_chains.yaml (Legacy-Pfade sales/*, einkauf/*)."
        ),
        test_selectors={
            "screenRoot": f"[data-testid='beleg-{slug}']",
            "summaryArea": "[data-testid='mask-summary']",
        },
        no_workflow_reason=_PRODUCTION_NO_WORKFLOW_REASON,
    )


def build_beleg_screen_definition(belegart: str) -> dict[str, Any]:
    return _build_via_parent(belegart)

def alle_beleg_screen_definitions() -> dict[str, dict[str, Any]]:
    return {screen_id(art): build_beleg_screen_definition(art) for art in BELEGARTEN}


# Native code release, restricted to the already approved visual-test tenant.
# These definitions are not editable Studio drafts and never mint Studio proof.
NATIVE_BELEG_TENANTS = frozenset({"00000000-0000-0000-0000-000000000051"})


def native_beleg_definition(mask_id: str, tenant_id: str) -> dict[str, Any] | None:
    if tenant_id not in NATIVE_BELEG_TENANTS:
        return None
    for art in BELEGARTEN:
        if screen_id(art) == mask_id:
            from app.core.document_screen_versions import document_definition
            return document_definition(art)
    return None
