# L3-Masken Screenshot Quick-Guide

## 🎯 Pragmatischer Ansatz

Da die automatische Klick-Erkennung auf dem RDP-Canvas Herausforderungen bietet, verwenden wir einen **hybriden Ansatz**:

### Option A: **Sie navigieren manuell + ich erstelle Screenshots**
1. **Sie öffnen die gewünschte L3-Maske** im Browser
2. **Sie sagen mir den Masken-Namen** (z.B. "Artikel-Stamm")
3. **Ich erstelle sofort einen Screenshot** via Playwright
4. **Ich dokumentiere die Maske** in einer strukturierten Liste

### Option B: **Ich übernehme Ihre Maus (falls möglich)**
- Falls Sie Fernzugriff auf Ihren Rechner erlauben, kann ich direkt navigieren

### Option C: **Manuelle Screenshots + Batch-Upload**
- Sie erstellen Screenshots selbst (Windows + Shift + S)
- Speichern in `l3-migration-toolkit/screenshots/l3-masks/`
- Benennung: `01_artikel-stamm.png`, `02_kunden-liste.png`, etc.
- Ich analysiere und dokumentiere alle Bilder auf einmal

## 📋 Zu erfassende Masken (Priorität)

### ⭐⭐⭐⭐⭐ KRITISCH (für Migration essentiell)
1. **Artikel-Stamm** - Artikelverwaltung
2. **Kunden-Stamm** - Kundenverwaltung
3. **Lieferschein** - Verkauf/Lieferschein
4. **Rechnung** - Fakturierung
5. **Auftrag** - Auftragserfassung
6. **Bestellung** - Einkaufsbestellung
7. **Lager-Bestand** - Lagerverwaltung
8. **PSM-Abgabe** - Pflanzenschutzmittel (BRANCHENSPEZIFISCH!)

### ⭐⭐⭐⭐ WICHTIG
9. **Kunden-Kontoauszug** - Offene Posten
10. **Lieferanten-Stamm** - Lieferantenverwaltung
11. **Artikelgruppen** - Kategorisierung
12. **Preislisten** - Preisverwaltung

### ⭐⭐⭐ NICE-TO-HAVE
13. **CRM-Dashboard** - Kundenbeziehungen
14. **Kalender** (bereits vorhanden)
15. **Statistiken/Reports**

## 🚀 Nächster Schritt

**Welche Option bevorzugen Sie?**
- **Option A:** Ich sage "fertig", Sie erstellen Screenshot
- **Option B:** Sie teilen Bildschirm/Fernzugriff
- **Option C:** Sie erstellen alle Screenshots selbst

Oder wir probieren einen **vierten Ansatz**: Ich gebe Ihnen präzise **Klick-Anweisungen** (z.B. "Klicken Sie auf 'ERFASSUNG' → dann 'Artikel'"), und Sie sagen mir, was passiert ist.

---

**Ihre Entscheidung?** (A, B, C, oder Alternative)

