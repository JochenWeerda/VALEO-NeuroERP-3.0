# Studio-Testmigration — Uebergabe 13.11.2026

Zweig `codex/sonar-coverage-20261113`, Weiterentwicklung auf dem Stand von PR #133.
Die Testmigration wurde vor den Edits im Workboard reserviert; spezialisierte
Agenten bearbeiteten Waagenliste und Autonomietests sowie anschliessend die
allgemeine Variantenbindung. Lead integrierte und pruefte die Aenderungen.

- Drei alte erwartete Fehlschlaege der Waagenliste durch fuenf echte
  Studio-Verhaltenstests ersetzt. Zentrale Ratsche 184 auf 181 gesenkt;
  ein neuer Driftwaechter bindet sechs UI-Fixtures an aktuelle Backend-Builder.
- 26 schnelle Tests der echten Autonomie-/Qualitaetslogik am simulierten DB-Rand.
  Lernen erteilt keine Rechte; Rolle, Politik, Delegation, Betrag, Qualitaet,
  Risiko und Einwand bleiben getrennte Voraussetzungen.
- Fuenf Kanaltests mit generiertem Studio-Vertrag. Vor Fix zwei rot, weil MCP
  oeffentliche strukturierte 409-/422-Details verlor; Transport korrigiert.
- Neun neue Variantenregressionen vor Fix rot. `maskVariant` wird nun validiert,
  kopiert, im Cache und in beiden Rendererpfaden weitergegeben; unveraenderter
  Belegvertrag `documentVariant` mitgeprueft. Kein zweiter Renderer/Rechteweg.

Nachweise: 104 Backendtests (62 + 33 + 9), 51 Frontendtests (13 + 38),
vollstaendige Frontend-Typpruefung Exit 0. Keine Datenbank/Container oder Builds
verwendet. Details in `docs/quality-assurance/studio-test-{waage,autonomie,kanaele,familienbindung}-20261113.md`
und `docs/quality-assurance/studio-teststrategie.md`.

Offen: 181 Altfaelle in 48 Testdateien und neun separate Smoke-Ausnahmen.
Vorgehen nach Fachrisiko, gueltige Fachinvarianten erhalten, alte Implementations-
annahmen erst nach echtem Ersatz entfernen. Keine erneute Wiederherstellung
handgebauter Seiten fuer alte Quelltexttests. Authentifizierung, RLS, SQL-Effekte
und Browserinteraktion benoetigen weiterhin ihre eigenen Nachweise. Kein Claim
einer Sonar-Gesamtabnahme; letzter gepruefter Main-Wert 70,9 Prozent / Ziel 80.

Die nicht versionierten lokalen Coverage-/Hook-Artefakte gehoeren nicht zur
Lieferung. Es wurde nicht im alten geteilten Hauptarbeitsbaum editiert.
