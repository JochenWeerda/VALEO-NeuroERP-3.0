# Semi-Automatischer L3-Masken-Erfassung Workflow

## 🎯 Realität

**Automatische Klicks in Guacamole RDP funktionieren nicht** - RDP fängt JavaScript-Events nicht ab.

**Pragmatische Lösung:** Hybrid-Ansatz

## ✅ Was funktioniert (100% automatisch)

1. ✅ Screenshot-Erfassung (Playwright Browser MCP)
2. ✅ OCR-Analyse (Tesseract)
3. ✅ Schema-Generierung (JSON + SQL)
4. ✅ Batch-Processing

## 🖱️ Was manuell bleibt

- **Navigation in L3** (Sie klicken auf Icons/Menüs)

## 🚀 Optimierter Workflow

### Sie tun:
1. Öffnen Sie Maske in L3 (z.B. Artikelstamm)
2. Sagen Sie: "Artikelstamm offen"

### Ich tue (automatisch):
3. Screenshot erstellen
4. OCR-Analyse durchführen  
5. Mask Builder Schema generieren (JSON + SQL)
6. Zur nächsten Maske

**Zeitaufwand pro Maske:** ~30 Sekunden (davon 25s automatisch!)

## 📋 Maske

nliste (Priorität)

### ⭐⭐⭐⭐⭐ KRITISCH
1. [ ] Artikelstamm
2. [ ] Kundenstamm
3. [ ] Lieferantenstamm
4. [ ] Lieferschein
5. [ ] Rechnung
6. [ ] Auftrag
7. [ ] Bestellung
8. [ ] PSM-Abgabe (Agrar!)

### ⭐⭐⭐⭐ WICHTIG
9. [ ] Lager-Bestand
10. [ ] Angebot
11. [ ] Wareneingang
12. [ ] Kunden-Kontoauszug

### ⭐⭐⭐ NICE-TO-HAVE
13. [ ] Inventur
14. [ ] CRM Dashboard
15. [ ] Kalender

## 🎬 Los geht's!

**Öffnen Sie jetzt die erste wichtige Maske (z.B. Artikelstamm) und sagen Sie Bescheid!**

Dann läuft der automatische Teil! 🚀

