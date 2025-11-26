"""Datenquellen-Lader für InfraStat."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator, Mapping

import csv


class CSVSourceLoader:
    """Lädt InfraStat-relevante Daten aus CSV-Dateien."""

    def __init__(self, delimiter: str = ";") -> None:
        self._delimiter = delimiter

    def load(self, file_path: Path) -> Iterator[Mapping[str, str]]:
        with file_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, delimiter=self._delimiter)
            for row in reader:
                yield row


class IterableSourceLoader:
    """Akzeptiert bereits vorliegende Records (z. B. aus Message-Bus)."""

    def load(self, records: Iterable[Mapping[str, str | float | int]]) -> Iterator[Mapping[str, str | float | int]]:
        for record in records:
            yield record

