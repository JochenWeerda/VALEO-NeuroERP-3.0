"""Waage-Endpunkte: Fehler- und Erfolgswege, die test_waage_api.py nicht erreicht (03.11.2026).

Import, Fehlerqueue, Kalibrierung und Pflichtfeldpruefung wurden nur bis zum ersten 404 geprueft. Hier laufen sie
bis zum Commit bzw. bis zum Rollback - ohne Datenbank, die Wirkung wird an der Sitzung abgelesen.
"""
from __future__ import annotations

import asyncio
import io
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, UploadFile

from app.api.v1.endpoints import waage

_NUTZER = {"sub": "nutzer-1"}


def _datei(inhalt: bytes) -> UploadFile:
    return UploadFile(filename="wiegungen.txt", file=io.BytesIO(inhalt))


def _waage_da():
    return patch.object(waage, "WaageRepository", return_value=MagicMock(get_by_id=MagicMock(return_value=object())))


class TestPartiepflichtKonfiguration:
    def test_artikelgruppe_aus_der_artikeltabelle(self):
        db = MagicMock()
        db.execute.return_value.fetchall.return_value = [("artikel_gruppe",)]
        assert asyncio.run(waage.get_partiepflicht_config(db=db))["config_source"] == "articles_table"


class TestWaagenStamm:
    def test_to_dict_liest_die_spalten_des_modells(self):
        from app.domains.operations.models import Waage as WaageModell

        modell = WaageModell(id="W-1", standort="Halle A", typ="LKW", max_kapazitaet=50)
        daten = waage._to_dict(modell)
        assert daten["id"] == "W-1"
        assert daten["standort"] == "Halle A"
        assert waage._to_dict(None) == {}

    def test_pflichtfeld_leer_ist_422(self):
        with pytest.raises(HTTPException) as fehler:
            asyncio.run(waage.update_waage("W-1", waage.WaageUpdate(standort=None), db=MagicMock(), tenant_id="t-1"))
        assert fehler.value.status_code == 422

    def test_waage_mit_wiegungen_ist_nicht_loeschbar(self):
        with patch.object(waage, "WaageRepository") as repo:
            repo.return_value.delete.side_effect = ValueError("hat Wiegungen")
            with pytest.raises(HTTPException) as fehler:
                asyncio.run(waage.delete_waage("W-1", db=MagicMock(), tenant_id="t-1"))
        assert fehler.value.status_code == 409


class TestAsciiImport:
    def test_unbekannte_waage_ist_404(self):
        with patch.object(waage, "WaageRepository") as repo:
            repo.return_value.get_by_id.return_value = None
            with pytest.raises(HTTPException) as fehler:
                asyncio.run(waage.import_ascii(_datei(b"W;1"), waage_id="fremd", db=MagicMock(), tenant_id="t-1", user=_NUTZER))
        assert fehler.value.status_code == 404

    def test_zu_grosse_datei_ist_413(self):
        db = MagicMock()
        with _waage_da(), pytest.raises(HTTPException) as fehler:
            asyncio.run(waage.import_ascii(_datei(b"x" * 1048577), waage_id="W-1", db=db, tenant_id="t-1", user=_NUTZER))
        assert fehler.value.status_code == 413
        db.commit.assert_not_called()

    def test_kein_utf8_ist_422(self):
        with _waage_da(), pytest.raises(HTTPException) as fehler:
            asyncio.run(waage.import_ascii(_datei(b"\xff\xfe\xfa"), waage_id="W-1", db=MagicMock(), tenant_id="t-1", user=_NUTZER))
        assert fehler.value.status_code == 422

    def test_erfolg_wird_festgeschrieben(self):
        db = MagicMock()
        with _waage_da(), patch.object(waage.scale_import, "import_records", return_value={"importiert": 1}) as importer:
            ergebnis = asyncio.run(waage.import_ascii(_datei(b"W;1"), waage_id="W-1", fehler_toleranz=False, db=db,
                                                      tenant_id="t-1", user=_NUTZER))
        assert ergebnis == {"importiert": 1}
        assert importer.call_args.args[1:] == ("t-1", "W-1", "W;1", False, "nutzer-1")
        db.commit.assert_called_once()

    def test_fehler_rollt_zurueck(self):
        db = MagicMock()
        with _waage_da(), patch.object(waage.scale_import, "import_records", side_effect=RuntimeError("kaputt")), \
                pytest.raises(RuntimeError):
            asyncio.run(waage.import_ascii(_datei(b"W;1"), waage_id="W-1", db=db, tenant_id="t-1", user=_NUTZER))
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestFehlerqueue:
    def test_liste_zeigt_die_fehler_des_mandanten(self):
        db = MagicMock()
        eintrag = object()
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [eintrag]
        with patch.object(waage.scale_import, "serialize_entry", return_value={"id": "E-1"}) as serialisiert:
            assert asyncio.run(waage.list_fehlerqueue(db=db, tenant_id="t-1", limit=5)) == [{"id": "E-1"}]
        serialisiert.assert_called_once_with(eintrag)
        db.query.return_value.filter.return_value.order_by.return_value.limit.assert_called_once_with(5)

    def test_wiederholen_schreibt_fest(self):
        db = MagicMock()
        with patch.object(waage.scale_import, "retry_entry", return_value={"status": "imported"}):
            assert asyncio.run(waage.retry_fehlerqueue_entry("E-1", db=db, tenant_id="t-1", user=_NUTZER)) == {"status": "imported"}
        db.commit.assert_called_once()

    def test_wiederholen_fehler_rollt_zurueck(self):
        db = MagicMock()
        with patch.object(waage.scale_import, "retry_entry", side_effect=HTTPException(404)), pytest.raises(HTTPException):
            asyncio.run(waage.retry_fehlerqueue_entry("E-1", db=db, tenant_id="t-1", user=_NUTZER))
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_verwerfen_setzt_den_status_und_protokolliert(self):
        db = MagicMock()
        eintrag = SimpleNamespace(status="error")
        with patch.object(waage.scale_import, "queue_entry", return_value=eintrag), \
                patch.object(waage.scale_import, "_event") as ereignis:
            assert asyncio.run(waage.delete_fehlerqueue_entry("E-1", db=db, tenant_id="t-1", user=_NUTZER)) == {
                "deleted": True, "id": "E-1"}
        assert eintrag.status == "dismissed"
        ereignis.assert_called_once_with(db, "t-1", "nutzer-1", eintrag, "dismissed")
        db.commit.assert_called_once()

    def test_verarbeiteter_eintrag_ist_409(self):
        db = MagicMock()
        eintrag = SimpleNamespace(status="imported")
        with patch.object(waage.scale_import, "queue_entry", return_value=eintrag), pytest.raises(HTTPException) as fehler:
            asyncio.run(waage.delete_fehlerqueue_entry("E-1", db=db, tenant_id="t-1", user=_NUTZER))
        assert fehler.value.status_code == 409
        assert eintrag.status == "imported"
        db.rollback.assert_called_once()


