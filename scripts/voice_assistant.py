# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import time
import queue
import json
import re
import threading
import atexit
import argparse
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path

# Optional audio deps (fallback auf Textmodus)
try:
    import sounddevice as sd
    import numpy as np
except Exception:
    sd = None
    np = None

try:
    import webrtcvad  # type: ignore
except Exception:
    webrtcvad = None  # type: ignore

try:
    from faster_whisper import WhisperModel  # type: ignore
except Exception:
    WhisperModel = None  # type: ignore

try:
    import pyttsx3  # type: ignore
except Exception:
    pyttsx3 = None  # type: ignore

import requests

PID_FILE = Path("output/runtime/voice_assistant.pid")
PID_FILE.parent.mkdir(parents=True, exist_ok=True)

@dataclass
class VoiceConfig:
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-oss-20b-small")
    stt_model: str = os.getenv("VOICE_STT_MODEL", "small")
    samplerate: int = int(os.getenv("VOICE_SR", "16000"))
    vad_aggr: int = int(os.getenv("VOICE_VAD", "2"))  # 0-3
    silence_ms: int = int(os.getenv("VOICE_SILENCE_MS", "800"))
    max_utt_ms: int = int(os.getenv("VOICE_MAX_UTT_MS", "15000"))
    language: str = os.getenv("VOICE_LANG", "de")
    device_in: Optional[str] = os.getenv("VOICE_MIC_DEVICE")
    device_out: Optional[str] = os.getenv("VOICE_SPK_DEVICE")

class LocalTTS:
    def __init__(self) -> None:
        self.engine = None
        if pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                rate = self.engine.getProperty('rate')
                self.engine.setProperty('rate', int(rate * 0.95))
            except Exception:
                self.engine = None

    def speak(self, text: str) -> None:
        if not text:
            return
        if self.engine is not None:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                return
            except Exception:
                pass
        print(f"[TTS] {text}")

class LocalSTT:
    def __init__(self, cfg: VoiceConfig) -> None:
        self.model = None
        if WhisperModel is not None:
            try:
                self.model = WhisperModel(cfg.stt_model, compute_type="int8")
            except Exception:
                self.model = None

    def transcribe(self, audio: 'np.ndarray', sr: int, language: str = "de") -> str:
        if self.model is None or np is None:
            return ""
        segments, _ = self.model.transcribe(audio, language=language)
        return " ".join(seg.text.strip() for seg in segments if seg.text)

class OllamaChat:
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip('/')
        self.model = model

    def chat(self, user_text: str) -> str:
        try:
            url = f"{self.base_url}/api/chat"
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "Du bist ein hilfreicher deutscher Assistent."},
                    {"role": "user", "content": user_text},
                ],
                "stream": False,
                "options": {"temperature": 0.3, "num_ctx": 1536, "num_predict": 384}
            }
            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")
        except Exception as e:
            return f"[LLM-Fehler] {e}"

# --------------------
# Intent Router & Skills
# --------------------

class DeliveryNoteSkill:
    def maybe_handle(self, text: str) -> Optional[Dict[str, Any]]:
        t = text.strip().lower()
        if not (t.startswith("erstelle") and "lieferschein" in t):
            return None
        m_cust = re.search(r"für\s+(?:landwirt\s+)?(?P<customer>[a-zäöüß\s.-]+?)\s+(?:über|für)\s+die\s+lieferung", t)
        customer = m_cust.group("customer").title().strip() if m_cust else None
        m_item = re.search(r"lieferung\s+von\s+(?P<qty>[\d,.]+)\s*(?P<unit>\w+)\s+(?P<prod>[a-zäöüß\s.-]+?)(?:,|\s)", t)
        qty=None; unit=None; product=None
        if m_item:
            try: qty = float(m_item.group("qty").replace(',', '.'))
            except: qty=None
            unit = m_item.group("unit").strip()
            product = m_item.group("prod").strip().title()
        delivery_date = "morgen" if "morgen" in t else ("heute" if "heute" in t else None)
        m_place = re.search(r"(?:in\s+sein|in\s+das|nach)\s+(?P<place>[a-zäöüß\s.-]+)", t)
        place = m_place.group("place").strip().title() if m_place else None
        if not (customer and qty and unit and product):
            return {"handled": False, "reason": "unvollständig", "detected": {"customer": customer, "qty": qty, "unit": unit, "product": product, "delivery_date": delivery_date, "place": place}}
        outdir = Path("output/delivery_notes"); outdir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        data = {"id": f"LS-{ts}", "timestamp": ts, "customer_name": customer,
                "items": [{"product": product, "quantity": qty, "unit": unit}],
                "delivery_date": delivery_date or "unbekannt", "instructions": place or "", "status": "entwurf"}
        filepath = outdir / f"{data['id']}.json"
        filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        ack = f"Lieferschein-Entwurf {data['id']} für {customer} erstellt. Bitte prüfen und mit Enter buchen."
        return {"handled": True, "ack": ack, "file": str(filepath), "payload": data}

