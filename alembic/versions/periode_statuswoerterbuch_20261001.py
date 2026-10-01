"""Eine Buchungsperiode hat einen Zustand, nicht drei Vokabulare.

In ``public.finance_accounting_periods.status`` standen drei Schreibweisen
nebeneinander: Die Verwaltungsmaske prueft ``OPEN|CLOSED|ADJUSTING``,
``close_period`` schrieb ``closed``, ``reopen_period`` schrieb ``offen``. Sieben
Buchungswege verglichen ``status != 'OPEN'``.

Die Folge war nicht theoretisch: Eine Wiedereroeffnung verlangte einen Grund,
protokollierte ihn — und setzte ``offen``. Die Waechter lasen ``offen != OPEN``
und sperrten weiter. Und ``ADJUSTING`` sperrte wie ``CLOSED``, war also
bedeutungslos.

Diese Migration normalisiert den Bestand und laesst die Datenbank das
Woerterbuch halten. Das Woerterbuch selbst steht in
``app/core/finance_periods.py``.

**GoBD.** Unveraenderbarkeit (Rz. 107 ff.): Eine abgeschlossene Periode darf
nicht mehr bebucht werden. Nachvollziehbarkeit (Rz. 30 ff.): Der Zustand einer
Periode muss eindeutig feststellbar sein. Eine Pruefbedingung ist die einzige
Stelle, an der sich das nicht mehr auseinanderentwickeln kann.

Am 01.10.2026 war die Tabelle in der gewachsenen **und** in der frisch
migrierten Datenbank leer; die Normalisierung ist heute ein Nullvorgang, die
Pruefbedingung wirkt ab der ersten Periode.

**Nicht angefasst:** ``domain_finance.period_closure`` ist leer und wird von
keinem Modul genannt — ihre Form (``fiscal_year``, ``fiscal_period``,
``dim_cost_center``, ``dim_profit_center``, ``dim_project_tag``, ``dim_region``)
deutet aber auf eine Controlling-Dimension, nicht auf eine Fibu-Periodensperre.
Eine Tabelle stillzulegen, deren Zweck man nur erraten kann, waere derselbe
Fehler in der anderen Richtung. Sie gehoert dem Controlling-Owner.

Revision ID: periode_statuswoerterbuch_20261001
Revises: kontrakt_ordnung_20261001
"""

from __future__ import annotations

from alembic import op

revision = "periode_statuswoerterbuch_20261001"
down_revision = "kontrakt_ordnung_20261001"
branch_labels = None
depends_on = None

#: Dasselbe Woerterbuch wie in ``app/core/finance_periods.py``. Eine Migration
#: darf nicht aus dem Anwendungscode importieren — sie muss auch dann laufen,
#: wenn der Code sich weiterbewegt hat.
ZUSTAENDE = ("OPEN", "CLOSED", "ADJUSTING")


def upgrade() -> None:
    # 1. Bestand normalisieren. Gross-/Kleinschreibung und die deutschen
    #    Schreibweisen zusammenfuehren.
    op.execute(
        """
        UPDATE public.finance_accounting_periods
        SET status = CASE lower(trim(status))
            WHEN 'closed'       THEN 'CLOSED'
            WHEN 'geschlossen'  THEN 'CLOSED'
            WHEN 'gesperrt'     THEN 'CLOSED'
            WHEN 'offen'        THEN 'OPEN'
            WHEN 'open'         THEN 'OPEN'
            WHEN 'adjusting'    THEN 'ADJUSTING'
            WHEN 'anpassung'    THEN 'ADJUSTING'
            ELSE upper(trim(status))
        END
        WHERE status IS NOT NULL
        """
    )

    # 2. Was danach noch nicht im Woerterbuch steht, ist ein echter Fund und
    #    darf nicht stillschweigend zu 'OPEN' werden — eine Periode, deren
    #    Zustand niemand benennen kann, ist kein Freibrief zum Buchen.
    op.execute(
        f"""
        DO $$
        DECLARE unbekannt text;
        BEGIN
            SELECT string_agg(DISTINCT status, ', ') INTO unbekannt
            FROM public.finance_accounting_periods
            WHERE status NOT IN ({", ".join(f"'{z}'" for z in ZUSTAENDE)});
            IF unbekannt IS NOT NULL THEN
                RAISE EXCEPTION
                    'Unbekannte Periodenzustaende: %. Erst zuordnen, dann '
                    'migrieren (app/core/finance_periods.py).', unbekannt;
            END IF;
        END $$;
        """
    )

    # 3. Die Datenbank haelt das Woerterbuch.
    op.execute(
        f"""
        ALTER TABLE public.finance_accounting_periods
            ADD CONSTRAINT ck_finance_accounting_periods_status
            CHECK (status IN ({", ".join(f"'{z}'" for z in ZUSTAENDE)}))
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE public.finance_accounting_periods "
        "DROP CONSTRAINT IF EXISTS ck_finance_accounting_periods_status"
    )
    # Die Normalisierung wird nicht zurueckgedreht: Zwei Schreibweisen fuer
    # denselben Zustand wiederherzustellen waere kein Rueckbau, sondern ein
    # neuer Fehler.
