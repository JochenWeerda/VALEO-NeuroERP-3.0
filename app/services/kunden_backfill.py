"""Phase 2D Schritt 3: Backfill public.kunden -> Domänensatelliten.

Kopiert die fachlichen Nebendomänen aus dem (vorerst unangetasteten) Stamm
``public.kunden`` in die in ``kunden_domain_tables_20260602`` angelegten
Satellitentabellen:

  - kunden_adressen        Haupt-/Postfachadresse
  - kunden_zahlung         Zahl-/Mahn-/Abrechnungs-Flags (1:1)
  - kunden_external_refs   legacy_kunden_nr / webshop_kunden_nr / tankkarte / kundenkarte
  - kunden_aggregates      1:1-Platzhalterzeile (Kennzahlen-Refresh aus Verkauf/FiBu separat)

Eigenschaften:
  - **idempotent**: Adressen via NOT EXISTS, Zahlung via UPSERT (ON CONFLICT),
    Refs via ON CONFLICT DO NOTHING, Aggregates via ON CONFLICT DO NOTHING.
    Mehrfachläufe sind sicher.
  - **verlustfrei/reversibel**: schreibt nur in die (anfangs leeren) Satelliten,
    ``public.kunden`` wird NICHT verändert. Rückgängig per TRUNCATE der Satelliten.
  - **Dry-Run-fähig**: ohne --apply werden nur die Kandidatenzahlen gezählt.

Nur nicht gelöschte Kunden (``geloescht = FALSE``) — deckungsgleich mit
``public.kunden_lookup``.

CLI:
    python -m app.services.kunden_backfill            # Dry-Run (zählt nur)
    python -m app.services.kunden_backfill --apply    # schreibt
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import text
from sqlalchemy.orm import Session

# Zahlungs-/Abrechnungsspalten: in Quelle und Ziel gleichnamig → 1:1-Kopie.
_ZAHLUNG_COLS = [
    "zahlungsbedingungen_tage", "skonto", "netto_kasse", "mahnwesen",
    "lastschriftverfahren", "sepa_verfahren", "mandat", "kontonutzung_rechnung",
    "kontoauszug_gewuenscht", "saldo_druck_rechnung", "druck_verbot_rechnung",
    "einzel_abrechnung", "sammel_abrechnung", "sammel_abrechnungskennzeichen",
    "bonus_berechtigung", "bonus_rechnungsempfaenger_id",
    "selbstabrechnung_durch_kunden", "offene_posten_nicht_aufrufen",
    "rabatt_verrechnung", "selbstabholer_rabatt",
]

# External-Ref-Typ -> Quellspalte in public.kunden
_EXTERNAL_REFS = {
    "legacy_kunden_nr": "legacy_kunden_nr",
    "webshop_kunden_nr": "webshop_kunden_nr",
    "tankkarte_ean": "tankkarte_ean_code",
    "kundenkarte": "kundenkarten_kennzeichen",
}


@dataclass
class BackfillResult:
    apply: bool
    counts: dict[str, int] = field(default_factory=dict)

    def render(self) -> str:
        mode = "APPLY" if self.apply else "DRY-RUN"
        lines = [f"# Kunden-Backfill ({mode})", ""]
        for k, v in self.counts.items():
            verb = "geschrieben" if self.apply else "Kandidaten"
            lines.append(f"- {k:28} {v:>6}  {verb}")
        return "\n".join(lines)


def _scalar(db: Session, sql: str, **params) -> int:
    return int(db.execute(text(sql), params).scalar() or 0)


def run_backfill(db: Session, apply: bool = False) -> BackfillResult:
    res = BackfillResult(apply=apply)

    # --- 1) Adressen: Haupt ---
    haupt_pred = (
        "FROM public.kunden k WHERE coalesce(k.geloescht, FALSE) = FALSE "
        "AND (k.strasse IS NOT NULL OR k.plz IS NOT NULL OR k.ort IS NOT NULL) "
        "AND NOT EXISTS (SELECT 1 FROM public.kunden_adressen a "
        "                WHERE a.kunden_nr = k.kunden_nr AND a.adress_typ = 'haupt')"
    )
    res.counts["adressen_haupt"] = _scalar(db, f"SELECT count(*) {haupt_pred}")
    if apply:
        db.execute(text(
            "INSERT INTO public.kunden_adressen "
            "(kunden_nr, adress_typ, strasse, plz, ort, land, ist_standard) "
            "SELECT k.kunden_nr, 'haupt', k.strasse, k.plz, k.ort, k.land, TRUE "
            + haupt_pred
        ))

    # --- 1b) Adressen: Postfach ---
    pf_pred = (
        "FROM public.kunden k WHERE coalesce(k.geloescht, FALSE) = FALSE "
        "AND (k.postfach IS NOT NULL OR k.postfach_plz IS NOT NULL OR k.postfach_ort IS NOT NULL) "
        "AND NOT EXISTS (SELECT 1 FROM public.kunden_adressen a "
        "                WHERE a.kunden_nr = k.kunden_nr AND a.adress_typ = 'postfach')"
    )
    res.counts["adressen_postfach"] = _scalar(db, f"SELECT count(*) {pf_pred}")
    if apply:
        db.execute(text(
            "INSERT INTO public.kunden_adressen "
            "(kunden_nr, adress_typ, postfach, postfach_plz, postfach_ort, ist_standard) "
            "SELECT k.kunden_nr, 'postfach', k.postfach, k.postfach_plz, k.postfach_ort, FALSE "
            + pf_pred
        ))

    # --- 2) Zahlung (1:1 Upsert) ---
    res.counts["zahlung"] = _scalar(
        db, "SELECT count(*) FROM public.kunden WHERE coalesce(geloescht, FALSE) = FALSE")
    if apply:
        cols = ", ".join(_ZAHLUNG_COLS)
        src = ", ".join(f"k.{c}" for c in _ZAHLUNG_COLS)
        upd = ", ".join(f"{c} = EXCLUDED.{c}" for c in _ZAHLUNG_COLS)
        db.execute(text(
            f"INSERT INTO public.kunden_zahlung (kunden_nr, {cols}) "
            f"SELECT k.kunden_nr, {src} FROM public.kunden k "
            "WHERE coalesce(k.geloescht, FALSE) = FALSE "
            f"ON CONFLICT (kunden_nr) DO UPDATE SET {upd}, updated_at = now()"
        ))

    # --- 3) External Refs (n Typen) ---
    refs_total = 0
    for ref_typ, src_col in _EXTERNAL_REFS.items():
        pred = (
            f"FROM public.kunden k WHERE coalesce(k.geloescht, FALSE) = FALSE "
            f"AND k.{src_col} IS NOT NULL AND btrim(k.{src_col}) <> '' "
            f"AND NOT EXISTS (SELECT 1 FROM public.kunden_external_refs r "
            f"  WHERE r.kunden_nr = k.kunden_nr AND r.ref_typ = :rt AND r.ref_wert = k.{src_col})"
        )
        n = _scalar(db, f"SELECT count(*) {pred}", rt=ref_typ)
        refs_total += n
        if apply and n:
            db.execute(text(
                "INSERT INTO public.kunden_external_refs (kunden_nr, ref_typ, ref_wert, quelle) "
                f"SELECT k.kunden_nr, :rt, k.{src_col}, 'public.kunden' " + pred +
                " ON CONFLICT (kunden_nr, ref_typ, ref_wert) DO NOTHING"
            ), {"rt": ref_typ})
    res.counts["external_refs"] = refs_total

    # --- 4) Aggregates: 1:1-Platzhalter (Kennzahlen-Refresh separat) ---
    agg_pred = (
        "FROM public.kunden k WHERE coalesce(k.geloescht, FALSE) = FALSE "
        "AND NOT EXISTS (SELECT 1 FROM public.kunden_aggregates g WHERE g.kunden_nr = k.kunden_nr)"
    )
    res.counts["aggregates_seed"] = _scalar(db, f"SELECT count(*) {agg_pred}")
    if apply:
        db.execute(text(
            "INSERT INTO public.kunden_aggregates (kunden_nr) "
            "SELECT k.kunden_nr " + agg_pred +
            " ON CONFLICT (kunden_nr) DO NOTHING"
        ))

    if apply:
        db.commit()
    return res


def main() -> None:
    import sys
    from app.core.database import SessionLocal

    apply = "--apply" in sys.argv
    db = SessionLocal()
    try:
        print(run_backfill(db, apply=apply).render())
    finally:
        db.close()


if __name__ == "__main__":
    main()