class SalesOrderSkill:
    def maybe_handle(self, text: str) -> Optional[Dict[str, Any]]:
        t=text.strip().lower()
        if not (t.startswith("erstelle") and ("auftrag" in t or "kundenauftrag" in t)):
            return None
        m_cust = re.search(r"für\s+(?P<customer>[a-zäöüß\s.-]+?)\s+(?:über|mit)\s+", t)
        customer = m_cust.group("customer").title().strip() if m_cust else None
        m_item = re.search(r"(?:über|mit)\s+(?P<qty>[\d,.]+)\s*(?P<unit>\w+)\s+(?P<prod>[a-zäöüß\s.-]+)", t)
        qty=None; unit=None; product=None
        if m_item:
            try: qty=float(m_item.group("qty").replace(',', '.'))
            except: qty=None
            unit=m_item.group("unit").strip(); product=m_item.group("prod").strip().title()
        outdir=Path("output/sales_orders"); outdir.mkdir(parents=True, exist_ok=True)
        ts=time.strftime("%Y%m%d_%H%M%S")
        if not (customer and qty and unit and product):
            return {"handled": False, "reason": "unvollständig"}
        data={"id":f"SO-{ts}","timestamp":ts,"customer_name":customer,
              "items":[{"product":product,"quantity":qty,"unit":unit}],"status":"entwurf"}
        fp = outdir/f"{data['id']}.json"; fp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        return {"handled": True, "ack": f"Auftrags-Entwurf {data['id']} erstellt. Bitte prüfen und Enter zum Buchen.", "file": str(fp), "payload": data}

class InvoiceSkill:
    def maybe_handle(self, text: str) -> Optional[Dict[str, Any]]:
        t=text.strip().lower()
        if not (t.startswith("erstelle") and ("rechnung" in t)):
            return None
        m_cust = re.search(r"für\s+(?P<customer>[a-zäöüß\s.-]+?)\s+(?:über|mit)\s+", t)
        customer = m_cust.group("customer").title().strip() if m_cust else None
        m_item = re.search(r"(?:über|mit)\s+(?P<qty>[\d,.]+)\s*(?P<unit>\w+)\s+(?P<prod>[a-zäöüß\s.-]+)\s*(?:zum\s+preis\s+von\s+(?P<price>[\d,.]+))?", t)
        qty=None; unit=None; product=None; price=None
        if m_item:
            try: qty=float(m_item.group("qty").replace(',','.'))
            except: qty=None
            unit=m_item.group("unit").strip(); product=m_item.group("prod").strip().title()
            price_raw=m_item.group("price")
            if price_raw:
                try: price=float(price_raw.replace(',','.'))
                except: price=None
        outdir=Path("output/invoices"); outdir.mkdir(parents=True, exist_ok=True)
        ts=time.strftime("%Y%m%d_%H%M%S")
        if not (customer and qty and unit and product):
            return {"handled": False, "reason": "unvollständig"}
        data={"id":f"INV-{ts}","timestamp":ts,"customer_name":customer,
              "items":[{"product":product,"quantity":qty,"unit":unit,"price":price}],
              "status":"entwurf"}
        fp = outdir/f"{data['id']}.json"; fp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        return {"handled": True, "ack": f"Rechnungs-Entwurf {data['id']} erstellt. Bitte prüfen und Enter zum Buchen.", "file": str(fp), "payload": data}

