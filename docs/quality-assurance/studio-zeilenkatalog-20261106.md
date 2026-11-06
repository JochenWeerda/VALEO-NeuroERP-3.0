# Studio-Zeilenkatalog 2026-11-06

Der Screen-Aktionskatalog nimmt neben Kopfaktionen auch `rowActions` aus Wurzeltabellen und Tabellen in Tabs auf. Die bestehende ID `mask:<screen>:<key>` bleibt eindeutig. Bei gleichen Schlüsseln gewinnt die erste ausführbare Aktion in der Reihenfolge Kopf, Wurzeltabellen, Tabtabellen; ein Stub verdrängt keinen ausführbaren Eintrag. Zeilenaktionen verlangen `entity_id`, auch bei Navigation und lokalen Kommandos; Pfadparameter `{id}` und `{entity_id}` werden ebenso bei Kopfaktionen erkannt.

Die Projektionsquelle erhält deklarierte Rechte und Schutzmerkmale unverändert. Diese Metadaten sind keine Berechtigungsprüfung: Der bestehende KI-Usability-Verbraucher übernimmt sie nicht in `ActionOut`; die Ausführung muss weiterhin den jeweiligen geschützten Fachweg und dessen Richtlinien verwenden. Es werden keine Rechte ergänzt.

Prüfungen: gezielte Tests für Webhook-Historie und Abmelden, Tab- und Wurzeltabellen, deterministische Duplikate und Objektbezug ergänzt. Abnahme durch Lead: 6 Tests bestanden; nach Aktualisierung 638 Aktionen auf 381 Masken, zuvor 543 Aktionen. Katalog-Driftcheck und Agent-Handbuch-Driftcheck gruen. Der erste Testlauf erkannte erwartungsgemaess das noch alte generierte JSON; nach Regeneration ist auch dieser Vertrag gruen.

CI-Nachlauf PR #115: Backend stoppte am abhaengigen MCP-Mask-Action-Map-Drift, vor den Backendtests. Die aus dem erweiterten Katalog abgeleitete config/mcp_mask_action_map.yaml ist nachgezogen; ihr eigener Driftcheck ist gruen. Die neu sichtbaren Aktionen erzeugen keine pauschale Schreibfreigabe; vier open_high und vier open_medium sind explizit sichtbar. Frontend, WCAG, Secret-/Dependency-Scan und Integritaet waren im Lauf 42243115958 gruen.
