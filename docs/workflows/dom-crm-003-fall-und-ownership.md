# DOM-CRM-003 - Fall und Ownership

## Ziel

CRM- und Servicefaelle mit Ownership, Folgeobjekten, Dubletten- und Abschlusslogik angleichen.

## Scope

- Kunden-, Opportunity- und Servicefaelle
- Ownership und Eskalationsrahmen
- Dubletten- und Folgeobjektpfade
- Abschluss- und Wiedervorlagebilder

## Dateibesitz

- `packages/frontend-web/src/pages/crm/*`
- `packages/frontend-web/src/pages/service/*`
- zugehoerige APIs und Agent-Ops-Verknuepfungen

## Abnahmekriterien

- CRM und Service tragen denselben Fallbezug, Ownership-Rahmen und Abschlusspfad.
- Dubletten, Folgeobjekte und Wiedervorlage erscheinen als fachliche Arbeitsobjekte statt Nebeninformationen.
- Timeline und naechste Aktion bleiben kompakt und entscheidungsorientiert.

## Risiken

- zu breite Streuung ueber CRM, Sales und Service
- Konflikte mit bereits ausgerolltem Agent-Ops- und Fallmodell
- Datenqualitaetsluecken bei Ownership-/Dubletteninformationen
