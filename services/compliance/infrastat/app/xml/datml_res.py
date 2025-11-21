"""Generiert DatML-RES-D Empfangsbestätigungen."""

from __future__ import annotations

from typing import Iterable

from xml.etree import ElementTree as ET

NAMESPACE = "http://www.destatis.de/schema/datml-res/2.0/de"
ET.register_namespace("", NAMESPACE)


class DatMLResBuilder:
    def __init__(self, submission_id: str, batch) -> None:
        self.submission_id = submission_id
        self.batch = batch

    def build(self, errors: Iterable[str] | None = None) -> str:
        root = ET.Element(_qn("DatML-RES-D"), attrib={"version": "2.0"})
        header = ET.SubElement(root, _qn("Pruefprotokoll"))
        ET.SubElement(header, _qn("Referenz"), attrib={"id": self.submission_id})
        if errors:
            for message in errors:
                entry = ET.SubElement(header, _qn("Pruefmeldung"))
                ET.SubElement(entry, _qn("Text")).text = message
        tree = ET.ElementTree(root)
        return ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True).decode("utf-8")


def _qn(tag: str) -> str:
    return f"{{{NAMESPACE}}}{tag}"
