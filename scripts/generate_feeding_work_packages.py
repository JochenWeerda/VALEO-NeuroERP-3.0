"""Generate the deterministic 240-package feeding delivery program.

The structured source stays reviewable here; generated Markdown is committed so
humans and agents can work without executing the generator first.
"""
from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).parents[1]
OUT = ROOT / "docs" / "specs" / "feeding" / "work-packages"

TRACKS = [
    ("organisation", "Betriebsakte und Zugriffsraum", "FEED-BUS-001/002, FEED-RBAC-003/004", None, "Betriebshierarchie und Zugriff sind tenant-sicher nutzbar"),
    ("tiergruppen", "Tiergruppen und Gruppenhistorie", "FEED-HERD-001/002/003", 1, "Tiergruppen sind fachlich vollstaendig und zeitlich nachvollziehbar"),
    ("einheiten", "Naehrstoffe, Einheiten und Rundung", "FEED-MAT-003, FEED-LAB-003", None, "Werte werden ohne Basis- oder Einheitenverlust verarbeitet"),
    ("futtermittel", "Futtermittel und Referenzwerte", "FEED-MAT-001/002", 3, "Futter ist versioniert, suchbar und solverfaehig"),
    ("analysen", "Futteranalysen und Provenienz", "FEED-LAB-001/002/004", 4, "Analysen sind plausibilisiert, freigegeben und nachweisbar"),
    ("bedarf", "Bedarfs- und Bewertungssysteme", "FEED-REQ-001/002", 3, "Bedarf ist regelversioniert und reproduzierbar"),
    ("ration-lifecycle", "Rationsversion und Lifecycle", "FEED-RAT-001/002/005", 6, "Rationsentscheidungen sind unveraenderlich und auditierbar"),
    ("editor", "Produktiver Rationseditor", "FEED-RAT-003/004, FEED-UI-002", 7, "Berater bearbeiten Rationen effizient und fehlerarm"),
    ("warnungen", "Bewertung und Warnungen", "FEED-EVAL-001/002", 7, "Jede Warnung ist erklaerbar und handlungsorientiert"),
    ("optimierung", "Optimierung und Infeasibility", "FEED-OPT-001/004/005", 6, "Solverlaeufe sind reproduzierbar und Konflikte erklaert"),
    ("varianten", "Variantenvergleich und Entscheidung", "FEED-CMP-001, FEED-RAT-005", 10, "Varianten werden transparent verglichen und begruendet"),
    ("plan", "Fuetterungsplan und Mischfolge", "FEED-PLAN-001/002", 11, "Freigegebene Rationen werden sicher ausfuehrbar"),
    ("ausfuehrung", "Ist-Fuetterung und Rueckmeldung", "FEED-ACT-001/002/004", 12, "Plan und tatsaechliche Fuetterung sind abgleichbar"),
    ("versorgung", "Bedarf, Bestand und Reichweite", "FEED-SUP-001/002/003", 12, "Versorgungsrisiken werden rechtzeitig sichtbar"),
    ("einkauf", "Kontrollierte Einkaufsuebergabe", "FEED-SUP-003", 14, "Bedarf wird ohne autonome Bestellung uebergeben"),
    ("leistung", "Leistung und Wirkungscontrolling", "FEED-PERF-001/002/003/004", 13, "Wirkung ist mit Datenabdeckung und Versionen messbar"),
    ("beratung", "Beratungsfall und Beobachtung", "FEED-CONS-001", 16, "Beratungsanlass und Entscheidung bilden eine Akte"),
    ("massnahmen", "Massnahmen und Wiedervorlage", "FEED-CONS-002, FEED-COLLAB-002", 17, "Massnahmen haben Owner, Termin und Wirksamkeitspruefung"),
    ("berichte", "Berichte und Nachweise", "FEED-REP-001/002/003", 18, "Freigegebene Staende werden reproduzierbar berichtet"),
    ("zusammenarbeit", "Zusammenarbeit und Benachrichtigung", "FEED-COLLAB-001/002", 17, "Beteiligte arbeiten scope- und ereignisbezogen zusammen"),
    ("labor", "Laborintegration und Quarantaene", "FEED-INT-001, FEED-LAB-002", 5, "Laborwerte gelangen idempotent und geprueft ins System"),
    ("herd-data", "Herdenmanagement-Delta-Sync", "FEED-HERD-004, FEED-INT-001", 2, "Moves, Deletes und Messwerte werden providerneutral synchronisiert"),
    ("mixer", "Mixer- und agrirouter-Austausch", "FEED-PLAN-003, FEED-INT-002/003", 13, "Planexport und Rueckmeldung wirken genau einmal"),
    ("agenten", "KI-Agenten und Governance", "FEED-UI-003, FEED-NFR-SEC", 20, "Agenten unterstuetzen erklaerbar innerhalb von Policies und Human Gates"),
]

