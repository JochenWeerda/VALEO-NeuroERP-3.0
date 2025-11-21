# L3-Masken Navigations-Koordinaten

Dokumentation der Klick-Koordinaten für die automatische Screenshot-Erfassung der L3-Masken über Guacamole RDP.

## 🎯 Methodik

Da RDP-Inhalte als `<canvas>` gerendert werden, müssen wir mit **Pixel-Koordinaten** arbeiten:
- **Viewport:** 1920×1080 (Standard)
- **Basis:** Top-Left Corner (0,0)
- **Koordinaten:** Relativ zum Canvas

## 📍 Haupt-Menü Koordinaten

### Top-Menü-Leiste (Y ≈ 60-90)

| Menü | X-Position | Y-Position | Beschreibung |
|------|-----------|-----------|--------------|
| DATEI | 80 | 75 | Datei-Menü |
| FAVORITEN | 180 | 75 | Favoriten (Icons darunter) |
| ALLGEMEIN | 280 | 75 | Allgemeine Funktionen |
| ERFASSUNG | 380 | 75 | Erfassungs-Masken |
| ABRECHNUNG | 480 | 75 | Abrechnungs-Funktionen |
| LAGER | 580 | 75 | Lager-Verwaltung |
| PRODUKTION | 680 | 75 | Produktions-Module |
| AUSWERTUNGEN | 780 | 75 | Reports & Auswertungen |
| SCHNITTSTELLE | 880 | 75 | Import/Export |
| FENSTER | 980 | 75 | Fenster-Verwaltung |

### Favoriten-Icons (Y ≈ 110-140)

| Icon | X-Position | Y-Position | Beschreibung |
|------|-----------|-----------|--------------|
| Kunden-Artikel | 200 | 125 | Kundenbezogene Artikel |
| Verkauf-Lieferschein | 320 | 125 | Lieferschein-Erfassung |
| Artikel-Stamm | 440 | 125 | Artikelstammdaten |
| Artikel-Konto | 560 | 125 | Artikel-Kontierung |
| CRM Dashboard | 680 | 125 | CRM-Übersicht |
| Abfrage-Center | 800 | 125 | Suchfunktion |

## 📋 Masken-Inventar mit Navigation

### 1. Artikel-Stamm
- **Navigation:** Favoriten-Icon (X:440, Y:125)
- **Alternative:** ERFASSUNG → Artikel
- **Wichtigkeit:** ⭐⭐⭐⭐⭐
- **Felder:** Artikel-Nr, Bezeichnung, EAN, Preis, Kostenstelle, Lager, etc.

### 2. Kunden-Artikel
- **Navigation:** Favoriten-Icon (X:200, Y:125)
- **Alternative:** ERFASSUNG → Kunden
- **Wichtigkeit:** ⭐⭐⭐⭐⭐
- **Felder:** Kunden-Nr, Name, Anschrift, Konditionen, etc.

### 3. Verkauf-Lieferschein
- **Navigation:** Favoriten-Icon (X:320, Y:125)
- **Alternative:** ERFASSUNG → Lieferschein
- **Wichtigkeit:** ⭐⭐⭐⭐⭐
- **Felder:** LS-Nr, Datum, Kunde, Positionen, Summe, etc.

### 4. Rechnung
- **Navigation:** ABRECHNUNG (X:480, Y:75) → Rechnung
- **Wichtigkeit:** ⭐⭐⭐⭐⭐
- **Felder:** RE-Nr, Datum, Kunde, Positionen, USt, Summe, etc.

### 5. Auftrag
- **Navigation:** ERFASSUNG (X:380, Y:75) → Auftrag
- **Wichtigkeit:** ⭐⭐⭐⭐
- **Felder:** Auftrags-Nr, Datum, Kunde, Positionen, Status, etc.

### 6. Bestellung
- **Navigation:** ERFASSUNG (X:380, Y:75) → Bestellung
- **Wichtigkeit:** ⭐⭐⭐⭐
- **Felder:** Best-Nr, Lieferant, Positionen, Liefertermin, etc.

