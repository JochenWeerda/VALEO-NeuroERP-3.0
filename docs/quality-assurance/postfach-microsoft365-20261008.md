# Postfächer mit Microsoft 365 (Slice POSTFACH-MICROSOFT365-20261008)

Stand: 2026-10-08 · Folgeslice zu [Postfächer je Mandant](mailkonto-mandant-20261008.md)

## Ergebnis

| Baustein | Inhalt |
|---|---|
| **Anbieter `microsoft`** | Microsoft 365 / Outlook als weiterer Anbieter, **nur** mit Anmeldung über Microsoft. Eine Prüfbedingung in der Datenbank (Migration `postfach_microsoft_20261008`) verbietet Passwort-SMTP. Microsoft baut SMTP AUTH mit Passwort ab, und viele Organisationen haben es schon abgeschaltet. |
| **Anmeldung** | Microsoft Identity Platform, delegiert, Scopes `offline_access openid email https://graph.microsoft.com/Mail.Send`. `MICROSOFT_OAUTH_TENANT` ist die Verzeichnis-ID des Kunden oder `organizations`. Der Refresh-Token liegt verschlüsselt im Postfach. Die Adresse kommt aus dem `id_token` (`email` bzw. `preferred_username`). |
| **Versand** | Über Microsoft Graph `POST /me/sendMail` statt SMTP. Erfolg heißt, dass Graph mit **202** angenommen hat; jede andere Antwort ist ein Fehler mit Grund. `saveToSentItems`: Die Nachricht liegt danach in „Gesendete Elemente“ des Postfachs. |
| **Alias** | Ein Alias auf ein Microsoft-Postfach sendet mit `from` = Alias-Adresse. Dafür braucht das angemeldete Postfach in Exchange „Senden als“, sonst lehnt Graph ab (`ErrorSendAsDenied`), und das wird als Fehler gemeldet. |
| **Ein Anmeldeweg für beide** | Google und Microsoft laufen jetzt über dieselben Wege: `POST /admin/postfaecher/{id}/anmeldung/start` und `POST /admin/postfaecher/anmeldung/abschluss`, Rückrufseite `/admin/postfaecher/anmeldung-rueckruf`. Der signierte `state` trägt Mandant, Postfach und Anbieter. In der Maske heißt die Aktion „Beim Anbieter anmelden“. |

## Nachweis

- `tests/test_postfaecher.py` hat jetzt 36 Tests, davon 5 neu für Microsoft. Abgedeckt sind:
  - Nur OAuth: Dienst und Prüfbedingung der Datenbank.
  - Anmeldung bis zum Versand: Verzeichnis-ID in der URL, Scopes, Token-Endpunkt, Refresh-Token verschlüsselt, Graph-Aufruf mit Bearer-Token, `saveToSentItems`, ohne `from` bei eigener Adresse.
  - Alias mit `from` und Namen.
  - Graph-Ablehnung ist kein Erfolg.
  - Der `state` trägt den Anbieter.
- Google- und HTTP-Tests sind unverändert grün. Microsoft und Google sind nur an `httpx.post` ersetzt.
- Vitest Postfächer: 4 grün.
- Gates im HEAD-Worktree grün: Doc-Generatoren, Tabellenkatalog, Single Head, Improvement-Pipelines, Response-Modelle (Schwelle 0), OpenAPI-Doku, Maskeninventar (100 SDs, 0 Lücken).

## Einrichtung (Betrieb)

1. Microsoft Entra ID → App-Registrierung (Web). Redirect-URI ist `https://<host>/admin/postfaecher/anmeldung-rueckruf`. Delegierte API-Berechtigungen: `Mail.Send`, `offline_access`, `openid`, `email`. Dann ein Client-Secret anlegen.
2. `MICROSOFT_OAUTH_CLIENT_ID`, `_CLIENT_SECRET`, `_REDIRECT_URI` und `_TENANT` setzen.
3. Die Google-Redirect-URI zeigt jetzt ebenfalls auf `/admin/postfaecher/anmeldung-rueckruf`.

## Offen

- Der Mask Builder hat keinen `multiselect`-Renderer; Verwendung und Rollen sind kommagetrennter Text.
