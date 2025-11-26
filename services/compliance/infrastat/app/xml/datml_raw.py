"""Erzeugt DatML-RAW-D konforme Meldungen (XStatistik 2.0)."""

from __future__ import annotations

from typing import Any, Dict, Iterable

from xml.etree import ElementTree as ET

NAMESPACE = "http://www.destatis.de/schema/datml-raw/2.0/de"
ET.register_namespace("", NAMESPACE)


class DatMLRawBuilder:
    """Erstellt DatML-RAW-D XML aus Batch-Daten."""

    def __init__(self, batch: Any) -> None:
        self.batch = batch

    def build(self) -> str:
        root = ET.Element(_qn("DatML-RAW-D"), attrib={"version": "2.0"})
        self._append_sender(root)
        self._append_receiver(root)
        self._append_messages(root)
        tree = ET.ElementTree(root)
        return ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True).decode("utf-8")

    def _append_sender(self, root: ET.Element) -> None:
        sender_info = self._metadata_dict().get("sender", {})
        sender = ET.SubElement(root, _qn("Absender"))
        organisation = ET.SubElement(sender, _qn("Organisation"))
        ET.SubElement(organisation, _qn("Name")).text = sender_info.get("name", "Unknown Sender")
        if sender_info.get("id"):
            ET.SubElement(organisation, _qn("Organisationseinheit")).text = sender_info["id"]

    def _append_receiver(self, root: ET.Element) -> None:
        receiver_info = self._metadata_dict().get("receiver", {})
        receiver = ET.SubElement(root, _qn("Empfaenger"))
        organisation = ET.SubElement(receiver, _qn("Organisation"))
        ET.SubElement(organisation, _qn("Name")).text = receiver_info.get("name", "Destatis")
        if receiver_info.get("id"):
            ET.SubElement(organisation, _qn("Organisationseinheit")).text = receiver_info["id"]

    def _append_messages(self, root: ET.Element) -> None:
        message = ET.SubElement(root, _qn("Nachricht"))
        message.attrib["lfdNr"] = "1"

        header = ET.SubElement(message, _qn("Nachrichtenkopf"))
        ET.SubElement(header, _qn("Berichtszeitraum")).text = self.batch.reference_period.strftime("%Y-%m")

        segments = ET.SubElement(message, _qn("Segmente"))
        for idx, line in enumerate(self._lines(), start=1):
            segment = ET.SubElement(segments, _qn("Segment"))
            segment.attrib["lfdNr"] = str(idx)
            ET.SubElement(segment, _qn("Datensegment")).text = _build_segment_payload(line)

    def _metadata_dict(self) -> Dict[str, Any]:
        return getattr(self.batch, "metadata", {}) or {}

    def _lines(self) -> Iterable[Any]:
        return getattr(self.batch, "lines", [])


def _qn(tag: str) -> str:
    return f"{{{NAMESPACE}}}{tag}"


def _build_segment_payload(line: Any) -> str:
    payload = {
        "commodity_code": line.commodity_code,
        "country_of_origin": line.country_of_origin,
        "country_of_destination": line.country_of_destination,
        "net_mass_kg": float(line.net_mass_kg),
        "invoice_value_eur": float(line.invoice_value_eur),
    }
    if line.statistical_value_eur is not None:
        payload["statistical_value_eur"] = float(line.statistical_value_eur)
    if line.delivery_terms:
        payload["delivery_terms"] = line.delivery_terms
    return str(payload)
