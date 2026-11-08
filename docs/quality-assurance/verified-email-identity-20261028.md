---
title: Bestaetigte E-Mail fuer Zugangsidentitaet
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Gezielter Integrationsnachweis mit ausdruecklichen Abnahmegrenzen.
---

# Bestaetigte E-Mail fuer Zugangsidentitaet

Signed Claims bestaetigen den Aussteller, nicht automatisch den Besitz einer
vom Benutzer aenderbaren E-Mail-Adresse. config/keycloak/user-profile.json
laesst E-Mail-Aenderungen durch Nutzer zu. Die emailbasierte Zugangspruefung
in Rations-/Grundfutterwegen darf deshalb nur email_verified als echtes JSON-
Boolean true akzeptieren. Fehlender/falscher Wert liefert keine Zugangsidentitaet;
keine Rueckfaelle auf Header oder andere Personen. Name bleibt nur Anzeige.

13 isolierte Claimfaelle plus5 vorhandene Audit-Servicefaelle bestanden (3,07s).
Unbestaetigte/falschtypisierte Claims und Header-Fallback werden negativ getestet;
bestaetigte Werte bleiben funktionsfaehig. Der vorhandene Rations-Aufrufervertrag
ist um einen echten 403-Fall fuer unbestaetigte Token-E-Mail ergaenzt. Keycloak-
Scope/Mapper sind statisch vorhanden; Benutzerkonten wurden nicht veraendert.
Dies ist keine neue Rollenvergabe oder persoenliche Login-/SQL-Abnahme.
