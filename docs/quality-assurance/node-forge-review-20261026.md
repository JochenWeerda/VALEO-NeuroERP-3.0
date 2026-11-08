---
title: node-forge Quellreview 2026-10-26
type: qa
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-26
---

# Erneute Evidenzpruefung

Offizielle Registry erneut abgefragt: node-forge1.4.0, dist.integrity identisch zur gespeicherten Originalintegritaet. Upstream-PR https://github.com/digitalbazaar/forge/pull/1152 ist offen und nicht gemergt; Kopf ceba34402e329f0365134f23fe19898756527d65. Aktueller Diff abgefragt: die zusaetzliche Pruefung der verschachtelten DigestAlgorithm-Kinder einschliesslich optionalem NULL entspricht exakt dem lokalen lib/rsa.js-Hunk. Kein verfuegbares neueres Paket als unbelegter Fix behauptet.

Frischer unveraenderter Produktionsaudit auf dem integrierten PR44-Lockfile: ein High-Befund fuer node-forge1.4.0. Audit-Exit1 bleibt als Rohbefund erhalten. Separater strikter Gate: scanner_findings1, source_backported1, blocked0, release_allowedtrue; exakte Patch-/Manifest-/Lock-/Installationshashes stimmen. Alle eingebundenen Laufzeitvertraege bestanden (12+2+5+5+8). RSA prueft gefaelschte verschachtelte DigestAlgorithm-Strukturen mit und ohne NULL sowie gueltige SHA256/SHA384-, PSS- und Zertifikatsignaturen.

Nur reviewed_on fuer node-forge auf2026-10-26 aktualisiert. review_by bleibt2026-10-28. Keine Schwellenaenderung, Ausnahme, Fristverlaengerung oder Verschleierung des Rohbefunds. Nach Fristablauf blockiert der bestehende Gate weiterhin. Artefakte des lokalen Audit-/Entscheidungslaufs liegen im nicht versionierten artifacts-Bereich.

Unabhaengiger CI-Nachweis: Docs Build40278987427 auf94c483cc0 ist success; damit ist der Inventar-Drift aus PR44 im Integrationszweig behoben. Gesamt-CI und Studio-Fertigstellung sind daraus nicht abgeleitet.
