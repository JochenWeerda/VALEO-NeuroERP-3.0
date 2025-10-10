***REMOVED*** PDF-Templates & Branding

***REMOVED******REMOVED*** Überblick

VALEO-NeuroERP unterstützt anpassbare PDF-Templates für Belege mit Logo, Farben und Layout-Varianten.

***REMOVED******REMOVED*** Konfiguration

***REMOVED******REMOVED******REMOVED*** Environment-Variablen

```bash
***REMOVED*** PDF-Template-Sprache
PDF_TEMPLATE_LANG=de  ***REMOVED*** oder 'en'

***REMOVED*** Seitengröße
PDF_PAGE_SIZE=A4  ***REMOVED*** oder 'LETTER'

***REMOVED*** Logo-Pfad
PDF_LOGO_PATH=/app/data/branding/logo.png

***REMOVED*** Firmen-Informationen
COMPANY_NAME="VALEO GmbH"
COMPANY_ADDRESS="Musterstraße 123"
COMPANY_CITY="12345 Musterstadt"
COMPANY_COUNTRY="Deutschland"
COMPANY_TAX_ID="DE123456789"
COMPANY_PHONE="+49 123 456789"
COMPANY_EMAIL="info@valeo.example.com"
COMPANY_WEBSITE="https://www.valeo.example.com"

***REMOVED*** Farben (Hex)
PDF_PRIMARY_COLOR="***REMOVED***003366"
PDF_SECONDARY_COLOR="***REMOVED***0066CC"
PDF_TEXT_COLOR="***REMOVED***333333"
```

***REMOVED******REMOVED*** Template-Struktur

***REMOVED******REMOVED******REMOVED*** Verfügbare Templates

```
data/templates/
├── invoice_de.json       ***REMOVED*** Rechnung (Deutsch)
├── invoice_en.json       ***REMOVED*** Invoice (English)
├── order_de.json         ***REMOVED*** Auftrag (Deutsch)
├── order_en.json         ***REMOVED*** Order (English)
├── delivery_de.json      ***REMOVED*** Lieferschein (Deutsch)
└── delivery_en.json      ***REMOVED*** Delivery Note (English)
```

***REMOVED******REMOVED******REMOVED*** Template-Format

```json
{
  "type": "invoice",
  "lang": "de",
  "page_size": "A4",
  "header": {
    "logo": true,
    "company_info": true,
    "document_title": "Rechnung"
  },
  "sections": [
    {
      "name": "customer",
      "label": "Rechnungsempfänger",
      "fields": ["name", "address", "city", "country"]
    },
    {
      "name": "positions",
      "label": "Positionen",
      "columns": [
        {"field": "sku", "label": "Artikel-Nr.", "width": 80},
        {"field": "description", "label": "Beschreibung", "width": 200},
        {"field": "quantity", "label": "Menge", "width": 50, "align": "right"},
        {"field": "unit_price", "label": "Einzelpreis", "width": 70, "align": "right", "format": "currency"},
        {"field": "total", "label": "Gesamt", "width": 70, "align": "right", "format": "currency"}
      ]
    },
    {
      "name": "totals",
      "label": "Summen",
      "fields": [
        {"field": "subtotal", "label": "Zwischensumme", "format": "currency"},
        {"field": "tax", "label": "MwSt. (19%)", "format": "currency"},
        {"field": "total", "label": "Gesamtsumme", "format": "currency", "bold": true}
      ]
    }
  ],
  "footer": {
    "text": "Zahlbar innerhalb 14 Tagen ohne Abzug.",
    "bank_info": true,
    "tax_info": true
  }
}
```

***REMOVED******REMOVED*** Logo hochladen

***REMOVED******REMOVED******REMOVED*** Via API

```bash
curl -X POST https://erp.valeo.example.com/api/branding/logo \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@logo.png"
```

***REMOVED******REMOVED******REMOVED*** Via kubectl (Kubernetes)

```bash
***REMOVED*** Create ConfigMap with logo
kubectl create configmap valeo-erp-logo \
  --from-file=logo.png=/path/to/logo.png \
  -n production

***REMOVED*** Mount in Deployment
***REMOVED*** (siehe k8s/helm/valeo-erp/values.yaml)
```

