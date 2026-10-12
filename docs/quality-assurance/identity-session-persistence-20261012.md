# Dauerhafter Sitzungszustand im bestehenden Redis

Stand: 2026-10-12. Slice `IDENTITY-SESSION-PERSISTENCE-20261012`.

Das ERP-Backend verwendet den vorhandenen Docker-Redis mit dem vorhandenen
`redis_data`-Volume. Die Konfiguration aktiviert AOF und `appendfsync always`.
Ein bestaetigter Widerruf soll auch einen Prozessneustart ueberstehen; deshalb
werden Schreibvorgaenge synchron gespeichert. Das verursacht mehr Schreiblatenz
als die bisherige Cache-Konfiguration. Der Sicherheitszustand hat hier Vorrang.

Der kontrollierte Nachweis lief aus dem tatsaechlichen Backend: eine eigene
synthetische Sitzung wurde widerrufen, derselbe Redis-Dienst neu gestartet,
und dieselbe Sitzung danach weiterhin mit 401 abgewiesen. Der eigene Testschluessel
wurde entfernt; vorhandene Daten und das Volume blieben erhalten.

Auf diesem Rechner erreicht `127.0.0.1:6379` aus Windows einen separaten
Windows-Redis. Lokale Sitzungsvertraege sind deshalb kein Neustartnachweis fuer
Docker. Dieser Dienst wurde nicht geaendert. Die 69 lokalen Sitzungs-, RSA- und
Transportvertraege bestanden; die Docker-Gegenprobe erfolgte separat.

Die versuchte engere Docker-Portbindung wurde von Windows blockiert. Die vorher
funktionierende Portbindung wurde wiederhergestellt; der Dienst laeuft wieder.
Eine Einschraenkung dieser Hostbindung ist damit nicht geliefert.

Dieser Slice liefert die dauerhafte Infrastrukturkonfiguration. Die vollstaendige
Session-API, Streaming-Widerrufe, Providerabmeldung, Benutzerdeaktivierung und
Agentensteuerung bleiben im uebergeordneten Identitaetsclaim. Der aktuelle
Backend-Nachweis verwendet dessen vorbereitete Sitzungsimplementierung; er ist
keine Abnahme der gesamten Architektur. AOF ersetzt keine Sicherung des Volumes.
