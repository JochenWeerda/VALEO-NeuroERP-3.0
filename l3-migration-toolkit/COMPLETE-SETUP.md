# L3 OCR Migration Pipeline - Vollständiges Setup

Basierend auf der offiziellen [Tesseract OCR Dokumentation](https://github.com/tesseract-ocr/tesseract).

## 📦 Schritt 1: Tesseract Installation (Windows)

### Option A: UB Mannheim Installer (Empfohlen)

1. **Download:**
   - Website: https://github.com/UB-Mannheim/tesseract/wiki
   - Datei: `tesseract-ocr-w64-setup-5.5.1.exe` (neueste Version)

2. **Installation:**
   ```powershell
   # Als Administrator ausführen
   # WICHTIG: Nur "English" Language Pack auswählen!
   # (Erfahrungswert: eng.traineddata funktioniert besser als deu.traineddata)
   ```

3. **PATH setzen:**
   ```powershell
   # PowerShell als Admin:
   $tesseractPath = "C:\Program Files\Tesseract-OCR"
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$tesseractPath", "Machine")
   ```

### Option B: Chocolatey

```powershell
# PowerShell als Admin:
choco install tesseract
# Standardmäßig wird English installiert (ausreichend!)
```

### Verifikation

```powershell
# Neue PowerShell-Session öffnen
tesseract --version
```

**Erwartete Ausgabe:**
```
tesseract 5.5.1
 leptonica-1.x.x
  libjpeg 9e : libpng 1.6.x : libtiff 4.x.x : zlib 1.2.x
```

## 📦 Schritt 2: Python Dependencies

```powershell
cd l3-migration-toolkit
pip install pytesseract pillow opencv-python numpy
```

**Verifikation:**
```python
python -c "import pytesseract, PIL, cv2, numpy; print('✅ Alle Dependencies OK')"
```

## 🧪 Schritt 3: OCR-Pipeline Test

```powershell
# Test mit vorhandenem Artikelstamm-Screenshot:
python ocr-pipeline.py screenshots/l3-masks/artikelstamm.png --debug

# Erwartete Ausgabe:
# 🔍 Analysiere: screenshots/l3-masks/artikelstamm.png
# 📊 Ergebnisse:
#    Gefundene Felder: 15+
#    Gefundene Tabs: 5+
#    Durchschn. Confidence: 85%+
```

**Output-Dateien:**
- `artikelstamm.ocr.json` - Strukturierte OCR-Ergebnisse
- `artikelstamm.debug.png` - Preprocessed Image (bei `--debug`)

## 🚀 Schritt 4: Vollautomatische Erfassung starten

```powershell
# Starte Batch-Prozess
python auto-capture-all-masks.py
```

**Workflow:**
1. Browser: http://localhost:8090/guacamole/#/client/MQBjAHBvc3RncmVzcWw
2. Script zeigt: "Bitte öffnen Sie: Artikelstamm"
3. Sie navigieren in L3 zur Maske
4. Sie drücken Enter
5. Screenshot wird erstellt (manuell oder automatisch)
6. OCR + LLM-Analyse läuft (30s)
7. JSON + SQL wird exportiert
8. Weiter zur nächsten Maske (15+ insgesamt)

## 📊 Erwartete Ergebnisse

Nach Abschluss:

```
schemas/
├── mask-builder/
│   ├── artikelstamm.json        ✅ Mask Builder Schema
│   ├── kundenstamm.json
│   ├── lieferschein.json
│   ├── rechnung.json
│   └── ... (15+ Masken)
├── sql/
│   ├── artikelstamm.sql         ✅ CREATE TABLE Statement
│   ├── kundenstamm.sql
│   └── ...
└── mappings/
    ├── migration-index.json     ✅ Vollständiger Index
    └── l3-to-valeo-extended.json
```

## 🔧 Konfiguration

### Tesseract-Pfad anpassen

Falls Tesseract nicht gefunden wird:

**In Python:**
```python
# ocr-pipeline.py anpassen:
ocr = L3MaskOCR(tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe")
```

**Oder CLI:**
```powershell
python ocr-pipeline.py screenshot.png --tesseract "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### LLM-Integration (Optional)

Für automatische Feldanalyse mit Claude/GPT:

**In `llm-field-analyzer.py`:**
```python
def _call_llm(self, prompt: str) -> str:
    # OpenAI
    import openai
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
    
    # ODER Anthropic
    import anthropic
    client = anthropic.Anthropic(api_key="...")
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
```

## 📈 Performance-Tuning

### OCR-Genauigkeit verbessern

**In `ocr-pipeline.py`, Methode `preprocess_image()`:**

```python
# Für bessere Ergebnisse bei:
# - Niedrige Auflösung → Upscaling hinzufügen
# - Verrauschte Bilder → Stärkere Denoising
# - Niedriger Kontrast → CLAHE-Parameter erhöhen

# Beispiel: Upscaling für niedrige Auflösung
if img.size[0] < 1920:
    scale_factor = 1920 / img.size[0]
    new_size = (int(img.size[0] * scale_factor), int(img.size[1] * scale_factor))
    img = img.resize(new_size, Image.Resampling.LANCZOS)
```

### Confidence-Threshold anpassen

```python
# In ocr-pipeline.py:
self.confidence_threshold = 70  # Standard: 60
```

## 🐛 Troubleshooting

### Problem: "tesseract is not recognized"

**Lösung:**
```powershell
# Prüfe PATH:
$env:Path -split ';' | Select-String "Tesseract"

# Falls leer, manuell setzen:
$env:Path += ";C:\Program Files\Tesseract-OCR"
```

### Problem: "Failed to load language 'deu'"

**Lösung:**
```powershell
# Prüfe Language Packs:
dir "C:\Program Files\Tesseract-OCR\tessdata"

# Falls deu.traineddata fehlt:
# Download von: https://github.com/tesseract-ocr/tessdata
# Kopieren nach: C:\Program Files\Tesseract-OCR\tessdata\
```

### Problem: Niedrige OCR-Genauigkeit (<80%)

**Lösungen:**
1. **Screenshot-Qualität erhöhen** (1920x1080 oder höher)
2. **Debug-Modus aktivieren:** `--debug` → Prüfe preprocessed Image
3. **Tesseract-Parameter optimieren:**
   ```python
   # In ocr-pipeline.py:
   ocr_data = pytesseract.image_to_data(
       processed_img,
       lang='deu+eng',
       config='--psm 6 --oem 1'  # PSM 6 = Uniform block, OEM 1 = LSTM only
   )
   ```

## 📚 Referenzen

- **Tesseract OCR GitHub:** https://github.com/tesseract-ocr/tesseract
- **Tesseract Dokumentation:** https://tesseract-ocr.github.io/
- **Windows Installer:** https://github.com/UB-Mannheim/tesseract/wiki
- **Trained Data:** https://github.com/tesseract-ocr/tessdata
- **pytesseract Docs:** https://pypi.org/project/pytesseract/

## ✅ Checkliste

- [ ] Tesseract 5.5.1+ installiert
- [ ] German Language Pack vorhanden (`deu.traineddata`)
- [ ] Python Dependencies installiert
- [ ] PATH-Variable gesetzt
- [ ] OCR-Test mit Artikelstamm-Screenshot erfolgreich
- [ ] Browser auf Guacamole RDP geöffnet
- [ ] Batch-Script `auto-capture-all-masks.py` bereit

**Status:** Bereit für automatische L3-Migration! 🎉

---

**Nächster Schritt:** 
```powershell
python auto-capture-all-masks.py
```