***REMOVED******REMOVED******REMOVED*** Logo-Anforderungen

- **Format:** PNG (transparent) oder JPG
- **Größe:** Max. 2 MB
- **Auflösung:** 300 DPI empfohlen
- **Abmessungen:** Max. 200x80 Pixel (wird automatisch skaliert)

***REMOVED******REMOVED*** Farben anpassen

***REMOVED******REMOVED******REMOVED*** Via Environment

```bash
***REMOVED*** In values.yaml oder ConfigMap
env:
  - name: PDF_PRIMARY_COLOR
    value: "***REMOVED***003366"
  - name: PDF_SECONDARY_COLOR
    value: "***REMOVED***0066CC"
```

***REMOVED******REMOVED******REMOVED*** Farbschema-Beispiele

**Corporate Blue:**
```
PRIMARY: ***REMOVED***003366
SECONDARY: ***REMOVED***0066CC
TEXT: ***REMOVED***333333
```

**Modern Green:**
```
PRIMARY: ***REMOVED***2E7D32
SECONDARY: ***REMOVED***66BB6A
TEXT: ***REMOVED***212121
```

**Professional Gray:**
```
PRIMARY: ***REMOVED***424242
SECONDARY: ***REMOVED***757575
TEXT: ***REMOVED***212121
```

***REMOVED******REMOVED*** Multi-Language Support

***REMOVED******REMOVED******REMOVED*** Sprache pro Beleg

```python
***REMOVED*** API-Request
POST /api/print/invoice/INV-00001
{
  "lang": "en",  ***REMOVED*** Override default
  "page_size": "LETTER"
}
```

***REMOVED******REMOVED******REMOVED*** Automatische Sprach-Erkennung

```python
***REMOVED*** Basierend auf Customer-Land
if customer.country in ["US", "GB", "CA"]:
    lang = "en"
elif customer.country in ["DE", "AT", "CH"]:
    lang = "de"
```

***REMOVED******REMOVED*** Custom Templates erstellen

***REMOVED******REMOVED******REMOVED*** 1. Template-Datei erstellen

```bash
***REMOVED*** Kopiere existierendes Template
cp data/templates/invoice_de.json data/templates/invoice_custom.json

***REMOVED*** Bearbeite Template
vim data/templates/invoice_custom.json
```

***REMOVED******REMOVED******REMOVED*** 2. Template registrieren

```python
***REMOVED*** In app/services/pdf_service.py
TEMPLATES = {
    "invoice_de": "data/templates/invoice_de.json",
    "invoice_en": "data/templates/invoice_en.json",
    "invoice_custom": "data/templates/invoice_custom.json",  ***REMOVED*** NEU
}
```

***REMOVED******REMOVED******REMOVED*** 3. Template verwenden

```bash
POST /api/print/invoice/INV-00001
{
  "template": "invoice_custom"
}
```

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Problem: Logo wird nicht angezeigt

**Ursache:** Pfad falsch oder Datei nicht gefunden

**Lösung:**
```bash
***REMOVED*** Check logo file
ls -lh /app/data/branding/logo.png

***REMOVED*** Check permissions
chmod 644 /app/data/branding/logo.png

***REMOVED*** Check ENV
echo $PDF_LOGO_PATH
```

***REMOVED******REMOVED******REMOVED*** Problem: Falsche Farben im PDF

**Ursache:** Hex-Code falsch formatiert

**Lösung:** Hex-Code muss mit `***REMOVED***` beginnen, z.B. `***REMOVED***003366`

***REMOVED******REMOVED******REMOVED*** Problem: Text abgeschnitten

**Ursache:** Column-Width zu klein

**Lösung:** Erhöhe `width` in Template-Definition

```json
{"field": "description", "width": 250}  // vorher 200
```

***REMOVED******REMOVED*** Best Practices

1. **Logo transparent:** PNG mit transparentem Hintergrund
2. **Farben kontrastreich:** Mindestens 4.5:1 Kontrast (WCAG AA)
3. **Templates versionieren:** Git-Commit bei Änderungen
4. **Test auf beiden Seitengrößen:** A4 und Letter
5. **Schriftgröße mindestens 9pt:** Für Lesbarkeit

***REMOVED******REMOVED*** Support

Bei Fragen: admin@valeo-erp.com

