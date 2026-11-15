# Rationsoptimierung: Einreichung nach Neuberechnung

Stand 2026-11-13. Bei geaenderten Rahmenbedingungen blieb nach einem Solverfehler das alte optimale Ergebnis einreichbar; die Regression wurde vor der Korrektur reproduziert. Eingaben in der Werkbank und ein erneuter Wizard invalidieren die bisherige Berechnung. Laufende Solverantworten tragen eine Revision; ueberholte Antworten ersetzen den aktuellen Stand nicht. Vor Entwurf und Statuswechsel wird die Revision erneut geprueft. Eine Vorschau kann nur bei unveraendertem Eingabestand uebernommen werden.

Gezielte Vitest-Pruefung: `rations-workbench-recalculation.test.tsx` und `rations-user-workflow.test.tsx`, 14 Tests bestanden (maximal zwei Worker). Geprueft wurden ungueltige und gueltige Leistungswerte, Sperre vor Blur, Fehler und Wiederholung, eine verzoegerte alte Solverantwort sowie bestehende Einreichungsablaeufe.

Grenze: Dies sichert die Browseroberflaeche ab; eine eigenstaendige serverseitige Verifikation der Bindung zwischen Solverergebnis und Eingabesnapshot ist damit nicht nachgewiesen. Ein bereits gestarteter Serverauftrag kann clientseitig nicht zurueckgenommen werden. Keine Datenbank- oder Docker-Ressourcen verwendet.
