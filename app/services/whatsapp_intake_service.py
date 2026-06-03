"""WhatsApp Bestell-Inbox: Freitext-Bestellungen → strukturierter Beleg-Entwurf.

Eingehende Nachrichten aus der Verkaufs-WhatsApp-Gruppe werden als Freitext erfasst
(Copy-Paste) und per LLM (Claude, Messages-API über httpx — kein SDK-Zwang) in
Kunde/Artikel/Menge/Termin/Silo/Preis zerlegt. Fällt der LLM-Pfad aus (kein
ANTHROPIC_API_KEY o. ä.), greift ein deterministischer Heuristik-Parser, damit der
Ablauf jederzeit funktioniert. Kunde wird gegen kunden_lookup gematcht, Artikel
best-effort gegen den Artikelstamm. Nach Bestätigung entsteht ein Kontakt am Kunden
(Brücke in den Flow Spine) und der Beleg wird vorbelegt.
"""

from __future__ import annotations

import json
import logging
import os
import re
import uuid
from typing import Any, Optional

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

_SCHEMA_HINT = (
    "Extrahiere die Bestellung als JSON (NUR JSON, keine Markdown-Blöcke, kein Text drumherum). "
    "Schema:\n"
    "{"
    '"kunde":"Name des Kunden wie genannt",'
    '"ort":"Ort falls genannt sonst null",'
    '"positionen":[{"artikel":"Produkt","menge":Zahl_oder_null,'
    '"einheit":"to|kg|LKW|Pal|Sack|Big-Bag|Stk|null","silo":"Silo/Lagerort oder null",'
    '"preis":Zahl_oder_null}],'
    '"termin":"Liefertermin als Freitext (z. B. Donnerstagmorgen) oder null",'
    '"logistik":"z. B. mit Hänger / Abholung / Zustellung oder null",'
    '"wie_letztes_mal":true_oder_false,'
    '"notiz":"Rest/Hinweise oder null"'
    "}\n"
    "Mengen: '20 to'->menge 20 einheit 'to'; '1 LKW'->1 'LKW'; 'Eine Pal'->1 'Pal'. "
    "'wie letztes Mal' setzt wie_letztes_mal=true. Mehrere Produkte = mehrere positionen."
)

# Bekannte Landhandel-Artikel-Kürzel → für Heuristik & Artikel-Match-Boost.
_ARTIKEL_HINTS = [
    "MLF", "KAS", "AHL", "Soja", "Schrot", "Mehlmischung", "Mehlischung", "MAT",
    "Kartoffelpülpe", "Pülpe", "Dünger", "Kalk", "Saatgut", "Mineral", "Kraftfutter",
]
_EINHEITEN = ["to", "t", "kg", "LKW", "Pal", "Palette", "Sack", "Big-Bag", "BigBag", "Stk"]


