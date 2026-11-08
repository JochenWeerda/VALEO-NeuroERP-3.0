---
title: Lokales Frontend auf Port 3000 aktualisiert
type: reference
owner: Codex
status: teilweise abgeschlossen
last_reviewed: 2026-10-23
---

# Lokale Laufzeitaktualisierung

Port3000 zeigte ein statisches Frontendimage vom16.Oktober ohne Quellcode-Mount. Quellcodeaenderungen konnten deshalb nicht sichtbar werden. Dockerfile.frontend musste dafuer nicht geaendert werden.

Das bisherige Image ist unter valeo-neuro-erp-frontend-web:before-ui-refresh-20261023 erhalten. Ausschliesslich frontend-web neu gebaut und mit --no-deps --no-build ersetzt. Neuer laufender Image-Digest: sha256:9dc7e71d9f4f471fa0a4018f95f640c3fb5ee240482bcbc6c2771d708413044c. Container erstellt2026-10-23, /healthz200 und Dockerstatus healthy. Kein Datenbank-/Volume-/Image-Prune und keine neue Testdatenbank.

Der Build erzeugte942 Routen und bestand. Nach echtem Browserreload ist die neue Adaptive-Workspace-Oberflaeche sichtbar (Dialog, Handlungsbedarf, Agrar-Kette, Inbox und Disposition). Screenshot artifacts/workspace-frontend-current-20261023.png zeigt den tatsaechlichen Zustand, inklusive Inbox404; kein Nachweis einer vollstaendigen Fachabnahme.

Das Backend besitzt vier langlebige Uvicornworker und eingebundene Quellen, aber sein Image stammt vom17.September. Bei der Bestandsaufnahme stand seine Entwicklungsdatenbank valeo_neuro_erp auf harvest_rule_store_20261015 und besass die neue Tour-Mandantenspalte nicht. Nicht mit dem gemeinsamen, bereits migrierten valeo_probe verwechseln. Der erste laufzeitgetreue Import des aktuellen Quellcodes scheiterte an alten lokalen Arbeitskopien: Dokumentenrepository ohne DocumentAlreadyExists/DocumentOwnershipError, Finanzrollen ohne freigegebene Konstanten, deps ohne effective_roles und Webshopservice ohne WebshopBestellungUnbekannt. Die konkreten Diffs wurden geprueft und nur die bereits veroeffentlichten fuehrenden Sicherheitsvertraege wiederhergestellt; Vorfassungen lokal in artifacts gesichert. Drei weitere reine Auth-Ruecknahmen sowie14 verschwundene Dokument-Schreibguards wurden ebenso gezielt korrigiert, Cursors Inbox-Mount blieb erhalten. Keine pauschale Ruecknahme anderer WIP-Dateien. Danach bestaetigte der Containerimport current_source_imports=true und inbox_registered=true. Im Root-Rollenvertrag bestanden57 Testfaelle; der Prozess wurde nach dem vollstaendigen Pytestbericht unterbrochen, daher kein zusaetzlicher sauberer Exit0-Gatenachweis behauptet.

Die sichtbare Inbox404 und die fehlende vollstaendige Backendabnahme bleiben offen, bis die geladenen Routen und Schema-Voraussetzungen nachgewiesen sind. Der lokale Frontendbuild enthaelt laufende Entwicklungsarbeit; er ist kein Ersatz fuer die CI-/Releasefreigabe des Workspace-Slices.


## Regulaerer Schema-Vorlauf und Backend

Die neun ausstehenden Revisionen wurden statisch geprueft: keine Upgrade-Datenloeschung oder Rechtevergabe. Entwicklungsdatenbank95.4MB, vorab0fremde aktive Transaktionen. Lokales komprimiertes Backup5.4MB unter artifacts/runtime-before-schema-20261023.dump; keine weitere Datenbank. Ausschliesslich Backend kurz pausiert, regulaeres alembic upgrade head mit Lock-/Statementtimeout, danach wieder freigegeben. Erfolg: loading_stop_fk_20261023 und sowohl Tour- als auch Inbox-Mandantenspalte konkret nachgewiesen. Vorherige Worker waeren bei Fehler unveraendert fortsetzbar gewesen. Anschliessend nur bestehenden Backendcontainer neu gestartet, keine Neuerstellung anderer Services. Anwendungs-/Browser-Nachlauf noch in Arbeit.

## Laufzeitnachweis nach Docker-Wiederanlauf

Nach regulaerem Docker-Wiederanlauf fuehrten vier parallel initialisierende Backendworker auf dem16GB-Host zu Speicherdruck. PostgreSQL beendete seine normale Wiederherstellung ohne Reset. docker-compose.local-preview.yml startet dieselbe Backendinstanz mit einem Worker und ergaenzt fuer dieselbe Frontendinstanz den Loopback-Port3001. Bestehende Compose-Konfiguration und Umgebungswerte wurden erhalten; keine zusaetzliche Datenbank oder Containerkopie.

Compose meldet Backend healthy. Lokale HTTP-Pruefung: Backend /health200, /api/v1/documents/inbox401 ohne Anmeldung statt404. Beide Frontendports3000 und3001 liefern /healthz200. Die abschliessende Studio-Sichtpruefung ist offen: Browser Use verweigerte den Zugriff auf den vorhandenen Fehler-Tab aufgrund seiner URL-Sicherheitsrichtlinie. Kein Umgehen der Sperre. Der vorherige Screenshot mit Inbox404 bleibt ausschliesslich historischer Zwischenstand.