class PurchaseOrderSkill:
    def maybe_handle(self, text: str) -> Optional[Dict[str, Any]]:
        t=text.strip().lower()
        if not (t.startswith("erstelle") and ("bestellung" in t or "einkauf" in t)):
            return None
        m_sup = re.search(r"bei\s+(?P<supplier>[a-zäöüß\s.-]+?)\s+(?:über|mit)\s+", t)
        supplier = m_sup.group("supplier").title().strip() if m_sup else None
        m_item = re.search(r"(?:über|mit)\s+(?P<qty>[\d,.]+)\s*(?P<unit>\w+)\s+(?P<prod>[a-zäöüß\s.-]+)", t)
        qty=None; unit=None; product=None
        if m_item:
            try: qty=float(m_item.group("qty").replace(',','.'))
            except: qty=None
            unit=m_item.group("unit").strip(); product=m_item.group("prod").strip().title()
        outdir=Path("output/purchase_orders"); outdir.mkdir(parents=True, exist_ok=True)
        ts=time.strftime("%Y%m%d_%H%M%S")
        if not (supplier and qty and unit and product):
            return {"handled": False, "reason": "unvollständig"}
        data={"id":f"PO-{ts}","timestamp":ts,"supplier_name":supplier,
              "items":[{"product":product,"quantity":qty,"unit":unit}],"status":"entwurf"}
        fp = outdir/f"{data['id']}.json"; fp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        return {"handled": True, "ack": f"Bestell-Entwurf {data['id']} erstellt. Bitte prüfen und Enter zum Buchen.", "file": str(fp), "payload": data}

class LeadSkill:
    def maybe_handle(self, text: str) -> Optional[Dict[str, Any]]:
        t=text.strip().lower()
        if not (t.startswith("lege") or t.startswith("erstelle")):
            return None
        if not ("lead" in t or "kontakt" in t):
            return None
        m_firma = re.search(r"firma\s+(?P<company>[a-zäöüß\s.-]+)", t)
        m_name = re.search(r"ansprechpartner\s+(?P<name>[a-zäöüß\s.-]+)", t)
        m_mail = re.search(r"(?:mail|email|e-mail)\s+(?P<email>\S+@\S+)", t)
        company = m_firma.group("company").title().strip() if m_firma else None
        name = m_name.group("name").title().strip() if m_name else None
        email = m_mail.group("email").strip() if m_mail else None
        outdir=Path("output/leads"); outdir.mkdir(parents=True, exist_ok=True)
        ts=time.strftime("%Y%m%d_%H%M%S");
        data={"id":f"LEAD-{ts}","timestamp":ts,"company":company,"contact_name":name,"email":email,"status":"entwurf"}
        fp = outdir/f"{data['id']}.json"; fp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        return {"handled": True, "ack": f"Lead-Entwurf {data['id']} erstellt. Bitte prüfen und Enter zum Buchen.", "file": str(fp), "payload": data}

class ActivitySkill:
    def maybe_handle(self, text: str) -> Optional[Dict[str, Any]]:
        t=text.strip().lower()
        if not ("termin" in t or "anruf" in t or "meeting" in t or "besuch" in t):
            return None
        m_cust = re.search(r"mit\s+(?P<who>[a-zäöüß\s.-]+)\s+am\s+(?P<date>\d{1,2}\.\d{1,2}\.\d{2,4})", t)
        who = m_cust.group("who").title().strip() if m_cust else None
        date = m_cust.group("date") if m_cust else None
        outdir=Path("output/activities"); outdir.mkdir(parents=True, exist_ok=True)
        ts=time.strftime("%Y%m%d_%H%M%S"); data={"id":f"ACT-{ts}","timestamp":ts,"who":who,"date":date,"type":"termin","status":"entwurf"}
        fp = outdir/f"{data['id']}.json"; fp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        return {"handled": True, "ack": f"Termin-Entwurf {data['id']} erstellt. Bitte prüfen und Enter zum Buchen.", "file": str(fp), "payload": data}

