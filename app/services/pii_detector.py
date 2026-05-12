"""
PII Detector + Masker — NC-C1/C2
Regex- und Pattern-basierte Erkennung und Maskierung personenbezogener Daten.
Reversibel fuer berechtigte Nutzer, irreversibel fuer Logs.
"""

from __future__ import annotations

import re
import hashlib
from dataclasses import dataclass
from typing import Optional


@dataclass
class PIIMatch:
    type: str
    value: str
    start: int
    end: int
    masked: str = ""


PII_PATTERNS: dict[str, re.Pattern] = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "iban": re.compile(r"\b[A-Z]{2}\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{0,2}\b"),
    "phone_de": re.compile(r"\b(?:\+49|0049|0)\s?[\d\s/\-]{6,14}\d\b"),
    "steuernummer": re.compile(r"\b\d{2,3}/\d{3}/\d{4,5}\b"),
    "personalausweis": re.compile(r"\b[A-Z0-9]{9,10}\b(?=.*ausweis)", re.IGNORECASE),
    "kreditkarte": re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
    "geburtsdatum": re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b"),
    "sozialversicherung": re.compile(r"\b\d{2}\s?\d{6}\s?[A-Z]\s?\d{3}\b"),
}

_REVERSIBLE_STORE: dict[str, str] = {}


def detect_pii(text: str, patterns: Optional[dict[str, re.Pattern]] = None) -> list[PIIMatch]:
    active = patterns or PII_PATTERNS
    matches: list[PIIMatch] = []
    for pii_type, pattern in active.items():
        for m in pattern.finditer(text):
            matches.append(PIIMatch(
                type=pii_type,
                value=m.group(),
                start=m.start(),
                end=m.end(),
            ))
    matches.sort(key=lambda x: x.start)
    return matches


def mask_irreversible(text: str, matches: Optional[list[PIIMatch]] = None) -> str:
    if matches is None:
        matches = detect_pii(text)
    result = text
    for m in sorted(matches, key=lambda x: x.start, reverse=True):
        placeholder = f"[{m.type.upper()}]"
        result = result[:m.start] + placeholder + result[m.end:]
    return result


def mask_reversible(text: str, matches: Optional[list[PIIMatch]] = None) -> tuple[str, dict[str, str]]:
    if matches is None:
        matches = detect_pii(text)
    result = text
    token_map: dict[str, str] = {}
    for m in sorted(matches, key=lambda x: x.start, reverse=True):
        token = f"<<PII:{hashlib.sha256(m.value.encode()).hexdigest()[:12]}>>"
        token_map[token] = m.value
        _REVERSIBLE_STORE[token] = m.value
        result = result[:m.start] + token + result[m.end:]
    return result, token_map


def unmask(text: str, token_map: Optional[dict[str, str]] = None) -> str:
    store = token_map or _REVERSIBLE_STORE
    result = text
    for token, original in store.items():
        result = result.replace(token, original)
    return result


def scan_dict(data: dict, path: str = "") -> list[PIIMatch]:
    all_matches: list[PIIMatch] = []
    for key, value in data.items():
        current_path = f"{path}.{key}" if path else key
        if isinstance(value, str):
            matches = detect_pii(value)
            for m in matches:
                m.masked = current_path
            all_matches.extend(matches)
        elif isinstance(value, dict):
            all_matches.extend(scan_dict(value, current_path))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, str):
                    matches = detect_pii(item)
                    for m in matches:
                        m.masked = f"{current_path}[{i}]"
                    all_matches.extend(matches)
                elif isinstance(item, dict):
                    all_matches.extend(scan_dict(item, f"{current_path}[{i}]"))
    return all_matches
