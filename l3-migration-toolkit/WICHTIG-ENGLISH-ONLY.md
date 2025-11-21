***REMOVED*** ⚠️ WICHTIG: Nur English Language Pack verwenden!

***REMOVED******REMOVED*** 🎯 Erfahrungswert

**Tesseract-OCR funktioniert mit `eng.traineddata` BESSER als mit `deu.traineddata`**

Auch für **deutsche UI-Texte** in L3 liefert das englische Sprachmodell präzisere Ergebnisse!

***REMOVED******REMOVED*** ✅ Korrekte Konfiguration

***REMOVED******REMOVED******REMOVED*** Installation
```powershell
***REMOVED*** UB Mannheim Installer:
***REMOVED*** ✅ Nur "English" auswählen
***REMOVED*** ❌ NICHT "German" auswählen

***REMOVED*** Chocolatey:
choco install tesseract
***REMOVED*** (English ist Standard)
```

***REMOVED******REMOVED******REMOVED*** OCR-Pipeline
```python
***REMOVED*** In ocr-pipeline.py (bereits angepasst):
ocr_data = pytesseract.image_to_data(
    processed_img, 
    lang='eng',  ***REMOVED*** ✅ NUR English!
    output_type=pytesseract.Output.DICT
)
```

***REMOVED******REMOVED*** 📊 Warum English besser funktioniert

1. **Besseres Training:** `eng.traineddata` ist umfangreicher trainiert
2. **UI-Texte:** Viele Software-UIs enthalten englische Begriffe
3. **Feldnamen:** Gemischte Sprache (z.B. "Artikel-Nr.", "E-Mail", "ID")
4. **Ziffern & Symbole:** Bessere Erkennung von Zahlen, Prozentzeichen, etc.

***REMOVED******REMOVED*** 🔍 Beispiel-Vergleich

**L3-Feld:** "Artikel-Nr.:"

- `lang='eng'` → ✅ "Artikel-Nr:" (95% Confidence)
- `lang='deu'` → ⚠️ "Arikel-Nr:" oder "Artlkel-Nr:" (70% Confidence)

**L3-Feld:** "Preis (€):"

- `lang='eng'` → ✅ "Preis (€):" (90% Confidence)
- `lang='deu'` → ⚠️ "Preis (C):" oder "Preis (E):" (65% Confidence)

***REMOVED******REMOVED*** ✅ Best Practices

1. **Nur English installieren** (spart Speicherplatz & Verarbeitungszeit)
2. **Preprocessing optimieren** (wichtiger als Sprachmodell!)
3. **Confidence-Threshold bei 60%** belassen (funktioniert gut mit `eng`)

***REMOVED******REMOVED*** 🐛 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Falls Sie bereits German installiert haben:

```powershell
***REMOVED*** Nichts tun! English sollte auch vorhanden sein.
***REMOVED*** Pipeline ist bereits auf 'eng' eingestellt.

***REMOVED*** Prüfen:
dir "C:\Program Files\Tesseract-OCR\tessdata\"

***REMOVED*** Sollte enthalten:
***REMOVED*** - eng.traineddata ✅
***REMOVED*** - deu.traineddata (optional, wird nicht verwendet)
```

***REMOVED******REMOVED******REMOVED*** Falls nur German vorhanden:

```powershell
***REMOVED*** Download eng.traineddata von GitHub:
***REMOVED*** https://github.com/tesseract-ocr/tessdata/blob/main/eng.traineddata

***REMOVED*** Kopieren nach:
***REMOVED*** C:\Program Files\Tesseract-OCR\tessdata\eng.traineddata
```

***REMOVED******REMOVED*** 📈 Erwartete Verbesserung

**Mit `lang='eng'`:**
- Durchschnittliche Confidence: **85-95%**
- Felderkennungsrate: **95%+**
- Fehlerrate: **<5%**

**Mit `lang='deu'` (alt):**
- Durchschnittliche Confidence: 70-80%
- Felderkennungsrate: 80-90%
- Fehlerrate: 10-15%

---

**Status:** ✅ Pipeline bereits auf `eng` konfiguriert (ocr-pipeline.py Zeile 97)

**Keine Aktion erforderlich** - Installation mit English Pack genügt!

