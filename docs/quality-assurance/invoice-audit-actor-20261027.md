---
title: Rechnungsaudit mit gepruefter Identitaet
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Gezielte Reparatur mit dokumentierten Abnahmegrenzen.
---

# INVOICE-AUDIT-ACTOR-20261027

Die drei Rechnungstransitionen übernehmen das Subject aus `get_current_user` über `gepruefter_akteur`. `bekannter_nutzer` ordnet es eindeutig einem aktiven Benutzer desselben Mandanten zu; die Audit-E-Mail stammt aus diesem Benutzerprofil. Die Statusänderung und der Audit-Eintrag werden gemeinsam committet; Ausnahmen beim Zuordnen, Schreiben oder Commit lösen Rollback aus. Der bestehende nachgelagerte Kreditoren-OP-Weg bleibt unverändert.

Gezielter Lauf `python -m pytest --noconftest tests/test_einkauf_invoice_audit_actor.py -q --no-cov`: 5 bestanden. Zwei unterschiedliche Subjects werden dem jeweiligen Benutzer zugeordnet; fehlende/ungekannte Identität und simulierter Audit-Commitfehler ändern den Status nicht. Der echte Service wird mit einer simulierten Session geprüft; ein SQL-Fremdschlüssel- oder realer Transaktionsnachweis ist damit nicht erbracht. Keine Datenbank für diesen Lauf. Python-Syntaxprüfung der geänderten Module erfolgreich.

Ein ergänzender direkter Routentest wurde abgebrochen, nachdem der Import des großen Compat-Routers lokal nicht zeitnah abgeschlossen war; er ist nicht Bestandteil des Tests. Ein erster pytest-Anlauf mit Standard-Conftest wurde ebenfalls abgebrochen und nicht als Nachweis verwendet. Drei Routen und sämtliche Service-Aufrufer wurden statisch überprüft. Reale Authentifizierung, DB-FK und Integrationssuite bleiben offen.
