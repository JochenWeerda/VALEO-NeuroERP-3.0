"""Aufbewahrungsrichtlinien auf geltendes Recht (BEG IV, Fristbeginn Kalenderjahresende) - 25.11.2026.

Revision ID: aufbewahrung_geltendes_recht_20261125
Revises: folgeartikel_fremdschluessel_20261124

Nutzerauftrag 25.11.2026: "Aufbewahrungspflichten und Fristen nach geltendem Recht umsetzen". Die Standardzeilen
(``tenant_id = 'default'``) aus ``add_gobd_compliance_20260220`` fuehrten Buchungsbelege und Rechnungen mit 10 Jahren
und Fristbeginn ab Erstellungs-/Vertragsdatum. Geltend (Katalog ``app/core/gobd_retention.py``):

- Buchungsbelege, Rechnungen, Lohnabrechnungen 8 Jahre (§ 147 Abs. 1 Nr. 4, Abs. 3 AO, § 14b UStG, BEG IV).
- Jahresabschluss, Inventar 10 Jahre; Handelsbriefe und Vertraege 6 Jahre.
- Fristbeginn immer Schluss des Kalenderjahres (§ 147 Abs. 4 AO, § 257 Abs. 5 HGB).
- Neu: Lieferscheine ohne Belegfunktion bis Erhalt/Versand der Rechnung (§ 147 Abs. 3 Satz 3/4 AO).

Mandanteneigene Zeilen bleiben unberuehrt.
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "aufbewahrung_geltendes_recht_20261125"
down_revision = "folgeartikel_fremdschluessel_20261124"
branch_labels = None
depends_on = None

AO_BELEG = "§ 147 Abs. 1 Nr. 4, Abs. 3 AO; § 257 Abs. 1 Nr. 4, Abs. 4 HGB (BEG IV)"
USTG = "§ 14b Abs. 1 UStG; § 147 Abs. 1 Nr. 4, Abs. 3 AO (BEG IV)"
AO_BUECHER = "§ 147 Abs. 1 Nr. 1, Abs. 3 AO; § 257 Abs. 1 Nr. 1, Abs. 4 HGB"
AO_BRIEF = "§ 147 Abs. 1 Nr. 2, 3, Abs. 3 AO; § 257 Abs. 1 Nr. 2, 3, Abs. 4 HGB"

#: (id, dokument_typ, jahre, trigger, grundlage) - geltend
NEU = [
    ("policy_buchungsbeleg", "BUCHUNGSBELEG", 8, "CALENDAR_YEAR_END", AO_BELEG),
    ("policy_eingangsrechnung", "EINGANGSRECHNUNG", 8, "CALENDAR_YEAR_END", USTG),
    ("policy_ausgangsrechnung", "AUSGANGSRECHNUNG", 8, "CALENDAR_YEAR_END", USTG),
    ("policy_lohnbuchung", "LOHNABRECHNUNG", 8, "CALENDAR_YEAR_END", AO_BELEG),
    ("policy_jahresabschluss", "JAHRESABSCHLUSS", 10, "CALENDAR_YEAR_END", AO_BUECHER),
    ("policy_inventar", "INVENTAR", 10, "CALENDAR_YEAR_END", AO_BUECHER),
    ("policy_handelsbrief", "HANDELSBRIEF", 6, "CALENDAR_YEAR_END", AO_BRIEF),
    ("policy_vertrag", "VERTRAG", 6, "CONTRACT_END", AO_BRIEF),
]
LIEFERSCHEIN = ("policy_lieferschein", "LIEFERSCHEIN", 0, "INVOICE_DATE", "§ 147 Abs. 3 Satz 3 und 4 AO",
                "Lieferscheine ohne Belegfunktion: bis Erhalt bzw. Versand der Rechnung")

#: Stand aus add_gobd_compliance_20260220 - fuer den Rueckweg
ALT = [
    ("policy_buchungsbeleg", 10, "FISCAL_YEAR_END", "§147 AO, §257 HGB"),
    ("policy_eingangsrechnung", 10, "CALENDAR_YEAR_END", "§14b UStG"),
    ("policy_ausgangsrechnung", 10, "CALENDAR_YEAR_END", "§14b UStG"),
    ("policy_lohnbuchung", 10, "CREATION_DATE", "§147 AO"),
    ("policy_jahresabschluss", 10, "CREATION_DATE", "§147 AO"),
    ("policy_inventar", 10, "FISCAL_YEAR_END", "§147 AO"),
    ("policy_handelsbrief", 6, "CREATION_DATE", "§257 HGB"),
    ("policy_vertrag", 10, "CONTRACT_END", "§195 BGB"),
]


def upgrade() -> None:
    bind = op.get_bind()
    for pid, _typ, jahre, trigger, grundlage in NEU:
        bind.execute(text(
            "UPDATE public.gobd_aufbewahrungsrichtlinien SET aufbewahrungs_jahre = :j, frist_trigger = :tr, "
            "gesetzliche_grundlage = :g, updated_at = now() WHERE id = :id AND tenant_id = 'default'"),
            {"id": pid, "j": jahre, "tr": trigger, "g": grundlage})
    pid, typ, jahre, trigger, grundlage, beschreibung = LIEFERSCHEIN
    bind.execute(text(
        "INSERT INTO public.gobd_aufbewahrungsrichtlinien (id, tenant_id, dokument_typ, beschreibung, "
        "aufbewahrungs_jahre, frist_trigger, gesetzliche_grundlage, aktiv) "
        "VALUES (:id, 'default', :typ, :b, :j, :tr, :g, true) ON CONFLICT (id) DO NOTHING"),
        {"id": pid, "typ": typ, "b": beschreibung, "j": jahre, "tr": trigger, "g": grundlage})


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(text("DELETE FROM public.gobd_aufbewahrungsrichtlinien WHERE id = 'policy_lieferschein' "
                      "AND tenant_id = 'default'"))
    for pid, jahre, trigger, grundlage in ALT:
        bind.execute(text(
            "UPDATE public.gobd_aufbewahrungsrichtlinien SET aufbewahrungs_jahre = :j, frist_trigger = :tr, "
            "gesetzliche_grundlage = :g WHERE id = :id AND tenant_id = 'default'"),
            {"id": pid, "j": jahre, "tr": trigger, "g": grundlage})
