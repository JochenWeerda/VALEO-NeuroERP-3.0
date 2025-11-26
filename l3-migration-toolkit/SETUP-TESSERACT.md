***REMOVED*** Tesseract-OCR Installation (Windows)

Tesseract ist erforderlich für die automatische Feldextraktion aus L3-Screenshots.

***REMOVED******REMOVED*** 📦 Installation

***REMOVED******REMOVED******REMOVED*** Option 1: Chocolatey (empfohlen)

**Als Administrator:**
```powershell
choco install tesseract --yes
```

***REMOVED******REMOVED******REMOVED*** Option 2: Manueller Download

1. **Download:**
   - https://github.com/UB-Mannheim/tesseract/wiki
   - Version: 5.x (neueste)
   - Datei: `tesseract-ocr-w64-setup-5.x.x.exe`

2. **Installation:**
   - Ausführen als Administrator
   - Installation nach: `C:\Program Files\Tesseract-OCR\`
   - **Wichtig:** Nur "English" Language Pack auswählen!
   - **Hinweis:** Erfahrungswert zeigt, dass `eng.traineddata` bessere Ergebnisse liefert als `deu.traineddata`, auch für deutsche UI-Texte!

3. **Umgebungsvariable setzen:**
   ```powershell
   [System.Environment]::SetEnvironmentVariable(
       "Path",
       [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";C:\Program Files\Tesseract-OCR",
       "Machine"
   )
   ```

***REMOVED******REMOVED*** ✅ Verifikation

```powershell
tesseract --version
```

**Erwartete Ausgabe:**
```
tesseract 5.x.x
 leptonica-1.x.x
  ...
```

***REMOVED******REMOVED*** 🔧 Python-Integration

Nach der Installation:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

Oder in `ocr-pipeline.py`:
```bash
python ocr-pipeline.py screenshots/artikelstamm.png --tesseract "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

***REMOVED******REMOVED*** 🐛 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Problem: "tesseract is not recognized"

**Lösung:** PATH-Variable nicht gesetzt

```powershell
***REMOVED*** Überprüfen:
$env:Path

***REMOVED*** Manuell setzen (temporär):
$env:Path += ";C:\Program Files\Tesseract-OCR"
```

***REMOVED******REMOVED******REMOVED*** Problem: "Language pack not found"

**Lösung:** English-Pack sollte standardmäßig vorhanden sein

```powershell
***REMOVED*** Prüfe ob eng.traineddata vorhanden:
dir "C:\Program Files\Tesseract-OCR\tessdata\eng.traineddata"

***REMOVED*** Falls nicht: Download von GitHub
***REMOVED*** https://github.com/tesseract-ocr/tessdata/blob/main/eng.traineddata
```

**Hinweis:** Verwenden Sie NUR `eng.traineddata` - funktioniert auch für deutsche UI-Texte!

***REMOVED******REMOVED*** 📚 Weitere Informationen

- **Dokumentation:** https://tesseract-ocr.github.io/
- **GitHub:** https://github.com/tesseract-ocr/tesseract
- **Windows Builds:** https://github.com/UB-Mannheim/tesseract/wiki

---

**Nach der Installation:** Führen Sie `python ocr-pipeline.py screenshots/l3-masks/artikelstamm.png` aus!

