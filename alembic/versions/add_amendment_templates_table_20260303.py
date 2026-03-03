"""add amendment_templates table and seed EHB/EB Nachtrag

Revision ID: a1b2c3d4e5f6
Revises: 9efbf36742d6
Create Date: 2026-03-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '9efbf36742d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'amendment_templates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('body_markdown', sa.Text(), nullable=False),
        sa.Column('sections_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id', name='amendment_templates_pkey'),
        sa.UniqueConstraint('code', name='amendment_templates_code_key'),
        schema='domain_shared',
    )
    op.create_index('ix_amendment_templates_code', 'amendment_templates', ['code'], unique=True, schema='domain_shared')

    # Seed: EHB/EB-Nachtrag (Vorlage 1:1 aus Anforderung)
    conn = op.get_bind()
    body_md = R'''## NACHTRAG / AMENDMENT Nr. [__]

**zum Kontrakt Nr. [__]** vom **[TT.MM.JJJJ]**

**Verkäufer:** [Firma / Landwirt, Anschrift]
**Käufer:** [Firma, Anschrift]
**Ware:** [z. B. Weizen/Raps/Gerste] **Erntejahr/Kampagne:** [**]
**Kontraktmenge:** [**] t  **Toleranz:** ±[__]% (Wahl: [ ] Verkäufer [ ] Käufer)

### A. Vertragsgrundlage (nur EHB/EB)

1. **Es gelten ausschließlich die Einheitsbedingungen im Deutschen Getreidehandel (EHB/EB), Neufassung gültig ab 01.12.2017**, soweit nachstehend nichts Abweichendes vereinbart ist. ([DLG e.V.](https://www.dlg.org/mediacenter/dlg-merkblaetter/dlg-merkblatt-421-einheitsbedingungen-im-deutschen-getreidehandel))
2. **Rangfolge:** (1) Dieser Nachtrag (inkl. Anlagen) → (2) Kontrakt → (3) EHB/EB.
3. Entgegenstehende/abweichende Bedingungen der Gegenpartei werden nicht Vertragsbestandteil.

---

## B. Änderungen (ersetzen die bisherigen Regelungen, im Übrigen bleibt alles unverändert)

### 1) Liefermodell / Lieferweg (bitte auswählen)

**Lieferart neu:**
[ ] **Strecke ab Landwirt (Hofabholung)** ab: [Adresse Hof / Abholpunkt]
[ ] **Anlieferung Lager → Lagerhaus** an: [Lagerhaus/Standort]
[ ] **Strecke direkt** an: [Empfänger/Lager/Werk, Ort]

**Übergabe-/Annahmestelle:** [**]
**Avisierung/Vorlauf:** [**] Stunden vor Abholung/Anlieferung
**Lieferfenster neu:** von **[__]** bis **[__]**
**Teillieferungen:** [ ] zulässig  [ ] nicht zulässig  **Mindestpartie:** [__] t

---

### 2) Transport / Fracht / Wartezeit

**Disposition/Transport durch:** [ ] Käufer  [ ] Verkäufer  [ ] Landhandel/Spediteur: [**]
**Frachtregel:** [ ] inkl.  [ ] zzgl.  [ ] pauschal [**] €/t  [ ] nach Nachweis
**Wartezeit frei:** [**] h, danach **[**] €/h** (oder: [Regelung])

---

### 3) Verwiegung / Probenahme / Analyse (Abrechnung maßgeblich)

**Maßgebliche Verwiegung:** [ ] Annahmewaage [Ort]  [ ] Hofwaage  [ ] sonst: [**]
**Probenahme:** [ ] bei Annahme  [ ] bei Abholung  [ ] kombiniert
**Analyse/Labor:** [ ] Lagerhauslabor  [ ] extern: [**]
**Charge/Lagerschein (falls Lagerware):** [__]

---

### 4) Qualität / Basis / Abzüge (nur wenn geändert)

**Qualitätsbasis:**
* Feuchte Basis [**]% (max [**]%)
* Protein Basis [__]%
* HL-Gewicht Basis [__] kg/hl
* Besatz Basis [**]% (max [**]%)
* Sonstiges (z. B. Geruch, Mutterkorn, DON): [__]

**Abrechnung bei Abweichung:**
[ ] Minderwert/Abzüge gemäß **Anlage 1 (Abzugstabelle)**
[ ] Trocknung/Reinigung gemäß **Anlage 2 (Kostenregelung)**
[ ] Individuelle Regel: [__]

**Zurückweisung nur bei (klar definieren):** [z. B. starker Fremdgeruch/Schimmel/Überschreitung Grenzwert __]

---

### 5) Menge / Umwidmung (optional)

[ ] **Mengenänderung:** neue Menge **[__] t** (ersetzt [**] t)
[ ] **Umwidmung Lagerware → Verkauf** zum **[Datum]** (Partie/Lagerschein [**])
**Eigentumsübergang:** [ ] am Umwidmungsdatum  [ ] bei Auslagerung  [ ] bei Abrechnung
**Lagergeld bis [Datum]:** trägt [ ] Landwirt [ ] Landhandel [ ] Käufer | Satz: [__]

---

### 6) Preis / Preisfixierung / Prämien (optional)

[ ] **Fixpreis neu:** **[__] €/t** für [**] t (Restmenge: [Regel])
[ ] **Preisfixierung:** Fixierung bis **[Datum/Uhrzeit]**, Fixierung via [E-Mail/Telefon]
[ ] **Prämie/Abschlag:** [Regel, z. B. Protein +** €/t je 0,5%]
[ ] **Vergleich/Buy-out:** Ausgleich [__] (Formel/pauschal)

---

### 7) Abrechnung / Zahlung (typisch Landwirt)

**Abrechnung:** binnen [**] Werktagen nach [ ] Verwiegung  [ ] Analyseabschluss
**Zahlung:** [**] Tage netto ab [ ] Abrechnung  [ ] Rechnung  [ ] Liefertag
**Skonto:** [ ] __% bei Zahlung binnen __ Tagen  [ ] entfällt
**Gutschrift/Selbstfakturierung:** [ ] ja  [ ] nein

---

### 8) Dokumente

Mit Lieferung/Abholung sind zu übergeben:
[ ] Lieferschein  [ ] Wiegeschein  [ ] Analyse/CoA (falls vorhanden)  [ ] Chargen-/Lagerschein  [ ] Sonstiges: [__]

---

## C. Schluss

Alle übrigen Bestimmungen des Kontrakts bleiben unverändert. Dieser Nachtrag tritt **mit Unterzeichnung** in Kraft (oder: ab **[Datum/Uhrzeit]**).

**Ort/Datum:** [__]

**Verkäufer** (rechtsverbindlich) ____________________  Name/Funktion: [**]
**Käufer** (rechtsverbindlich) ______________________  Name/Funktion: [**]

**Anlagen (falls genutzt):**
Anlage 1 Abzugstabelle Qualität | Anlage 2 Trocknung/Reinigung | Anlage 3 Fracht/Standgeld
'''
    # sections_schema: Felddefinitionen für Formular (B.1–B.8, C)
    sections_schema = {
        "sections": [
            {"key": "b1", "title": "Liefermodell / Lieferweg", "fields": [
                {"key": "lieferart", "label": "Lieferart", "type": "choice", "options": ["Strecke ab Landwirt (Hofabholung)", "Anlieferung Lager → Lagerhaus", "Strecke direkt"]},
                {"key": "abholpunkt", "label": "Adresse Hof / Abholpunkt", "type": "text"},
                {"key": "lagerhaus_standort", "label": "Lagerhaus/Standort", "type": "text"},
                {"key": "empfaenger_ort", "label": "Empfänger/Lager/Werk, Ort", "type": "text"},
                {"key": "uebergabe_annahmestelle", "label": "Übergabe-/Annahmestelle", "type": "text"},
                {"key": "avisierung_stunden", "label": "Avisierung/Vorlauf (Stunden)", "type": "text"},
                {"key": "lieferfenster_von", "label": "Lieferfenster von", "type": "date"},
                {"key": "lieferfenster_bis", "label": "Lieferfenster bis", "type": "date"},
                {"key": "teillieferungen", "label": "Teillieferungen", "type": "choice", "options": ["zulässig", "nicht zulässig"]},
                {"key": "mindestpartie_t", "label": "Mindestpartie (t)", "type": "text"}
            ]},
            {"key": "b2", "title": "Transport / Fracht / Wartezeit", "fields": [
                {"key": "disposition_durch", "label": "Disposition/Transport durch", "type": "choice", "options": ["Käufer", "Verkäufer", "Landhandel/Spediteur"]},
                {"key": "spediteur", "label": "Landhandel/Spediteur", "type": "text"},
                {"key": "frachtregel", "label": "Frachtregel", "type": "choice", "options": ["inkl.", "zzgl.", "pauschal €/t", "nach Nachweis"]},
                {"key": "fracht_pauschal", "label": "Pauschal €/t", "type": "text"},
                {"key": "wartezeit_frei_h", "label": "Wartezeit frei (h)", "type": "text"},
                {"key": "standgeld_eur_h", "label": "danach €/h", "type": "text"}
            ]},
            {"key": "b3", "title": "Verwiegung / Probenahme / Analyse", "fields": [
                {"key": "massgebliche_verwiegung", "label": "Maßgebliche Verwiegung", "type": "choice", "options": ["Annahmewaage", "Hofwaage", "sonst"]},
                {"key": "verwiegung_ort", "label": "Ort/Details", "type": "text"},
                {"key": "probenahme", "label": "Probenahme", "type": "choice", "options": ["bei Annahme", "bei Abholung", "kombiniert"]},
                {"key": "analyse_labor", "label": "Analyse/Labor", "type": "choice", "options": ["Lagerhauslabor", "extern"]},
                {"key": "analyse_extern", "label": "Extern (Name)", "type": "text"},
                {"key": "charge_lagerschein", "label": "Charge/Lagerschein (Lagerware)", "type": "text"}
            ]},
            {"key": "b4", "title": "Qualität / Basis / Abzüge", "fields": [
                {"key": "feuchte_basis", "label": "Feuchte Basis %", "type": "text"},
                {"key": "feuchte_max", "label": "Feuchte max %", "type": "text"},
                {"key": "protein_basis", "label": "Protein Basis %", "type": "text"},
                {"key": "hl_gewicht_basis", "label": "HL-Gewicht Basis kg/hl", "type": "text"},
                {"key": "besatz_basis", "label": "Besatz Basis %", "type": "text"},
                {"key": "besatz_max", "label": "Besatz max %", "type": "text"},
                {"key": "sonstiges_qualitaet", "label": "Sonstiges (Geruch, Mutterkorn, DON)", "type": "text"},
                {"key": "abrechnung_abweichung", "label": "Abrechnung bei Abweichung", "type": "choice", "options": ["Anlage 1 Abzugstabelle", "Anlage 2 Trocknung/Reinigung", "Individuelle Regel"]},
                {"key": "zurueckweisung_nur_bei", "label": "Zurückweisung nur bei", "type": "text"}
            ]},
            {"key": "b5", "title": "Menge / Umwidmung", "fields": [
                {"key": "mengenaenderung", "label": "Mengenänderung (t)", "type": "text"},
                {"key": "ersetzt_menge_t", "label": "ersetzt (t)", "type": "text"},
                {"key": "umwidmung_datum", "label": "Umwidmung zum Datum", "type": "date"},
                {"key": "umwidmung_partie", "label": "Partie/Lagerschein", "type": "text"},
                {"key": "eigentumsuebergang", "label": "Eigentumsübergang", "type": "choice", "options": ["am Umwidmungsdatum", "bei Auslagerung", "bei Abrechnung"]},
                {"key": "lagergeld_traegt", "label": "Lagergeld trägt", "type": "choice", "options": ["Landwirt", "Landhandel", "Käufer"]},
                {"key": "lagergeld_satz", "label": "Lagergeld Satz", "type": "text"}
            ]},
            {"key": "b6", "title": "Preis / Preisfixierung / Prämien", "fields": [
                {"key": "fixpreis_neu", "label": "Fixpreis neu €/t", "type": "text"},
                {"key": "fixpreis_fuer_t", "label": "für (t)", "type": "text"},
                {"key": "preisfixierung_bis", "label": "Preisfixierung bis (Datum/Uhrzeit)", "type": "text"},
                {"key": "fixierung_via", "label": "Fixierung via", "type": "text"},
                {"key": "praemie_abschlag", "label": "Prämie/Abschlag (Regel)", "type": "text"},
                {"key": "vergleich_buyout", "label": "Vergleich/Buy-out", "type": "text"}
            ]},
            {"key": "b7", "title": "Abrechnung / Zahlung", "fields": [
                {"key": "abrechnung_werktage", "label": "Abrechnung binnen (Werktage)", "type": "text"},
                {"key": "abrechnung_nach", "label": "nach", "type": "choice", "options": ["Verwiegung", "Analyseabschluss"]},
                {"key": "zahlung_tage", "label": "Zahlung (Tage netto)", "type": "text"},
                {"key": "zahlung_ab", "label": "ab", "type": "choice", "options": ["Abrechnung", "Rechnung", "Liefertag"]},
                {"key": "skonto", "label": "Skonto", "type": "text"},
                {"key": "gutschrift_selbstfakturierung", "label": "Gutschrift/Selbstfakturierung", "type": "choice", "options": ["ja", "nein"]}
            ]},
            {"key": "b8", "title": "Dokumente", "fields": [
                {"key": "dokumente", "label": "Mit Lieferung zu übergeben", "type": "multichoice", "options": ["Lieferschein", "Wiegeschein", "Analyse/CoA", "Chargen-/Lagerschein"]},
                {"key": "dokumente_sonstiges", "label": "Sonstiges", "type": "text"}
            ]},
            {"key": "c", "title": "Schluss", "fields": [
                {"key": "ort_datum", "label": "Ort/Datum", "type": "text"},
                {"key": "eintritt_ab", "label": "Nachtrag tritt in Kraft (Datum/Uhrzeit oder mit Unterzeichnung)", "type": "text"},
                {"key": "verkaeufer_name_funktion", "label": "Verkäufer Name/Funktion", "type": "text"},
                {"key": "kaeufer_name_funktion", "label": "Käufer Name/Funktion", "type": "text"}
            ]}
        ],
        "version": "1.0",
        "ehb_eb_ref": "https://www.dlg.org/mediacenter/dlg-merkblaetter/dlg-merkblatt-421-einheitsbedingungen-im-deutschen-getreidehandel"
    }
    import json
    conn.execute(
        sa.text("""
            INSERT INTO domain_shared.amendment_templates (id, code, name, description, body_markdown, sections_schema, is_active)
            VALUES (:id, :code, :name, :description, :body_markdown, CAST(:sections_schema AS jsonb), true)
        """),
        {
            "id": "tpl-ehbeb-nachtrag-001",
            "code": "EHBEB_NACHTRAG",
            "name": "Nachtrag EHB/EB (Lager ↔ Lagerhaus / Strecke ↔ Landwirt)",
            "description": "Nachtrag zum Kontrakt nur mit Einheitsbedingungen (EHB/EB), inländisch Lager ↔ Lagerhaus / Strecke ↔ Landwirt.",
            "body_markdown": body_md,
            "sections_schema": json.dumps(sections_schema),
        },
    )


def downgrade() -> None:
    op.drop_index('ix_amendment_templates_code', table_name='amendment_templates', schema='domain_shared')
    op.drop_table('amendment_templates', schema='domain_shared')
