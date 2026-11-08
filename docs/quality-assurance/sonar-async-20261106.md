# Sonar Async 2026-11-06

Asynchrone Effect-Aufrufe nutzen die vorhandene Fehlerbehandlung der jeweiligen Loader. Einkaufsaktionen warten ihre Nachladung ab; der Wizard behandelt Validierungsfehler im vorhandenen Fehlerdialog. Fehler der Zahlungsaktionen werden in den Pending-Aufträgen behandelt.

IBAN-Lookups ergänzen ausschließlich lokale Formularentwürfe und setzen sie auf geändert; sie speichern nicht. Veraltete Antworten nach einem IBAN-Wechsel werden ignoriert. Bankname und BIC werden nur ersetzt, wenn der jeweilige aktuelle Wert seit Beginn des Lookups unverändert ist. So aktualisiert ein IBAN-Wechsel alte Daten, während zwischenzeitliche manuelle Eingaben erhalten bleiben. Beim Zahlungslauf verwendet die Neuanlage keine künstliche ID `new`; ausdrückliches Speichern nutzt den Create-Weg.

Gezielte Vitest-Abnahme: `debitoren-iban-lookup.test.tsx` und `zahlungslauf-iban-lookup.test.tsx`, sieben Tests bestanden. Geprüft sind lokale Anreicherung ohne implizites Speichern, ein Lookup je Eingabe, veraltete Antworten, manuelle Änderungen während des Abrufs und ausdrückliches Speichern einschließlich POST statt PUT beim Zahlungslauf. Der Debitor-Mock bildet `updateData` als Speicher-Alias ab. Zusätzlich bestand `bank-account-form-contract.test.tsx` (ein Test). Die abschliessende vollstaendige Frontend-Typpruefung durch den Lead ist gruen.
