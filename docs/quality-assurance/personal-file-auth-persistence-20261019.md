# Personalakten: gepruefte Rechte und echte Persistenz

Stand: 19.10.2026. Owner Codex. PERSONAL-FILE-AUTH-PERSISTENCE-20261019.

## Geschlossene Befunde

Zwei zuvor allein durch actorRole gesteuerte Wege verlangen die vorhandenen Personal-Fachrollen aus gepruefter Anmeldung. Lesen erlaubt PERSONAL_LESEN, PERSONAL_BEARBEITEN, PERSONAL_ADMIN oder admin; Anlegen nur PERSONAL_BEARBEITEN, PERSONAL_ADMIN oder admin. Der Queryparameter ist beim GET ein Ansichtsfilter innerhalb bereits erteilter HR-Leserechte; beim POST entfaellt er. Der im Rumpf mitgeschickte createdBy-Wert entscheidet nicht mehr ueber den Urheber. Gepruefter Token-Subject wird unverkuerzt gespeichert.

Die zuvor nicht migrierte Tabelle domain_hr.employee_file_documents besitzt jetzt eine additive kanonische Migration. Mandanten-FK, Dokumentmetadaten, Sichtbarkeitsklassen, Aufbewahrungsdatum und Ursprungskennung werden wirklich gespeichert. Ein gemeinsamer Mandanten-/Mitarbeiterindex stuetzt das Lesemodell. Keine konkurrierende Beleg- oder Binaerablage; DMS-Referenzen bleiben Metadaten.

Leere Personalakten liefern eine leere Datenbankansicht. SQL-Fehler werden generisch mit503 beantwortet und zurueckgerollt; Demo-Fallback und falscher Speichererfolg sind entfernt. Kalenderdatum und Datumsreihenfolge werden vor SQL validiert, ungueltige Daten nicht mehr still durch heute ersetzt. Fehlendes Ausstellungsdatum verwendet weiterhin den konfigurierten Geschaeftstag; Schaltjahre bleiben korrekt.

## Nachweise

Vorhandener valeo_probe reserviert und auf fremde aktive Transaktionen geprueft. Nur der neue additive Upgrade-Schritt wurde angewendet, keine weitere Datenbank/Container, kein Reset. Die eigene noch offene Status-Leseverbindung blockierte den ersten Versuch am Alembic-Versionsfeld; Locktimeout brach ohne Teilaenderung ab, nach Freigabe lief die Migration erfolgreich.

Erster Personalakten-/Service-Lauf55 bestanden. Nach Datumsvalidierung59 bestanden; eine alte Erwartung des stillen Datumsersatzes war rot und wurde durch Ablehnung ersetzt. Gezielter Geschaeftszeit-Nachlauf2 bestanden, einschliesslich fehlendem Datum und Schaltjahr. Insgesamt60 unterschiedliche Faelle dieser vier Dateien abgenommen.

Die neuen SQL-Vertraege verwenden echte signierte RSA-Token, die produktive Bearer-/Mandantenmiddleware sowie kontrollierte JWKS-/Sitzungslease-Testgrenzen. Zwei eigene Mandanten liegen in einer aeusseren Rollbacktransaktion; Endpunktcommits loesen nur Savepoints. Geprueft sind: unberechtigte Rollen mit fuenf actorRole-Werten ohne SQL, readonly verweigertes Schreiben, erhaltener eigener und unveraenderter fremder Datenbestand, Header-Mandantenfaelschung, fehlende Anmeldung, ueberschriebener Rumpfurheber, leere Akte, reale SQL-Fehler ohne falschen Erfolg/private Fehlertexte sowie drei ungueltige Datumsfaelle vor SQL.

Die zwei eigenen OpenAPI-Operationen, Migration und physische Tabelle sind projiziert. Vierzehn bereits committete Masken-/Audit-/Mail-/Mobil-Lineagebeziehungen wurden gleichzeitig nachgezogen, statt unrichtige Katalognachweise zu behalten. Tabellenkatalog673 Tabellen; Codeinventare und Agent-Handbuch gegen HEAD-Eingaben geprueft. personal.py bleibt bei3083 Zeilen; keine erhoehte Godfile-Grenze.

## Grenzen

Keine Personalselbstbedienung oder globale Vorgesetztenberechtigung behauptet. HR-Leserechte bleiben mandantenweite Fachrechte; fehlende feinere Betriebs-/Mitarbeiterbeziehungen duerfen nicht ueber actorRole simuliert werden. DMS-Binaerinhalte, vollstaendige Aufbewahrungs-/Loeschprozesse und andere historische HR-Pilotpfade sind eigenstaendige Vertraege. Entwicklungsdatenbank und laufender Backendcode sind durch die Pruefstandabnahme nicht migriert oder ausgerollt. Gesamter OpenAPI-/GitHub-Nachlauf wird getrennt erfasst, kein pauschales CI-Gruen.


## Integrierte Schlusspruefung

Alle60 Faelle nochmals gegen eine ausschliesslich aus aktuellem Git-HEAD und den eigenen HR-Aenderungen aufgebaute Quellansicht bestanden. Importierte Anwendungsmodule wurden auf diese Herkunft geprueft. Vollstaendige OpenAPI-Projektion wiederholt erzeugt und stabil; keine nur auf alten Arbeitskopien beruhende API-Abnahme. Parallel gelieferte Steuerkategorienmigration per leerem Mergekopf zusammengefuehrt, beide Zweige unveraendert erhalten. Ein DAG-Vertrag prueft den einzigen Kopf und beide Eltern. Auf gemeinsamem Probe vor Upgrade null fremde aktive Transaktionen; nur ausstehender Steuerzweig und Merge ausgefuehrt. Entwicklung weiterhin unveraendert.
