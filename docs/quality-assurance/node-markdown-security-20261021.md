# Markdown-Sicherheitskorrektur – 21.10.2026

Der vollstaendige Lockscan bestaetigte drei neue Befunde gegen markdown-it14.3.1.
Der vorhandene globale Override ist jetzt auf Herstellerpatch14.3.3 gesetzt.
Rootmanifest und Lock wurden regulaer mit pnpm erzeugt; Paketbestand3012 bleibt
bis auf die Markdown-Patchidentitaet gleich.36 Workspaces frozen bestanden.
Keine Majorversion erzwungen, keine gemeinsame Installation geaendert.

Primaerquellen: [Referenzen](https://github.com/advisories/GHSA-gfr2-rv44-r23c),
[Typografie](https://github.com/advisories/GHSA-r7fv-28h4-cvq7),
[Inline-HTML](https://github.com/advisories/GHSA-vfgh-jcmw-g37q).

## Funktionale Gegenprobe

Offizielle npm-Archive beider Versionen per SHA512 und jeweils57 installierte
JS/MJS/CJS-Dateien vollstaendig verifiziert. Derselbe Vertrag gegen beide:
Original14.3.1 besteht normalen Betrieb und unabgeschlossene Labels; sechs
weitere Problemformen laufen ins8s-Limit.14.3.3 besteht alle8 Vertraege.

Jede grosse Eingabe wird in einem eigenen lokalen Unterprozess mit8s-Zeitlimit,
128MiB V8-Heaplimit und4KiB Ausgabelimit verarbeitet; keine Endlosschleifen im
CI-Hauptprozess. Der Heapparameter ist kein harter Gesamt-RSS-Speichergrenzwert.
Geprueft: Referenztitel/-label, gegensaetzliche Quotes und vier ungeschlossene
HTML-Formen bei aktivierter HTML-Option. Normalfall prueft Ueberschriften,
Referenzen, Typografie sowie explizites und standardmaessig abgeschaltetes HTML.
Das Zeitlimit ist ein grosszuegiger Regressionsschutz, keine zugesicherte Latenz.

## Gemeinsame Sicherheit

45/45 Runtime-/Failclosed-Vertraege bestanden. Der vorhandene Audit-CLI ruft
den Markdownvertrag zusaetzlich auf; dessen Testpfad-Override wird zuvor entfernt.
Manifest-/Lockhashes der zwei bestehenden Quellreparaturen wurden nach der
erneuten gemeinsamen Abnahme nachgezogen. Quellpatches, Pruefschwellen und
bereits geltende Reviewfrist28.10. bleiben unveraendert.

Production-Audit weiter2 High (belegte node-forge/braces-Quellreparaturen),
Auditentscheidung0 blocked. Vollscan inklusive Entwicklung10 auf7 Befunde:
3 High/4 Moderate; alle3 Markdownbefunde entfernt. Andere offene Pakete
(stream-json, http-cache-semantics, sprintf-js) bleiben getrennte Folgearbeit.
Keine generelle Sicherheitsfreigabe aus einem Teilscan.

ChromaDB wurde nicht entfernt oder aktualisiert. Die bestehende bis23.10.
geltende Embedded-Bewertung wurde gegen98 unveraenderte kanonische Dateien
und12 Failclosed-Vertraege bestaetigt. Keine neue Risikobewertung, kein frischer
Python-Scannerlauf, keine Fristverlaengerung oder Alertschliessung.

CI-Gesamtnachlauf nach Push separat erforderlich. Das Studio-Gesamtziel und die
vollstaendige Altmaskenmigration bleiben offen.
