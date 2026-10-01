"""Das zentrale Kontraktregister bekommt eine Migration.

``domain_contracts.contracts``, ``.contract_versions`` und
``.contract_obligations`` legt keine Migration an. Auf einer frischen
Installation meldet deshalb **jeder** Weg der Kontrakte-Engine
(``central_contracts.py``) 503: anlegen, auflisten, verlaengern, Pflichten
fuehren, Auswertung.

Die Form ist woertlich aus dem Modul uebernommen — aus den ``INSERT``-Spalten,
den Pydantic-Modellen (``ContractOut``, ``ObligationOut``) und den
Wertemengen, die es selbst prueft. Erfunden ist daran nichts.

Drei Dinge sind ergaenzt, und jedes fuer einen benannten Grund:

* **Fremdschluessel** von Version und Pflicht auf den Kontrakt, mit
  ``ON DELETE CASCADE``: Eine Vertragsversion ohne Vertrag ist kein Dokument.
* **Pruefbedingungen** auf die vier Wertemengen, die das Modul ohnehin prueft
  (``ContractTypeValues``, ``ContractStatusValues``, ``CounterpartyTypeValues``,
  ``ObligationTypeValues``/``ObligationStatusValues``). Was die Anwendung
  verlangt, soll die Datenbank halten — sonst steht beim naechsten Schreibweg
  wieder ein Wort drin, das keine Maske kennt.
* **Eine Kontraktnummer je Haus.** Sie ist die Kennung, unter der ein Haus den
  Vertrag fuehrt; zweimal dieselbe waere eine Fehlbedienung, keine Konfiguration.
  Der Versionszaehler ist je Kontrakt eindeutig — ``_next_version_number`` zieht
  ihn aus ``MAX(version_number) + 1``, und zwei gleichzeitige Aenderungen
  duerfen nicht beide die 2 bekommen.

Was diese Migration **nicht** entscheidet: welche der vorhandenen
Kontrakttabellen die fuehrende ist (``domain_einkauf.kontrakte``,
``domain_inventory.agrar_contracts``, ``domain_ops.kon_contract``,
``domain_portal.customer_contracts``, die Satelliten in ``domain_kontrakte``
ohne Kopftabelle — und dieses Register). Das ist eine Fachfrage des
Domaenen-Owners; siehe ``docs/quality-assurance/kontraktregister-20261001.md``.

Revision ID: kontraktregister_20261001
Revises: webhook_zustellprotokoll_20261001
"""

from __future__ import annotations

from alembic import op

revision = "kontraktregister_20261001"
down_revision = "webhook_zustellprotokoll_20261001"
branch_labels = None
depends_on = None

#: Die Wertemengen stehen als Mengen in ``central_contracts.py``. Hier als
#: Tupel, damit die Pruefbedingung eine feste Reihenfolge hat.
VERTRAGSARTEN = ("EINKAUF", "VERKAUF", "AGRAR", "DIENSTLEISTUNG", "MIETE", "PACHT")
VERTRAGSSTAENDE = ("ENTWURF", "AKTIV", "ABGELAUFEN", "GEKUENDIGT")
PARTNERARTEN = ("CUSTOMER", "SUPPLIER")
PFLICHTARTEN = ("LIEFERUNG", "ZAHLUNG", "LEISTUNG", "MELDUNG")
PFLICHTSTAENDE = ("OFFEN", "ERLEDIGT", "UEBERFAELLIG")


