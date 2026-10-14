# DOC-STORE-MANDANT: Der alte Dokumentspeicher liefert Listen nur im eigenen Mandanten

Stand: 2026-10-14 · Slice `DOC-STORE-MANDANT-20261014` · Folge aus `FIN-LESEWEGE-MANDANT-20261013`

## Befund

Beim Abschluss von FIN-LESEWEGE-MANDANT war offen geblieben, dass der Mandantenfilter des alten
Dokumentspeichers (`documents`) Belege ohne Mandant mitliefert. Die Bestandsaufnahme der Aufrufer ergab mehr:

| Weg | Zustand bis 14.10.2026 |
|---|---|
| `DocumentRepository.list_documents` / `count_documents` | Filter `tenantId` hieß „dieser Mandant **oder kein Mandant**“ |
| `list_docs` (`compat_helpers`) und `_list_docs` (`compat.py`) | ohne Mandant **kein Filter** — alle Mandanten; `list_docs` fiel bei leerer Liste zusätzlich auf den Prozessspeicher zurück |
| Prozessspeicher (`list_from_store` ohne Repository) | ebenfalls „oder kein Mandant“ |
| Kundenportal `GET /portal/bestellungen`, `/rechnungen`, `/anfragen`, `/naehrstoffbilanzen`, `/dashboard`, `/feldbuch` (Rückfall) | lasen Aufträge, Rechnungen, Anfragen und Lieferscheine **ohne Mandant** — die Belege aller Mandanten |
| `GET /sales/{doc_type}` (Verkaufsbrücke) | **ohne Mandant** — alle Mandanten |
| Bestellungen (`PurchaseOrderService`: Liste, Einzelabruf, Änderungsprotokoll) | hatte der eigene Mandant keine Bestellung, kamen die Bestellungen **aller Mandanten** |

Der Mandant selbst war in allen Fällen vorhanden und geprüft (`get_tenant_id` aus der Anmeldung) — er wurde nur
nicht benutzt.

## Was jetzt gilt

- Der Filter ist streng: ein Beleg ohne Mandant gehört niemandem, in Datenbank und Prozessspeicher.
- Lesen ohne Mandant liefert nichts. Kein Rückfall auf den Prozessspeicher.
- Portal, Verkaufsbrücke und Bestellweg lesen im Mandanten der Anmeldung; der Rückfall auf fremde Bestellungen
  ist entfernt.

## Nachweis

- `tests/test_dokumentspeicher_mandant.py` (11, frische Datenbank `valeo_probe`; vor der Änderung alle rot):
  Liste und Zählung ohne fremde und mandantenlose Belege; ohne Mandant leer; kein Prozessspeicher-Rückfall;
  Prozessspeicher streng; vier Portalwege und Dashboard; Verkaufsbrücke; Bestellung ohne fremden Rückfall.
- Regressionsmenge: 24 Testdateien, die Dokumentspeicher, Compat-Dienste, Portal und Bestellweg berühren —
  439 grün, 7 übersprungen, 4 rot. Die vier (`test_compat_einkauf_anfragen.py` ×3: 403 ohne geprüften Mandanten;
  `test_process_kernel_wave1_contracts.py::test_payment_run_approve_…`: erwartetes SQL) sind auf HEAD ohne diese
  Änderung ebenso rot — vorbestehend, nicht Teil dieses Slices.
- OpenAPI: generierte Spezifikation gegen die committete verglichen — keine Abweichung.
- **Gewachsene Datenbank** (`valeo_neuro_erp`, nur gelesen): 11 Belege im Speicher; ohne Mandant sind die sechs
  bekannten Ausgangsrechnungen `INV-Q-…` und eine Eingangsrechnung. Sie erscheinen in keiner Liste mehr.
  `scripts/belege_mandant_nachtragen.py` ordnet zu, was eine Buchung eindeutig nennt. Nichts geändert.

## Offen (nicht in diesem Slice)

- **Einzelabruf** `DocumentRepository.get_document` kennt keinen Mandanten (die Belegnummer ist systemweit
  eindeutig). Jeder Weg muss den Mandanten des gelesenen Belegs selbst prüfen; die Finanzwege tun das seit
  FIN-LESEWEGE-MANDANT, andere Aufrufer (`ap_approval_workflow`, `finance_clearing`, `op_skonto_auszifferung`,
  `sales_credit_notes`, `sales_invoice_einvoice`, `mcp_execution_service`, …) sind nicht geprüft.
- **Kundentrennung im Portal:** Das Portal zeigt jetzt den eigenen Mandanten — aber innerhalb des Mandanten
  weiterhin die Belege **aller Kunden**. Eine Portal-Anmeldung, die an einen Kunden gebunden ist, gibt es auf
  diesen Wegen nicht (`portal_shop` nimmt den Kunden aus dem Token-`sub`, aus `X-User-ID` oder aus einem
  Parameter). Das ist eine Entscheidung über das Identitätsmodell des Portals.
- **Tabellen ohne Mandantenspalte:** `domain_ops.ops_dokumente` und `ops_rahmenvertraege` (gewachsen: je 0 Zeilen)
  sowie `ops_zertifikate` (61 Zeilen; das ORM-Modell kennt die Spalte ebenfalls nicht). Die Portalwege
  `/portal/dokumente`, `/vertraege`, `/zertifikate` und die Dokumentkachel des Dashboards lesen daraus mandantenlos.
  Braucht Migration und eine Zuordnung der 61 Zertifikate.
