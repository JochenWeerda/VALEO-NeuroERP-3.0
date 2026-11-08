# Identitaetsgrenzen der isolierten Tests

Stand: 2026-10-12. Unterclaim von `IDENTITY-CONTROL-20261012`.

Die Rollenvertraege fuer Abschluss, Hauptbuch, Zahlungsverkehr/Stammdaten und
Bewerbungen setzen bereits einen Testnutzer. Ihre Mini-Anwendungen setzen nun
auch einen ausdruecklichen Testmandanten. Dadurch erreicht die Anfrage wieder
die zu pruefende Rollenentscheidung statt an einer fehlenden Anmeldung zu enden.

Die zentrale Fixture ersetzt Anmeldung nur in der separaten Kompatibilitaets-App
`app.main`. Der Produktionsdienst `main:app` akzeptiert dadurch keinen Dev-Token.
Diese Tests belegen Rollenentscheidungen, keine Provider- oder Mandantensicherheit;
dafuer gelten die getrennten RSA-/Transportvertraege.

Nachweis: die vier Rollenvertragsdateien bestehen mit 3959 Faellen, ohne zentrale
Fixture und ohne Datenbank. Es wurde kein Container oder Pruefstand angelegt oder
zurueckgesetzt. Die gesamte CI und weitere betroffene Fachtests bleiben zu pruefen.

Handshake: `tests/test_zahlung_stammdaten_rollen_vertrag.py` ist nach diesem Commit
fuer Claudes Debitoren-/Kreditoren-Regel freigegeben. Die 67 Finanz-Nachbarfaelle
bleiben in seinem Slice. Die 28 bereichsfremden Brueckenwege brauchen fachlich
passende Rechte; eine pauschale Finanzrolle ist dafuer nicht vorgesehen.

Der uebergeordnete Identitaetsclaim bleibt in Arbeit: Sitzungsbetrieb, Agentenmandate,
Freigaben und Ressourcenbegrenzung sind mit diesem Testmeilenstein nicht abgeschlossen.
