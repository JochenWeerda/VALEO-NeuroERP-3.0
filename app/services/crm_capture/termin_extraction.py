"""Deterministische Termin-Extraktion aus E-Mails (UIX-073, Stufe 1).

Erkennt deutsche Datums-/Zeitmuster ("12.07.", "Montag 14 Uhr", "KW 29",
"morgen frueh", "zwischen 8 und 10") und Bezugsobjekte (Bestell-/Kontrakt-/
Lieferschein-Nummern, Absender-Domain) — ohne LLM, ohne DB, zeitzonen-fix
Europe/Berlin. Reine Funktionen: Text → Kandidaten. Die Kandidaten werden vom
Pipeline-Schritt zu calendar_items(status='proposed') — NIE Auto-Confirm.

Der optionale LLM-Fallback (Feature-Flag) validiert seine Ausgabe gegen diese
Stufe-1-Kandidaten (kein frei erfundenes Datum) und ist hier bewusst NICHT Teil
des deterministischen Kerns.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

BERLIN = ZoneInfo("Europe/Berlin")

_MONTHS = {
    "januar": 1, "februar": 2, "maerz": 3, "märz": 3, "april": 4, "mai": 5,
    "juni": 6, "juli": 7, "august": 8, "september": 9, "oktober": 10,
    "november": 11, "dezember": 12,
}
# Wochentage (0=Montag) inkl. Kurzformen.
_WEEKDAYS = {
    "montag": 0, "mo": 0, "dienstag": 1, "di": 1, "mittwoch": 2, "mi": 2,
    "donnerstag": 3, "do": 3, "freitag": 4, "fr": 4, "samstag": 5, "sa": 5,
    "sonntag": 6, "so": 6,
}
# Tageszeit-Defaults (Stunde) fuer unscharfe Angaben.
_DAYPART = {"frueh": 8, "früh": 8, "vormittag": 9, "mittag": 12, "nachmittag": 14, "abend": 18}


@dataclass
class ObjectRef:
    type: str  # purchase_order | contract | delivery_note | supplier
    id: str
    confidence: float


@dataclass
class TerminCandidate:
    extracted_text: str
    start: str            # ISO (mit Zeit) oder ISO-Datum bei all_day
    end: str | None
    all_day: bool
    matched_object: ObjectRef | None
    confidence: float

    def to_dict(self) -> dict:
        d = asdict(self)
        if self.matched_object is None:
            d["matched_object"] = None
        return d


# ── Datum ────────────────────────────────────────────────────────────────────

_RE_DMY = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.?(\d{4}|\d{2})?(?!\d)")
_RE_D_MONTH = re.compile(r"\b(\d{1,2})\.?\s+(" + "|".join(_MONTHS) + r")\b", re.IGNORECASE)
_RE_KW = re.compile(r"\bKW\s?(\d{1,2})\b", re.IGNORECASE)


def _resolve_year(day: int, month: int, anchor: date, explicit: int | None) -> int:
    if explicit is not None:
        return explicit + 2000 if explicit < 100 else explicit
    # Ohne Jahr: naechstes Auftreten ab Anker (Vergangenheit → Folgejahr).
    candidate = date(anchor.year, month, day)
    return anchor.year if candidate >= anchor else anchor.year + 1


def _parse_date(segment: str, anchor: date) -> tuple[date, str] | None:
    low = segment.lower()

    if "uebermorgen" in low or "übermorgen" in low:
        return anchor + timedelta(days=2), "uebermorgen"
    if "morgen" in low:
        return anchor + timedelta(days=1), "morgen"
    if re.search(r"\bheute\b", low):
        return anchor, "heute"

    m = _RE_DMY.search(segment)
    if m:
        day, month = int(m.group(1)), int(m.group(2))
        if 1 <= day <= 31 and 1 <= month <= 12:
            year = _resolve_year(day, month, anchor, int(m.group(3)) if m.group(3) else None)
            try:
                return date(year, month, day), m.group(0)
            except ValueError:
                return None

    m = _RE_D_MONTH.search(segment)
    if m:
        day = int(m.group(1))
        month = _MONTHS[m.group(2).lower()]
        year = _resolve_year(day, month, anchor, None)
        try:
            return date(year, month, day), m.group(0)
        except ValueError:
            return None

    m = _RE_KW.search(segment)
    if m:
        week = int(m.group(1))
        if 1 <= week <= 53:
            # Montag der ISO-Kalenderwoche.
            monday = date.fromisocalendar(anchor.year if week >= anchor.isocalendar().week else anchor.year + 1, week, 1)
            return monday, m.group(0)

    for name, dow in _WEEKDAYS.items():
        if re.search(rf"\b{name}\b", low):
            delta = (dow - anchor.weekday()) % 7
            delta = delta or 7  # "Montag" heute → naechster Montag
            return anchor + timedelta(days=delta), name

    return None


# ── Zeit ─────────────────────────────────────────────────────────────────────

_RE_RANGE = re.compile(r"\bzwischen\s+(\d{1,2})\s+und\s+(\d{1,2})\b", re.IGNORECASE)
_RE_RANGE2 = re.compile(r"\b(\d{1,2})\s?-\s?(\d{1,2})\s*Uhr\b", re.IGNORECASE)
_RE_HHMM = re.compile(r"\b(\d{1,2}):(\d{2})\b")
_RE_HHUHR = re.compile(r"\b(?:um\s+)?(\d{1,2})(?:\s?Uhr)\b", re.IGNORECASE)


def _parse_time(segment: str) -> tuple[time, time | None, str] | None:
    m = _RE_RANGE.search(segment) or _RE_RANGE2.search(segment)
    if m:
        h1, h2 = int(m.group(1)), int(m.group(2))
        if 0 <= h1 <= 23 and 0 <= h2 <= 23:
            return time(h1), time(h2), m.group(0)

    m = _RE_HHMM.search(segment)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mi <= 59:
            return time(h, mi), None, m.group(0)

    m = _RE_HHUHR.search(segment)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            return time(h), None, m.group(0)

    low = segment.lower()
    for word, hour in _DAYPART.items():
        if word in low:
            return time(hour), None, word

    return None


# ── Bezugsobjekt ─────────────────────────────────────────────────────────────

_OBJECT_PATTERNS = [
    ("purchase_order", re.compile(r"\b(?:Bestellung|Bestell-?Nr\.?|PO)[\s:#-]*([0-9]{3,8})\b", re.IGNORECASE)),
    ("contract", re.compile(r"\b(?:Kontrakt|Vertrag)[\s:#-]*([A-Z]?-?[0-9]{2,8})\b", re.IGNORECASE)),
    ("delivery_note", re.compile(r"\b(?:Lieferschein|LS)[\s:#-]*([A-Z]?-?[0-9]{2,8})\b", re.IGNORECASE)),
]


def extract_object_reference(text: str, sender_domain: str | None = None) -> ObjectRef | None:
    for obj_type, pattern in _OBJECT_PATTERNS:
        m = pattern.search(text)
        if m:
            return ObjectRef(type=obj_type, id=m.group(1).lstrip("-"), confidence=0.86)
    if sender_domain:
        return ObjectRef(type="supplier", id=sender_domain.lower(), confidence=0.5)
    return None


# ── Kombination ──────────────────────────────────────────────────────────────

def _segments(text: str) -> list[str]:
    # Satz-Enden nur nach einem Buchstaben trennen — sonst zerreisst der Punkt
    # in deutschen Datumsangaben ("12.07. um 14 Uhr") Datum und Zeit.
    parts = re.split(r"[\n\r]+|(?<=[A-Za-zäöüÄÖÜß])[.!?]\s+", text)
    return [p.strip() for p in parts if p.strip()]


def extract_termine(
    text: str,
    *,
    received_at: datetime,
    sender_domain: str | None = None,
) -> list[TerminCandidate]:
    """Extrahiert Termin-Kandidaten. received_at ist der Anker fuer relative
    Angaben (morgen, Wochentag, KW). Rueckgabe kann leer sein (kein Termin)."""
    anchor = received_at.astimezone(BERLIN).date() if received_at.tzinfo else received_at.date()
    obj = extract_object_reference(text, sender_domain)
    candidates: list[TerminCandidate] = []
    seen: set[tuple[str, str | None]] = set()

    for segment in _segments(text):
        parsed_date = _parse_date(segment, anchor)
        parsed_time = _parse_time(segment)
        if parsed_date is None and parsed_time is None:
            continue
        # Nur Zeit ohne Datum ist zu unspezifisch → verwerfen.
        if parsed_date is None:
            continue

        d, date_text = parsed_date
        all_day = parsed_time is None
        if all_day:
            start_iso = d.isoformat()
            end_iso = None
            confidence = 0.55
        else:
            t_start, t_end, time_text = parsed_time
            start_dt = datetime.combine(d, t_start, tzinfo=BERLIN)
            start_iso = start_dt.isoformat()
            end_iso = datetime.combine(d, t_end, tzinfo=BERLIN).isoformat() if t_end else None
            confidence = 0.9
            date_text = f"{date_text} {time_text}"

        # Relative/unscharfe Anker senken die Konfidenz leicht.
        if date_text.split()[0] in {"morgen", "uebermorgen", "heute"} or date_text.split()[0] in _WEEKDAYS:
            confidence -= 0.1

        key = (start_iso, end_iso)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            TerminCandidate(
                extracted_text=segment[:200],
                start=start_iso,
                end=end_iso,
                all_day=all_day,
                matched_object=obj,
                confidence=round(min(1.0, confidence), 2),
            )
        )

    return candidates


def build_source_key(mail_id: str, index: int) -> str:
    """Idempotenz-Schluessel je Kandidat (Re-Ingest erzeugt keine Dubletten)."""
    return f"{mail_id}:{index}"
