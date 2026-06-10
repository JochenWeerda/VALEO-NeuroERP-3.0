from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


ZERO = Decimal("0.00")


@dataclass(frozen=True)
class PosAccountDefinition:
    name: str
    account_type: str
    category: str


ACCOUNT_DEFINITIONS: dict[str, PosAccountDefinition] = {
    "1000": PosAccountDefinition("Kasse", "asset", "current_assets"),
    "1200": PosAccountDefinition("Bank / EC", "asset", "current_assets"),
    "1210": PosAccountDefinition("PayPal / Verrechnung", "asset", "current_assets"),
    "1400": PosAccountDefinition("Forderungen aus Lieferungen und Leistungen", "asset", "current_assets"),
    "1600": PosAccountDefinition("Gutscheinverbindlichkeiten", "liability", "current_liabilities"),
    "1800": PosAccountDefinition("Privatentnahmen / Barauszahlungen", "equity", "equity"),
    "2150": PosAccountDefinition("Kassendifferenzen", "expense", "operating_expenses"),
    "8400": PosAccountDefinition("Umsatzerloese POS", "revenue", "revenue"),
}


@dataclass(frozen=True)
class PosClosingAmounts:
    cash_sales: Decimal = ZERO
    card_sales: Decimal = ZERO
    paypal_sales: Decimal = ZERO
    b2b_sales: Decimal = ZERO
    voucher_redemptions: Decimal = ZERO
    voucher_issues: Decimal = ZERO
    cash_withdrawals: Decimal = ZERO
    cash_difference: Decimal = ZERO

    @property
    def sales_total(self) -> Decimal:
        return (
            self.cash_sales
            + self.card_sales
            + self.paypal_sales
            + self.b2b_sales
            + self.voucher_redemptions
        )


@dataclass(frozen=True)
class PosAccountingLine:
    account_number: str
    debit: Decimal
    credit: Decimal
    description: str


def build_pos_closing_lines(amounts: PosClosingAmounts) -> list[PosAccountingLine]:
    lines: list[PosAccountingLine] = []

    cash_debit = amounts.cash_sales + amounts.voucher_issues
    if cash_debit > ZERO:
        lines.append(PosAccountingLine("1000", cash_debit, ZERO, "Kasseneinnahmen Bar"))
    if amounts.card_sales > ZERO:
        lines.append(PosAccountingLine("1200", amounts.card_sales, ZERO, "EC- und Kartenzahlungen"))
    if amounts.paypal_sales > ZERO:
        lines.append(PosAccountingLine("1210", amounts.paypal_sales, ZERO, "PayPal-Zahlungen"))
    if amounts.b2b_sales > ZERO:
        lines.append(PosAccountingLine("1400", amounts.b2b_sales, ZERO, "B2B-Forderungen"))
    if amounts.voucher_redemptions > ZERO:
        lines.append(
            PosAccountingLine("1600", amounts.voucher_redemptions, ZERO, "Eingeloeste Gutscheine")
        )
    if amounts.sales_total > ZERO:
        lines.append(PosAccountingLine("8400", ZERO, amounts.sales_total, "Umsatzerloese POS"))
    if amounts.voucher_issues > ZERO:
        lines.append(
            PosAccountingLine("1600", ZERO, amounts.voucher_issues, "Ausgegebene Gutscheine")
        )
    if amounts.cash_withdrawals > ZERO:
        lines.extend(
            [
                PosAccountingLine(
                    "1800", amounts.cash_withdrawals, ZERO, "Barentnahme / Barauszahlung"
                ),
                PosAccountingLine("1000", ZERO, amounts.cash_withdrawals, "Barentnahme aus Kasse"),
            ]
        )
    if amounts.cash_difference > ZERO:
        lines.extend(
            [
                PosAccountingLine("2150", amounts.cash_difference, ZERO, "Kassenfehlbetrag"),
                PosAccountingLine("1000", ZERO, amounts.cash_difference, "Kassenfehlbetrag Abgang"),
            ]
        )
    elif amounts.cash_difference < ZERO:
        difference = abs(amounts.cash_difference)
        lines.extend(
            [
                PosAccountingLine("1000", difference, ZERO, "Kassenueberbestand"),
                PosAccountingLine("2150", ZERO, difference, "Kassenueberbestand"),
            ]
        )

    debit = sum((line.debit for line in lines), ZERO)
    credit = sum((line.credit for line in lines), ZERO)
    if debit != credit:
        raise ValueError(f"POS-Buchung ist nicht ausgeglichen: Soll={debit}, Haben={credit}")
    return lines
