#!/usr/bin/env python3
"""
GAP-Analyse Generator für Sales/Order-to-Cash

Dieses Script:
1. Liest Evidence aus evidence/screenshots/sales/ und swarm/handoffs/ui-explorer-sales-*.md
2. Erstellt/aktualisiert gap/matrix-sales.csv
3. Generiert gap/gaps-sales.md mit priorisierten GAP-Cards

Usage:
    python swarm/make_gaps_sales.py
"""

import os
import csv
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# Pfade
ROOT = Path(__file__).parent.parent
EVIDENCE_DIR = ROOT / "evidence" / "screenshots" / "sales"
HANDOFFS_DIR = ROOT / "swarm" / "handoffs"
GAP_DIR = ROOT / "gap"
MATRIX_FILE = GAP_DIR / "matrix-sales.csv"
GAPS_FILE = GAP_DIR / "gaps-sales.md"


@dataclass
class GapCard:
    """Eine GAP-Card mit allen relevanten Informationen"""
    card_id: str
    capability_ids: List[str]
    gap_title: str
    status: str
    priority: str
    bi: int
    pf: int
    rc: int
    ia: int
    score: float = 0.0
    screenshots: List[str] = field(default_factory=list)
    flows: List[str] = field(default_factory=list)
    traces: List[str] = field(default_factory=list)
    gap_description: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    solution_type: str = ""
    technical_implementation: str = ""
    playwright_tests: str = ""
    dependencies: List[str] = field(default_factory=list)
    owner: str = ""
    notes: str = ""
    
    def calculate_score(self):
        """Berechnet den Prioritäts-Score"""
        if self.ia > 0:
            self.score = (self.bi * self.pf * self.rc) / self.ia
        else:
            self.score = 0.0


