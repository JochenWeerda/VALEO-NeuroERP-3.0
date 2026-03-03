"""seed Anlage 1 (Abzugstabelle Qualität) amendment template

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


BODY_ANLAGE1 = R'''
## Anlage 1 – Abzugstabelle Qualität (EHB/EB)

**Verwendung:** Minderwert/Abzüge bei Abweichung von der Qualitätsbasis (Nachtrag B.4).
Es gelten die Einheitsbedingungen im Deutschen Getreidehandel (EHB/EB).

---

### Weizen (Beispielwerte, anpassbar)

| Abweichung | Abzug €/t |
|------------|-----------|
| Feuchte je 0,5 % über Basis (max. 16 %) | 1,50 |
| Protein je 0,1 % unter Basis | 0,80 |
| HL-Gewicht je 1 kg/hl unter Basis | 0,40 |
| Besatz je 0,5 % über Basis (max. 2 %) | 2,00 |

---

### Gerste (Beispielwerte, anpassbar)

| Abweichung | Abzug €/t |
|------------|-----------|
| Feuchte je 0,5 % über Basis (max. 15 %) | 1,50 |
| HL-Gewicht je 1 kg/hl unter Basis | 0,35 |
| Besatz je 0,5 % über Basis (max. 2 %) | 1,80 |

---

### Raps (Beispielwerte, anpassbar)

| Abweichung | Abzug €/t |
|------------|-----------|
| Feuchte je 0,5 % über Basis (max. 9 %) | 2,00 |
| Ölgehalt je 1 % unter Basis | 3,00 |
| Besatz je 0,5 % über Basis (max. 2 %) | 2,50 |

---

*Basis und Maximalwerte sowie Abzugssätze sind vertraglich zu vereinbaren (Nachtrag B.4).*
'''


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text("""
            INSERT INTO domain_shared.amendment_templates (id, code, name, description, body_markdown, sections_schema, is_active)
            VALUES (:id, :code, :name, :description, :body_markdown, CAST(:sections_schema AS jsonb), true)
        """),
        {
            "id": "tpl-anlage1-abzug-001",
            "code": "ANLAGE1_ABZUGSTABELLE",
            "name": "Anlage 1 – Abzugstabelle Qualität (Weizen/Gerste/Raps)",
            "description": "Typische Abzugstabelle für Qualitätsabweichungen (Feuchte, Protein, HL-Gewicht, Besatz) zur Auswahl im EHB/EB-Nachtrag.",
            "body_markdown": BODY_ANLAGE1,
            "sections_schema": "{}",
        },
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM domain_shared.amendment_templates WHERE code = 'ANLAGE1_ABZUGSTABELLE'")
    )
