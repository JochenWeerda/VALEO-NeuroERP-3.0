***REMOVED*** @valero-neuroerp/notifications-domain

**Multi-Channel Notification Platform** für VALEO-NeuroERP 3.0

***REMOVED******REMOVED*** 📋 Features

- ✅ **Multi-Channel** (Email, SMS, WhatsApp, Push, Webhook)
- ✅ **Template-System** (Handlebars mit Variablen)
- ✅ **Kanal-Adapter-Pattern**
- ✅ **Rate-Limiting & Retry**
- ✅ **Zustellnachweise & Tracking**
- ✅ **Event-Driven** (NATS Consumer)

***REMOVED******REMOVED*** 🚫 Abgrenzung

❌ Keine Geschäftslogik (Preise, Verträge, Lagerbestände)  
❌ Nur Nachrichtenversand!

***REMOVED******REMOVED*** 🚀 Quick Start

```bash
npm install
npm run migrate:gen
npm run dev  ***REMOVED*** Port 3080
```

***REMOVED******REMOVED*** 📡 API

```
POST /notifications/api/v1/messages/send  - Nachricht senden
GET  /notifications/api/v1/messages/:id   - Nachricht abrufen
```

***REMOVED******REMOVED*** 💡 Beispiel

```json
POST /notifications/api/v1/messages/send
{
  "channel": "Email",
  "templateKey": "invoice_email_de",
  "locale": "de-DE",
  "payload": {
    "customerName": "Müller GmbH",
    "invoiceNumber": "INV-2025-001",
    "amount": 5250
  },
  "recipients": [{ "type": "Email", "value": "kunde@example.com" }],
  "priority": "High"
}
```

***REMOVED******REMOVED*** 🔗 Integration

- **Document Domain** → PDF-Anhänge
- **Sales Domain** → Rechnungsversand
- **Contracts Domain** → Vertragsbestätigungen
- **Quality Domain** → Prüfergebnis-Alerts

***REMOVED******REMOVED*** 📊 Port: 3080

**Status:** ✅ MVP Ready
