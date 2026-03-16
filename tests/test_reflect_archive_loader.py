from __future__ import annotations

from pathlib import Path

import pytest

from scripts.simple_activate_reflect_archive import (
    ArchiveTextFileSpec,
    ReflectArchiveSourceError,
    load_archive_documents,
    read_archive_text_file,
)


class FakeCollection:
    def __init__(self):
        self.inserted: list[dict] = []

    def insert_one(self, document: dict) -> None:
        self.inserted.append(document)


def test_read_archive_text_file_rejects_null_bytes(tmp_path: Path):
    file_path = tmp_path / "tasks.md"
    file_path.write_bytes(b"broken\x00content")

    with pytest.raises(ReflectArchiveSourceError) as exc:
        read_archive_text_file(file_path)

    assert "Null-Bytes" in str(exc.value)


def test_load_archive_documents_rejects_missing_required_file(tmp_path: Path):
    collection = FakeCollection()
    specs = [ArchiveTextFileSpec(tmp_path / "tasks.md", required=True)]

    with pytest.raises(ReflectArchiveSourceError) as exc:
        load_archive_documents(collection, specs, collection_name="tasks")

    assert "Pflichtdatei fehlt" in str(exc.value)


def test_load_archive_documents_skips_missing_optional_but_requires_one_loaded(tmp_path: Path):
    collection = FakeCollection()
    specs = [ArchiveTextFileSpec(tmp_path / "tasks-new.md", required=False)]

    with pytest.raises(ReflectArchiveSourceError) as exc:
        load_archive_documents(collection, specs, collection_name="tasks")

    assert "Keine Dateien" in str(exc.value)


def test_load_archive_documents_loads_required_and_optional_files(tmp_path: Path):
    collection = FakeCollection()
    required_file = tmp_path / "tasks.md"
    optional_file = tmp_path / "tasks-new.md"
    required_file.write_text("alpha", encoding="utf-8")
    optional_file.write_text("beta", encoding="utf-8")

    inserted = load_archive_documents(
        collection,
        [
            ArchiveTextFileSpec(required_file, required=True),
            ArchiveTextFileSpec(optional_file, required=False),
        ],
        collection_name="tasks",
    )

    assert inserted == 2
    assert [doc["filename"] for doc in collection.inserted] == ["tasks.md", "tasks-new.md"]


def test_read_archive_text_file_falls_back_to_latin1(tmp_path: Path):
    file_path = tmp_path / "tasks.md"
    file_path.write_bytes("ä".encode("latin-1"))

    assert read_archive_text_file(file_path) == "ä"
