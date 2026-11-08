# Belegprojektion: ausdrückliche Testgrenze

Stand: 2026-10-12. Slice `IDENTITY-REMAINING-WIRING-20261012`.

Der Registrierungsvertrag verwendet jetzt ausdrücklich `app.main`, die
Kompatibilitäts-App mit der zentral deklarierten Testidentität. Er prüft die
HTTP-Verdrahtung mit FakeProjection und ist kein Nachweis der produktiven
JWT-/Sitzungsprüfung. `main:app` und dessen Sicherheitsmiddleware werden
weder überschrieben noch abgeschwächt. Claudes vorherige Importkorrektur des
Projektionsmoduls bleibt erhalten.

Die vier vorhandenen Projektionsverträge prüfen auch die mandantenbezogene,
idempotente Projektion mit eigenen Service-Attrappen. Kein fachlicher
Datenbank-Schreibtest und kein neues Testschema. Die Produktionsauth wird
weiter durch die getrennten RSA-/Sitzungsverträge geprüft.

Die zwei Snapshot-Bestandsfälle sind davon unabhängig weiterhin offen:
`read_model_snapshots` benötigt einen kanonischen Migrationsvertrag; die bloß
in einer gewachsenen Datenbank vorhandene Tabelle genügt nicht.
