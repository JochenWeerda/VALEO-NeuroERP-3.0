---
title: ERP Prozesskarte
description: Visuelle Übersicht der 6 kritischen ERP-Prozessketten mit Events, Policies und externen Gates.
---

# ERP Prozesskarte

Visuelle Übersicht der 6 kritischen Geschäftsprozesse in VALEO NeuroERP 3.0.
Jede Kette zeigt Belege, Events, Policies und externe Gates.

---

## 1. O2C — Order-to-Cash (CRM360)

**Kette:** Kunde → Angebot → Auftrag → Lieferschein → Rechnung → Zahlung/OP-Auszifferung

```mermaid
flowchart LR
    K([Kundenstamm\ncustomer_number]) --> A
    A[Angebot\nstatus=accepted] -->|Konvertierung| B
    B[Auftrag\nsource_offer_id] -->|Positionen-Prefill| C
    C[Lieferschein\nsales_order_id] -->|Rechnungs-Erstellung| D
    D[Rechnung\ninvoice_number GoBD] -->|Zahlungseingang| E
    E[OP-Auszifferung\nop_status=ausgeziffert]

    B -.->|Event: order.confirmed| EVT1((NATS))
    C -.->|Event: delivery.shipped| EVT1
    D -.->|Event: invoice.posted| EVT1

    style E fill:#22c55e,color:#fff
    style EVT1 fill:#f59e0b,color:#fff
```

**Kritische Invarianten:**

- `sales_order_id` auf Lieferschein muss mit Auftrag-ID übereinstimmen
- GoBD: `invoice_number` darf nicht `null` sein
- OP-Saldo nach Vollzahlung exakt 0

---

## 2. P2P — Procure-to-Pay

**Kette:** Lieferant → Bestellung → Wareneingang → 3-Wege-Match → Eingangsrechnung/Kreditoren-OP

```mermaid
flowchart LR
    S([Lieferant\nstamm]) --> PO
    PO[Bestellung\nstatus=ordered] -->|Wareneingang| GR
    GR[Wareneingang\nreceived_at] -->|Match| M
    M{3-Wege-Match\nPreisabw. ≤ 2%} -->|OK| AP
    M -->|Abweichung >2%| BLK([Klärfall\nBlocker])
    AP[Eingangsrechnung\nop_id=Kreditoren-OP]

    GR -.->|Event: goods.received| EVT2((NATS))
    AP -.->|Event: ap.invoice.posted| EVT2

    style AP fill:#22c55e,color:#fff
    style BLK fill:#ef4444,color:#fff
    style EVT2 fill:#f59e0b,color:#fff
```

**Kritische Invarianten:**

- Preisabweichung im 3-Wege-Match ≤ 2 % (sonst Klärfall)
- Kreditoren-OP muss bei Eingangsrechnung angelegt sein
- `received_at` Pflichtfeld für Wareneingang

---

## 3. FiBu — OP-Lifecycle & DATEV-Export

**Kette:** Offener Posten → Zahlung → Auszifferung → (Periodenabschluss) → DATEV-Export

```mermaid
flowchart LR
    OP[Offener Posten\nop_status=offen\nfaelligkeit] -->|Zahlungseingang| Z
    Z[Zahlung\namount] -->|Auszifferung| CL
    CL[Ausgeziffert\noffen=0.00] --> PA
    PA{Periodenabschluss\nStatus=closed?} -->|Ja| DE
    PA -->|Noch offen| MH[Mahnung\nMahnstufe+1]
    DE[DATEV-Export\nentry_count >0\nfile_path]

    CL -.->|Event: op.cleared| EVT3((NATS))
    PA -.->|GoBD-Sperre| LCK([Periode gesperrt])

    style CL fill:#22c55e,color:#fff
    style DE fill:#22c55e,color:#fff
    style LCK fill:#6366f1,color:#fff
    style EVT3 fill:#f59e0b,color:#fff
```

**Kritische Invarianten:**

- Ausgezifferter OP-Saldo exakt 0,00
- DATEV-Export: `entry_count > 0` und `file_path` gesetzt
- GoBD: Periodensperre verhindert Nachbuchungen in geschlossener Periode

---

## 4. WMS/Agrar — Ernteannahme & Rückverfolgbarkeit

**Kette:** Annahme → Waage → Lot → Silozelle → QS-Freigabe → Trace

