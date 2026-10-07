---
title: CPython 3.13.16 - Herstellerfix und verbleibender POP3-Backport
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: lokal_geprueft
last_reviewed: 2026-10-07
---

# CPython-Herstellerfix

`Dockerfile.backend` verwendet jetzt echtes Python 3.13.16 in beiden Stages.
Das [Herstellerrelease vom 30.09.2026](https://www.python.org/downloads/release/python-31316/)
behebt CVE-2026-82049: Tarfile loest das Ziel eines Hardlinks vor dem Verlinken
auf, damit ein kopierter relativer Symlink nicht aus dem Extraktionsziel fuehrt.
Der offizielle Docker-Manifest `python:3.13.16-slim-bookworm` ist vorhanden.
Keine Versionsfaelschung, Scanner-Ausnahme oder Absenkung eines Gates.

## Bewusste Bereinigung

Die bisherigen IDNA-, URL-Credential- und ZIP-Backports sind in der neuen
Herstellerlaufzeit durch dieselben bestehenden Verhaltenstests abgedeckt.
Ihre Patchdateien und die drei zusaetzlichen Stdlib-Kopien im Runtime-Stage
sind entfernt. `config/security/cpython-3.13.16/` enthaelt nur noch den
POP3-Backport mit unveraenderter SHA256, Lizenz und aktualisierter Herkunft.
Die alten Pfadreferenzen in historischen Abnahmen bleiben historische Evidenz.

Der POP3-Schutz ist weiterhin erforderlich: Das unveraenderte offizielle
Windows-Embed-Release akzeptiert noch CR, LF, NUL und DEL im Befehl.
Mit dem echten Backport werden diese vor dem Schreiben zurueckgewiesen;
ein normaler USER-Befehl funktioniert weiterhin. Der Builder prueft weiterhin
die exakte Interpreterversion und wendet Patches ohne Fuzz an. Beide Stages
fuehren die vollstaendige Behavior-Pruefung aus.

## Abnahme und Grenzen

- Offizielles Windows-Embed-Python 3.13.16 plus genau ein POP3-Backport:
  fuenf Sicherheitstests bestanden; keine zusaetzlichen Bibliotheken installiert.
- Neuer Tarfile-Vertrag prueft den tatsaechlichen Aufruf von `os.link` mit dem
  aufgeloesten Ziel. Dateisystemoperationen sind isoliert gemockt, damit der
  Test ohne Windows-Symlinkrechte und ohne reale Dateien ausserhalb des
  Extraktionsziels auskommt.
- Derselbe neue Vertrag scheitert wie erwartet auf dem offiziellen
  `v3.13.15/Lib/tarfile.py`: `realpath` wird dort vor dem Link nicht aufgerufen.
- Unveraenderter POP3-Patch passt mit `git apply --check` auf die offizielle
  3.13.16-Quelle; SHA256 `efec029f5da02b71f709ec26a2b1abb45ab5e754f230d4bebc0f6a21192c23a5`.
- Kein Image-Pull, Docker-Build, neuer Container, DB-Test, Reset oder Migration.

Linux-Imagebau und aktueller Grype-Scan bleiben im bestehenden Security-Workflow
nachzuweisen. Die lokale Windows-Abnahme ersetzt diese nicht. Ein offener alter
Code-Scanning-Alert ist kein Nachweis fuer das neu gebaute Image. Node-Audit und
weitere Security-Befunde sind mit diesem Interpreterfix nicht geschlossen.
