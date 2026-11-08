# Belastbare Compliance-Teilpruefungen

Stand19.10.2026; CI-COMPLIANCE-REAL-20261019. Technische Vertragspruefung, keine rechtliche Gesamtzertifizierung.

Der alte Workflow wandte die globale App-Coverage auf wenige Teiltests an, erzeugte die angekuendigten JUnit-Dateien nicht und ersetzte fehlende Nachweise durch eine Erfolgsmeldung. GoBD enthielt Platzhalter sowie nicht belastbare selbst erzeugte Auditnachweise.

## Umsetzung und Nachweise

GDPR nutzt die abgenommenen signierten Provider-/Mandanten-/SQL-Vertraege und gezielte Fehlerfaelle. Der exakte neue Teiljob hat22 bestandene Tests und100 Prozent Coverage des GDPR-Moduls bei80 Prozent Mindestwert. Die globale App-Schwelle60 in pytest.ini und der vollstaendige Quality-Gate-Testlauf bleiben unveraendert.

GoBD verwendet die bestehenden Journal-Hashketten-, Betrags- und Lebenszyklusvertraege: echte PostgreSQL-Sperren, Vorgaengerhash, Mandantengrenzen, ungueltige Betraege, konkurrierende Aenderungen und Erhalt von Metadaten. Initial90 Tests gruen:81 Journalfaelle und neun Berichtsfaelle. Nach Erweiterung nochmals elf Berichtsfaelle gruen. Eigene kurzlebige Schemas im vorhandenen valeo_probe werden durch bestehende Fixtures aufgeraeumt; keine neue Datenbank oder Container und kein Reset. In CI wird ausschliesslich die bereits vom Job bereitgestellte Datenbank verwendet. Der ueberfluessige Inventarseed entfällt.

Beide Teiljobs erzeugen JUnit explizit. Fehlendes Uploadartefakt ist ein Fehler. Der Bericht verlangt erfolgreichen Jobstatus und nichtleere, lesbare XML-Ergebnisse ohne Fehler oder uebersprungene Faelle; auch widerspruechliche Summenzaehler sperren. Elf Positiv-/Negativfaelle geprueft. Der echte Generator akzeptiert die beiden lokal erzeugten JUnit-Dateien. Bericht bleibt auch bei roter Bewertung als Artefakt verfuegbar, soweit erzeugt.

Die GoBD-Teilpruefung erhebt keine globale Abdeckungsbehauptung und deaktiviert die unpassende Voll-App-Messung nur fuer diesen begrenzten Vertragstest. Die Gesamtmessung und Sonar-Schwellen werden nicht gesenkt. Vollstaendige Aufbewahrungs-, DATEV-, Nummernkreis-, Belegketten- und Datenschutzprozessabnahme sind damit nicht pauschal bewiesen. Der GitHub-Nachlauf dieser Workflowaenderung ist noch abzuwarten; kein gruenes Gesamtgate behauptet.