class GapAnalyzer:
    """Hauptklasse für GAP-Analyse"""
    
    def __init__(self):
        self.gaps: List[GapCard] = []
        self.evidence_files: List[str] = []
        self.handoff_files: List[str] = []
        
    def scan_evidence(self):
        """Scannt Evidence-Verzeichnisse nach Screenshots und Handoffs"""
        if EVIDENCE_DIR.exists():
            for file in EVIDENCE_DIR.glob("*.png"):
                self.evidence_files.append(file.name)
            for file in EVIDENCE_DIR.glob("*.json"):
                self.evidence_files.append(file.name)
        
        if HANDOFFS_DIR.exists():
            for file in HANDOFFS_DIR.glob("ui-explorer-sales-*.md"):
                self.handoff_files.append(file.name)
        
        print(f"[OK] {len(self.evidence_files)} Evidence-Dateien gefunden")
        print(f"[OK] {len(self.handoff_files)} Handoff-Dateien gefunden")
    
    def load_matrix(self) -> List[Dict]:
        """Lädt die Matrix-Daten"""
        if not MATRIX_FILE.exists():
            print(f"[WARN] Matrix-Datei nicht gefunden: {MATRIX_FILE}")
            return []
        
        rows = []
        with open(MATRIX_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                rows.append(row)
        
        return rows
    
    def create_gap_from_matrix_row(self, row: Dict, index: int) -> Optional[GapCard]:
        """Erstellt eine GapCard aus einer Matrix-Zeile"""
        try:
            capability_id = row.get('Capability_ID', '').strip()
            if not capability_id:
                return None
            
            status = row.get('NeuroERP_Status(Yes/Partial/No)', 'No').strip() or 'No'
            priority_str = row.get('Priorität(MUSS/SOLL/KANN)', 'KANN').strip()
            
            priority_map = {'MUSS': 5, 'SOLL': 3, 'KANN': 1}
            pf = priority_map.get(priority_str, 1)
            
            bi = 3
            rc = 2
            ia = 3
            
            screenshots = [s.strip() for s in row.get('Evidence_Screenshot_IDs', '').split(',') if s.strip()]
            flows = [f.strip() for f in row.get('Evidence_Flow_IDs', '').split(',') if f.strip()]
            
            gap_title = row.get('Subcapability', capability_id)
            solution_type = row.get('Loesungstyp(A/B/C/D)', 'C').strip() or 'C'
            gap_description = row.get('Gap_Beschreibung', '').strip()
            
            card = GapCard(
                card_id=f"SALES-{index:03d}",
                capability_ids=[capability_id],
                gap_title=gap_title,
                status=status,
                priority=priority_str,
                bi=bi,
                pf=pf,
                rc=rc,
                ia=ia,
                screenshots=screenshots,
                flows=flows,
                gap_description=gap_description,
                solution_type=solution_type,
                owner=row.get('Owner', '').strip(),
                notes=row.get('Notes', '').strip()
            )
            
            card.calculate_score()
            return card
        except Exception as e:
            print(f"[WARN] Fehler beim Erstellen der GapCard: {e}")
            return None
    
    def generate_gaps_markdown(self):
        """Generiert die gaps-sales.md Datei"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        sorted_gaps = sorted(
            self.gaps, 
            key=lambda g: (g.score, {'MUSS': 3, 'SOLL': 2, 'KANN': 1}.get(g.priority, 0)), 
            reverse=True
        )
        
        status_counts = {'Yes': 0, 'Partial': 0, 'No': 0}
        for gap in self.gaps:
            status_counts[gap.status] = status_counts.get(gap.status, 0) + 1
        
        total = len(self.gaps)
        
        md = f"""# GAP-Liste Verkauf (Order-to-Cash) – Valero NeuroERP

Stand: {today}

Scope: Verkauf / CRM / Quote-to-Cash / Fulfillment / Billing-to-Cash

Evidence-Quelle:

- /evidence/screenshots/sales/*

- /swarm/handoffs/ui-explorer-sales-*.md

- Playwright traces/videos

Referenz:

- gap/capability-model-sales.md

- gap/matrix-sales.csv

---

## 1) Priorisierungslogik

### 1.1 Bewertungsdimensionen (1–5)

**A) Business Impact (BI)**  

1 = geringe Auswirkung / selten genutzt  

3 = merkliche Auswirkung auf Umsatz/Prozess  

5 = kritisch für Kernumsatz / Kundenzufriedenheit / Cashflow  

**B) Pflichtgrad (PF)**  

MUSS = 5  

SOLL = 3  

KANN = 1  

**C) Risiko / Compliance (RC)**  

1 = kein Risiko  

3 = mittleres Risiko (z.B. vertraglich, steuerlich indirekt)  

5 = hohes Risiko (z.B. gesetzliche Pflicht, Audit-Lücke)  

**D) Implementierungsaufwand (IA)**  

1 = sehr klein (Konfig / Verdrahtung / UI-Feld)  

3 = mittel (Workflow, Adapter, 1–2 Screens + Logik)  

5 = groß (Neues Modul / tiefe Logik / viele Abhängigkeiten)

### 1.2 Score-Formel

**Prioritäts-Score (PS) = (BI × PF × RC) / IA**

- Ergebnis typischerweise 1–125  

- Je höher, desto früher umsetzen.  

- Bei Gleichstand: zuerst **MUSS**, dann niedrigere IA.

---

## 2) Zusammenfassung

### 2.1 TOP-Gaps nach Score

| Rank | Capability_ID | Gap-Titel | Status | PS | Lösungstyp | Owner |
|---|---|---|---|---:|---|---|
"""
        
        for i, gap in enumerate(sorted_gaps[:10], 1):
            md += f"| {i} | {', '.join(gap.capability_ids)} | {gap.gap_title} | {gap.status} | {gap.score:.1f} | {gap.solution_type} | {gap.owner} |\n"
        
        md += f"""
### 2.2 Abdeckung (Snapshot)

- Yes: {status_counts['Yes']}  

- Partial: {status_counts['Partial']}  

- No: {status_counts['No']}  

- Gesamt: {total}

---

## 3) GAP-Details (Solution-Cards)

> Jede Card ist ein umsetzbares Ticket-Paket.  

> Evidence MUSS immer Screenshot/Flow/Trace referenzieren.

---

"""
        
        for gap in sorted_gaps:
            screenshots_str = ', '.join([f"`{s}`" for s in gap.screenshots]) if gap.screenshots else "*keine*"
            flows_str = ', '.join([f"`{f}`" for f in gap.flows]) if gap.flows else "*keine*"
            traces_str = ', '.join([f"`{t}`" for t in gap.traces]) if gap.traces else "*keine*"
            acceptance_str = '\n  - '.join(gap.acceptance_criteria) if gap.acceptance_criteria else "*Zu definieren*"
            deps_str = ', '.join(gap.dependencies) if gap.dependencies else "*keine*"
            
            md += f"""### CARD {gap.card_id} — {gap.gap_title}

**Capability_ID(s):** {', '.join(gap.capability_ids)}  

**Status in NeuroERP:** {gap.status}  

**Priorität (MUSS/SOLL/KANN):** {gap.priority}  

**Score-Berechnung:**  

- BI = {gap.bi}  

- PF = {gap.pf}  

- RC = {gap.rc}  

- IA = {gap.ia}  

**PS = ({gap.bi}×{gap.pf}×{gap.rc})/{gap.ia} = {gap.score:.1f}**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): {screenshots_str}  

- Flow(s): {flows_str}  

- Trace(s): {traces_str}  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

{gap.gap_description or '*Zu ergänzen - siehe capability-model-sales.md*'}

**Zielverhalten / Akzeptanzkriterien**  

- {acceptance_str}

**Lösungstyp**  

- {gap.solution_type} = {'Konfiguration/Verdrahtung' if gap.solution_type == 'A' else 'Integration/Adapter' if gap.solution_type == 'B' else 'neues Feature/Modul' if gap.solution_type == 'C' else 'UX/Reifegrad/Edge-Case'}

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

{deps_str}

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

"""
        
        md += """## 4) Nächste Schritte

1. UI-Explorer durch Verkaufsmodule jagen (Lead → Quote → Order → Delivery → Invoice → Payment).  

2. Evidence in matrix-sales.csv eintragen.  

3. Aus matrix automatisch Cards befüllen (Agent).  

4. Feature-Backlog + Umsetzung nach Score.

---

## 5) Agent-Loop Integration

**ROLE: Feature-Engineer**

Input:

- gap/gaps-sales.md

- gap/matrix-sales.csv

- evidence + traces

Task:

1. Nimm die höchste Card (Rank 1).

2. Erstelle Pflichten-Umsetzung:

   - Konfig/Workflow/Code

3. Ergänze/Erstelle Playwright-Tests.

4. Evidence aktualisieren.

5. PR/Branch erstellen.

Output:

- Code + Tests

- Evidence

- Update matrix-sales.csv (Status -> Yes)

- Notiz /swarm/handoffs/feature-sales-top1.md

"""
        
        GAPS_FILE.write_text(md, encoding='utf-8')
        print(f"[OK] {GAPS_FILE} generiert")
    
    def run(self):
        """Hauptmethode"""
        print("[INFO] Starte GAP-Analyse fuer Sales...")
        
        GAP_DIR.mkdir(exist_ok=True)
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        
        self.scan_evidence()
        
        matrix_rows = self.load_matrix()
        
        for index, row in enumerate(matrix_rows, 1):
            gap = self.create_gap_from_matrix_row(row, index)
            if gap:
                self.gaps.append(gap)
        
        print(f"[OK] {len(self.gaps)} Gaps gefunden")
        
        self.generate_gaps_markdown()
        
        print("[OK] GAP-Analyse abgeschlossen!")
        print(f"[INFO] Ergebnisse in {GAPS_FILE}")


if __name__ == "__main__":
    analyzer = GapAnalyzer()
    analyzer.run()

