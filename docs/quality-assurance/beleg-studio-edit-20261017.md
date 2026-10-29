# Gemeinsame Belegbearbeitung in neun Studio-Varianten

## Umsetzung

Der vorhandene Beleg-Builder ergaenzt dieselbe registrierte PUT-Aktion docflow.update in allen neun Fachvarianten. Die append-only Familienfassung 1.1.0 erhaelt alle historischen Fassungen. Die zentrale native Detailseite laedt fuer Bearbeitung den gesamten kanonischen Beleg mit allen Positionen und verwirft unpassende Identitaeten, Versionen, Arten oder Status. Der Dialog verwendet den gemeinsamen Formstate und Tabellenrenderer. Metadaten, Preise, Kontierung und Charge bleiben bei Mengenbearbeitung erhalten, auch wenn die Variante sie nicht zeigt. Navigation waehrend des Ladens oeffnet keine alte Maske; doppeltes Laden wird unterbunden. Eine explizit geleerte Textreferenz wird uebertragen. Nach fehlgeschlagenem Speichern bleiben Eingaben mit derselben Version fuer den erneuten Versuch erhalten; die Meldung erscheint im Dialog. Der abschliessende Knopf heisst Entwurf speichern.

Der versionierte Transportadapter verwendet PUT und den vorhandenen Versions-/Idempotenzvertrag. Er akzeptiert ausschliesslich die deklarierten Eingaben und die bestaetigte Antwort dieses Entwurfs in der naechsten Version. Fremde Methoden, Status-/Urheberangaben, Agentenaufrufe und eine scheinbare schreibfreie Vorschau bleiben gesperrt. Der bisherige POST-Weg anderer Commands bleibt erhalten.

Der Domain-Command weist Positionsvollersatz bei vorhandenen Positionsherkunfts- oder Belegkettenverweisen vor jeder Mutation ab. Dies verhindert das Entfernen von Herkunft und Teilmengenbeziehungen. Es ist keine fertig implementierte positionsbezogene Korrektur. Allgemeine Headerupdates werden hierdurch nicht zu Fachkorrekturen erklaert.

## Nachweis und Grenzen

147 Backendvertraege fuer Varianten, Versionshistorie, Studio-Katalog/-Import, Provenienz und SQL-Updates bestanden. 55 gezielte Frontendvertraege einschliesslich drei nativer Dialog-/Formularintegrationen und die Typpruefung bestanden. Der abschliessende Stand einschliesslich Einkaufskontierung und Steuersatz ist erneut gruen. Weitere 43 bestehende Rechte-/Freigabevertraege bestanden. Variantenregister und alle fuenf Agent-Handbuchartefakte sind synchron. Historische Basis-/Variantenfassungen wurden exakt mit dem Vorgaenger verglichen und bleiben unveraendert. Der Tabellenkatalog ergaenzt nur zwei eigene SQL-Leseverbrauchergruppen; physische Schemata bleiben unveraendert. Der vorherige komplette Tabellenrenderer-Nachlauf bestand mit 1416 Tests in 277 Dateien; er ist kein Vollsuite-Nachweis dieser neuen Integration.

Keine neue Datenbank, Container, Migration, Rechtevergabe oder Agentenschreibfreigabe. SQL nutzt den vorhandenen valeo_probe. Es wurden in dieser Integration keine realen Geschaeftsbelege im Browser gespeichert und keine alten Einstiege umgeleitet. Preisgeschuetzte Vollbearbeitung verlangt weiterhin das vorhandene Preisleserecht; reine Lager-Mengenbearbeitung braucht einen passenden, getrennt abgenommenen Eingabevertrag. Die allgemeine Studio-Prozessfreigabe bleibt unveraendert gesperrt, solange das konkrete Fachprofil fehlt.

Varianten- und Alt-Einstieg-Matrix: [Eine Studio-Belegmaske](../design/beleg-studio-variantenmatrix.md).
