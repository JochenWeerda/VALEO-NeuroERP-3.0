"""Fuenf Spalten, die der Code schreibt und keine Migration anlegt.

Angebot und Auftrag lesen und schreiben Felder, die es nur in gewachsenen
Entwicklungsdatenbanken gibt — dort sind sie irgendwann von Hand entstanden.
In einer frischen Datenbank fehlen sie, und dann bricht schon das Anlegen
eines Angebots:

    column "customer_name" of relation "sales_offers" does not exist

Betroffen:

| Tabelle                 | Spalte         | benutzt von                        |
|-------------------------|----------------|------------------------------------|
| ``sales_offers``        | customer_name  | ``POST /sales/offers/``            |
| ``sales_offers``        | is_pauschale   | Angebotskopf                       |
| ``sales_orders``        | is_pauschale   | Auftragskopf                       |
| ``sales_order_items``   | ek_price       | Deckungsbeitrag je Position        |
| ``sales_order_items``   | unit           | Mengeneinheit je Position          |

Typen und Vorgabewerte sind aus der gewachsenen Datenbank uebernommen, damit
beide Staende danach dasselbe bedeuten. Alle Spalten sind nullable: Es gibt
Bestandszeilen ohne diese Werte, und ein Pflichtfeld wuerde die Migration auf
jeder gewachsenen Datenbank scheitern lassen.

``IF NOT EXISTS`` sorgt dafuer, dass die Migration auf beiden Staenden laeuft.

Revision ID: verkauf_fehlende_spalten_20260929
Revises: lieferschein_status_bedingung_20260929
"""

from __future__ import annotations

from alembic import op

revision = "verkauf_fehlende_spalten_20260929"
down_revision = "lieferschein_status_bedingung_20260929"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE domain_crm.sales_offers
            ADD COLUMN IF NOT EXISTS customer_name VARCHAR(255),
            ADD COLUMN IF NOT EXISTS is_pauschale BOOLEAN DEFAULT FALSE;
        """
    )
    # Ein Angebot ohne Gueltigkeitsdatum ist ein normales Angebot. Der
    # Endpunkt laesst das Feld leer, wenn niemand eines angibt; die Tabelle
    # verlangte es. In der gewachsenen Datenbank ist die Bedingung laengst
    # weg — hier zieht der Stand nach, statt sie nur dort zu dulden.
    #
    # Die uebrigen NOT-NULL-Bedingungen dieser Tabellen bleiben stehen,
    # obwohl die gewachsene Datenbank sie auch nicht mehr hat: currency,
    # status, total_amount, version und die Zeitstempel fuellt der Endpunkt
    # immer. Nur was der Code wirklich leer laesst, wird geloest.
    op.execute(
        """
        ALTER TABLE domain_crm.sales_offers
            ALTER COLUMN valid_until DROP NOT NULL;
        """
    )
    op.execute(
        """
        ALTER TABLE domain_crm.sales_orders
            ADD COLUMN IF NOT EXISTS is_pauschale BOOLEAN DEFAULT FALSE;
        """
    )
    op.execute(
        """
        ALTER TABLE domain_crm.sales_order_items
            ADD COLUMN IF NOT EXISTS ek_price NUMERIC(14, 4),
            ADD COLUMN IF NOT EXISTS unit VARCHAR(20) DEFAULT 'kg';
        """
    )

    # Den Attestierenden "system" gibt es wirklich.
    #
    # domain_audit.attestations.created_by zeigt per Fremdschluessel auf
    # domain_shared.users (ON DELETE RESTRICT). Der Druckpfad des
    # Lieferscheins faellt auf "system" zurueck, wenn aus der Anfrage kein
    # Benutzer hervorgeht — und lief damit in einen 500er: Der Nachdruck
    # eines gebuchten Lieferscheins war nicht moeglich.
    #
    # Die Zeile ist bewusst als das benannt, was sie ist. Eine Attestierung
    # soll sagen, wer sie abgegeben hat; steht hier "system", heisst das:
    # ohne erkennbaren Benutzer erfasst. Das ist eine Auskunft, kein Name.
    # Die Pflichtfelder von domain_shared.users sind in einer frischen und
    # einer gewachsenen Datenbank **verschieden**: frisch verlangt
    # keycloak_id, gewachsen first_name, last_name und tenant_id. Gesetzt
    # wird deshalb die Vereinigung beider Mengen. Den Mandanten `system`
    # legt schon erp_kontenrahmen_skr03_20260927 an; hier steht er zur
    # Sicherheit noch einmal, damit die Reihenfolge keine Rolle spielt.
    op.execute(
        """
        INSERT INTO domain_shared.tenants (id, name, domain, is_active)
        VALUES ('system', 'System', 'system.local', TRUE)
        ON CONFLICT (id) DO NOTHING;
        """
    )
    # Benutzername und E-Mail sind bewusst nicht schlicht "system": In
    # gewachsenen Datenbanken gibt es bereits ein System-Konto unter einer
    # UUID (`00000000-…-0001`, Benutzername `system`). Dieses Konto bleibt
    # unangetastet. Gebraucht wird hier eine Zeile mit der **Kennung**
    # `system`, weil der Druckpfad genau diesen Wert in `created_by`
    # schreibt — und der Name sagt, was ein solcher Eintrag bedeutet.
    op.execute(
        """
        INSERT INTO domain_shared.users
            (id, keycloak_id, username, email, first_name, last_name, tenant_id)
        VALUES ('system', 'system-ohne-benutzerkennung',
                'system-ohne-benutzerkennung',
                'system-ohne-benutzerkennung@valeo-neuroerp.invalid',
                'System', 'ohne Benutzerkennung', 'system')
        ON CONFLICT DO NOTHING;
        """
    )


def downgrade() -> None:
    # Bewusst kein DROP: Die Spalten tragen inzwischen Daten, und der Code
    # schreibt sie. Ein Rueckbau wuerde die Endpunkte zerlegen, nicht
    # zuruecksetzen.
    pass
