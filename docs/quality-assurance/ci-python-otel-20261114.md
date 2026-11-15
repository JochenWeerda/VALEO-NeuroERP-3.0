---
title: Python OpenTelemetry Trace-Kontext Sicherheitskorrektur
type: qa
audience: [entwickler, qa, sicherheit]
owner: Codex
status: active
last_reviewed: 2026-11-14
---

# Python OpenTelemetry Trace-Kontext Sicherheitskorrektur

Slice `CI-PYTHON-OTEL-20261114`. Der CI-Bericht von Lauf 43574426020
meldete `opentelemetry-api` 1.45.1 mit CVE-2026-126360. Laut
[Herstelleradvisory](https://github.com/open-telemetry/opentelemetry-python/security/advisories/GHSA-mf5v-w3w3-f6cg)
koennen manipulierte Trace-Kontexte mit Zeilenumbruch aus nicht-HTTP-Carriern
quadratische Laufzeit ausloesen; 1.45.2 begrenzt die Eingabe vor der Auswertung.

Root-Requirements setzen API, SDK und OTLP-HTTP-Exporter auf 1.45.2 und die
FastAPI-/SQLAlchemy-Instrumentierung auf 0.66b2. Das
[SDK-Metadatum](https://pypi.org/pypi/opentelemetry-sdk/1.45.2/json) bindet
API 1.45.2 und semantische Konventionen 0.66b2 exakt; die vorherigen
Instrumentierungspins waeren daher nicht kompatibel. Andere Pakete wurden nicht
gezielt angehoben; keine Scanner-Ausnahme.

In isolierter Python-3.11-Umgebung wurden die fuenf Pakete samt Abhaengigkeiten
installiert; `pip check` ergab keine Konflikte. Der neue subprocess-begrenzte
Vertrag bestaetigt unveraenderte gueltige Trace-/Span-ID und zuegige Ablehnung
von 200.000 Zeichen mit CRLF, CRLF allein und Ueberlaenge. Ein Audit der
isolierten Umgebung meldete keine OpenTelemetry-Befunde, aber 23 Befunde in
den von Python mitgelieferten alten venv-Bootstrappaketen `pip` und
`setuptools`; dies ist kein erfolgreicher Umgebungs-Gesamtaudit.
Der erste lokale `pip-audit -r requirements.txt` endete am 14.11.
gegen 14:10 MEZ ohne OpenTelemetry-Fund, aber mit drei anderen Befunden fuer
transitives `soupsieve` 2.10 (CVE-2026-126190, CVE-2026-126193,
CVE-2026-126191). Ursache der Abweichung zum CI-Ausgangsartefakt mit 4.1:
lokales Python 3.11.0 unterschreitet das vom
[Paket](https://pypi.org/pypi/soupsieve/4.1/json) verlangte 3.11.5;
CI verwendete 3.11.18. Auch 4.0 erfordert mindestens 3.11.5. Root-README
nennt diese Mindestversion und das Manifest pinnt gezielt 4.1, statt eine
anfaellige Ersatzversion aufzuloesen. Herstellerhinweise:
[Descendant-Kombinator](https://github.com/facelessuser/soupsieve/security/advisories/GHSA-mmhr-3c5m-f64f),
[Selector-ReDoS](https://github.com/facelessuser/soupsieve/security/advisories/GHSA-6655-6qjp-jx7x),
[verschachtelte Selektoren](https://github.com/facelessuser/soupsieve/security/advisories/GHSA-7g44-g9rc-x53w).

Eine getrennte, wiederverwendbare Python-3.11.13-Umgebung bestand `pip check`
und die zwei gezielten Tests fuer Trace-Kontext sowie die echte Produkt-/Preis-/
Bildselektorverarbeitung des Wettbewerbsmonitors ohne Netz. Der erneute
`pip-audit -r requirements.txt` mit Python 3.11.13 (Start 14.11. 14:17 MEZ)
meldete keine bekannten Schwachstellen und Exit 0. Der Scanner ignorierte
fehlerhaft lesbare Cache-Eintraege und fragte erneut ab. Dies ist ein
Windows-Nachweis; Linux-CI-Nachlauf steht aus. Die isolierte Umgebung enthielt
die betroffenen fuenf OpenTelemetry-Pakete, BeautifulSoup, Soup Sieve und die
Pruefwerkzeuge, nicht die vollstaendige Projektinstallation. Keine Datenbank,
Container oder Migration.