class TestKalibrierung:
    def test_status_nach_faelligkeit(self):
        heute = date(2026, 11, 3)
        with patch.object(waage, "business_today", return_value=heute):
            assert waage._kalibrierung_status(None) == "faellig"
            assert waage._kalibrierung_status("2026-12-01") == "ok"
            assert waage._kalibrierung_status((heute - timedelta(days=10)).isoformat()) == "faellig"
            assert waage._kalibrierung_status((heute - timedelta(days=31)).isoformat()) == "ueberfaellig"
            assert waage._kalibrierung_status("kein-datum") == "unbekannt"

    def _waage(self):
        return SimpleNamespace(id="W-1", letzte_eichung=datetime(2025, 5, 5, tzinfo=timezone.utc),
                               naechste_eichung=datetime(2027, 5, 5, tzinfo=timezone.utc), eichamt="Alt",
                               zertifikat_nr="Z-1", updated_by=None)

    def test_unbekannte_waage_beim_lesen_ist_404(self):
        with patch.object(waage, "WaageRepository") as repo:
            repo.return_value.get_by_id.return_value = None
            with pytest.raises(HTTPException) as fehler:
                asyncio.run(waage.get_kalibrierung("fremd", db=MagicMock(), tenant_id="t-1"))
        assert fehler.value.status_code == 404

    def test_naechste_vor_letzter_eichung_ist_422(self):
        db = MagicMock()
        with patch.object(waage.scale_import, "locked_scale", return_value=self._waage()), pytest.raises(HTTPException) as fehler:
            asyncio.run(waage.update_kalibrierung("W-1", waage.WaageCalibrationUpdate(naechste_eichfaelligkeit=date(2024, 1, 1)),
                                                  db=db, tenant_id="t-1", user=_NUTZER))
        assert fehler.value.status_code == 422
        db.commit.assert_not_called()

    def test_aenderung_mit_audit_und_ereignis(self):
        db = MagicMock()
        geeicht = self._waage()
        aenderung = waage.WaageCalibrationUpdate(letztes_eichdatum=date(2026, 11, 2), naechste_eichfaelligkeit=date(2028, 11, 2),
                                                 eichamt="Eichamt Oldenburg")
        with patch.object(waage.scale_import, "locked_scale", return_value=geeicht), \
                patch("app.services.mask_action_runtime_service._write_audit") as audit:
            ergebnis = asyncio.run(waage.update_kalibrierung("W-1", aenderung, db=db, tenant_id="t-1", user=_NUTZER))
        assert ergebnis["letztes_eichdatum"] == "2026-11-02"
        assert ergebnis["naechste_eichfaelligkeit"] == "2028-11-02"
        assert ergebnis["eichamt"] == "Eichamt Oldenburg"
        assert geeicht.updated_by == "nutzer-1"
        assert audit.call_args.kwargs["action_key"] == "waage.calibration.update"
        ereignis = db.add.call_args.args[0]
        assert ereignis.event_type == "waage.calibration.updated"
        assert ereignis.tenant_id == "t-1"
        db.commit.assert_called_once()

    def test_schreibfehler_rollt_zurueck(self):
        db = MagicMock()
        with patch.object(waage.scale_import, "locked_scale", return_value=self._waage()), \
                patch("app.services.mask_action_runtime_service._write_audit", side_effect=RuntimeError("kaputt")), \
                pytest.raises(RuntimeError):
            asyncio.run(waage.update_kalibrierung("W-1", waage.WaageCalibrationUpdate(eichamt="Neu"), db=db, tenant_id="t-1",
                                                  user=_NUTZER))
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestDoppelwiegung:
    def test_fachlicher_fehler_rollt_zurueck_und_bleibt_fachlich(self):
        db = MagicMock()
        db.execute.return_value.scalar.side_effect = [2026, 41]
        auftrag = waage.WiegescheinMitDoppelwiegung(
            waage_id="WA-1", kfz_kennzeichen="HB-1",
            wiegung_erweitert=waage.WiegungErweitert(waage_id="WA-1", brutto_kg=1000, tara_kg=400, zielschein_typ="VL"))
        with patch.object(waage, "finalize_menge_from_outbound_weighing", side_effect=HTTPException(409, "Frachtbrief gesperrt")), \
                pytest.raises(HTTPException) as fehler:
            asyncio.run(waage.create_dual_wiegung(payload=auftrag, tenant_id="t-1", db=db))
        assert fehler.value.status_code == 409
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
