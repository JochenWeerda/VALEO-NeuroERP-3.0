# Simulierte externe Production-Readiness-Pruefung

Stand: 2026-06-09

> Eine Simulation ersetzt keine gesetzliche Zertifizierung, Herstellerpruefung oder Unterschrift.
> Fehlende Live-Evidenz bleibt ein blockierendes externes Gate.

## Simulierter Steuerberater / GoBD-Pruefer

Standard: GoBD, AO §§ 146/147, VALEO-Zusatzstandard

- `GOBD-01` PASS: Unveraenderbarkeit und Gegenbuchung
- `GOBD-02` PASS: Nachvollziehbare Audit-Kette
- `GOBD-03` PASS: Datenzugriff und Export
- `GOBD-04` EXTERNAL_GATE: Verfahrensdokumentation und Betriebsnachweis
  Externes Gate: Steuerberater-Abnahme der konkreten Verfahrensdokumentation

## Simulierter Kassen-Nachschau-/KassenSichV-Pruefer

Standard: KassenSichV Stand 14.01.2026, DSFinV-K 2.4, strengere VALEO-Gates

- `KASSE-01` PASS: Unmittelbarer Transaktionsstart und Abschluss
- `KASSE-02` PASS: Belegpflichtdaten und Signaturreferenz
- `KASSE-03` PASS: DSFinV-K 2.4 Export- und Tagesabschluss-Gate
- `KASSE-04` EXTERNAL_GATE: Reale TSE-/Pruefwerkzeugvalidierung
  Externes Gate: Hersteller-/Pruefwerkzeug-Abnahme mit produktiver TSE

## Simulierter BSI-/ISO-27001-Auditor

Standard: BSI IT-Grundschutz plus VALEO Null-Toleranz fuer ungepruefte Produktionskonfiguration

- `SEC-01` PASS: IAM, Least Privilege und Tenant-Isolation
- `SEC-02` PASS: Blockierende High/Critical-Scans und SBOM
- `SEC-03` PASS: Backup und regelmaessiger Restore-Test
- `SEC-04` EXTERNAL_GATE: Incident-, Rollback- und Monitoring-Vertrag
  Externes Gate: Betriebsuebung mit realem Cluster und Alarmkanal

## Simulierter Datenschutzbeauftragter

Standard: DSGVO Art. 5, 25, 30, 32, 33/34 plus VALEO-Nachweispflichten

- `DSGVO-01` PASS: Privacy by Design und Zugriffstrennung
- `DSGVO-02` PASS: Verzeichnis von Verarbeitungstaetigkeiten
- `DSGVO-03` PASS: Breach-Prozess und Fristnachweis
- `DSGVO-04` EXTERNAL_GATE: AVV, DSFA und reale Organisationsfreigabe
  Externes Gate: DSB-/Rechtsfreigabe und unterschriebene AVV/DSFA

## Simulierter Betriebs-/Notfallpruefer

Standard: BSI Datensicherung/Notfallmanagement plus strengere Release-Evidenz

- `OPS-01` PASS: Immutable Release-Artefakte und geschuetzte Environments
- `OPS-02` PASS: Migration vor Rollout und automatischer Smoke
- `OPS-03` PASS: Rollback bei fehlgeschlagenem Smoke
- `OPS-04` EXTERNAL_GATE: Wiederanlauf, RTO/RPO und Alarmierung im Zielbetrieb
  Externes Gate: Beobachteter Restore-/Incident-Drill im produktionsnahen Cluster

## Gesamturteil

Repo-seitige Evidenz ist nur dann bestanden, wenn alle referenzierten Artefakte vorhanden sind.
Der Go-live bleibt blockiert, solange mindestens ein externes Gate nicht durch reale Evidenz geschlossen ist.