STAGES = [
    ("Vertrag und erste Journey", "ein kleinster realer Nutzerfall funktioniert Ende-zu-Ende", "Happy Path mit persistiertem Ergebnis und sichtbarer Herkunft", "Contract-/Domain-Test fuer den ersten Nutzerfall schlaegt fehl", "kleinsten Domain-, API- und Meridian-Pfad implementieren", "Begriffe und Grenzen am Domainmodell ausrichten", "fokussierte Domain-, API- und Screen-Suite", "M"),
    ("Grenzen und Validierung", "ungueltige oder unvollstaendige Eingaben werden sicher erklaert", "Grenz-, Missing- und Conflict-Faelle liefern stabile Fehler", "Boundary-/Property-Test reproduziert die ungeschuetzte Grenze", "Validierung und ProblemDetails minimal ergaenzen", "Validierungsregeln zentralisieren", "Happy Path plus Boundary-/Property-Suite", "S"),
    ("Tenant und Berechtigung", "nur berechtigte Personen sehen und aendern den fachlichen Scope", "Tenant, Rolle und Business-Grant werden serverseitig erzwungen", "negativer Isolation-/403-Test zeigt den Zugriff", "Policy am Application-Service/Endpoint schliessen", "Policy-Duplikate in zentralen Guard ueberfuehren", "Authz-, Enumeration- und Tenant-Regression", "M"),
    ("Version und Audit", "Entscheidungen bleiben zeitlich und fachlich nachvollziehbar", "Aenderung erzeugt Version/Audit statt historischen Stand zu ueberschreiben", "Workflow-/Repository-Test zeigt verlorene Historie", "Versionierung und Auditereignis minimal persistieren", "Event- und Auditnamen vereinheitlichen", "Lifecycle-, Migration- und Audit-Suite", "M"),
    ("Fehler und Wiederaufnahme", "Nutzer koennen nach Konflikt oder Teilausfall sicher fortsetzen", "Retry ist idempotent und Fehlerzustand handlungsorientiert", "Idempotenz-/Recovery-Test erzeugt Doppelwirkung oder Sackgasse", "Idempotency Key, Journal oder Resume-Punkt ergaenzen", "Fehlerklassen und Kompensation schaerfen", "Failure-, Retry- und Concurrency-Regression", "M"),
    ("Meridian UX und Accessibility", "die Aufgabe ist auf Desktop und mobil zugaenglich bedienbar", "native ScreenDefinition, Tastatur, Focus, Empty/Error/Loading und WCAG sind abgedeckt", "Component-/axe-Test zeigt fehlenden Bedienvertrag", "ScreenDefinition/RenderPlan und kleinstes Domain-Overlay ergaenzen", "freie UI-Logik in Runtime-Vertrag zurueckfuehren", "Component-, axe-, Keyboard- und Route-Suite", "M"),
    ("Events und Integration", "nachgelagerte Prozesse erhalten ein stabiles, nachweisbares Signal", "Outbox/Event oder neutraler Port ist schemafest und genau-einmal-wirksam", "Contract-/Replay-Test zeigt Drift oder Doppelwirkung", "Event/Port plus Idempotenz minimal implementieren", "Mapping und Provideradapter trennen", "Schema-, Replay-, Outbox- und Connector-Suite", "L"),
    ("Performance und Beobachtbarkeit", "der Nutzerfall bleibt unter realer Last steuerbar", "Budget, Metriken, Traces und fachliche Alarmgrenzen sind nachgewiesen", "Benchmark verletzt bewusst das vereinbarte Budget", "Query/Cache/Batching und Metrik minimal optimieren", "Optimierung ohne Semantikaenderung isolieren", "Benchmark-, Explain-, Resilience- und SLO-Suite", "M"),
    ("Migration und Kompatibilitaet", "Bestandsdaten und bestehende Konsumenten wechseln ohne Bruch", "Upgrade, Backfill, Dual-Read/Switch und Forward-Fix sind geprueft", "Migrations-/Aequivalenztest zeigt Drift zum Bestand", "additive Migration und idempotenten Backfill liefern", "Kompatibilitaetsadapter befristen und dokumentieren", "Upgrade-, Backfill-, Golden- und API-Regression", "L"),
    ("Release-Journey und Betriebsabnahme", "die Capability ist fuer den Pilotbetrieb abnahmefaehig", "E2E-Journey, Security, A11y, Runbook, Flag und Rollback sind gruen", "Release-Journey scheitert am letzten offenen Nutzerergebnis", "fehlende vertikale Luecke ohne Scope-Ausweitung schliessen", "tote Adapter/Flags entfernen und Doku synchronisieren", "vollstaendige Capability-, Playwright- und Release-Gates", "L"),
]


