# PDF-Templates & Branding

## Überblick

VALEO-NeuroERP unterstützt anpassbare PDF-Templates für Belege mit Logo, Farben und Layout-Varianten.

## Konfiguration

### Environment-Variablen

```bash
# PDF-Template-Sprache
PDF_TEMPLATE_LANG=de  # oder 'en'

# Seitengröße
PDF_PAGE_SIZE=A4  # oder 'LETTER'

# Logo-Pfad
PDF_LOGO_PATH=/app/data/branding/logo.png

# Firmen-Informationen
COMPANY_NAME="VALEO GmbH"
COMPANY_ADDRESS="Musterstraße 123"
COMPANY_CITY="12345 Musterstadt"
COMPANY_COUNTRY="Deutschland"
COMPANY_TAX_ID="DE123456789"
COMPANY_PHONE="+49 123 456789"
COMPANY_EMAIL="info@valeo.example.com"
COMPANY_WEBSITE="https://www.valeo.example.com"

# Farben (Hex)
PDF_PRIMARY_COLOR="#003366"
PDF_SECONDARY_COLOR="#0066CC"
PDF_TEXT_COLOR="#333333"
```

## Template-Struktur

### Verfügbare Templates

```
data/templates/
├── invoice_de.json       # Rechnung (Deutsch)
├── invoice_en.json       # Invoice (English)
├── order_de.json         # Auftrag (Deutsch)
├── order_en.json         # Order (English)
├── delivery_de.json      # Lieferschein (Deutsch)
└── delivery_en.json      # Delivery Note (English)
```

### Template-Format

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

## Logo hochladen

### Via API

```bash
curl -X POST https://erp.valeo.example.com/api/branding/logo \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@logo.png"
```

### Via kubectl (Kubernetes)

```bash
# Create ConfigMap with logo
kubectl create configmap valeo-erp-logo \
  --from-file=logo.png=/path/to/logo.png \
  -n production

# Mount in Deployment
# (siehe k8s/helm/valeo-erp/values.yaml)
```

### Logo-Anforderungen

- **Format:** PNG (transparent) oder JPG
- **Größe:** Max. 2 MB
- **Auflösung:** 300 DPI empfohlen
- **Abmessungen:** Max. 200x80 Pixel (wird automatisch skaliert)

## Farben anpassen

### Via Environment

```bash
# In values.yaml oder ConfigMap
env:
  - name: PDF_PRIMARY_COLOR
    value: "#003366"
  - name: PDF_SECONDARY_COLOR
    value: "#0066CC"
```

### Farbschema-Beispiele

**Corporate Blue:**
```
PRIMARY: #003366
SECONDARY: #0066CC
TEXT: #333333
```

**Modern Green:**
```
PRIMARY: #2E7D32
SECONDARY: #66BB6A
TEXT: #212121
```

**Professional Gray:**
```
PRIMARY: #424242
SECONDARY: #757575
TEXT: #212121
```

## Multi-Language Support

### Sprache pro Beleg

```python
# API-Request
POST /api/print/invoice/INV-00001
{
  "lang": "en",  # Override default
  "page_size": "LETTER"
}
```

### Automatische Sprach-Erkennung

```python
# Basierend auf Customer-Land
if customer.country in ["US", "GB", "CA"]:
    lang = "en"
elif customer.country in ["DE", "AT", "CH"]:
    lang = "de"
```

## Custom Templates erstellen

### 1. Template-Datei erstellen

```bash
# Kopiere existierendes Template
cp data/templates/invoice_de.json data/templates/invoice_custom.json

# Bearbeite Template
vim data/templates/invoice_custom.json
```

### 2. Template registrieren

```python
# In app/services/pdf_service.py
TEMPLATES = {
    "invoice_de": "data/templates/invoice_de.json",
    "invoice_en": "data/templates/invoice_en.json",
    "invoice_custom": "data/templates/invoice_custom.json",  # NEU
}
```

### 3. Template verwenden

```bash
POST /api/print/invoice/INV-00001
{
  "template": "invoice_custom"
}
```

## Troubleshooting

### Problem: Logo wird nicht angezeigt

**Ursache:** Pfad falsch oder Datei nicht gefunden

**Lösung:**
```bash
# Check logo file
ls -lh /app/data/branding/logo.png

# Check permissions
chmod 644 /app/data/branding/logo.png

# Check ENV
echo $PDF_LOGO_PATH
```

### Problem: Falsche Farben im PDF

**Ursache:** Hex-Code falsch formatiert

**Lösung:** Hex-Code muss mit `#` beginnen, z.B. `#003366`

### Problem: Text abgeschnitten

**Ursache:** Column-Width zu klein

**Lösung:** Erhöhe `width` in Template-Definition

```json
{"field": "description", "width": 250}  // vorher 200
```

## Best Practices

1. **Logo transparent:** PNG mit transparentem Hintergrund
2. **Farben kontrastreich:** Mindestens 4.5:1 Kontrast (WCAG AA)
3. **Templates versionieren:** Git-Commit bei Änderungen
4. **Test auf beiden Seitengrößen:** A4 und Letter
5. **Schriftgröße mindestens 9pt:** Für Lesbarkeit

## Support

Bei Fragen: admin@valeo-erp.com