```mermaid
flowchart LR
    ACC[Ernteannahme\nnetto_gewicht_kg] -->|Wiegeschein| W
    W[Wiegeschein\nwt_id] -->|Lot-Erstellung| L
    L[Lot\nlot_number] -->|Einlagerung| SC
    SC[Silozelle\nstock ≤ capacity] -->|QS-Prüfung| QS
    QS{QS-Ergebnis} -->|freigegeben| TR
    QS -->|gesperrt| BLK2([Lot gesperrt\nkein Versand])
    QS -->|bedingt| TR
    TR[Trace-Record\nharvest_acceptance_id\nsilo_cell_id]

    L -.->|Event: lot.created| EVT4((NATS))
    QS -.->|Event: qs.result.set| EVT4

    style TR fill:#22c55e,color:#fff
    style BLK2 fill:#ef4444,color:#fff
    style EVT4 fill:#f59e0b,color:#fff
```

**Kritische Invarianten:**

- Silozelle darf `capacity_kg` nicht überschreiten
- QS-Status muss in `{freigegeben, gesperrt, bedingt}` — kein unbekannter Status
- Trace-Record verknüpft Lot mit Annahme und Silozelle (Rückverfolgbarkeit)

---

## 5. POS/TSE — Kassiervorgang & Tagesabschluss

**Kette:** Bon → Zahlung → TSE-Signatur → Tagesabschluss → DSFinV-K → FIBU

```mermaid
flowchart LR
    BON[Kassenbon\nbon_nummer] -->|Zahlung| ZAH
    ZAH[Zahlung\nbar/EC/digital] -->|TSE-Signatur| TSE
    TSE([TSE\nextern]) -->|signiert| TA
    TA[Tagesabschluss\nZ-Nummer] -->|Export| DSF
    DSF[DSFinV-K\nPflicht §146a AO] -->|FIBU-Buchung| FIB
    FIB[Journal-Entry\nKasse/Erlös]

    TSE -.->|Gate: TSE erreichbar?| EG([Externes Gate])
    DSF -.->|Gate: Finanzamt-Format| EG

    style TSE fill:#f59e0b,color:#fff
    style EG fill:#ef4444,color:#fff
    style FIB fill:#22c55e,color:#fff
```

**Kritische Invarianten:**

- Jeder Bon muss TSE-signiert sein (§146a AO)
- Tagesabschluss: Z-Nummer eindeutig und fortlaufend
- DSFinV-K-Export: gesetzliches Pflichtformat für GoBD/BP

!!! warning "Externe Gates"
    TSE-Dienst und DSFinV-K-Validierung sind externe Systeme. Ausfall → Offline-Queue
    (POS läuft weiter, Nachsignierung beim Reconnect).

---

## 6. QS/Reklamation — Labor bis CAPA

**Kette:** Labor → Sperre/Freigabe → Retoure/Gutschrift → CAPA

```mermaid
flowchart LR
    LAB[Laborprüfung\nProbe] -->|Ergebnis| QSE
    QSE{QS-Entscheid} -->|Freigabe| FRG[Freigabe\nLot freigegeben]
    QSE -->|Sperre| SPR[Sperre\nLot gesperrt]
    SPR -->|Retoure| RET[Retoure\ncredit_memo]
    RET -->|Gutschrift| GUT[Gutschrift\nop_status=ausgeziffert]
    GUT -->|CAPA| CAP[CAPA-Maßnahme\nWiederholung verhindern]

    SPR -.->|Event: lot.blocked| EVT6((NATS))
    RET -.->|Event: return.created| EVT6
    CAP -.->|Gate: Qualitätszertifikat| EG2([Ext. Gate])

    style FRG fill:#22c55e,color:#fff
    style CAP fill:#6366f1,color:#fff
    style EG2 fill:#ef4444,color:#fff
    style EVT6 fill:#f59e0b,color:#fff
```

**Kritische Invarianten:**

- Gesperrtes Lot darf nicht ausgeliefert werden
- Gutschrift muss Kreditoren-/Debitoren-OP ausziffern
- CAPA-Maßnahme schließt den Reklamationszyklus

---

## Legende

| Symbol | Bedeutung |
|---|---|
| 🟢 Grün | Endstatus / Erfolg |
| 🔴 Rot | Blockierung / Fehler |
| 🟡 Amber | Event / NATS-Nachricht |
| 🟣 Lila | Interner Gate / Sperre |
| `EVT` → NATS | Outbox-Event wird publiziert |
| `Ext. Gate` | Abhängigkeit von externem System |

## Semantische Tests

Die Business-Invarianten dieser Prozesskarten sind in
[`tests/test_semantic_e2e_matrix_001.py`](../../tests/test_semantic_e2e_matrix_001.py)
als automatisierte Unit-Tests abgesichert (44 Tests, O2C/P2P/FiBu/WMS).

---

*Generiert: 2026-06-26 · Quelle: `WORKFLOW-PROCESS-MAP-001` · Basis: `app/services/semantic_e2e_chain_service.py`*
