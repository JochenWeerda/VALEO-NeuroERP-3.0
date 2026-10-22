---
title: PHP-Sicherheitspruefung 22.10.2026
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-22
version: 1.0.0
description: Offizielles PHP-Advisory gegen lokale Projektlaufzeiten abgeglichen.
---

# PHP-Sicherheitspruefung

Das [offizielle Advisory vom 21.10.2026](https://www.php.net/archive/2026.php#2026-10-21-5) beschreibt CVE-2026-109618 und CVE-2026-109619 (nicht authentifizierte Codeausfuehrung). Reparierte Upstream-Versionen: 8.5.12, 8.4.27, 8.3.36 und 8.2.35; Distributoren koennen Rueckportierungen liefern. Fuer PHP 8.1 und aelter gibt es keine Upstream-Sicherheitsversorgung mehr.

## Lokaler Nachweis

Am 22.10. wurden alle 25 laufenden vorhandenen Projektcontainer mit `command -v php` geprueft: kein Treffer. Der einzige gestoppte Container ist der Keycloak-Pruefcontainer (Java), kein PHP-Dienst. Container wurden weder gestartet noch ersetzt. Auf Windows kein Treffer fuer Get-Command/where php, keinen laufenden PHP-/Apache-/IIS-/Nginx-Prozess und keine registrierte PHP-/XAMPP-/Wamp-/Laragon-Installation in den 64-/32-Bit- und Benutzer-Uninstallzweigen gefunden. Bekannte Installationsorte C:/php, C:/xampp/php, C:/wamp64 und C:/laragon/bin/php liefern keine php.exe. Projektdateien und Docker-/Compose-/Composer-Definitionen liefern keinen PHP-Bezug.

Damit ist fuer den geprueften lokalen VALEO-Betrieb keine zu aktualisierende PHP-Laufzeit nachgewiesen. Es wurde kein Patch als installiert behauptet und keine unbenutzte PHP-Abhaengigkeit hinzugefuegt. Die Pruefung ist kein Vollscan aller Dateien oder fremder Server; nicht registrierte portable Installationen ausserhalb der geprueften Orte und externe Hostingkonten sind damit nicht abgedeckt. Bei einer spaeter identifizierten PHP-Komponente muss deren tatsaechliche Laufzeit samt Webserverarbeitern auf die passende reparierte Version aktualisiert und nach Neustart erneut geprueft werden.
