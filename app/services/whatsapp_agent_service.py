"""
WA-AGENT-001 — WhatsApp Bestellagent

Verarbeitet eingehende WhatsApp-Nachrichten, extrahiert Bestelldetails via LLM,
legt Sales Orders im ERP an und sendet strukturierte Antworten zurück.

Prozesskette:
  Textnachricht → Kundensuche via Telefonnummer → LLM-Extraktion →
  Vollständigkeitsprüfung → Rückfrage ODER Auftrag anlegen → Antwort

DSGVO: Gesprächskontext wird nur im Arbeitsspeicher (tenant-isoliert) gehalten,
kein Logging personenbezogener Nachrichteninhalte.
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("whatsapp.agent")

# ─── In-Memory-Kontext (tenant-isoliert) ─────────────────────────────────────
# { tenant_id: { phone_number: ConversationState } }
_CONV_STORE: dict[str, dict[str, "ConversationState"]] = {}

# ─── In-Memory Order-Log (nur für Simulator, keine Produktion) ───────────────
_ORDER_LOG: dict[str, list[dict]] = {}  # { tenant_id: [order_dict] }


@dataclass
class ExtractedOrder:
    artikel: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None          # t, dt, kg, Stk
    lieferdatum: Optional[str] = None      # ISO YYYY-MM-DD
    lieferort: Optional[str] = None
    anmerkung: Optional[str] = None
    konfidenz: float = 0.0                 # 0.0–1.0
    fehlende_felder: list[str] = field(default_factory=list)


@dataclass
class ConversationState:
    phone: str
    kunden_nr: Optional[str] = None
    kunden_name: Optional[str] = None
    turn: int = 0
    partial_order: Optional[ExtractedOrder] = None
    last_question: Optional[str] = None    # Welches Feld wurde zuletzt erfragt
    history: list[dict] = field(default_factory=list)  # [{role, content}]


# ─── System-Prompt ─────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """Du bist der digitale Bestellassistent eines deutschen Landhandels-ERP.
Du empfängst WhatsApp-Nachrichten von Landwirten und extrahierst daraus Bestellinformationen.

AUFGABE: Antworte IMMER mit validem JSON — kein Freitext, keine Markdown-Blöcke.

JSON-Schema:
{
  "artikel": "Artikelname oder null",
  "menge": Zahl oder null,
  "einheit": "t" | "dt" | "kg" | "Stk" | null,
  "lieferdatum": "YYYY-MM-DD" oder null,
  "lieferort": "Adresse/Hof-Name oder null",
  "anmerkung": "Besonderheiten oder null",
  "konfidenz": 0.0–1.0,
  "fehlende_felder": ["menge", "lieferdatum"],
  "klartext_antwort": "Was du dem Kunden antworten würdest (Deutsch, Du-Form, max 2 Sätze)"
}