def package_section(track_index: int, stage_index: int) -> str:
    slug, title, requirements, base_track, track_acceptance = TRACKS[track_index]
    stage_title, benefit, acceptance, red, green, refactor, regression, effort = STAGES[stage_index]
    number = track_index * 10 + stage_index + 1
    package_id = f"FEED-WP-{number:03d}"
    dependencies: list[str] = []
    if base_track:
        dependencies.append(f"FEED-WP-{base_track * 10:03d}")
    if stage_index:
        dependencies.append(f"FEED-WP-{number - 1:03d}")
    depends = ", ".join(dict.fromkeys(dependencies)) or "keine"
    test_a = (number - 1) % 200 + 1
    test_b = (number + 66) % 200 + 1
    return f"""## {package_id} — {title}: {stage_title}

**Nutzen:** Im Bereich {title} {benefit}; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** {requirements}. **Abhaengig von:** {depends}. **Aufwand:** {effort} (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** {track_acceptance}; {acceptance}. Nachweis ueber FEED-T{test_a:03d} und FEED-T{test_b:03d}.

**Red:** {red}; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** {green}; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** {refactor}, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** {regression} sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.
"""


def _write_or_check(path: Path, content: str, *, check: bool) -> None:
    if check:
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            raise SystemExit(f"feeding work-package drift: {path.relative_to(ROOT)}")
        return
    path.write_text(content, encoding="utf-8")


def generate(*, check: bool = False) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    expected: set[Path] = set()
    index_rows = []
    for track_index, (slug, title, requirements, _base, _acceptance) in enumerate(TRACKS):
        start = track_index * 10 + 1
        end = start + 9
        path = OUT / f"{track_index + 1:02d}-{slug}.md"
        expected.add(path)
        header = f"""---
title: "Arbeitspakete {start:03d}–{end:03d} — {title}"
type: plan
audience: [produkt, architektur, entwickler, qa, agent]
owner: domain/agrar
status: geplant
last_reviewed: 2026-07-15
version: 1.0.0
generated_by: scripts/generate_feeding_work_packages.py
---

# {title}

Requirements: {requirements}. Paketstatus und TDD-Laufnachweis werden bei Claim im Workboard/Slice gefuehrt; dieses Dokument bleibt der stabile Liefervertrag.

"""
        body = "\n".join(package_section(track_index, stage) for stage in range(10))
        _write_or_check(path, header + body, check=check)
        index_rows.append(f"| {start:03d}–{end:03d} | [{title}]({path.name}) | {requirements} |")
    for stale in OUT.glob("[0-9][0-9]-*.md"):
        if stale not in expected:
            if check:
                raise SystemExit(f"stale feeding work-package file: {stale.relative_to(ROOT)}")
            stale.unlink()
    index = """---
title: "Fuetterungsberatung — 240 vertikale TDD-Arbeitspakete"
type: plan
audience: [produkt, architektur, entwickler, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
generated_by: scripts/generate_feeding_work_packages.py
---

# Arbeitsprogramm

Jedes Paket ist einzeln claimbar und liefert ein pruefbares Nutzerergebnis. Die zehn Pakete je Capability sind keine getrennten Technikphasen: jedes durchlaeuft die jeweils betroffenen Schichten vertikal und folgt Red → Green → Refactor → Regression. Aufwand ist eine Vor-Refinement-Schaetzung, kein Terminversprechen.

| Pakete | Capability | Requirements |
|---|---|---|
""" + "\n".join(index_rows) + "\n"
    _write_or_check(OUT / "README.md", index, check=check)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    generate(check=parser.parse_args().check)
