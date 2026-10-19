# Reparaturen aus authentifiziertem Runtime-Sweep

Stand19.10.2026, RUNTIME-READ-REPAIRS-20261019.

Run39271752353 fuehrte1033 GET-Ziele mit echter Provideridentitaet aus:957 erfolgreich,60 erwartete Verweigerungen, keine401, elf konfigurierte503, vier500 und ein Folgeabbruch. Der Bericht vom19.10. ist massgeblich; das Uploadartefakt enthaelt auch einen historischen Juli-Bericht, der nicht als aktueller Nachweis verwendet wird.

## Reparaturen

- NumberingServicePG erwartete AsyncSession, die konfigurierte Dependency lieferte Session. execute/commit warten nur tatsaechliche Awaitables ab; Router verwendet dieselbe Grenze. Signaturen behalten asynchrone Verbraucher; die konkrete Dependency ist korrekt als Session typisiert.
- Einkauf-Report fragte die entfernte einkauf_bestellungen-Tabelle ohne Mandantenfilter ab. Die verschluckte Ausnahme hinterliess die Transaktion unbrauchbar. Aggregation verwendet jetzt denselben mandantengebundenen Dokumentspeicher wie der Standardbericht und Decimal fuer die Summe. Kein SQL-Fehler wird zu einer vermeintlich leeren Auswertung umgedeutet. Keine neue Serviceklasse oder konkurrierendes Modell; Compat-Dateilaenge sinkt.
- users.get_current_user ueberschattete den importierten Authenticator und wurde in spaeteren Routen faelschlich als Abhaengigkeit verwendet. Eindeutiger Alias erhaelt die gepruefte Identitaet. Alle drei Profil-Lesepfade verwenden den vorhandenen lokalen Benutzerbestand direkt, statt die abstrakte alte Repositoryklasse zu instanziieren. Eigenes Profil wird ueber Providerkennung zugeordnet; Verzeichnis verlangt vorhandene Adminrolle, fremde Einzelprofile403, fremde Mandanten404. ARRAY-Rollen werden im bestehenden String-Ausgabevertrag korrekt serialisiert. Keine neue Rolle oder Rechtevergabe.
- Vollstaendiger Generatorabgleich fand fuer den bereits committeten delegierenden mask_commands-Adapter fehlende Inventar-/Domainzuordnung. Genau dieser Adapter wird platform zugeordnet; fremder Quellcode unveraendert. Strikter Architekturabgleich:941/941 Routen,302/302 Services,462/462 Endpunkte. Kein neuer Container oder Domaenenvertrag.

## Abnahme und Grenzen

Final sieben Tests bestanden: vier echte SQL-/Providervertraege mit mehreren HTTP-Positiv-/Negativfaellen, AsyncSession-Kompatibilitaet und zwei bestehende Verträge zur Verkaufsbelegnummer. JWKS und Redis-Leasepruefung im Test kontrolliert, produktive Signatur-/Mandantenmiddleware aktiv. Bestehender valeo_probe, ausschliesslich eigene synthetische Datensaetze, aeussere Transaktion/Savepoints und Rollback. Keine neue DB, Container, Migration oder Reset. Sechs betroffene GET-OpenAPI-Operationen mit aktuellem HEAD verglichen: unveraendert; fremde neue Pfade nicht aus altem Export ueberschrieben.

GitHub-Runtime-Nachlauf der Reparaturen steht noch aus.19 abgelaufene Ausnahmen bleiben sperrend; konfigurierte503 sind keine erfolgreiche Fachabnahme. Alte schreibende lokale Nutzerwege und erste Nummernkreis-Erstellung sind mit diesen Reads nicht abgenommen; insbesondere werden fehlende abstrakte Passwortmethoden nicht durch Scheinimplementierungen freigeschaltet. Die vorhandene5000-Beleg-Grenze und bisherige abgeleitete Lieferantenbewertungen sind keine vollstaendige fachliche Reportingabnahme. Gesamt-Sonar-/Full-UAT-Nachweise bleiben getrennt offen.
