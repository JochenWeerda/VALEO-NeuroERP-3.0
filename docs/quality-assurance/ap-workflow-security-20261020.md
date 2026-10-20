# AP-Freigabe und Buchung: Sicherheitsabnahme 2026-10-20

## Verbindlicher Vertrag

HTTP, native Maskenaktion und reale Prozesskernel-Kommandos verwenden denselben
AP-Fachservice. Mandant, vollstaendige Urheberkennung und bestehende Finanzrollen
kommen aus gepruefter Identitaet. Aufruferfelder requested_by/approved_by und
Kernel-issuer_role verleihen keine Rechte. Entscheider sind von Ersteller,
letztem Bearbeiter und Antragsteller getrennt; technische/delegierte Agentenkonten
entscheiden keine menschliche Freigabe.

Jede Entscheidung braucht die aktuelle approval_request_id. Der Antrag bindet
unveraenderten Beleginhalt, Rollenregel, Anzahl unabhaengiger Pruefer und Ablaufzeit.
Alte ungebundene Antraege muessen erneut angefragt werden. Wiederholte gleiche
Stimmen haben keine Doppelwirkung; abweichende Stimmen, fremde Referenzen,
Inhaltsaenderungen und abgelaufene Antraege werden abgewiesen. Unbekannte Zustaende
und Datenbankausfaelle erzeugen keine fingierte Genehmigung.

AP-Pruefung und zentrale Buchungsfreigabe sind getrennte bestehende Fachpruefungen.
Buchung braucht beide sowie offene Periode und gueltige Steuerkontierung. Journal,
OP, Dokument, verpflichtendes FiBu-Audit und Outbox werden gemeinsam abgeschlossen.
Nach Buchung ist die tatsaechliche eigene Journalreferenz fuer den Zahlungsstatus
massgeblich. Abgeschlossene Belege koennen nicht geloescht oder neu freigegeben werden.
Bestehende Dokumente wechseln beim Upsert niemals den Mandanten; Anlage ist insert-only.

Der obsolete MCP-Adapter finance.ap_invoice.freigeben wurde entfernt. Eine generische
Vorschlagsgenehmigung ist kein Ersatz fuer diese konkrete persoenliche Fachfreigabe.
Der Vorschlag bleibt moeglich; die Maskenprojektion sperrt Agentenausfuehrung und zeigt
den Freigabeknopf nur bei serverseitig nachgewiesener Entscheidungsberechtigung.

## Nachweise und Grenzen

Die SQL-Vertraege laufen ausschliesslich auf dem vorhandenen valeo_probe ohne Reset,
Migration oder neue Datenbanken/Container. Rollback-Faelle hinterlassen keine Fachdaten.
Die echten Parallelitaetspruefungen beseitigen nur ihre eigenen Fachdaten; je Lauf bleiben
fuenf minimale synthetische, unveraenderbare Auditzeilen als absichtlicher Nachweis erhalten.
Die vollstaendige synthetische Buchung prueft ausgeglichenes Journal (119/119), OP,
Urheber, Outbox sowie vollstaendigen Rollback bei Outbox-SQL-Fehler.

Dies ist eine Quellcode-/Pruefstandabnahme, keine Behauptung einer Browserabnahme oder
Auslieferung an den lokal noch aus aelteren Arbeitskopien gestarteten Backendcontainer.
Die neun separat dokumentierten physischen Tabellenluecken werden hier nicht durch
Loeschen von Katalogeintraegen verdeckt. Globale Prozesskernel-Persistenz/Idempotenz
anderer Fachkommandos ist durch diesen AP-Slice nicht vollstaendig abgenommen.

Zwischenabnahme: 87 AP-/Kernel-/Steuer-/Zweitwege-Vertraege bestanden; zuvor 565
weitere erfolgreiche Faelle im breiten Lauf, dessen fuenf veraltete Testaufbauten
anschliessend gezielt korrigiert und mit 18 Faellen gruen nachgeprueft wurden.
Frontend: vier Vertragsfaelle und vollstaendige Typpruefung bestanden.
Private Commit-Guards fuer 60 Dateien bestanden. Der gemeinsame Endstand mit
der inzwischen eingegangenen Studio-Lieferung wird separat erneut abgenommen.

## Zusammengefuehrte Abnahme

AP-Meilenstein338b34973 wurde mit der parallelen Studio-Lieferung bis e0a657298
zusammengefuehrt. Drei generierte Konflikte wurden aus den vereinigten Quellen
aufgeloest; keine Fachquellen zurueckgenommen. 572 Backend-/SQL-/Adaptervertraege
bestanden auf unveraenderten kanonischen Anwendungsquellen. Zusaetzlich bestanden
24 Faelle der tatsaechlich mitgelieferten Einkaufslisten-Kommandos, Rechteprojektion
und Studio-Ratsche: zusammen596 Backendpruefungen. Zwei tatsaechliche Kernel-Buchungsfaelle pruefen
Erfolg und kompletten Outbox-Fehlerrollback; geaenderte Steuersaetze koennen keine
abweichenden Betraege unter alter AP-Pruefung buchen.

