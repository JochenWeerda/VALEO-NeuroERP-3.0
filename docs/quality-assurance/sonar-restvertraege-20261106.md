# Sonar-Restvertraege 06.11.2026

Regex-Alternativen fuer Finanz-/Lagerprofile sind explizit gruppiert; die bisherige Unterscheidung zwischen Domain-Praefix und enthaltenem Fachbegriff bleibt bestehen. Die ueberfluessige SCREEN_ID-Alternative im Konstantenleser ist entfernt; [A-Z_]+ umfasst diesen Namen unveraendert.

Vier redundante UI-/Adapterzweige sind vereinfacht, ohne Werte oder Berechtigungen zu aendern. Der STT-Eingabeplatzhalter zeigt ein HTTPS-Beispiel; vorhandene lokale Konfigurationen werden weder umgeschrieben noch als TLS-faehig ausgegeben.

Die Niederlassungsauswahl ist ein nativer Button mit voller Zeilenbreite und sichtbarem Tastaturfokus. Enter/Leertaste erhalten dieselbe Auswahlwirkung wie der Mausklick, ohne Formularsubmit.

Abnahme: 31 bestehende Studio-Gate-/L3-Vertraege bestanden. Gemeinsame Frontend-Typpruefung bestanden; weitere gezielte IBAN-Regressionen im Async-Nachweis. Keine neuen Testdatenbanken oder Container; keine Sonar-Ausnahme und keine abgesenkte Schwelle.
