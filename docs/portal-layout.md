# Kundenportal Layout (CustomerPortalLayout)

**Datei:** `packages/frontend-web/src/layouts/CustomerPortalLayout.tsx`  
**Routen:** Alle unter `/portal` (Shop, Bestellungen, Feldbuch, Nährstoffbilanzen, etc.)

---

## Übersicht

Das Kundenportal nutzt ein eigenes Layout, getrennt von der Hauptanwendung. Es ist für mobile Nutzung optimiert (Handy/Tablet) mit Touch-freundlicher Navigation.

---

## Anwender vs. Kunde

| Nutzertyp | Rollen | "Zur Startseite" sichtbar? |
|-----------|--------|----------------------------|
| **Anwender** (intern) | `admin`, `user`, `manager` | Ja |
| **Kunde** (reiner Portal-Nutzer) | keine ERP-Rollen | Nein |

### Anwender

- Mitarbeiter mit Zugang zur Hauptanwendung (ERP).
- Können im Kundenportal testen, Kundenansicht prüfen oder Demo-Daten nutzen.
- Sehen einen **"Zur Startseite"**-Button im Header und im mobilen Menü.
- Der Button führt zur Route `/` (Startseite/Dashboard der Hauptanwendung).

### Kunden

- Reine Portal-Nutzer (z.B. Landwirte mit Kundenkonto).
- Keine Rollen `admin`, `user` oder `manager`.
- Der "Zur Startseite"-Button wird **nicht** angezeigt; sie bleiben im Portal-Kontext.

---

## Rollenprüfung

```ts
// Anwender (nicht reine Kunden) → dürfen zurück zur Hauptanwendung
const isAnwender = hasRole('admin') || hasRole('user') || hasRole('manager')
```

- `useAuth().hasRole()` prüft gegen `user.roles` und `admin:all`-Scope.
- Weitere Rollen können bei Bedarf ergänzt werden.

---

## UI-Positionen

| Bereich | Position |
|---------|----------|
| Desktop Header | Button neben dem Portal-Logo (links) |
| Mobile Sheet-Menü | Erster Eintrag in der Navigation (hervorgehoben) |

---

## Referenzen

- **Auth:** `@/hooks/useAuth`, `@/lib/auth.ts`
- **Routen:** `app/routes.tsx` – Portal-Routen unter `/portal`
- **Rollen-Roadmap:** `docs/ROLE-BASED-UI-ROADMAP.md`
