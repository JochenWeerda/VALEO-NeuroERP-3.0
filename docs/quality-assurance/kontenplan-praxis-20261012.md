# Kontenplanpflege nach gängiger Praxis

Stand: 2026-10-12 · Slice `KONTENPLAN-PRAXIS-20261012` · Auftrag: „gängige Praxis übernehmen",
„Pflegemaske Kontenplan anfassen" · baut auf
[Gemeinsamer Kontenrahmen: Pflegerecht](kontenrahmen-pflegerecht-20261012.md)

## Die Praxis, an der sich der Slice ausrichtet

Vorgabe des Auftraggebers, sinngemäß nach SAP und Dynamics:

1. **Anzeige und Pflege sind getrennt.** Konten dürfen breit sichtbar sein; anlegen und ändern ist
   einem begrenzten Personenkreis vorbehalten.
2. **Das Pflegerecht ist delegierbar** und hängt nicht an technischen Adminrechten.
3. **Änderungen mit größerer Wirkung brauchen zusätzlich eine Bestätigung.**
4. **Benutzte Konten bleiben erhalten.** Vor dem Löschen werden Referenzen geprüft; für nicht
   löschbare Konten ist die Sperre der Weg.
5. **Ein „Ja, wirklich" ersetzt nie das nötige Recht.**

Im Kontenplan wird also nicht im Tagesgeschäft eingegriffen: Die Buchhaltung bucht, den Kontenplan
pflegen wenige.

## Umsetzung

| Praxis | vorher | jetzt |
|---|---|---|
| 1, 2 | Konto anlegen und ändern: Schreibrolle der Buchhaltung; deaktivieren: Finanzleitung | anlegen, ändern, deaktivieren: `kontenpflege` = `KONTENPLAN_PFLEGE` (delegierbar), `FINANCE_ADMIN`, `admin`. Lesen unverändert breit; wer nur `KONTENPLAN_PFLEGE` hat, liest den Kontenplan auch |
| 2 (gemeinsamer Rahmen) | – | zusätzlich `KONTENRAHMEN_PFLEGE`; das Pflegerecht des Hauses reicht dafür nicht |
| 3 | Rückfrage nur vor dem Deaktivieren, ohne Folge zu nennen | Deaktivieren nennt Konto und Folge; Ändern verlangt einen zweiten Klick („Ja, ändern"), wenn das Konto zum gemeinsamen Rahmen gehört oder die Kontenart wechselt |
| 4 | Prüfung auf Buchungen fragte eine Beziehung ab, die das Modell nicht hat – sie griff nie | bebuchtes Konto: Deaktivieren 409, Wechsel der Kontenart 409; Bezeichnung und Kategorie bleiben änderbar |
| 5 | – | Die Bestätigung liegt nur in der Maske. Das Recht prüft der Weg vor dem ersten Datenbankzugriff, mit oder ohne Bestätigung |

Die Pflegemaske (`pages/finance/chart-of-accounts.tsx`) zeigt außerdem den **Grund einer
Ablehnung** (bisher nur „Fehler beim Aktualisieren") und kennzeichnet Konten des gemeinsamen Rahmens
mit „Gemeinsamer Rahmen".

`/accounts` (zweiter Weg auf dieselbe Tabelle) folgt derselben Rolle.

## Geänderte Dateien

- `app/auth/finance_roles.py` – `kontenpflege`; `kontenplan_read` um `KONTENPLAN_PFLEGE` erweitert
- `app/api/v1/endpoints/chart_of_accounts.py`, `app/api/v1/endpoints/accounts.py`
- `tests/test_kontenplan_mandant_vertrag.py`, `tests/test_hauptbuch_rollen_vertrag.py`
- `packages/frontend-web/src/pages/finance/chart-of-accounts.tsx`

In der Maske lagen drei fremde, nicht committete Klassenänderungen. Sie sind im Arbeitsbaum erhalten
und nicht Teil dieses Commits.

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `tests/test_kontenplan_mandant_vertrag.py` gegen `valeo_probe` (echte Datenbank, zwei Mandanten, echte Buchungszeile) | 27 bestanden |
| `tests/test_hauptbuch_rollen_vertrag.py` (jetzt 14 Rollen × 54 Wege, Zugangsklasse „pflege") | 818 bestanden |
| alle Testdateien, die Kontenplan, `/accounts` oder Finanzrollen berühren | 1333 bestanden, 2 übersprungen |
| Schnittstellenbeschreibung der betroffenen Pfade | unverändert |
| `tsc --noEmit`, ESLint auf der Maske | ohne Fehler |

**Sichtprüfung** (Vite :3001, Playwright headless, nichts geschrieben):

- 28 von 29 Konten tragen „Gemeinsamer Rahmen".
- Bearbeiten eines solchen Kontos zeigt „Dieses Konto gehört zum gemeinsamen Kontenrahmen. Die
  Änderung gilt für alle Mandanten."; der erste Klick auf „Speichern" sendet nichts und macht den
  Knopf zu „Ja, ändern".
- Deaktivieren fragt „Konto 1400 „Debitoren" wirklich deaktivieren? …" mit Folge und dem Zusatz für
  den gemeinsamen Rahmen.

Nicht im Browser geprüft: die Anzeige einer Ablehnung. Der Entwicklungsnutzer trägt `admin` und wird
nicht abgelehnt; die Ablehnungen selbst (403, 409 mit Begründung) belegt der Vertrag.

## Betrieb

- Wer Konten pflegen soll, ohne Finanzleitung zu sein, bekommt `KONTENPLAN_PFLEGE`.
- Wer den gemeinsamen Rahmen pflegen soll, bekommt zusätzlich `KONTENRAHMEN_PFLEGE`.
- **Die Buchhaltung (`FINANCE_BEARBEITEN`) kann nach dem Einspielen keine Konten mehr anlegen oder
  ändern.**

## Offen

- **Die Sperre fehlt.** Praxis 4 nennt für nicht löschbare Konten die Sperre. Das Konto hat kein
  solches Feld: `allow_manual_entries` steht in Schema und Maske, aber nicht in der Tabelle – die
  Maske zeigt „Manuell: Ja/Nein" und speichert es nicht, ebenso die Währung. Eine echte Sperre braucht
  eine Spalte (Migration) und die Prüfung in jedem Buchungsweg. Eigener Slice.
- **Deaktivierte Konten** lassen sich nicht wieder aktivieren und erscheinen in keiner Liste.
- **„Export" in der Pflegemaske** ist ein Knopf ohne Wirkung.
- **Änderungsprotokoll:** Die Wege schreiben `log_fibu_audit`; eine Ansicht dazu gibt es in der Maske
  nicht.
