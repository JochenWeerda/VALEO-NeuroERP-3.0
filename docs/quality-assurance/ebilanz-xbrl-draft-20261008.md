---
title: Amtlicher eBilanz-Katalog und echter XML-Entwurf
type: reference
audience: [entwickler, qa, agent, betrieb]
owner: Codex
status: lokal_geprueft
last_reviewed: 2026-10-08
---

# eBilanz XBRL-Entwurf

## Umfang und Nachweis

Die 14 historischen Teilfelder mit falschen GCD-Pfaden sind durch 3944 amtlich
abgeleitete GCD-/Kernkonzepte ersetzt. Namespaces, deutsche Standardlabels,
Typen, abstrakte Elemente, Nillability, Periodentyp und Balance stammen aus
dem [amtlichen 6.9-Paket](https://www.esteuer.de/download/taxonomie_20250618/german-gaap-taxonomy-v6.9-2025-04-01-xbrl.zip).
SHA256: `accd62202d73c036910fee118b30730f0392934afc9730617788e30a0480df87`.
Branchen, Dimensionskataloge und ERiC-Regeln sind kein Bestandteil dieses
Konzeptkatalogs. Alle Runtime-Zugriffe erfolgen lokal; keine Requests ins Internet.

`build_ebilanz_taxonomy_catalog.py <amtliches-zip> --check` prueft Paket-Hash
und byteidentische Ausgabe. Derselbe Aufruf ohne --check generiert den Katalog.
Andere Pakete muessen als neuer Versionierungs-/Fachclaim abgenommen werden;
kein stilles Ersetzen des Hashes. Die Konzeptliste wird beim ersten Zugriff
einmal geladen, dann wiederverwendet. API-Paging: limit 1..1000, Default 100,
skip ab 0, stabil nach Konzeptname. Vorhandene GET-Antwort bleibt eine Liste.

`POST /api/v1/ebilanz/export/{export_id}/xbrl-entwurf` erzeugt echte XML-Bytes
aus expliziten einfachen Fakten. Entity-Identifier und dessen URI-Scheme werden
angegeben; Finanzwerte sind Dezimalstrings, keine gerundeten Floats. Bekannte
Konzepte, einfache Typen, XML-Zeichen, nil-Zulaessigkeit und Perioden werden
geprueft. Vier lokale Entwurfsvoraussetzungen (Name, Land, Beginn, Ende) sind
ausdruecklich keine amtliche Mussfeldmatrix. Beginn/Ende in den Fakten muessen
mit den gespeicherten Exportperioden uebereinstimmen. Unbekannte, abstrakte,
Tupel- oder noch nicht abgenommene Typen liefern 422 statt geratener Fakten.
Maximal 2000 Fakten; Texte je Fakt maximal 10000 Zeichen.

Neue Exportmetadaten verwenden 6.9 fuer Periodenbeginn 2025/2026 und verlangen
Uebereinstimmung des Wirtschaftsjahrs mit dem Beginn. Historische Exporte werden
nicht umgeschrieben. Der XML-Weg lehnt andere Taxonomieversionen und IFRS mit
409 ab. Finance-Leserechte bleiben zentral, Download verlangt Schreibrechte;
fremde/fehlende Export-ID 404. Cache-Control no-store, Downloaddateiname aus
validierter UUID. Kein DB-Write/Commit fuer den Download, kein Ticket und keine
Umstellung auf VALIDIERT/UEBERTRAGEN/ANGENOMMEN. Paketgroesse bleibt 0, weil
die XML-Bytes hier nicht archiviert werden.

## Abnahme

49 Tests gruen (4,78 s): 28 reine Katalog-/XML-Regressionsvertraege und die
bestehenden/erweiterten echten HTTP-/PostgreSQL-Vertraege. Deterministische
Ausgabe, amtliche Konzepte/Labels/Hash, fehlende/abstrakte/Tupel-Fakten,
Dezimal-/Datum-/XML-Fehler, Periodenkonflikte, Paging, Rechte und Fremdmandant,
echte XML-Antwort und unveraenderte Status-/Ticket-/Groessenwerte geprueft.
Ein dabei erkannter Typfehler (persistierte Perioden sind im gewachsenen Schema
Text) wurde durch explizite ISO-Datumsnormalisierung am Download behoben.
Testdaten ausschliesslich eigene Tenantdatensaetze mit aeusserer Transaktion
und Savepoints im vorhandenen valeo_probe, Revision offenes_schliessen_20261008.
Keine neue DB/Container, Migration, Reset oder Ressourcenbereinigung.

OpenAPI deterministisch erzeugt: 3105 Pfade; einzig neuer Pfad ist der
XML-Download mit expliziter application/xml-Antwort. Die vorhandenen 30
doppelten Pfad-/Methodengruppen bleiben unveraendert und sind kein Abschluss
der globalen Routerbereinigung. Architekturzuordnung des neuen Services wird
explizit ueber den Finance-Prefixvertrag abgenommen.
25 Architekturvertraege gruen; complete/check: 935/935 Routen, 277/277 Services,
454/454 Endpoints zugeordnet. Alle drei Codeinventare aktuell; Antwort- und
Beschreibungsgates ohne verbleibende Luecke bei Schwelle 0.

Handshake zum geteilten Baum: Ein Architektur-Generator wurde versehentlich
lokal ausgefuehrt. Der bereits gestagte fremde Architekturindex ist erhalten;
die neue lokale Ausgabe wird nicht als Lieferstand verwendet. Der vorherige
ungestagte Inhalt wurde mangels gesicherter Kopie nicht blind zurueckgesetzt.
Die Lieferung verwendet ausschliesslich den isoliert generierten Index.

## Offene externe und fachliche Abnahmen

CI-Nachtrag 2026-10-08: Die ersten GitHub-Doku-Laeufe auf d81a86b38 waren rot,
weil der neue Slice Pflichtfelder des AI-Harness vermisste und ADR-079 noch
nicht im generierten MkDocs-Nav stand. Eigene Lieferfehler korrigiert, kein Gate
abgeschwaecht. Isolierte committed-source-Abnahme: Harness, ADR-Nav (84 ADRs),
Markdown (121 Dateien), Governance (101 Dateien), Staleness (88 Seiten), drei
Codeinventare, Containerinventar und fuenf Handbuchartefakte gruen. Vollstaendiger
MkDocs-Build erfolgreich in 57,19 s; vorhandene Linkwarnungen sind weiterhin
offen und werden nicht als fehlerfreie Gesamtdokumentation ausgegeben.
Nach dem fremden Meilenstein a2a71801c erneut auf dessen vollstaendigem
committed Stand geprueft: alle genannten Gates und MkDocs-Build gruen (53,81 s).

XML ist ein **Entwurf**, Header `X-XBRL-Status: DRAFT_UNVALIDATED`. Die lokale
Vorpruefung bestaetigt weder vollstaendige XBRL-/Rechenregelgueltigkeit noch
amtliche Annahme. Bilanz-/GuV-Kontenzuordnung, Tupel/Dimensionen, Arelle-
Vollvalidierung und ERiC mit Zertifikat/Empfangsquittung bleiben offen.
Taxonomie 6.10 ist kein freigeschalteter aktueller ERiC-Echtweg.
ELSTER-Registrierung vom Nutzer abgesendet, Zugang wird nachgereicht;
kein SDK/Lizenzannahme vorgetaeuscht. Readiness bleibt nicht bereit.
[ADR-079](../adr/adr-079-ebilanz-xbrl-drafts.md) dokumentiert die Grenze.