Alle ausgefuehrten Gates bestanden: exakte Godfile- und Paginierungsratsche,
Codeinventare, Screen-Aktionskatalog, MCP-Map und -Referenz, CLI-Register,
Agent-Handbuch, C4, vollstaendige Architekturzuordnung und strikter Architekturdrift.
OpenAPI:3222 Pfade, zweimal identische Ableitung, keine verlorenen Pfade.
Physischer Tabellenkatalog einschliesslich Spalten/Constraints exakt erhalten;
nur Code-/Maskenverweise nachgezogen.

Oberflaeche: sieben Faelle aus AP-Antragsbindung und neuer nativer Studio-Liste
bestanden. Der erste Vitest-Start scheiterte vor den Tests an einem gesperrten
Systemtemp-Rename; ein eigenes Arbeits-Tempverzeichnis beseitigte die Umgebungssperre.
Die nachgelagerte Node-Projektpruefung fand zwei vorhandene Buildaltlasten:
ungueltiges allowedHosts=all sowie einen ungenutzten Alternativconfig mit nicht
deklariertem Analysepaket. Verbraucherpruefung ergab nur Config-/Ignoreverweise.
Alternativconfig und diese Verweise sind entfernt; regulaerer Vite-Config erlaubt
localhost/frontend-web und zusaetzliche Hosts nur explizit per VITE_ALLOWED_HOSTS.
Keine Paketinstallation oder neue zweite Buildkonfiguration.

GitHub-Nachlauf wird nach Lieferung separat festgehalten; lokale Gateergebnisse
behaupten kein vollstaendiges GitHub-CI-Gruen und keine Live-Browserabnahme.

Vollstaendige Frontend-Typpruefung und vorgelagerter Node-Konfigurationsbuild bestanden
ohne Fehler. Die tatsaechlich geladene Vite-Konfiguration bestaetigt die Host-Allowlist
localhost/frontend-web. Sieben Oberflaechentests bestanden.

## Zweiter paralleler Nachlauf

Der erste Main-Push wurde wegen inzwischen eingegangener paralleler Commits
korrekt ohne Ueberschreiben zurueckgewiesen. Die Lieferung bis86d54acb1 ist
zusaetzlich erhalten. 653 Backend-/SQL-/Studio-/PCN-Vertraege und anschliessend
63 weitere Katalog-/Kanalmetadatenvertraege bestanden:716 Backendpruefungen.
Alle Anwendungsmodule kamen aus unveraenderten kanonischen Integrationsquellen.
Die weiteren Faelle verwenden die vorhandenen Finanzrollen auch in den reinen
Dispatchbeispielen; dort wurden keine Geschaeftsschreibrechte hinzugefuegt.

19 Oberflaechentests bestanden, ebenso die vollstaendige Frontend-Typpruefung und
der erzwungene Node-Konfigurationsbuild. Das regulaere type-check-Paketkommando
baut diesen Node-Teil nun selbst vorab; ein frischer Checkout setzt damit keine
zufaellig vorhandenen Konfigurations-Deklarationsdateien mehr voraus.

Alle erneut ausgefuehrten Qualitaets-/Architekturgates bestanden. OpenAPI3229 Pfade,
reproduzierbar und ohne Pfadverlust.103 Aktionsrechte sind aus Serverrollen abgeleitet.
Der aktuelle Upstream-Tabellenkatalog blieb physisch exakt erhalten; nur Lineage wurde
aktualisiert. Der Testkonflikt mit dem veralteten direkten AP-MCP-Adapter wurde zugunsten
der verbindlichen menschlichen Entscheidung und der neuen Studio-Pruefungen aufgeloest.
GitHub-CI und lokaler Browserbetrieb sind weiterhin getrennte Nachweise.

## Pflicht-Gateauswahl

Der neue SQL-Vertrag war in der Vollsuite enthalten, seine gemeinsame case-Fixture
forderte jedoch require_db noch nicht an. Dadurch waehlte das separate schnelle
PostgreSQL-Pflichtgate nicht alle neuen AP-Faelle aus. Die Fixture und beide echten
Parallelitaetstests fordern nun require_db an; die bestehende Sammlung markiert
auch transitive Verbraucher in Kernel-/Maskenvertraegen als needs_live_db.

Exakt der CI-Selektor, lokal mit PYTEST_REQUIRE_DB_STRICT=1 gegen valeo_probe:
71 bestanden,39 reine andere Faelle abgewaehlt. Unveraenderter Anwendungscode,
keine neue Datenbank oder Container, kein Reset. Die71 Faelle sind eine streng
nachgepruefte Teilmenge der716, keine zusaetzlich aufaddierte Pruefzahl.
Auf7ee86fc80 waren OpenAPI-Drift, Rollenvertraege, PostgreSQL-Gate, Docs-Build/-Governance,
kritische semantische E2E-Pfade und Compliance auf GitHub bereits erfolgreich;
Gesamtpipeline/Quality Gate liefen beim Abruf noch.
