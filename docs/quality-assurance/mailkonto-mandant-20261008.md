# Postfächer je Mandant: IONOS, Google, SMTP, Alias – mit Freigaben (Slice MAILKONTO-MANDANT-20261008)

Stand: 2026-10-08 · Folgeslice zu [Offenes schließen](offenes-schliessen-20261008.md)

## Auftrag

Die Nutzerentscheidung: Es gibt keinen eigenen Mailserver. Der Mandant trägt seinen Dienst ein; IONOS und Google sind sofort dabei. Ergänzt während der Arbeit: Ein Mandant führt mehrere Postfächer (`info@`, `dispo@`, `fibu@`, `zentrale@`, persönliche Postfächer) mit Zugriff je Rolle oder je Mitarbeiter.

## Ergebnis

| Baustein | Inhalt |
|---|---|
| **Postfächer** (`domain_shared.mailkonten`, Migration `mailkonto_mandant_20261008`) | Beliebig viele je Mandant. Die Kennung ist je Mandant eindeutig, es gibt höchstens ein Standard-Postfach. Prüfbedingungen: Ein Geheimnis ist nur verschlüsselt (`v1:`) erlaubt, ein Alias hat kein eigenes Geheimnis und verweist auf ein echtes Postfach. |
| **Anbieter** | Vorlagen: `ionos` (smtp.ionos.de:587, STARTTLS, Benutzer = Adresse), `google` (smtp.gmail.com:587, STARTTLS) mit **App-Passwort** oder **Google-Anmeldung** (OAuth2, SMTP XOAUTH2, Refresh-Token), `smtp` für jeden anderen Server, `alias` für eine eigene Absenderadresse mit der Anmeldung eines anderen Postfachs („Senden als“). |
| **Verwendung** | Jedes Postfach nennt, wofür es automatisch genommen wird: `einkauf`, `verkauf`, `fibu`, `dispo`, `newsletter`, `allgemein`. Bestellmails gehen über das Einkaufs-Postfach, Newsletter über das Newsletter-Postfach. Gewählt wird nach ausdrücklichem Postfach, dann passender Verwendung, dann Standard. |
| **Zugriff** | `admin` darf immer. Ein persönliches Postfach darf nur sein Inhaber nutzen. Sonst gilt die Freigabe für Rollen und/oder Benutzer; ohne Freigabe dürfen alle im Mandanten. Ohne Freigabe für das gewählte Postfach wird nicht gesendet, sondern mit 403 abgelehnt. `/admin/postfaecher/verfuegbar` zeigt einem Nutzer nur die Postfächer, aus denen er senden darf. |
| **Versand** (`mail_versand`) | Ein Postfach des Mandanten hat Vorrang. Fehlt es, wird das Plattformkonto aus den Umgebungsvariablen genutzt, sonst gibt es eine klare Absage. Zugangsdaten gehen nur über SSL oder STARTTLS. Bietet ein Server kein STARTTLS, wird nicht angemeldet. |
| **Prüfung** | „Testmail senden“ trägt `geprueft` erst ein, wenn der Server die Nachricht angenommen hat; sonst `fehler` mit Grund. |
| **Geheimnisse** (`app/core/geheimnis.py`) | AES-256-GCM, gebunden an Mandant und Zweck. Schlüssel aus `VALEO_SECRET_KEY`. **Ohne Schlüssel wird nichts gespeichert (503)**, es gibt weder Klartext- noch Wegwerf-Rückfall. Das Passwort wird nie zurückgegeben (`hat_geheimnis`). |
| **Maske** | Screen Definition `admin/postfaecher` (Capture-Muster, TS-Spiegel per Vertrag identisch), gezeichnet vom Mask Builder. Neu im Mask Builder: der Feldtyp **`password`** (verdeckt, `autocomplete=new-password`, zeigt nie einen gespeicherten Wert). Die Testmail fragt den Empfänger über `ActionInputDialog` ab. Entfernen fragt vorher nach. Google-Rückruf über `/admin/postfaecher/google-rueckruf`. |

