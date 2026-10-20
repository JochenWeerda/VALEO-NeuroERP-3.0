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
