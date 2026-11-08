---
title: Typisierte Aktionseingaben und Kontingenttransport
last_updated: 2026-10-15
status: active
owner: Codex
---

# Typisierte Aktionseingaben und Kontingenttransport

Die reale Kontingentmaske scheiterte mit HTTP 422: deklarierte Zahlen wurden als Zeichenketten gesendet; nach deren Korrektur enthielt der Request weiterhin Sitzungsdaten (subject, tenant_id, Fristen), die der strikte Budget-Command zu Recht ablehnte.

ActionInputDialog uebergibt deklarierte Zahlen jetzt als JSON-Zahlen. Null bleibt erhalten, optionale leere Zahlen werden nicht zu Null, Textkennungen behalten fuehrende Nullen. Der eng auf die beiden bestehenden Budgetaktions-Endpunkte begrenzte Transportadapter projiziert ausschliesslich die passenden fachlichen Felder. Identitaet und Mandant stammen weiterhin aus verifizierter Authentifizierung. Andere Commands bleiben unveraendert. Servervalidierung, Vorschau, Begruendung und Rollenpruefung wurden nicht abgeschwaecht.

18 Frontendtests bestanden (Eingabedialog, Budgettransport, Laufzeit-Eingabefluss); TypeScript-Pruefung bestanden. Reale Browserabnahme: serverseitige Vorschau, Bestaetigung und Auditbegruendung fuehrten zu einem Mandantenbudget von exakt 10.000 Token und einem Nutzer-Unterkontingent derselben Hoehe mit null Unterkontingenten. Das ist dieselbe Kapazitaet, keine Verdoppelung. Lesender Redis-Nachweis: genau zwei Budgets, genau ein Testnutzerbudget mit Limit 10.000. Keine Datenbank und kein Container angelegt.

Screenshot: artifacts/harvest-browser-20261015/token-budget-assigned.jpg. Die temporaeren Finanz- und Kontingentrechte wurden nach der finanziellen Abnahme entzogen, Sitzungen beendet und die synthetische Prueferkennung gesperrt. Der Kontingentempfaenger erhielt keine Verwaltungsrechte.
