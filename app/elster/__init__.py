"""
ELSTER Integration — UStVA-XML nach offiziellem ERiC-Schema.
Referenz: https://www.elster.de (ERiC-Dokumentation), JuryOberst/Elster (GitHub).
Encoding: ISO-8859-15 (offizielle Anforderung für UStVA-Upload).
"""

from .ustva_xml import build_ustva_elster_xml

__all__ = ["build_ustva_elster_xml"]