### 7. Lager-Bestand
- **Navigation:** LAGER (X:580, Y:75) → Bestand
- **Wichtigkeit:** ⭐⭐⭐⭐
- **Felder:** Artikel, Lager, Menge, Reserviert, Verfügbar, etc.

### 8. PSM-Abgabe (Pflanzenschutz)
- **Navigation:** ERFASSUNG (X:380, Y:75) → PSM oder ALLGEMEIN → Agrar
- **Wichtigkeit:** ⭐⭐⭐⭐⭐ (BRANCHENKRITISCH)
- **Felder:** PSM-Nr, Kunde, Menge, Sachkunde-Nachweis, etc.

### 9. CRM-Dashboard
- **Navigation:** Favoriten-Icon (X:680, Y:125)
- **Alternative:** ALLGEMEIN → CRM
- **Wichtigkeit:** ⭐⭐⭐
- **Felder:** Kontakte, Leads, Aktivitäten, etc.

### 10. Kunden-Kontoauszug
- **Navigation:** AUSWERTUNGEN (X:780, Y:75) → Debitoren
- **Wichtigkeit:** ⭐⭐⭐⭐
- **Felder:** Offene Posten, Zahlungen, Mahnungen, etc.

## 🎬 Screenshot-Sequenz

### Phase 1: Favoriten (Schnellzugriff)
1. `00_l3-startseite.png` - Kalender (Startseite)
2. `01_artikel-stamm.png` - Klick auf Artikel-Stamm Icon
3. `02_kunden-artikel.png` - Klick auf Kunden-Artikel Icon
4. `03_verkauf-lieferschein.png` - Klick auf Verkauf-Lieferschein Icon

### Phase 2: ERFASSUNG-Menü
5. `04_auftrag.png` - ERFASSUNG → Auftrag
6. `05_bestellung.png` - ERFASSUNG → Bestellung
7. `06_psm-abgabe.png` - ERFASSUNG → PSM (falls vorhanden)

### Phase 3: ABRECHNUNG-Menü
8. `07_rechnung.png` - ABRECHNUNG → Rechnung
9. `08_gutschrift.png` - ABRECHNUNG → Gutschrift (falls vorhanden)

### Phase 4: LAGER-Menü
10. `09_lager-bestand.png` - LAGER → Bestand
11. `10_inventur.png` - LAGER → Inventur (falls vorhanden)

### Phase 5: AUSWERTUNGEN-Menü
12. `11_kunden-kontoauszug.png` - AUSWERTUNGEN → Debitoren
13. `12_umsatz-statistik.png` - AUSWERTUNGEN → Umsatz

## 📊 Koordinaten-Kalibrierung

**Wichtig:** Diese Koordinaten sind **Schätzwerte** basierend auf typischen UI-Layouts. 

### Kalibrierungs-Schritte:
1. **Manueller Test:** Erste Screenshots mit geschätzten Koordinaten
2. **Anpassung:** Koordinaten basierend auf tatsächlicher Menü-Position korrigieren
3. **Validierung:** Automatisches Skript mit finalen Koordinaten ausführen

### Tool zur Koordinaten-Ermittlung:
```javascript
// In Browser-Console (bei laufender RDP-Session):
document.querySelector('canvas').addEventListener('click', (e) => {
  const rect = e.target.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  console.log(`Klick-Position: X=${x}, Y=${y}`);
});
```

## 🔄 Nächste Schritte

- [ ] Manuelle Koordinaten-Kalibrierung durchführen
- [ ] Screenshots aller 12+ Hauptmasken erstellen
- [ ] Feldlisten für jede Maske dokumentieren
- [ ] Mapping zu VALEO-NeuroERP-Masken erstellen
- [ ] Playwright-Skript mit finalen Koordinaten ausführen

---

**Status:** 🟡 In Arbeit - Koordinaten werden während manueller Navigation ermittelt
**Letzte Aktualisierung:** {{ TIMESTAMP }}

