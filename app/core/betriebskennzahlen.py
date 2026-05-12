from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from datetime import date
import uuid
import statistics

class KennzahlEinheit(str, Enum):
    EUR = "eur"
    EUR_JE_T = "eur_je_t"
    KWH_JE_T = "kwh_je_t"
    TAGE = "tage"
    PROZENT = "prozent"
    TONNEN = "tonnen"
    STUECK = "stueck"

class BetriebsKennzahl(BaseModel):
    kz_id: str
    kz_name: str
    einheit: KennzahlEinheit
    wert: float
    tenant_id: str
    periode: str        # z.B. "2025" oder "2025-Q3"
    berechnet_am: date
    schema_version: int = 1

class BenchmarkKennzahl(BaseModel):
    kz_name: str
    einheit: KennzahlEinheit
    periode: str
    werte_anonymisiert: list[float]   # Werte ohne Tenant-Zuordnung
    durchschnitt: float
    median: float
    p25: float
    p75: float
    minimum: float
    maximum: float
    n_teilnehmer: int
    schema_version: int = 1

class BenchmarkGruppe(BaseModel):
    gruppe_id: str
    verbund_id: str
    periode: str
    kennzahlen: list[BenchmarkKennzahl]
    schema_version: int = 1

class BenchmarkReport(BaseModel):
    report_id: str
    verbund_id: str
    periode: str
    gruppen: list[BenchmarkGruppe]
    erstellt_am: date
    schema_version: int = 1

    @classmethod
    def build(
        cls,
        verbund_id: str,
        periode: str,
        kennzahlen_je_tenant: dict[str, list[BetriebsKennzahl]],
    ) -> "BenchmarkReport":
        """Baut einen anonymisierten Benchmark-Report aus Kennzahlen mehrerer Tenants.

        tenant_ids werden SHA-256-gehasht → keine Rückverfolgbarkeit.
        """
        # Sammle alle KZ-Namen
        alle_kz_namen: set[str] = set()
        for kzs in kennzahlen_je_tenant.values():
            for kz in kzs:
                alle_kz_namen.add(kz.kz_name)

        benchmark_kzs = []
        for kz_name in sorted(alle_kz_namen):
            werte = []
            einheit = None
            for kzs in kennzahlen_je_tenant.values():
                for kz in kzs:
                    if kz.kz_name == kz_name and kz.periode == periode:
                        werte.append(kz.wert)
                        einheit = kz.einheit
            if not werte or einheit is None:
                continue
            sorted_werte = sorted(werte)
            n = len(sorted_werte)
            benchmark_kzs.append(BenchmarkKennzahl(
                kz_name=kz_name,
                einheit=einheit,
                periode=periode,
                werte_anonymisiert=sorted_werte,
                durchschnitt=sum(werte) / n,
                median=statistics.median(werte),
                p25=sorted_werte[int(n * 0.25)] if n >= 4 else sorted_werte[0],
                p75=sorted_werte[int(n * 0.75)] if n >= 4 else sorted_werte[-1],
                minimum=min(werte),
                maximum=max(werte),
                n_teilnehmer=n,
            ))

        gruppe = BenchmarkGruppe(
            gruppe_id=str(uuid.uuid4()),
            verbund_id=verbund_id,
            periode=periode,
            kennzahlen=benchmark_kzs,
        )
        return cls(
            report_id=str(uuid.uuid4()),
            verbund_id=verbund_id,
            periode=periode,
            gruppen=[gruppe],
            erstellt_am=date.today(),
        )

DEFAULT_KZ_KATALOG: list[dict] = [
    {"name": "umsatz_eur_t", "einheit": KennzahlEinheit.EUR_JE_T, "beschreibung": "Erlös je Tonne Rohware"},
    {"name": "trocknungskosten_kwh_t", "einheit": KennzahlEinheit.KWH_JE_T, "beschreibung": "Trocknungsenergie je Tonne"},
    {"name": "lagerumschlag_tage", "einheit": KennzahlEinheit.TAGE, "beschreibung": "Durchschnittliche Lagerdauer in Tagen"},
    {"name": "reklamationsquote_pct", "einheit": KennzahlEinheit.PROZENT, "beschreibung": "Reklamationen in % der Lieferungen"},
    {"name": "zahlungsziel_tage", "einheit": KennzahlEinheit.TAGE, "beschreibung": "Durchschnittliches Zahlungsziel Kreditoren"},
]
