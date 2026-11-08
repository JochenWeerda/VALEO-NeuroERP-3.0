---
title: Studio-Publikation an serverseitigen Pruefstand binden
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-13
---

# Studio-Publikationssnapshot

Die HTTP-Publikation prueft Katalog und Readiness einer gelesenen Entwurfskopie. Der anschliessende Statuswechsel verlangt jetzt exakt denselben Inhalt, Mandanten, Entwurf, Editor, Status und Aenderungszeitpunkt. Zwischenzeitliche Aenderungen werden mit 409 abgewiesen statt ungepruefte Metadaten zu veroeffentlichen. Fehlende Entwuerfe ergeben auch beim zweiten Schritt 404.

SQL-Speichern und Statuswechsel sperren die betreffende mandantenbezogene Zeile mit SELECT FOR UPDATE bis Commit/Rollback. Der explizite Test-Speicher serialisiert beide Schreiboperationen mit RLock. Aktualisieren einer unbekannten SQL-Entwurfs-ID legt keinen neuen Entwurf mehr an.

Abnahme: 78 Faelle in test_meridian_screen_studio_api.py, test_meridian_screen_studio_persistence.py, test_studio_token_identity.py, test_studio_publish_snapshot.py und test_uix090_studio_validation.py bestanden auf dem gemeinsamen valeo_probe (control_findings_20261013). Neue HTTP-Negativfaelle veraendern Inhalt, Editor beziehungsweise Status innerhalb der Pruefung und verlangen Ablehnung ohne Runtime-Publikation. Der SQL-Fall belegt Ablehnung eines veralteten Snapshots und Erfolg eines unveraenderten Snapshots. Keine neue Datenbank, Migration oder Ressourcenbereinigung.

Grenzen: Die Bindung gilt fuer den serverseitigen HTTP-Pruefschritt. Ein verpflichtender vom Browser angezeigter Review-Hash, eine unveraenderliche Publikationshistorie und ein geschlossenes Review-Statusmodell sind weiterhin offen. Interne set_status-Aufrufer koennen den optionalen Snapshot noch weglassen; sie ersetzen keine HTTP-Freigabe. Das bisherige Speicher-Fallback und dessen Mehrprozessverhalten bleiben separate Arbeit. Diese Tests beweisen keine vollstaendige Konkurrenzabnahme mit zwei gleichzeitig laufenden SQL-Transaktionen und keine reale Browserabnahme.
