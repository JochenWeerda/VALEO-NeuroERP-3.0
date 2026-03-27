# CTS-009 — Rohwaren-Positionsmonitor (Long/Short)

## Zweck

Der Einkauf muss jederzeit wissen, ob die Genossenschaft bei Rohwaren wie Sojaschrot, Rapsschrot, Mais oder Maismehl **Long** oder **Short** ist. Eine Unterdeckung (Short-Position) entsteht, wenn mehr Verkaufskontrakte mit Landwirten abgeschlossen wurden als durch Einkaufskontrakte am Boersenmarkt oder bei Lieferanten gedeckt sind. Bei steigenden Boersenpreisen fuehrt das zu erheblichen Verlusten.

## Fachliche Logik

### Begriffe (Warenterminmarkt)

| Begriff | Bedeutung | Risiko |
|---------|-----------|--------|
| **Long** | Einkauf uebersteigt Verkauf → Ware gesichert / im Lager | Preisverfall (Lagerrisiko) |
| **Short** | Verkauf uebersteigt Einkauf → Lieferverpflichtung ohne Deckung | **Steigende Preise** (Boersenrisiko!) |
| **Balanced** | Einkauf ≈ Verkauf | Gering |

### Berechnung pro Artikel

```
SELL-Seite = Summe aller offenen Verkaufskontrakt-Restmengen (contract_type = VERKAUF)
BUY-Seite  = Summe aller offenen Einkaufs-/Zukaufskontrakt-Restmengen (EINKAUF + ZUKAUF)

Netto-Position  = BUY-Rest - SELL-Rest
Deckungsgrad    = BUY-Rest / SELL-Rest × 100%
Signal          = Positiv → LONG | Negativ → SHORT | Null → BALANCED
Spread          = Durchschnitts-VK-Preis - Durchschnitts-EK-Preis
```

### Praxis-Szenario (Sojaschrot)

1. Genossenschaft schliesst im Fruehjahr 5 Verkaufskontrakte ueber insgesamt 2.000 t Sojaschrot mit Landwirten (Futtermittel)
2. Bisher nur 1 Einkaufskontrakt ueber 800 t am Markt gedeckt
3. **Netto-Position = 800 - 2.000 = -1.200 t → SHORT**
4. **Deckungsgrad = 800/2.000 = 40%** → **kritische Unterdeckung**
5. Steigt der Sojaschrot-Preis an der Boerse um 50 EUR/t → 1.200 t × 50 EUR = 60.000 EUR potenzieller Verlust

## Betroffene Dateien

### Backend
- `app/services/kontrakt_position_service.py` — Berechnungslogik (KontraktPositionService)
- `app/api/v1/endpoints/kontrakte.py` — GET /kontrakte/positionen

### Frontend
- `pages/kontrakte/KontraktPositionsmonitor.tsx` — Haupt-Dashboard (Route: /kontrakte/positionen)
- `pages/kontrakte/FrmKontraktDetail.tsx` — Short-Warnung im Kontraktdetail
- `pages/kontrakte/LstKontraktUebersicht.tsx` — Link zum Monitor

## API

### GET /api/v1/kontrakte/positionen

**Parameter:**
- `article_ids` (optional): Komma-separierte Artikel-IDs zum Filtern
- `include_done` (optional, default false): Erledigte Kontrakte einbeziehen

**Response:**
```json
{
  "positions": [
    {
      "article_id": "ART-SOJA-001",
      "article_desc": "Sojaschrot 44/7",
      "buy_contract_qty": 800,
      "buy_rest_qty": 600,
      "buy_avg_price": 420.00,
      "buy_contract_count": 1,
      "sell_contract_qty": 2000,
      "sell_rest_qty": 1800,
      "sell_avg_price": 450.00,
      "sell_contract_count": 5,
      "net_position": -1200,
      "signal": "SHORT",
      "coverage_pct": 33.3,
      "spread": 30.00
    }
  ],
  "total_short_articles": 1,
  "total_long_articles": 0,
  "total_balanced_articles": 0,
  "most_critical": { ... }
}
```

## UI-Elemente

### 1. Positionsmonitor-Dashboard (/kontrakte/positionen)
- **KPI-Karten**: Short-Anzahl (rot), Long-Anzahl (gruen), Balanced (grau), kritischster Spread
- **Kritische-Unterdeckung-Banner**: Hervorgehobene Warnung fuer den am staerksten unterdeckten Artikel
- **Positionstabelle**: Pro Artikel: Signal, Deckungsgrad, VK/EK-Mengen, Preise, Netto, Spread
- **Filter**: "Nur Short-Positionen", "Erledigte einbeziehen"
- **Auto-Refresh**: Alle 30 Sekunden

### 2. Kontraktdetail — Short-Warnung
- Rote Alert-Box wenn Artikel dieses Kontrakts unterdeckt sind
- Gruene Statusleiste wenn alle Artikel gedeckt

### 3. Kontraktliste — Quick-Links
- Button "Long/Short-Monitor" in der Toolbar
- Button "Alarme" in der Toolbar

## Quellen / Fachliche Grundlage

- Kaack Terminhandel: "Long = Ware produzieren/lagern, Short = Ware auf Termin gekauft, noch nicht besitzen"
- Agrarmarktpodcast: "Physisch Short = Lieferverpflichtung ohne Bestand → Boersenrisiko"
- CME Group: Long Hedge = Kauf-Futures gegen steigende Preise, Short Hedge = Verkauf-Futures gegen fallende Preise

## Status

**Umgesetzt** (2026-03-27) — Backend-Service, API, Dashboard, Integration in Kontraktdetail und -liste.

## Naechste Schritte (optional)

- Futures/Hedging-Positionen parallel abbilden (finanziell Long/Short neben physisch)
- Schwellenwerte pro Artikel konfigurierbar (z.B. "unter 70% Deckung = Alarm")
- E-Mail/Push-Benachrichtigung bei neuen Short-Positionen
- Historischer Positionsverlauf (Zeitreihe)
