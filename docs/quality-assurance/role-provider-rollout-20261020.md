# Rollenbeschreibungen und Belegscope-Rollout

Stand20.10.2026, Codex. Bestehender Rollenvertrag, keine zweite Rechteverwaltung.

Provisionierung uebernimmt Beschreibungen aller vorhandenen Fach-/Grundrollen aus dem kanonischen Katalog. Bestehende Rollen werden nur bei abweichender Beschreibung aktualisiert; vollstaendige Darstellung wird vorher gelesen und nachher einschliesslich Identitaet, Attribute und Composite-Metadaten verglichen. Fehlende verifizierte Kennung, HTTP-Fehler oder unvollstaendige Persistenz sperren. Historische manager-Rolle wird nicht neu angelegt. Statische Realmdateien enthalten dieselben Beschreibungen; keine Benutzer oder neuen Rollenzuweisungen.

36 Tests mit36 Unterfaellen bestanden, darunter Rollen-/Scope-Reconciliation und negative Metadatenvertraege. Lokaler bestehender Keycloak:17 Beschreibungen aktualisiert,42 vorhandene Rollen zurueckgelesen. Ausschliesslich manager aus beiden Belegscope-Mappings entfernt; belege:read besitzt16, belege:write neun deklarierte Rollen. Vollstaendige Zuordnungen danach geprueft. Wiederholung20.10. meldet null Beschreibungsupdates und dieselben Mappings. Zugangsdaten und Token ausschliesslich im Speicher, keine Ausgabe/Ablage. Keine Benutzer-, Kennwort-, Composite-, Client- oder Sitzungszuweisung geaendert.

Grenze: Dies ersetzt weder Backenddeployment noch frische Benutzeranmeldung. Bereits ausgestellte Token laufen nach bestehender Sitzungs-/Tokenpolitik aus; die alte manager-Rolle muss zugleich durch den bereits committeten zentralen Backendguard unwirksam sein. Der lokale Backendmount enthaelt noch aeltere Arbeitsdateien; Deployment separat abnehmen.
