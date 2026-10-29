---
title: Studio-Transportgrenzen und Schutz der ERP-Identitaetskopfzeilen
type: reference
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Befund und korrigiertes Verhalten

Eingebettete Twin-/Kalender- und Zusammenfassungsendpunkte wurden bisher nicht vollstaendig gegen den Studio-Quellenkatalog geprueft. Diese Renderer laden selbst Daten. Der gemeinsame Axios-Client haengte zudem ERP-Anmeldung und Mandantenkontext auch an absolute Fremdziele an. Eine freie eingebettete URL war deshalb ein echter Ausweichweg gegen die bisherige Transportgrenze.

Der Client prueft jetzt vor Tokenbeschaffung und Kopfzeilenaufbau die tatsaechliche Zielorigin gegen konfigurierte API und aktuelle App. Fremdziele, Protokoll-/Benutzerinfo-Tricks, abweichende Request-Basis und mehrdeutige Backslash-/Steuerzeichen-URLs werden vor dem Adapter abgewiesen. Fehlermeldungen enthalten die URL nicht. Legitime konfigurierte API-/Proxyziele behalten ihre normale Anmeldung.

Serverseitig werden auch eingebettete endpoint-, summaryEndpoint- und countEndpoint-Felder gegen die bestehende Leseliste geprueft. Schreibend deklarierte Helferendpunkte muessen registriert sein; freie Erstellung ist kein Studio-Command. Maskennavigation bleibt auf eindeutige lokale Pfade beschraenkt. Das bisherige grain.v1-Profil zertifiziert keine unerfassten Creation-/Twin-/Kalender-/Quellenvorschlagswege. Seine SQL-Fachkette, Rollen, Vier-Augen-Regel und Inhaltsbindung bleiben unveraendert.

## Vorschau ohne eingebettete Live-Transporte

Ein zentraler RenderPlan-Vorschauvertrag entfernt nicht abgenommene eingebettete Live-Widgets und Navigation, schaltet Fachaktionen und Mikrofon in der Vorschau ab und entfernt Zeilen-/Sammelaktionen. Die betreffenden Widgets werden als noch separat abzunehmend kenntlich gemacht. Er veraendert weder die gespeicherte Definition noch den gecachten Plan der echten Maske. Die bereits genehmigte reine Getreide-Kalkulationsprobe bleibt bedienbar; ihre eigenen Tests pruefen weiterhin die ausschliesslich synthetische Berechnung.

## Nachweise

16 Ziel-/Axiosfaelle: erlaubte Aufrufe erreichen den abgefangenen Adapter mit normaler Testanmeldung; verbotene Aufrufe erreichen weder Tokenbeschaffung noch Adapter. Es wurden keine echten Fremdverbindungen aufgebaut und keine echten Zugangsdaten benutzt.

Zwei echte Renderer-/Cachefaelle pruefen ausbleibende Live-GETs fuer eingebettete Ansichten und unveraenderten Live-Plan. Zwei bestehende interaktive Kalkulationsfaelle bleiben gruen. Alle 31 serverseitigen Transportfaelle bestehen, einschliesslich des echten Speicherendpunkts: HTTP 400 vor Persistenz. Der kombinierte Lauf hatte 128 weitere bestandene Faelle inklusive SQL-Freigabe; der einzige zuerst falsche Test-Routerpfad wurde korrigiert und der HTTP-Fall sowie alle 31 Transportfaelle erneut gruen abgenommen.

Vollstaendige Frontend-Suite: 1373 Tests in 274 Dateien bestanden. Typpruefung und regulaere Commitpruefungen gehoeren zur Endabnahme. Kein API-Endpunkt oder MCP-Schreibrecht hinzugefuegt, keine Datenbank/kein Container angelegt. Das ist eine gezielte Transportabsicherung, keine Behauptung der vollstaendigen Belegmigration.