## Mit behoben

| Befund | Behebung |
|---|---|
| Das IMAP-Passwort und der STT-API-Schlüssel des CRM-Connectors lagen **im Klartext** in `tenants.settings`. | Jetzt verschlüsselt; Altwerte bleiben lesbar und werden beim nächsten Speichern verschlüsselt. |
| `PUT /admin-suite/capture-connectors` und die Test-/Abrufwege hatten **keine Rollenprüfung**: Jeder angemeldete Nutzer konnte das Postfach umstellen, aus dem das CRM liest. | Nur noch `admin`. |
| `compat.py` importierte `save_to_store` ohne Verwendung. | Entfernt. |

## Nachweis

- `tests/test_postfaecher.py`, 31 Tests gegen `valeo_probe`. SMTP und Google sind nur an `smtplib` und `httpx` ersetzt. Abgedeckt sind:
  - Verschlüsselung: gebunden an Mandant und Zweck, ohne Schlüssel kein Speichern, die Datenbank verbietet Klartext.
  - IONOS-Vorlage; ein leeres Passwort behält das alte.
  - Kennung, Standard-Postfach und Alias-Regeln.
  - Rollen, persönliche Postfächer und Verwendung vor Standard; die Absenderwahl zeigt nur Freigegebenes.
  - Ein fremder Mandant sieht nichts.
  - Versand: Anmeldung und Absender, Alias, Ablehnung ohne Freigabe, Testmail-Status.
  - Google von der Anmeldung bis zum Versand mit XOAUTH2; `state` eines fremden Mandanten oder mit falscher Signatur wird abgelehnt.
  - HTTP: Verwaltung nur für `admin`, Absenderwahl, die Bestellmail läuft über das Einkaufs-Postfach, ohne Schlüssel 503.
  - IMAP-Passwort verschlüsselt, Altwert und Rollenprüfung.
  - Maske: im Register, Bereitschaft 1.0, Governance ohne Fehler, Passwortfeld, TS-Spiegel identisch.
- Vitest `pages/admin/postfaecher.test.tsx` (4 Tests): Passwort verdeckt, Bearbeiten lädt ohne Passwort, Speichern schickt Listen, Entfernen fragt nach, Testmail meldet den Serverfehler.
- Regressionen: 1171 Backend-Tests und 263 Mask-Builder-Tests grün.
- Gates im HEAD-Worktree grün: gitleaks ohne Fund, Godfile (`admin_suite.py` 1038 → 1035), Doc-Generatoren, Tabellenkatalog, Response-Modelle (Schwelle 0) und Maskeninventar (100 SDs, 0 Lücken).
- Live auf der Dev-Umgebung antworten Liste und Verwendungen mit 200. Anlegen antwortet ehrlich mit 503, weil `VALEO_SECRET_KEY` dort nicht gesetzt ist.

## Einrichtung (Betrieb)

1. `VALEO_SECRET_KEY` setzen (`openssl rand -base64 32`). Den Schlüssel nicht wechseln, solange Zugangsdaten liegen.
2. Für die Google-Anmeldung braucht die Plattform einen OAuth-Client (Google Cloud Console, Scope `https://mail.google.com/`). Zu setzen sind `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET` und `GOOGLE_OAUTH_REDIRECT_URI` = `https://<host>/admin/postfaecher/google-rueckruf`. Ohne Client funktioniert Google mit App-Passwort.
3. Bei IONOS und Gmail muss eine Alias-Adresse im Postfach als Absender erlaubt sein: IONOS über einen Alias, Gmail über „Senden als“.

## Offen (benannt)

- Microsoft 365 (OAuth2 / Graph) folgt als eigener Slice.
- Die Felder Verwendung und Rollen sind kommagetrennter Text: Der Mask Builder hat noch keinen `multiselect`-Renderer.
- Weitere Fachwege, etwa Mahnung oder Rechnung per E-Mail, nutzen die Postfachwahl, sobald sie versenden. Heute versenden nur Bestellkommunikation, Newsletter und Testmail.