class WhatsAppIntakeService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    # ── Extraktion ────────────────────────────────────────────────────────
    def extract(self, raw_text: str) -> tuple[dict, str, float]:
        """Gibt (parsed, engine, confidence) zurück."""
        key = os.environ.get("ANTHROPIC_API_KEY")
        if key:
            try:
                parsed = self._extract_llm(raw_text, key)
                return parsed, "claude", 0.9
            except Exception as exc:  # pragma: no cover - Netzwerk/Key-Fehler
                logger.warning("whatsapp_llm_extract_fehlgeschlagen: %s — fallback heuristik", exc)
        return self._extract_heuristik(raw_text), "heuristik", 0.45

    def _extract_llm(self, raw_text: str, key: str) -> dict:
        resp = httpx.post(
            _ANTHROPIC_URL,
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": _MODEL,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": f"{_SCHEMA_HINT}\n\nNachricht:\n{raw_text}"}],
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        body = resp.json()
        out = body["content"][0]["text"].strip()
        # robustes JSON-Parsing (evtl. mit Fences)
        out = re.sub(r"^```(?:json)?|```$", "", out.strip()).strip()
        return json.loads(out)

    def _extract_heuristik(self, raw_text: str) -> dict:
        """Deterministischer Fallback: erste Zeile/Anfang = Kunde, Mengen+Einheiten je Zeile."""
        text_clean = raw_text.strip()
        wie_letztes = bool(re.search(r"wie letztes mal", text_clean, re.I))
        # Kunde: erstes Wort-Cluster vor einer Menge oder vor "Futterbestellung X"
        kunde = None
        m = re.search(r"(?:futterbestellung|bestellung)\s+([A-ZÄÖÜ][\wäöüß.&\- ]{1,40}?)(?=\s+(?:zu|\d|wie|für|mit))", text_clean, re.I)
        if m:
            kunde = m.group(1).strip()
        if not kunde:
            first = text_clean.splitlines()[0].strip()
            m2 = re.match(r"([A-ZÄÖÜ][\wäöüß.&\- ]{1,40}?)\s+(?:\d|ein|eine|\d+\s*(?:to|t|LKW|Pal))", first, re.I)
            kunde = (m2.group(1).strip() if m2 else first[:60])

        positionen: list[dict] = []
        einh = "|".join(re.escape(e) for e in _EINHEITEN)
        for mm in re.finditer(rf"(\d+(?:[.,]\d+)?)\s*({einh})\b\s*([\wäöüß./\- ]{{0,30}})", text_clean, re.I):
            menge = float(mm.group(1).replace(",", "."))
            einheit = mm.group(2)
            rest = (mm.group(3) or "").strip(" .,-")
            artikel = None
            for hint in _ARTIKEL_HINTS:
                if re.search(re.escape(hint), text_clean, re.I):
                    # nimm das Hint-Wort + ggf. folgendes Wort als Artikel
                    am = re.search(rf"{re.escape(hint)}\w*(?:\s+\w+)?", text_clean, re.I)
                    if am:
                        artikel = am.group(0).strip()
                        break
            if not artikel:
                artikel = rest or "—"
            silo_m = re.search(r"silo\s*\d+", text_clean, re.I)
            positionen.append({
                "artikel": artikel, "menge": menge, "einheit": einheit,
                "silo": (silo_m.group(0) if silo_m else None), "preis": None,
            })
        if not positionen:
            positionen.append({"artikel": text_clean[:60], "menge": None, "einheit": None, "silo": None, "preis": None})

        termin_m = re.search(r"\b(sofort|heute|morgen|montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)\w*", text_clean, re.I)
        return {
            "kunde": kunde, "ort": None, "positionen": positionen,
            "termin": (termin_m.group(0) if termin_m else None),
            "logistik": ("mit Hänger" if re.search(r"hänger", text_clean, re.I) else None),
            "wie_letztes_mal": wie_letztes, "notiz": None,
        }

    # ── Matching ──────────────────────────────────────────────────────────
    def match_kunde(self, kunde_text: Optional[str], ort: Optional[str]) -> Optional[dict]:
        """Fuzzy-Match gegen kunden_lookup.

        Tokens des Kundennamens werden mit OR gegen name/matchcode geprüft (mind. ein
        Treffer ist Pflicht); ein evtl. genannter Ort dient als Ranking-Boost, NICHT als
        harte Bedingung — so matcht 'Lindena Dornum' auf 'A. & H. Lindena GbR' (Dornum),
        ohne dass 'Dornum' im Namen stehen muss.
        """
        if not kunde_text:
            return None
        tokens = [t for t in re.split(r"[\s.,&:]+", kunde_text) if len(t) >= 3][:4]
        if not tokens:
            return None
        ort_tokens = [t for t in tokens]
        if ort:
            ort_tokens += [t for t in re.split(r"[\s.,]+", ort) if len(t) >= 3]
        name_score = " + ".join(f"(CASE WHEN name ILIKE :t{i} OR matchcode ILIKE :t{i} THEN 1 ELSE 0 END)" for i in range(len(tokens)))
        ort_score = " + ".join(f"(CASE WHEN ort ILIKE :o{i} THEN 1 ELSE 0 END)" for i in range(len(ort_tokens))) or "0"
        where = " OR ".join(f"name ILIKE :t{i} OR matchcode ILIKE :t{i}" for i in range(len(tokens)))
        params: dict[str, Any] = {f"t{i}": f"%{tok}%" for i, tok in enumerate(tokens)}
        params.update({f"o{i}": f"%{tok}%" for i, tok in enumerate(ort_tokens)})
        sql = (
            f"SELECT kunden_nr, name, plz, ort, business_partner_id, ({name_score}) AS nscore, ({ort_score}) AS oscore "
            f"FROM kunden_lookup WHERE {where} ORDER BY nscore DESC, oscore DESC, length(name) ASC LIMIT 1"
        )
        try:
            r = self.db.execute(text(sql), params).mappings().first()
        except Exception:
            self.db.rollback()
            return None
        if not r:
            return None
        return {"kunden_nr": r["kunden_nr"], "name": r["name"], "plz": r.get("plz"), "ort": r.get("ort")}

    def match_artikel(self, artikel_text: Optional[str]) -> Optional[dict]:
        if not artikel_text or artikel_text == "—":
            return None
        token = re.split(r"[\s/]+", artikel_text.strip())[0]
        if len(token) < 2:
            return None
        try:
            r = self.db.execute(
                text(
                    "SELECT article_number, name FROM domain_inventory.articles "
                    "WHERE is_active IS NOT FALSE AND (name ILIKE :q OR article_number ILIKE :q) "
                    "ORDER BY length(name) LIMIT 1"
                ),
                {"q": f"%{token}%"},
            ).mappings().first()
        except Exception:
            self.db.rollback()
            return None
        return {"article_number": r["article_number"], "name": r["name"]} if r else None

    # ── Persistenz / Workflow ─────────────────────────────────────────────
    def _enrich(self, parsed: dict) -> dict:
        kunde = self.match_kunde(parsed.get("kunde"), parsed.get("ort"))
        for pos in parsed.get("positionen", []) or []:
            art = self.match_artikel(pos.get("artikel"))
            if art:
                pos["match_article_number"] = art["article_number"]
                pos["match_name"] = art["name"]
        parsed["match_kunde"] = kunde
        return parsed

    def create_inbox(self, raw_text: str, absender: Optional[str], quelle: str = "whatsapp") -> dict:
        parsed, engine, conf = self.extract(raw_text)
        parsed = self._enrich(parsed)
        kunde = parsed.get("match_kunde") or {}
        new_id = str(uuid.uuid4())
        self.db.execute(
            text(
                """
                INSERT INTO public.whatsapp_bestellungen
                  (id, raw_text, absender, quelle, status, parsed, kunden_nr, kunde_text, engine, confidence, tenant_id)
                VALUES
                  (:id, :raw, :abs, :q, 'geparst', CAST(:parsed AS JSONB), :knr, :ktext, :eng, :conf, :tid)
                """
            ),
            {
                "id": new_id, "raw": raw_text, "abs": absender, "q": quelle,
                "parsed": json.dumps(parsed, ensure_ascii=False),
                "knr": kunde.get("kunden_nr"), "ktext": parsed.get("kunde"),
                "eng": engine, "conf": conf, "tid": self.tenant_id,
            },
        )
        self.db.commit()
        return self.get(new_id)

    def get(self, inbox_id: str) -> dict:
        r = self.db.execute(
            text(
                "SELECT id, raw_text, absender, quelle, eingegangen_am, status, parsed, kunden_nr, "
                "kunde_text, beleg_typ, beleg_ref, engine, confidence "
                "FROM public.whatsapp_bestellungen WHERE id = :id AND tenant_id = :t"
            ),
            {"id": inbox_id, "t": self.tenant_id},
        ).mappings().first()
        return self._row(r) if r else {}

    def list_inbox(self, status: Optional[str] = None) -> list[dict]:
        sql = (
            "SELECT id, raw_text, absender, quelle, eingegangen_am, status, parsed, kunden_nr, "
            "kunde_text, beleg_typ, beleg_ref, engine, confidence "
            "FROM public.whatsapp_bestellungen WHERE tenant_id = :t"
        )
        params: dict[str, Any] = {"t": self.tenant_id}
        if status:
            sql += " AND status = :s"
            params["s"] = status
        sql += " ORDER BY eingegangen_am DESC LIMIT 200"
        rows = self.db.execute(text(sql), params).mappings().all()
        return [self._row(r) for r in rows]

    def bestaetigen(self, inbox_id: str, kunden_nr: Optional[str], beleg_typ: str, parsed_override: Optional[dict]) -> dict:
        """Verkäufer bestätigt: Kunde fixieren, Beleg-Typ setzen, Kontakt am Kunden anlegen."""
        cur = self.get(inbox_id)
        if not cur:
            return {}
        knr = kunden_nr or cur.get("kunden_nr")
        parsed = parsed_override or cur.get("parsed") or {}
        self.db.execute(
            text(
                "UPDATE public.whatsapp_bestellungen SET status='bestaetigt', kunden_nr=:knr, "
                "beleg_typ=:bt, parsed=CAST(:p AS JSONB), updated_at=now() WHERE id=:id AND tenant_id=:t"
            ),
            {"knr": knr, "bt": beleg_typ, "p": json.dumps(parsed, ensure_ascii=False), "id": inbox_id, "t": self.tenant_id},
        )
        # Kontakt am Kunden (Brücke in den Flow Spine) — nur wenn Kunde gematcht.
        if knr:
            pos_txt = "; ".join(
                f"{p.get('menge') or ''} {p.get('einheit') or ''} {p.get('artikel') or ''}".strip()
                for p in (parsed.get("positionen") or [])
            )
            self.db.execute(
                text(
                    """
                    INSERT INTO public.kunden_kontakte
                      (kunden_nr, richtung, art, kurzinfo, notiz, weiterleitung_an, bediener, verweis, tenant_id)
                    VALUES (:knr, 'ein', 'whatsapp', :kurz, :notiz, 'Disposition', :bed, :verweis, :tid)
                    """
                ),
                {
                    "knr": knr, "kurz": f"WhatsApp-Bestellung: {pos_txt[:280]}" or "WhatsApp-Bestellung",
                    "notiz": cur.get("raw_text"), "bed": cur.get("absender"),
                    "verweis": f"Bestell-Inbox {inbox_id[:8]}", "tid": self.tenant_id,
                },
            )
        self.db.commit()
        return self.get(inbox_id)

    def verwerfen(self, inbox_id: str) -> dict:
        self.db.execute(
            text("UPDATE public.whatsapp_bestellungen SET status='verworfen', updated_at=now() WHERE id=:id AND tenant_id=:t"),
            {"id": inbox_id, "t": self.tenant_id},
        )
        self.db.commit()
        return self.get(inbox_id)

    def _row(self, r) -> dict:
        d = dict(r)
        d["id"] = str(d["id"])
        if d.get("eingegangen_am") is not None:
            d["eingegangen_am"] = d["eingegangen_am"].isoformat()
        if d.get("confidence") is not None:
            d["confidence"] = float(d["confidence"])
        return d
