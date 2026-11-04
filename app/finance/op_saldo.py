"""OP-Saldo eines Debitors oder Kreditors aus ``domain_erp.offene_posten``.

Fuehrend fuer den offenen Betrag ist ``offen``: jeder Zahlungs-, Auszifferungs- und Stornoweg
schreibt diese Spalte (``open_amount`` fuehren nur einzelne Anlagewege mit, live weicht sie ab).
Offen ist ein Posten mit ``op_status`` ``offen`` oder ``teilweise`` und Restbetrag > 0.

``{verweis}`` ist ein Code-Literal des Aufrufers (Debitor- oder Kreditorverweis), Werte sind gebunden.
"""

OP_SALDO_SQL = """
    SELECT
        COALESCE(SUM(offen), 0) AS open_balance,
        COUNT(*) AS open_item_count,
        MIN(COALESCE(due_date, faelligkeit)) AS oldest_due_date
    FROM domain_erp.offene_posten
    WHERE tenant_id = :tenant_id
      AND konto_typ = :konto_typ
      AND op_status IN ('offen', 'teilweise')
      AND offen > 0
      AND {verweis}
"""