def _in(spalte: str, werte: tuple[str, ...]) -> str:
    liste = ", ".join(f"'{wert}'" for wert in werte)
    return f"{spalte} IN ({liste})"


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_contracts")

    op.execute(
        f"""
        CREATE TABLE IF NOT EXISTS domain_contracts.contracts (
            id                 VARCHAR(64)  PRIMARY KEY,
            tenant_id          VARCHAR(80)  NOT NULL,
            contract_number    VARCHAR(64)  NOT NULL,
            contract_type      VARCHAR(32)  NOT NULL,
            title              TEXT         NOT NULL,
            counterparty_id    VARCHAR(80)  NOT NULL,
            counterparty_type  VARCHAR(16)  NOT NULL DEFAULT 'CUSTOMER',
            status             VARCHAR(16)  NOT NULL DEFAULT 'ENTWURF',
            start_date         TIMESTAMPTZ,
            end_date           TIMESTAMPTZ,
            auto_renewal_days  INTEGER,
            notice_period_days INTEGER,
            total_value_eur    NUMERIC(14, 2),
            created_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            CONSTRAINT ck_contracts_type        CHECK ({_in('contract_type', VERTRAGSARTEN)}),
            CONSTRAINT ck_contracts_status      CHECK ({_in('status', VERTRAGSSTAENDE)}),
            CONSTRAINT ck_contracts_partnerart  CHECK ({_in('counterparty_type', PARTNERARTEN)}),
            CONSTRAINT ck_contracts_laufzeit    CHECK (
                start_date IS NULL OR end_date IS NULL OR end_date >= start_date
            )
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_contracts.contract_versions (
            id               VARCHAR(64)  PRIMARY KEY,
            contract_id      VARCHAR(64)  NOT NULL
                REFERENCES domain_contracts.contracts (id) ON DELETE CASCADE,
            tenant_id        VARCHAR(80)  NOT NULL,
            version_number   INTEGER      NOT NULL,
            changed_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            changed_by       VARCHAR(255) NOT NULL DEFAULT 'system',
            change_summary   TEXT         NOT NULL DEFAULT '',
            content_snapshot JSONB        NOT NULL DEFAULT '{}'::jsonb,
            CONSTRAINT ck_contract_versions_nummer CHECK (version_number >= 1)
        )
        """
    )

    op.execute(
        f"""
        CREATE TABLE IF NOT EXISTS domain_contracts.contract_obligations (
            id              VARCHAR(64)  PRIMARY KEY,
            contract_id     VARCHAR(64)  NOT NULL
                REFERENCES domain_contracts.contracts (id) ON DELETE CASCADE,
            tenant_id       VARCHAR(80)  NOT NULL,
            obligation_type VARCHAR(32)  NOT NULL,
            due_date        TIMESTAMPTZ  NOT NULL,
            description     TEXT         NOT NULL,
            status          VARCHAR(16)  NOT NULL DEFAULT 'OFFEN',
            created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            CONSTRAINT ck_contract_obligations_art    CHECK ({_in('obligation_type', PFLICHTARTEN)}),
            CONSTRAINT ck_contract_obligations_status CHECK ({_in('status', PFLICHTSTAENDE)})
        )
        """
    )

    # Eine Kontraktnummer je Haus.
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_contracts_tenant_nummer "
        "ON domain_contracts.contracts (tenant_id, contract_number)"
    )
    # Ein Versionszaehler je Kontrakt. `_next_version_number` zieht ihn aus
    # MAX(version_number) + 1; zwei gleichzeitige Aenderungen duerfen nicht
    # beide die 2 bekommen.
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_contract_versions_kontrakt_nummer "
        "ON domain_contracts.contract_versions (contract_id, version_number)"
    )

    # Gelesen wird "meine Kontrakte, neueste zuerst" und "was laeuft bald aus?".
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_contracts_tenant_angelegt "
        "ON domain_contracts.contracts (tenant_id, created_at DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_contracts_tenant_ende "
        "ON domain_contracts.contracts (tenant_id, status, end_date)"
    )
    # Und "die Pflichten dieses Kontrakts nach Faelligkeit" sowie "was ist in
    # meinem Haus ueberfaellig?".
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_contract_obligations_kontrakt_faellig "
        "ON domain_contracts.contract_obligations (contract_id, due_date)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_contract_obligations_tenant_status "
        "ON domain_contracts.contract_obligations (tenant_id, status, due_date)"
    )


def downgrade() -> None:
    # Kein DROP TABLE: Die Tabellen tragen Vertraege eines Hauses und deren
    # Aenderungsgeschichte. Zurueckgenommen werden nur die Indizes, die diese
    # Migration zusaetzlich angelegt hat.
    for index in (
        "ux_contracts_tenant_nummer",
        "ux_contract_versions_kontrakt_nummer",
        "ix_contracts_tenant_angelegt",
        "ix_contracts_tenant_ende",
        "ix_contract_obligations_kontrakt_faellig",
        "ix_contract_obligations_tenant_status",
    ):
        op.execute(f"DROP INDEX IF EXISTS domain_contracts.{index}")
