# ISO 27001 Quarterly Access Review – Prozess

**Steuerung:** A.9.2 User Access Management – Access-Review

**Frequenz:** Vierteljährlich (geplant: Q1, Q2, Q3, Q4)

**Status:** Implementiert (Prozess)

---

## 1. Zweck

Regelmäßige Prüfung, ob Berechtigungen noch den Anforderungen entsprechen (Least Privilege, Segregation of Duties).

---

## 2. Ablauf

| Schritt | Verantwortlich | Aktion |
|--------|----------------|--------|
| 1 | CISO / Security Officer | Termin festlegen (z. B. letzte Woche jedes Quartals) |
| 2 | CISO | Export der Rollen- und Rechtezuweisungen aus Keycloak / ERP |
| 3 | Abteilungsleiter | Bestätigung: Zugriffe für ihre Mitarbeiter noch erforderlich? |
| 4 | CISO | Entfernung nicht mehr benötigter Zugriffe |
| 5 | CISO | Dokumentation im Audit-Log (wer, wann, welche Änderung) |

---

## 3. Checkliste pro Quartal

- [ ] Zugriffsübersicht exportiert (Keycloak, ERP-Rollen)
- [ ] Abteilungsleiter-Bestätigungen eingeholt
- [ ] Überflüssige Berechtigungen entfernt
- [ ] Änderungen im Audit-Log dokumentiert
- [ ] Protokoll archiviert (z. B. `docs/compliance/access-review-YYYY-Qn.md`)

---

## 4. Verweise

- [ISO 27001 Gap Analysis](iso27001-gap-analysis.md) – A.9.2
- `SECURITY-FOUNDATION-AUDIT.md` (Repo-Root) – Audit-Logging