REGELN:
- Wenn Artikel und Menge vorhanden (konfidenz >= 0.8): fehlende_felder leer, klare Bestätigung.
- Wenn wichtige Felder fehlen: fehlende_felder mit max. 1-2 konkreten Rückfragen befüllen.
- Einheiten normieren: "Tonnen" → "t", "Doppelzentner/Dezitonnen/dt" → "dt", "Kilo" → "kg".
- Datum: "nächste Woche" → konkretes ISO-Datum ableiten. Heute ist {heute}.
- Typische Agrar-Artikel: Winterweizen, Raps, Gerste, Mais, Triticale, Dünger, Saatgut, PSM.
- Menge: deutsche Zahlen erkennen ("zwanzig" → 20, "achtzig" → 80).
- Bei klartext_antwort: kurz, freundlich, auf Deutsch. Keine Emojis außer am Schluss.
"""


def _get_conv(tenant_id: str, phone: str) -> ConversationState:
    tenant_store = _CONV_STORE.setdefault(tenant_id, {})
    if phone not in tenant_store:
        tenant_store[phone] = ConversationState(phone=phone)
    return tenant_store[phone]


def _reset_conv(tenant_id: str, phone: str) -> None:
    _CONV_STORE.get(tenant_id, {}).pop(phone, None)


def _find_customer_by_phone(tenant_id: str, phone: str) -> tuple[Optional[str], Optional[str]]:
    """
    In Produktion: DB-Lookup in domain_crm.customers nach phone_number.
    Im Simulator: Demo-Mapping.
    Gibt (kunden_nr, name) zurück.
    """
    _DEMO_PHONES = {
        "+4917612345678": ("K-10001", "Landwirt Müller"),
        "+4915123456789": ("K-10002", "Betrieb Schmidt GbR"),
        "+4916987654321": ("K-10003", "Agrar Hoffmann KG"),
    }
    return _DEMO_PHONES.get(phone, (None, None))


def _call_llm(tenant_id: str, messages: list[dict], heute: str) -> Optional[str]:
    """Ruft das LLM-Gateway auf. Gibt JSON-String zurück oder None bei Fehler."""
    try:
        from app.services.llm_gateway import LLMGateway
        # LLMGateway benötigt eine DB-Session für Tenant-Settings; ohne DB nutzen wir
        # direkt den anthropic-Client falls ANTHROPIC_API_KEY gesetzt ist.
        import os
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return None
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        system = _SYSTEM_PROMPT.replace("{heute}", heute)
        response = client.messages.create(
            model=os.environ.get("WHATSAPP_AGENT_MODEL", "claude-haiku-4-5-20251001"),
            max_tokens=512,
            system=system,
            messages=messages,
        )
        return response.content[0].text if response.content else None
    except Exception as exc:
        logger.warning("LLM-Aufruf fehlgeschlagen: %s", exc)
        return None


def _fallback_extract(text: str) -> ExtractedOrder:
    """
    Einfacher regex-Fallback wenn LLM nicht verfügbar.
    Erkennt Zahlen + bekannte Artikel-Stems.
    """
    order = ExtractedOrder()
    artikel_map = {
        r"weizen": "Winterweizen",
        r"raps": "Raps",
        r"gerste": "Wintergerste",
        r"mais": "Körnermais",
        r"triticale": "Triticale",
        r"hafer": "Hafer",
        r"d.nger|harnstoff|kalk": "Düngemittel",
        r"saatgut": "Saatgut",
    }
    t = text.lower()
    for pat, name in artikel_map.items():
        if re.search(pat, t):
            order.artikel = name
            break

    # Menge
    m = re.search(r"(\d+[\.,]?\d*)\s*(t\b|tonnen?|dt\b|doppelzentner|kg\b|kilo)", t)
    if m:
        order.menge = float(m.group(1).replace(",", "."))
        raw_einheit = m.group(2).lower()
        if raw_einheit.startswith("t"):
            order.einheit = "t"
        elif raw_einheit.startswith("d"):
            order.einheit = "dt"
        else:
            order.einheit = "kg"

    fehlend = []
    if not order.artikel:
        fehlend.append("artikel")
    if not order.menge:
        fehlend.append("menge")
    order.fehlende_felder = fehlend
    order.konfidenz = 0.7 if (order.artikel and order.menge) else 0.2
    return order


def _parse_llm_response(raw: str) -> Optional[ExtractedOrder]:
    """Parst JSON aus LLM-Antwort in ExtractedOrder."""
    try:
        # Entferne eventuelle Markdown-Blöcke
        clean = re.sub(r"```json|```", "", raw).strip()
        data = json.loads(clean)
        return ExtractedOrder(
            artikel=data.get("artikel"),
            menge=float(data["menge"]) if data.get("menge") is not None else None,
            einheit=data.get("einheit"),
            lieferdatum=data.get("lieferdatum"),
            lieferort=data.get("lieferort"),
            anmerkung=data.get("anmerkung"),
            konfidenz=float(data.get("konfidenz", 0.5)),
            fehlende_felder=data.get("fehlende_felder", []),
        ), data.get("klartext_antwort", "")
    except Exception:
        return None, None


def _create_order_in_erp(
    tenant_id: str,
    kunden_nr: Optional[str],
    kunden_name: Optional[str],
    order: ExtractedOrder,
    phone: str,
) -> dict:
    """
    Legt den Auftrag im ERP an. In Produktion: POST /api/v1/sales/orders.
    Im Simulator: In-Memory-Log.
    """
    order_id = f"WA-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    entry = {
        "id": order_id,
        "tenant_id": tenant_id,
        "kunden_nr": kunden_nr or "UNBEKANNT",
        "kunden_name": kunden_name or phone,
        "artikel": order.artikel,
        "menge": order.menge,
        "einheit": order.einheit or "t",
        "lieferdatum": order.lieferdatum,
        "lieferort": order.lieferort,
        "anmerkung": order.anmerkung,
        "quelle": "whatsapp",
        "phone": phone,
        "erstellt_am": datetime.now(timezone.utc).isoformat(),
        "status": "OFFEN",
    }
    _ORDER_LOG.setdefault(tenant_id, []).append(entry)
    logger.info("WhatsApp-Auftrag angelegt: %s", order_id)
    return entry


def _format_confirmation(order_entry: dict, kunden_name: Optional[str]) -> str:
    name_part = f" {kunden_name}" if kunden_name else ""
    datum = f", Lieferung {order_entry['lieferdatum']}" if order_entry.get("lieferdatum") else ""
    ort = f" nach {order_entry['lieferort']}" if order_entry.get("lieferort") else ""
    return (
        f"👍 Auftrag {order_entry['id']} angelegt{name_part}: "
        f"{order_entry['menge']} {order_entry['einheit']} {order_entry['artikel']}"
        f"{datum}{ort}. "
        f"Lieferschein und Rechnung stehen nach Lieferung im Portal bereit."
    )


# ─── Haupt-Einstiegspunkt ──────────────────────────────────────────────────

def process_whatsapp_message(
    tenant_id: str,
    phone: str,
    text: str,
) -> str:
    """
    Verarbeitet eine eingehende WhatsApp-Textnachricht.
    Gibt den Antwort-Text zurück (wird an den Absender gesendet).
    """
    conv = _get_conv(tenant_id, phone)

    # Kundenzuordnung (einmalig)
    if not conv.kunden_nr:
        kunden_nr, kunden_name = _find_customer_by_phone(tenant_id, phone)
        conv.kunden_nr = kunden_nr
        conv.kunden_name = kunden_name

    conv.turn += 1
    conv.history.append({"role": "user", "content": text})

    heute = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # ── Unbekannter Kunde ────────────────────────────────────────────────────
    if not conv.kunden_nr and conv.turn == 1:
        return (
            "Hallo! Ich bin der Bestellassistent Ihres Landhandels. "
            "Leider konnte ich Ihre Nummer nicht zuordnen. "
            "Bitte nennen Sie Ihre Kundennummer oder rufen Sie uns an: 0800-VALEO."
        )

    # ── LLM-Extraktion ──────────────────────────────────────────────────────
    llm_raw = _call_llm(tenant_id, conv.history, heute)

    if llm_raw:
        result = _parse_llm_response(llm_raw)
        if result and isinstance(result, tuple):
            order, klartext = result
        else:
            order, klartext = None, None
    else:
        order, klartext = None, None

    # Fallback wenn LLM nicht verfügbar
    if order is None:
        order = _fallback_extract(text)
        klartext = None

    # Partiellen Stand aus vorheriger Runde zusammenführen
    if conv.partial_order:
        prev = conv.partial_order
        if not order.artikel and prev.artikel:
            order.artikel = prev.artikel
        if not order.menge and prev.menge:
            order.menge = prev.menge
            order.einheit = order.einheit or prev.einheit
        if not order.lieferdatum and prev.lieferdatum:
            order.lieferdatum = prev.lieferdatum
        if not order.lieferort and prev.lieferort:
            order.lieferort = prev.lieferort
        # Konfidenz neu bewerten
        if order.artikel and order.menge:
            order.konfidenz = max(order.konfidenz, 0.8)
            order.fehlende_felder = [
                f for f in order.fehlende_felder if f not in ("artikel", "menge")
            ]

    conv.partial_order = order

    # ── Vollständig → Auftrag anlegen ──────────────────────────────────────
    if order.konfidenz >= 0.8 and order.artikel and order.menge and not order.fehlende_felder:
        entry = _create_order_in_erp(tenant_id, conv.kunden_nr, conv.kunden_name, order, phone)
        reply = _format_confirmation(entry, conv.kunden_name)
        _reset_conv(tenant_id, phone)
        conv.history.append({"role": "assistant", "content": reply})
        return reply

    # ── Rückfrage ──────────────────────────────────────────────────────────
    if klartext:
        reply = klartext
    else:
        fehlend = order.fehlende_felder or ["Menge und Artikel"]
        felder_str = " und ".join(fehlend[:2])
        reply = (
            f"Danke! Ich brauche noch folgende Angabe(n) um die Bestellung abzuschließen: "
            f"{felder_str}. Bitte ergänzen Sie kurz."
        )
    conv.history.append({"role": "assistant", "content": reply})
    return reply


# ─── Order-Log Abfrage (Simulator) ─────────────────────────────────────────

def get_order_log(tenant_id: str) -> list[dict]:
    return list(reversed(_ORDER_LOG.get(tenant_id, [])))


def get_conversation_state(tenant_id: str, phone: str) -> Optional[dict]:
    conv = _CONV_STORE.get(tenant_id, {}).get(phone)
    if not conv:
        return None
    return {
        "phone": conv.phone,
        "kunden_nr": conv.kunden_nr,
        "kunden_name": conv.kunden_name,
        "turn": conv.turn,
        "partial_order": {
            "artikel": conv.partial_order.artikel,
            "menge": conv.partial_order.menge,
            "einheit": conv.partial_order.einheit,
            "lieferdatum": conv.partial_order.lieferdatum,
            "lieferort": conv.partial_order.lieferort,
            "konfidenz": conv.partial_order.konfidenz,
            "fehlende_felder": conv.partial_order.fehlende_felder,
        } if conv.partial_order else None,
        "history": conv.history,
    }
