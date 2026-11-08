---
title: WhatsApp-Vorbereitung mit verifiziertem Mandantenzugriff
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-11
description: Drei Benachrichtigungs- und Outbox-Endpunkte nutzen zentrale OIDC-Mandanten- und Scope-Guards.
---

# WhatsApp-Zugriffsschutz

## Befund und Umsetzung

Die beiden Vorbereitungs-Endpunkte nahmen den Mandanten aus dem Rumpf, der
Outbox-Leser aus der Query; alle drei fielen auf dev-tenant zurueck. Im lokalen
Router waren ohne Anmeldung Schreiben und Lesen jeder benannten Outbox moeglich.
Eine globale Bearer-Pruefung allein bindet den Request-Mandanten nicht an das Token.

Alle drei Wege in whatsapp_notify.py verwenden jetzt den bestehenden
get_verified_tenant_id aus app/auth/tenant.py und require_scopes aus
app/auth/guards.py. Diese beziehen die Identitaet ueber die bestehende OIDC-
Validierung; keine zweite JWT-Implementierung oder neues Auth-Modell.

- POST /api/v1/whatsapp/dev/notify/lieferankuendigung: crm:write.
- POST /api/v1/whatsapp/dev/notify/dokument-ready: crm:write.
- GET /api/v1/whatsapp/dev/outbox: crm:read.
- Bestehendes admin:all erlaubt beide Operationen, bleibt jedoch auf den
  geprueften Token-Mandanten begrenzt.
- Rumpf-/Query-Mandant optional ohne Default; bei Angabe muss er dem verifizierten
  Mandanten entsprechen. Auch Header-Widerspruch, fehlendes sub und
  fehlende/widerspruechliche tenant_id-/mandanten_id-Claims werden abgewiesen.

Nur Vorbereitungsentwuerfe, kein Browser- oder Netzwerkversand. Endpunkte,
Responsefelder und Templates bleiben erhalten. Der optionale Request-Mandant
ist eine Konsistenzpruefung und kein Umschalter.

## Abnahme

Vor Reparatur: 31 von 32 HTTP-Gegenproben rot, nur expliziter gleicher Mandant
funktionierte bereits. Final 63 Tests gruen in 2,14 Sekunden: 34 HTTP-Vertraege,
16 Vorbereitungsgegenproben und 13 bestehende WhatsApp-Template-/Outboxvertraege.

Die HTTP-Tests nutzen einen echten FastAPI-Router und dessen Dependencies,
zwei unterschiedliche Identitaeten/Mandanten sowie admin:all. Nur der externe
OIDC-Provider wird an verify ersetzt; damit wird keine echte Tokensignatur oder
Providerkonfiguration abgenommen. SQLAlchemy-Verbindungen sind explizit verboten.
Die Tests pruefen reale In-Memory-Outbox-Wirkungen und deren Ausbleiben bei
Ablehnung; keine DB-Isolation oder Browserkonto-Bindung damit nachgewiesen.

Code-Inventare (drei), Architekturindex (939/939 Routen) und Agent-Handbuch
(fuenf Artefakte) auf isoliertem HEAD plus eigenen Aenderungen driftfrei geprueft.
Fremde noch nicht committete Generatorartefakte sind nicht Teil der Abnahme.

## Verbraucher und offene Punkte

Die beiden internen Fachverbraucher in sales_delivery_notes.py rufen den
Benachrichtigungsdienst direkt auf; sie werden durch diese Routerkorrektur nicht
veraendert oder zusaetzlich abgesichert. kunden_nr, Telefonnummer und Portal-URL
sind in der Vorbereitung weiterhin Requestwerte; deren Fach-/Objektpruefung ist
vor einem echten Browserversand erforderlich.

Die vorhandene Seite portal/whatsapp-simulator.tsx nutzt ein waehlbares tenantId
und direkte Axios-Aufrufe. Sie liegt als fremdes WIP im geteilten Baum und wurde
nicht editiert. Ihr Aufrufervertrag muss auf verifizierte Anmeldung und passenden
Mandanten nachgezogen werden; der alte dev-tenant-/Dev-Token-Weg reicht fuer diese
drei Endpunkte nicht mehr. Kein Sicherheitsfallback zur Erhaltung des Simulators.

Meta-Webhook, Bestellsimulator und Bestell-Inbox sind separate Wege und durch
diesen Fix nicht vollstaendig isoliert. Dauerhafte Outbox, Replay und
Browserkontozuordnung bleiben im offenen WHATSAPP-WEB-INTEGRATION-20261011.
