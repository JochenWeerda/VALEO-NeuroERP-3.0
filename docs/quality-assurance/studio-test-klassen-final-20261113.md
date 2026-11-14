# Gemeinsame Maskenklassen statt alter Stiltests — 13.11.2026

31 Quelltexttests aus `service-annahme-feldservice-uix.test.ts` prueften ausschliesslich alte Hooks, Layoutkomponenten, Touchklassen oder Farbliterale. Keiner der entfernten Faelle pruefte positiv einen Fachbefehl, ein Datenfeld oder einen Navigationsweg. Faelle mit solchen Erwartungen bleiben erhalten. Auch aussagekraeftige Pending-/Fehlersemantik wurde nicht entfernt.

Ersatz: `render-plan/mask-class-presentation.test.tsx` fuehrt fuenf echte Floorplans in Hell und Dunkel durch Compiler und Renderer aus. Geprueft werden lesbar deklarierte Hauptueberschrift, beschriftetes Eingabefeld, ausloesbare Primaeraktion, gesperrte Gefahraktion ohne Aufruf, Mindestzielklassen und unveraendertes Theme. Zusammen mit `studio-theme-contrast.test.ts` und `components/ui/button-touch.test.tsx`: **94 Tests bestanden**, Exit 0. Die vorhandene Kontrastmatrix prueft die semantischen Farbtoken aller Themes.

Grenzen: JSDOM ist keine Pixel-/Touchgeraeteabnahme. Die synthetischen Klassendefinitionen beweisen keine einzelne Fachvariante, keine Netzwerkaktion und keine Serverberechtigung. Der Ersatz prueft die bisher zentral gemeinten Darstellungsinvarianten am gemeinsamen Mechanismus; er bestaetigt keine fehlenden Fachfunktionen.

## Einzelnachweis der entfernten Quelltextfaelle

| Alter Fall | Ehemalige Quelldatei(en) | Ersatz |
|---|---|---|
| stellt Retouren beschriftet 44 px ohne Rohblau | einkauf/retouren.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Feldservice mit h1 und 44-px-Aktionen | agribusiness/field-service-tasks.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Zahlungslauf-Theater nur am Desktop | finance/zahlungslauf-kreditoren.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt UStVA-Theater nur am Desktop | finance/ustva.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Abschluss-Theater nur am Desktop | finance/abschluss.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Rechnungseingaenge-Liste zuerst | einkauf/rechnungseingaenge-liste.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt QS-Ausnahmen Arbeit zuerst ohne Rohrot | qualitaet/ausnahmen.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Gutschriften Theater nur am Desktop | einkauf/gutschriften-belastungen.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Dashboards ohne Theater auf Touch | dashboard/sales-dashboard.tsx, dashboard/einkauf-dashboard.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Frachttarife ohne 5-px-Win32-Toolbar | strecke/speditionen-fracht-preise.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Field-Service neu mit NativeSelect und 44 px | agribusiness/field-service-task-neu.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Field-Service edit mit NativeSelect und 44 px | agribusiness/field-service-task-edit.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt PSM-Beratung ohne Rohblau | agrar/psm/beratung.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt PSM-Wasserschutz mit Status-Tokens | agrar/psm/wasserschutz.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Kontakt-Detail mit 44-px-Zurueck | crm/kontakt-detail.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Saatgut-Stamm mit 44-px-Zurueck | agrar/saatgut-stamm.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Duenger-Stamm mit 44-px-Zurueck | agrar/duenger-stamm.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Landwirte-Liste mit 44-px-Zeilenaktionen | agribusiness/farmers.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Maschinen-Auslastung Arbeit zuerst am Touch | agrar/maschinenauslastung.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt CRM-Kundenstamm-Aktionen 44 px | crm/kunden-stamm.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Lead-Generierung mit 44-px-Vorschau | crm/lead-generierung.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Bedarfsdeckung mit keyed Reklass und Tokens | crm/bedarfsdeckung-cockpit.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Kommissionierung mit 44-px-Bestaetigen | lager/kommissionierung.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Payment-Matching Arbeit zuerst am Touch | finance/payment-matching.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt FIBU-Zahlungseingaenge Arbeit zuerst am Touch | fibu/zahlungseingaenge.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Periodenabschluss mit Tokens und 44 px | finance/periodenabschluss.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt AP-Rechnungen mit 44-px-Zeilenaktionen | finance/ap-invoices-list.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt FIBU-Uebersicht Arbeit zuerst und 44 px | fibu/buchhaltungsuebersicht.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Zeiterfassung Arbeit zuerst und 44 px | personal/zeiterfassung.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Monatswerte Theater nur am Desktop | fibu/monatswerte.tsx | Klassen-/Touch-/Kontrastvertrag |
| stellt Kassen-Uebernahme 44 px | pos/uebernahme-kasse.tsx | Klassen-/Touch-/Kontrastvertrag |