class DunningSkill:
    def maybe_handle(self, text: str) -> Optional[Dict[str, Any]]:
        t=text.strip().lower()
        if not ("mahnung" in t or "mahne" in t):
            return None
        m_inv = re.search(r"rechnung\s+(?P<num>[a-z0-9-./]+)", t)
        num = m_inv.group("num") if m_inv else None
        outdir=Path("output/dunning"); outdir.mkdir(parents=True, exist_ok=True)
        ts=time.strftime("%Y%m%d_%H%M%S"); data={"id":f"DN-{ts}","timestamp":ts,"invoice_number":num,"status":"entwurf"}
        fp = outdir/f"{data['id']}.json"; fp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        return {"handled": True, "ack": f"Mahnung-Entwurf {data['id']} erstellt. Bitte prüfen und Enter zum Buchen.", "file": str(fp), "payload": data}

class PaymentMatchSkill:
    def maybe_handle(self, text: str) -> Optional[Dict[str, Any]]:
        t=text.strip().lower()
        if not ("zahlung" in t and ("zuordnen" in t or "buchen" in t)):
            return None
        m_amt = re.search(r"betrag\s+(?P<amt>[\d,.]+)", t); amt=None
        if m_amt:
            try: amt=float(m_amt.group("amt").replace(',','.'))
            except: amt=None
        m_ref = re.search(r"referenz\s+(?P<ref>.+)$", t)
        ref = m_ref.group("ref").strip() if m_ref else None
        outdir=Path("output/payments"); outdir.mkdir(parents=True, exist_ok=True)
        ts=time.strftime("%Y%m%d_%H%M%S"); data={"id":f"PAY-{ts}","timestamp":ts,"amount":amt,"reference":ref,"status":"entwurf"}
        fp = outdir/f"{data['id']}.json"; fp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        return {"handled": True, "ack": f"Zahlungs-Entwurf {data['id']} erstellt. Bitte prüfen und Enter zum Buchen.", "file": str(fp), "payload": data}

class StockInquirySkill:
    def maybe_handle(self, text: str) -> Optional[Dict[str, Any]]:
        t=text.strip().lower()
        if not ("bestand" in t and ("wie viel" in t or "wieviel" in t or "zeige" in t)):
            return None
        m_prod = re.search(r"(?:von|für)\s+(?P<prod>[a-zäöüß\s.-]+)$", t)
        prod = m_prod.group("prod").strip().title() if m_prod else None
        outdir=Path("output/stock_queries"); outdir.mkdir(parents=True, exist_ok=True)
        ts=time.strftime("%Y%m%d_%H%M%S"); data={"id":f"STOCKQ-{ts}","timestamp":ts,"product":prod}
        fp = outdir/f"{data['id']}.json"; fp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        return {"handled": True, "ack": f"Bestandsabfrage {data['id']} für {prod} erfasst.", "file": str(fp), "payload": data}

class RAGQuerySkill:
    def maybe_handle(self, text: str) -> Optional[Dict[str, Any]]:
        t=text.strip().lower()
        if not (t.startswith("recherchiere") or t.startswith("rag") or t.startswith("suche im code")):
            return None
        q = re.sub(r"^(recherchiere|rag|suche im code)\s*", "", t).strip()
        outdir=Path("output/rag_queries"); outdir.mkdir(parents=True, exist_ok=True)
        ts=time.strftime("%Y%m%d_%H%M%S")
        hits: List[Dict[str, Any]]=[]
        try:
            import sys
            sys.path.insert(0, str(Path('.').resolve()))
            from linkup_mcp.memory.rag_manager import RAGMemoryManager  # type: ignore
            m = RAGMemoryManager()
            m.build_index(["linkup_mcp"])  # gezielter Ordner
            hits = m.query(q or "", top_k=5)
        except Exception:
            pass
        data={"id":f"RAGQ-{ts}","timestamp":ts,"query":q,"hits":hits}
        fp = outdir/f"{data['id']}.json"; fp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        ack = f"RAG-Abfrage {data['id']} gespeichert. {len(hits)} Treffer."
        return {"handled": True, "ack": ack, "file": str(fp), "payload": data}

