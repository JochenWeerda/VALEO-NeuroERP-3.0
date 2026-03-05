# GoBD: Belegnummer bei abgebrochener Beleg-Eingabe

## Fragestellung

Wenn eine Beleg-Eingabe (z. B. neue Buchung, Lieferschein, Rechnung) vom Anwender **abgebrochen** wird („Abbrechen“, „Verwerfen“, Schließen ohne Speichern): Was passiert mit der **Beleg-Nummer**, falls sie bereits vergeben wurde? Soll sie in den Nummernkreis „zurück“, und ist das GoBD-konform?

## GoBD-Grundsätze (Auszug)

- **Vollständigkeit (§146 AO):** Lückenlose, nachvollziehbare Nummerierung; Lücken müssen erklärbar sein.
- **Unveränderbarkeit:** Kein nachträgliches Löschen/Verschleiern von Belegen.
- **Nachvollziehbarkeit:** Jede vergebene Nummer muss im System nachvollziehbar sein (ob genutzt oder verworfen).

## Empfohlene Vorgehensweise

### 1. Belegnummer erst beim Speichern vergeben (empfohlen)

- Die **nächste Belegnummer** wird **nur beim tatsächlichen Speichern** des Belegs vom Server vergeben (z. B. in `POST /api/v1/...` oder im Nummernkreis-Service).
- Beim **Abbruch** wurde noch **keine** Nummer verbraucht → es gibt **keine Lücke** und **keinen Pool-Rücklauf**.
- **GoBD:** Unkritisch, da keine Lücken entstehen und keine Rückgabe-Logik nötig ist.

**Umsetzung im System:**

- Nummernkreis-API (z. B. `POST /api/numbering/next` oder domain-spezifisch) **nur beim Erzeugen des persistierten Belegs** aufrufen, nicht beim Öffnen der Maske.
- In der Erfassungsmaske: Platzhalter „wird beim Speichern vergeben“ oder vorläufige Anzeige „–“ bis zum ersten Speichern.

### 2. Belegnummer beim Öffnen reservieren („Vorschau“)

- Wenn fachlich gewünscht, kann die **nächste Nummer beim Öffnen** der Erfassung angefordert werden (z. B. für Anzeige „Entwurf Nr. …“).
- Wenn der Anwender **abbrich**t:
  - **Option A – Lücke belassen:** Die reservierte Nummer wird **nicht** wieder freigegeben. Es entsteht eine **Lücke** im Nummernkreis. GoBD-konform, wenn:
    - Lücken in der **Belegnummern-Kontrolle** (`/api/gobd/belegnummern`) erkannt und ggf. in der Verfahrensdokumentation als „Entwürfe verworfen“ dokumentiert werden.
  - **Option B – Zurück in den Pool:** Die Nummer wird wieder freigegeben und kann für den **nächsten** Beleg genutzt werden. GoBD-konform nur dann, wenn:
    - Der **Verzicht** auf die Nummer („Entwurf verworfen“, kein buchhalterischer Effekt) **protokolliert** wird (z. B. Audit-Log: „Belegnummer XY zurückgegeben, Entwurf nicht gespeichert“).
    - Die **Wiederverwendung** derselben Nummer für einen **anderen** Beleg nachvollziehbar ist (kein doppelter buchhalterischer Beleg unter derselben Nummer).

**Empfehlung:** Option A (Lücke belassen) ist einfacher und in der Praxis oft ausreichend; Option B erfordert saubere Protokollierung und ggf. Anpassung der Nummernkreis-Logik („return“/Storno der Reservierung).

### 3. Keine Wiederverwendung ohne Dokumentation

- Eine **bereits für einen gespeicherten Beleg** vergebene Nummer darf **nicht** „zurück in den Pool“ und für einen anderen Beleg wiederverwendet werden (Storno-Belege erhalten eigene Nummer/Verweis).
- **Storno:** Eigenen Beleg (Stornobeleg) mit neuer Nummer erfassen, Verweis auf ursprünglichen Beleg (GoBD-konform).

## Zusammenfassung

| Szenario | Belegnummer-Vergabe | Bei Abbruch | GoBD |
|----------|----------------------|------------|------|
| **Empfohlen** | Nur beim Speichern | Keine Nummer vergeben → nichts zurückzugeben | ✅ Unkritisch |
| Reservierung beim Öffnen, Abbruch | Nummer war reserviert | Lücke belassen ODER zurückgeben + protokollieren | ✅ Wenn Lücken erklärt bzw. Rückgabe protokolliert wird |
| Reservierte Nummer zurückgeben ohne Protokoll | – | Nicht empfohlen | ⚠️ Nachvollziehbarkeit gefährdet |

## Technische Anmerkungen (VALEO NeuroERP)

- **NumberingServicePG** (`app/services/numbering_service_pg.py`): `next_number()` erhöht den Zähler sofort; es gibt derzeit **keine** „Rückgabe“-API. Eine spätere Erweiterung (z. B. „release_number“ für reservierte, nicht gespeicherte Entwürfe) müsste mit Audit-Log und klarer Semantik umgesetzt werden.
- **Docflow** (`_allocate_doc_number`): Vergabe beim Erstellen des Dokuments; Abbruch vor Speichern verbraucht keine Nummer, wenn die Allokation erst beim finalen Create erfolgt.
- **Buchungserfassung / Journal:** Belegnummer (entry_number) sollte idealerweise **erst bei POST** (Speichern) vom Backend vergeben werden, nicht beim Öffnen der Maske.

Dieses Dokument ist Teil der GoBD-Compliance-Dokumentation (siehe `docs/GOBD-COMPLIANCE.md`).
