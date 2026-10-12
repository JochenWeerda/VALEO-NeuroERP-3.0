"""WhatsApp Bestell-Inbox: Freitext-Bestellungen → strukturierter Beleg-Entwurf.

Eingehende Nachrichten aus der Verkaufs-WhatsApp-Gruppe werden als Freitext erfasst
(Copy-Paste) und per LLM (Claude, Messages-API über httpx — kein SDK-Zwang) in
Kunde/Artikel/Menge/Termin/Silo/Preis zerlegt. Fällt der LLM-Pfad aus (kein
ANTHROPIC_API_KEY o. ä.), greift ein deterministischer Heuristik-Parser, damit der
Ablauf jederzeit funktioniert. Kunde wird gegen kunden_lookup gematcht, Artikel
gegen mandantengebundene Stammdaten. Nach Bestätigung entsteht ein Kontakt am Kunden
(Brücke in den Flow Spine) und der Beleg wird vorbelegt.
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from copy import deepcopy
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class WhatsAppReferenceError(ValueError):
    """A selected reference is unavailable or ambiguous in the tenant."""

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
    def __init__(self, db: Session, tenant_id: str) -> None:
        if not isinstance(tenant_id, str) or not tenant_id.strip() or len(tenant_id) > 64:
            raise ValueError("Explicit tenant context required")
        self.db = db
        self.tenant_id = tenant_id

    # ── Extraktion ────────────────────────────────────────────────────────
    def extract(self, raw_text: str) -> tuple[dict, str, float]:
        """Gibt (parsed, engine, confidence) zurück.

        Nutzt das anbieterunabhängige LLM-Gateway (Anbieterwahl des Admins, inkl.
        Tenant-Konfiguration). Fällt bei fehlendem Anbieter/Fehler deterministisch
        auf die Heuristik zurück."""
        from app.services.llm_gateway import LLMGateway, parse_json_object

        out = LLMGateway(self.db, self.tenant_id).complete_or_none(
            f"{_SCHEMA_HINT}\n\nNachricht:\n{raw_text}", max_tokens=1024
        )
        if out:
            try:
                return parse_json_object(out), "claude", 0.9
            except Exception:
                logger.warning("whatsapp_llm_parse_fehlgeschlagen — fallback heuristik")
        return self._extract_heuristik(raw_text), "heuristik", 0.45

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
        """Fuzzy-Match im eigenen aktiven Business-Partner-Kontext.

        Tokens des Kundennamens werden mit OR gegen name/matchcode geprüft (mind. ein
        Treffer ist Pflicht); ein evtl. genannter Ort dient als Ranking-Boost, NICHT als
        harte Bedingung — so matcht 'Lindena Dornum' auf 'A. & H. Lindena GbR' (Dornum),
        ohne dass 'Dornum' im Namen stehen muss.
        """
        if not isinstance(kunde_text, str) or not kunde_text.strip():
            return None
        tokens = [t for t in re.split(r"[\s.,&:]+", kunde_text) if len(t) >= 3][:4]
        if not tokens:
            return None
        ort_tokens = [t for t in tokens]
        if isinstance(ort, str) and ort:
            ort_tokens += [t for t in re.split(r"[\s.,]+", ort) if len(t) >= 3]
        name_score = " + ".join(f"(CASE WHEN k.name ILIKE :t{i} OR k.matchcode ILIKE :t{i} THEN 1 ELSE 0 END)" for i in range(len(tokens)))
        ort_score = " + ".join(f"(CASE WHEN k.ort ILIKE :o{i} THEN 1 ELSE 0 END)" for i in range(len(ort_tokens))) or "0"
        where = " OR ".join(f"k.name ILIKE :t{i} OR k.matchcode ILIKE :t{i}" for i in range(len(tokens)))
        params: dict[str, Any] = {f"t{i}": f"%{tok}%" for i, tok in enumerate(tokens)}
        params.update({f"o{i}": f"%{tok}%" for i, tok in enumerate(ort_tokens)})
        params["tenant"] = self.tenant_id
        sql = (
            f"SELECT k.kunden_nr, k.name, k.plz, k.ort, k.business_partner_id, ({name_score}) AS nscore, ({ort_score}) AS oscore "
            "FROM public.kunden_lookup k JOIN domain_crm.business_partners bp "
            "ON bp.partner_id::text = k.business_partner_id::text "
            "WHERE bp.tenant_id = :tenant AND bp.is_customer IS TRUE AND bp.status = 'active' AND ("
            f"{where}) ORDER BY nscore DESC, oscore DESC, length(name) ASC LIMIT 2"  # nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden
        )
        rows = self.db.execute(text(sql), params).mappings().all()
        if len(rows) != 1:
            return None
        r = rows[0]
        return {"kunden_nr": r["kunden_nr"], "name": r["name"], "plz": r.get("plz"), "ort": r.get("ort")}

    def _customer_by_number(self, number: str) -> dict:
        rows = self.db.execute(text(
            "SELECT k.kunden_nr, k.name1 AS name, k.plz, k.ort FROM public.kunden k "
            "JOIN domain_crm.business_partners bp ON bp.partner_id::text = k.business_partner_id::text "
            "WHERE k.kunden_nr = :number AND bp.tenant_id = :tenant "
            "AND k.geloescht IS NOT TRUE AND bp.is_customer IS TRUE AND bp.status = 'active' "
            "LIMIT 2 FOR SHARE OF k, bp"
        ), {"number": number, "tenant": self.tenant_id}).mappings().all()
        if len(rows) != 1:
            raise WhatsAppReferenceError("Unavailable customer reference")
        return dict(rows[0])

    def match_artikel(self, artikel_text: Optional[str]) -> Optional[dict]:
        if not isinstance(artikel_text, str) or not artikel_text.strip() or artikel_text == "—":
            return None
        token = re.split(r"[\s/]+", artikel_text.strip())[0]
        if len(token) < 2:
            return None
        rows = self.db.execute(
            text(
                "SELECT article_number, name FROM domain_inventory.articles "
                "WHERE tenant_id = :t AND is_active IS NOT FALSE "
                "AND (name ILIKE :q OR article_number ILIKE :q) "
                "ORDER BY length(name) LIMIT 2"
            ),
            {"q": f"%{token}%", "t": self.tenant_id},
        ).mappings().all()
        if len(rows) != 1:
            return None
        return {"article_number": rows[0]["article_number"], "name": rows[0]["name"]}

    @staticmethod
    def _positions(parsed: dict) -> list[dict]:
        positions = parsed.get("positionen")
        if positions is None:
            return []
        if not isinstance(positions, list) or any(not isinstance(p, dict) for p in positions):
            raise WhatsAppReferenceError("Invalid order positions")
        return positions

    def _validate_references(self, parsed: dict, customer_number: Optional[str]) -> dict:
        result = deepcopy(parsed)
        result["match_kunde"] = self._customer_by_number(customer_number) if customer_number is not None else None
        for pos in self._positions(result):
            refs = [pos[key] for key in ("match_article_number", "article_number") if pos.get(key) is not None]
            if not refs:
                pos.pop("match_name", None)
                continue
            if any(not isinstance(ref, str) or not ref.strip() for ref in refs) or len(set(refs)) != 1:
                raise WhatsAppReferenceError("Invalid article reference")
            rows = self.db.execute(text(
                "SELECT name FROM domain_inventory.articles WHERE tenant_id=:tenant "
                "AND article_number=:number AND is_active IS NOT FALSE LIMIT 2 FOR SHARE"
            ), {"tenant": self.tenant_id, "number": refs[0]}).mappings().all()
            if len(rows) != 1:
                raise WhatsAppReferenceError("Unavailable article reference")
            pos["match_name"] = rows[0]["name"]
        return result

    # ── Persistenz / Workflow ─────────────────────────────────────────────
    def _enrich(self, parsed: dict) -> dict:
        parsed = deepcopy(parsed)
        kunde = self.match_kunde(parsed.get("kunde"), parsed.get("ort"))
        for pos in self._positions(parsed):
            for key in ("match_article_number", "match_name", "article_number"):
                pos.pop(key, None)
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

    def bestaetigen(self, inbox_id: str, kunden_nr: Optional[str], beleg_typ: str, parsed_override: Optional[dict], *, actor: str) -> dict:
        """Verkäufer bestätigt: Kunde fixieren, Beleg-Typ setzen, Kontakt am Kunden anlegen."""
        if not isinstance(actor, str) or not actor.strip() or len(actor) > 120:
            raise ValueError("Verified actor required")
        cur = self.get(inbox_id)
        if not cur:
            return {}
        knr = cur.get("kunden_nr") if kunden_nr is None else kunden_nr
        parsed = (cur.get("parsed") or {}) if parsed_override is None else parsed_override
        parsed = self._validate_references(parsed, knr)
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
                    "notiz": cur.get("raw_text"), "bed": actor,
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