class SystemSkill:
    def maybe_handle(self, text: str) -> Optional[Dict[str, Any]]:
        t=text.strip().lower()
        if "openwebui" in t or "web ui" in t:
            return {"handled": True, "ack": "OpenWebUI bitte mit dem vordefinierten Befehl starten (Port 8501)."}
        return None

class IntentRouter:
    def __init__(self) -> None:
        self.skills = [
            DeliveryNoteSkill(),
            SalesOrderSkill(),
            InvoiceSkill(),
            PurchaseOrderSkill(),
            LeadSkill(),
            ActivitySkill(),
            DunningSkill(),
            PaymentMatchSkill(),
            StockInquirySkill(),
            RAGQuerySkill(),
            SystemSkill(),
        ]
    def route(self, text: str) -> Optional[Dict[str, Any]]:
        for s in self.skills:
            res = s.maybe_handle(text)
            if res:
                return res
        return None

# --------------------
# Recorder, Review & Main
# --------------------

def review_and_maybe_book(file_path: str, tts: LocalTTS) -> bool:
    try:
        p = Path(file_path)
        data = json.loads(p.read_text(encoding="utf-8"))
        print("\n===== Entwurf zur Prüfung =====")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print("===== Ende Entwurf =====\n")
        tts.speak("Bitte prüfen. Drücken Sie Enter zum Buchen oder 'n' zum Abbrechen.")
        ans = input("Enter = Buchen, 'n' = Abbrechen > ").strip().lower()
        if ans == 'n':
            tts.speak("Abgebrochen. Entwurf wurde gespeichert.")
            return False
        # buchen
        data['status'] = 'gebucht'
        data['booked_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tts.speak("Gebucht.")
        return True
    except Exception as e:
        print(f"[Review-Fehler] {e}")
        return False

class Recorder:
    def __init__(self, cfg: VoiceConfig) -> None:
        self.cfg = cfg
        self._q: queue.Queue = queue.Queue()
        self._stream = None
        self._stop = threading.Event()
        self._vad = webrtcvad.Vad(cfg.vad_aggr) if webrtcvad is not None else None

    def _callback(self, indata, frames, time_info, status):  # type: ignore
        if status:
            pass
        self._q.put(indata.copy())
        return None

    def start(self) -> None:
        if sd is None or np is None:
            raise RuntimeError("Audio-Bibliotheken nicht verfügbar (sounddevice/numpy)")
        self._stop.clear()
        self._stream = sd.InputStream(
            samplerate=self.cfg.samplerate,
            channels=1,
            dtype='int16',
            callback=self._callback,
            device=self.cfg.device_in
        )
        self._stream.start()

    def stop(self) -> None:
        self._stop.set()
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def listen_once(self) -> Optional['np.ndarray']:
        if sd is None or np is None:
            return None
        sr = self.cfg.samplerate
        frame_ms = 30
        frame_len = int(sr * frame_ms / 1000)
        silence_needed = int(self.cfg.silence_ms / frame_ms)
        max_frames = int(self.cfg.max_utt_ms / frame_ms)

        voiced_started = False
        silence_count = 0
        frames: List['np.ndarray'] = []
        start_t = time.time()
        while True:
            try:
                chunk = self._q.get(timeout=2.0)
            except queue.Empty:
                if not frames:
                    return None
                else:
                    break
            data = chunk.reshape(-1)
            for i in range(0, len(data), frame_len):
                f = data[i:i+frame_len]
                if len(f) < frame_len:
                    continue
                is_speech = True
                if self._vad is not None:
                    try:
                        is_speech = self._vad.is_speech(f.tobytes(), sr)
                    except Exception:
                        is_speech = True
                frames.append(f.copy())
                if is_speech:
                    voiced_started = True
                    silence_count = 0
                else:
                    if voiced_started:
                        silence_count += 1
                if voiced_started and silence_count >= silence_needed:
                    return np.concatenate(frames, axis=0)
                if len(frames) >= max_frames:
                    return np.concatenate(frames, axis=0)
            if time.time() - start_t > (self.cfg.max_utt_ms / 1000.0 + 5):
                break
        if frames:
            return np.concatenate(frames, axis=0)
        return None

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lokaler Sprachassistent für VALEO NeuroERP")
    parser.add_argument("--auto", action="store_true", help="Automatisch lauschen (kein Enter nötig, nur Entwürfe – keine Buchung)")
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    cfg = VoiceConfig()
    if args.auto:
        try:
            PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
        except Exception:
            pass
        atexit.register(lambda: PID_FILE.exists() and PID_FILE.unlink(missing_ok=True))

    print("[VOICE] Lokaler Sprachassistent – Enter zum Starten, Strg+C zum Beenden.")
    print("[VOICE] LLM:", cfg.llm_model, "@", cfg.llm_base_url)
    print("[VOICE] STT:", cfg.stt_model, "Samplerate:", cfg.samplerate)

    tts = LocalTTS()
    stt = LocalSTT(cfg)
    rec = Recorder(cfg)
    chat = OllamaChat(cfg.llm_base_url, cfg.llm_model)
    router = IntentRouter()

    if sd is None or np is None:
        print("[WARN] sounddevice/numpy nicht verfügbar – Textmodus aktiv.")
        while True:
            try:
                text = input("[Du] > ").strip()
                if not text:
                    continue
                intent = router.route(text)
                if intent and intent.get("handled"):
                    fp = intent.get("file")
                    if fp and not args.auto:
                        print(intent.get("ack", "Entwurf erstellt."))
                        booked = review_and_maybe_book(fp, tts)
                        if booked:
                            print("[System] Buchung abgeschlossen.")
                        else:
                            print("[System] Buchung abgebrochen. Entwurf bleibt erhalten.")
                        continue
                    ack = intent.get("ack", "Auftrag ausgeführt.")
                    print(f"[System] {ack}")
                    tts.speak(ack)
                    continue
                resp = chat.chat(text)
                print(f"[Assistent] {resp}")
                tts.speak(resp)
            except KeyboardInterrupt:
                break
        return

    try:
        rec.start()
        if args.auto:
            print("[VOICE] Auto-Modus aktiv: kontinuierliches Zuhören. Nur Entwürfe, keine Buchung.")
            while True:
                audio = rec.listen_once()
                if audio is None or audio.size == 0:
                    continue
                audio_f32 = (audio.astype('float32') / 32768.0)
                text = stt.transcribe(audio_f32, cfg.samplerate, language=cfg.language)
                if not text:
                    continue
                print(f"[Du] {text}")
                intent = router.route(text)
                if intent and intent.get("handled"):
                    ack = intent.get("ack", "Entwurf erstellt.")
                    print(f"[System] {ack}")
                    tts.speak(ack)
                    continue
                resp = chat.chat(text)
                print(f"[Assistent] {resp}")
                tts.speak(resp)
        else:
            while True:
                input("[VOICE] Drücke Enter und spreche (VAD stoppt bei Stille)...")
                print("[VOICE] Aufnahme…")
                audio = rec.listen_once()
                if audio is None or audio.size == 0:
                    print("[VOICE] Nichts aufgenommen.")
                    continue
                audio_f32 = (audio.astype('float32') / 32768.0)
                print("[VOICE] Transkribiere…")
                text = stt.transcribe(audio_f32, cfg.samplerate, language=cfg.language)
                print(f"[Du] {text}")
                if not text:
                    continue
                intent = router.route(text)
                if intent and intent.get("handled"):
                    fp = intent.get("file")
                    if fp:
                        print(intent.get("ack", "Entwurf erstellt."))
                        booked = review_and_maybe_book(fp, tts)
                        if booked:
                            print("[System] Buchung abgeschlossen.")
                        else:
                            print("[System] Buchung abgebrochen. Entwurf bleibt erhalten.")
                        continue
                    print("[VOICE] Frage LLM…")
                    resp = chat.chat(text)
                    print(f"[Assistent] {resp}")
                    tts.speak(resp)
                    continue
                print("[VOICE] Frage LLM…")
                resp = chat.chat(text)
                print(f"[Assistent] {resp}")
                tts.speak(resp)
    except KeyboardInterrupt:
        pass
    finally:
        rec.stop()
        if args.auto:
            try:
                PID_FILE.unlink(missing_ok=True)
            except Exception:
                pass

if __name__ == "__main__":
    main()
