Spezifikation
XStatistik 2.0.1
XStatistik — XÖV-Standard für die amtliche Statistik
Veröffentlicht 15.12.2010
Copyright © 2010 Statistisches Bundesamt
iii
Inhaltsverzeichnis
Vorwort ...................................................................................................................... ix
1. Einleitung ................................................................................................................ 1
1.1. Die amtliche Statistik ..................................................................................... 1
1.2. Entwicklung von XStatistik .............................................................................. 1
1.3. Aufbau der Spezifikation ................................................................................ 2
2. Datenerhebung ........................................................................................................ 3
2.1. Akteure ........................................................................................................ 3
2.2. Datengewinnung vorbereiten ........................................................................... 4
2.3. Dienstleister für Datenmeldung beauftragen ...................................................... 5
2.4. Rohdaten melden .......................................................................................... 6
2.5. Einzelmeldung weiterleiten ............................................................................. 7
2.6. Datenempfang bestätigen ............................................................................... 8
3. Informationsmodell ................................................................................................. 11
3.1. Übersicht der Hauptgruppen ......................................................................... 11
3.2. Hauptgruppe: Datenerhebung ....................................................................... 11
3.2.1. Übersicht zum Schema ...................................................................... 11
3.2.2. Nachrichten der Hauptgruppe ............................................................. 11
Übersicht der Nachrichten ................................................................... 11
DatML-RAW-D ..................................................................................... 11
DatML-RES-D ...................................................................................... 14
3.2.3. Spezifische Typen der Hauptgruppe ..................................................... 16
Übersicht der hauptgruppenspezifischen Typen ...................................... 16
3.3. Allgemeine Typen ........................................................................................ 16
3.3.1. Baukasten ........................................................................................ 16
Übersicht zum Schema ....................................................................... 16
Übersicht der Typen ............................................................................ 17
Absender ........................................................................................... 18
AnforderungEmpfangsbestaetigung ....................................................... 22
Anschrift ........................................................................................... 23
Anwendung ....................................................................................... 28
Berichtszeitraum ................................................................................ 30
Berichtszeitraum.Sequence .................................................................. 32
Berichtszeitraumdatum ....................................................................... 33
Berichtszeitraumdatum.Choice ............................................................. 35
Berichtszeitraumdatum.Choice.Sequence .............................................. 37
Datei ................................................................................................. 38
Datei.Choice ...................................................................................... 42
Datenattribute .................................................................................... 43
Dateneingang .................................................................................... 44
Dateneingang.Choice .......................................................................... 46
Datensegment .................................................................................... 48
Datensegment.Choice ......................................................................... 49
Dokumententyp .................................................................................. 51
Dokumentinstanz ............................................................................... 52
Empfaenger ....................................................................................... 55
Erhebung ........................................................................................... 58
Fehler ............................................................................................... 60
Formular ............................................................................................ 63
Funktionselement ............................................................................... 65
Hilfsmerkmal ..................................................................................... 65
Identitaet .......................................................................................... 68
Kontakt ............................................................................................. 69
Kontakt.Sequence .............................................................................. 71
Korrektur ........................................................................................... 74
Material ............................................................................................ 76
XStatistik 2.0.1
iv
Meldungsart ...................................................................................... 77
Merkmal ............................................................................................ 80
Merkmal.Choice ................................................................................. 82
Merkmalsgruppe ................................................................................ 83
Merkmalsgruppe.Choice ...................................................................... 85
Nachricht ........................................................................................... 87
Nachrichtenkopf ................................................................................. 89
Optionen ........................................................................................... 92
Ordnungsmerkmal .............................................................................. 93
Ordnungsmerkmal.Sequence ............................................................... 96
Ordnungsmerkmal.Sequence.Choice ..................................................... 97
Organisation ...................................................................................... 99
Person ............................................................................................ 100
Protokoll .......................................................................................... 103
Pruefdokument ................................................................................. 104
Pruefmeldung .................................................................................. 107
Pruefnachricht .................................................................................. 112
Pruefprotokoll .................................................................................. 114
Pruefstatus ...................................................................................... 115
Pruefung .......................................................................................... 116
Satz ................................................................................................ 119
Satz.Choice ...................................................................................... 121
Segment .......................................................................................... 122
StatistischerKontext .......................................................................... 124
StatistischerKontext.Choice ................................................................ 128
Test ................................................................................................ 130
3.3.2. Basisdatentypen ............................................................................. 130
Übersicht zum Schema ...................................................................... 130
Übersicht der Typen .......................................................................... 131
Leertyp ............................................................................................ 132
PositiveInteger.Halbjahr ..................................................................... 132
PositiveInteger.Jahr ........................................................................... 132
PositiveInteger.Monat ........................................................................ 133
PositiveInteger.Pruefstufe .................................................................. 133
PositiveInteger.Quartal ...................................................................... 134
PositiveInteger.Tag ............................................................................ 134
PositiveInteger.Woche ....................................................................... 134
Pruefstufe ........................................................................................ 135
String.Datenformat ........................................................................... 136
String.Datentraeger ........................................................................... 137
String.Datum .................................................................................... 138
String.Formatiert ............................................................................... 139
String.Position ................................................................................. 141
String.SchluesselGewicht ................................................................... 142
String.TextKlasse .............................................................................. 143
String.TextKlasseNoDefault ................................................................. 144
String.TextZeileHTML ......................................................................... 145
String.Uhrzeit ................................................................................... 146
String.Wert ....................................................................................... 147
StringLatin.NormalizedString .............................................................. 149
StringLatin.Token .............................................................................. 150
Token.Datenformat ........................................................................... 150
Token.Datentraeger ........................................................................... 150
Token.Dokumentstatus ...................................................................... 151
Token.FormatEmpfangsbestaetigung ................................................... 151
Token.FormatPosition ........................................................................ 152
Token.Formatklasse .......................................................................... 152
Token.Pruefstatus ............................................................................. 153
XStatistik 2.0.1
v
Token.Versandart .............................................................................. 154
Token.Version.DatML-RAW-D ............................................................... 154
Token.Version.DatML-RES-D ................................................................ 154
vi
vii
Abbildungsverzeichnis
1.1. Die Leistungsprozesse der Statistikproduktion .......................................................... 1
2.1. Übersicht der XStatistik-Anwendungsfälle für die Datenerhebung ................................. 3
2.2. Anwendungsfall: Datengewinnung vorbereiten .......................................................... 5
2.3. Anwendungsfall: Dienstleister für Datenmeldung beauftragen ...................................... 6
2.4. Anwendungsfall: Rohdaten melden .......................................................................... 7
2.5. Anwendungsfall: Einzelmeldung weiterleiten ............................................................. 8
2.6. Anwendungsfall: Datenempfang bestätigen ............................................................... 9
3.1. xst:DatML-RAW-D ................................................................................................. 12
3.2. xst:DatML-RES-D .................................................................................................. 15
3.3. xst:Absender ....................................................................................................... 19
3.4. xst:AnforderungEmpfangsbestaetigung ................................................................... 22
3.5. xst:Anschrift ........................................................................................................ 24
3.6. xst:Anwendung .................................................................................................... 28
3.7. xst:Berichtszeitraum ............................................................................................. 31
3.8. xst:Berichtszeitraum.Sequence .............................................................................. 32
3.9. xst:Berichtszeitraumdatum .................................................................................... 34
3.10. xst:Berichtszeitraumdatum.Choice ........................................................................ 35
3.11. xst:Berichtszeitraumdatum.Choice.Sequence ......................................................... 37
3.12. xst:Datei ........................................................................................................... 39
3.13. xst:Datei.Choice ................................................................................................. 42
3.14. xst:Datenattribute .............................................................................................. 43
3.15. xst:Dateneingang ............................................................................................... 44
3.16. xst:Dateneingang.Choice ..................................................................................... 46
3.17. xst:Datensegment .............................................................................................. 48
3.18. xst:Datensegment.Choice .................................................................................... 50
3.19. xst:Dokumententyp ............................................................................................ 51
3.20. xst:Dokumentinstanz .......................................................................................... 53
3.21. xst:Empfaenger .................................................................................................. 56
3.22. xst:Erhebung ..................................................................................................... 59
3.23. xst:Fehler .......................................................................................................... 61
3.24. xst:Formular ...................................................................................................... 64
3.25. xst:Funktionselement ......................................................................................... 65
3.26. xst:Hilfsmerkmal ................................................................................................ 66
3.27. xst:Identitaet ..................................................................................................... 68
3.28. xst:Kontakt ........................................................................................................ 70
3.29. xst:Kontakt.Sequence ......................................................................................... 72
3.30. xst:Korrektur ...................................................................................................... 74
3.31. xst:Material ....................................................................................................... 76
3.32. xst:Meldungsart ................................................................................................. 78
3.33. xst:Merkmal ...................................................................................................... 80
3.34. xst:Merkmal.Choice ............................................................................................ 82
3.35. xst:Merkmalsgruppe ........................................................................................... 84
3.36. xst:Merkmalsgruppe.Choice ................................................................................ 86
3.37. xst:Nachricht ..................................................................................................... 88
3.38. xst:Nachrichtenkopf ........................................................................................... 90
3.39. xst:Optionen ..................................................................................................... 92
3.40. xst:Ordnungsmerkmal ........................................................................................ 94
3.41. xst:Ordnungsmerkmal.Sequence .......................................................................... 96
3.42. xst:Ordnungsmerkmal.Sequence.Choice ............................................................... 97
3.43. xst:Organisation ................................................................................................ 99
3.44. xst:Person ....................................................................................................... 101
3.45. xst:Protokoll .................................................................................................... 103
3.46. xst:Pruefdokument ........................................................................................... 105
3.47. xst:Pruefmeldung ............................................................................................. 108
3.48. xst:Pruefnachricht ............................................................................................ 112
XStatistik 2.0.1
viii
3.49. xst:Pruefprotokoll ............................................................................................. 114
3.50. xst:Pruefstatus ................................................................................................. 115
3.51. xst:Pruefung .................................................................................................... 116
3.52. xst:Satz .......................................................................................................... 120
3.53. xst:Satz.Choice ................................................................................................ 121
3.54. xst:Segment .................................................................................................... 123
3.55. xst:StatistischerKontext ..................................................................................... 125
3.56. xst:StatistischerKontext.Choice .......................................................................... 128
3.57. xst:Test ........................................................................................................... 130
3.58. xst:Leertyp ...................................................................................................... 132
3.59. xst:Pruefstufe .................................................................................................. 135
3.60. xst:String.Datenformat ...................................................................................... 136
3.61. xst:String.Datentraeger ..................................................................................... 137
3.62. xst:String.Datum .............................................................................................. 138
3.63. xst:String.Formatiert ......................................................................................... 139
3.64. xst:String.Position ............................................................................................ 141
3.65. xst:String.SchluesselGewicht ............................................................................. 142
3.66. xst:String.TextKlasse ......................................................................................... 143
3.67. xst:String.TextKlasseNoDefault ........................................................................... 144
3.68. xst:String.TextZeileHTML .................................................................................... 145
3.69. xst:String.Uhrzeit ............................................................................................. 146
3.70. xst:String.Wert ................................................................................................. 148
ix
Vorwort
In diesem Dokument werden der XÖV-Standard XStatistik sowie die am Nachrichtenaustausch
beteiligten Prozesse beschrieben. XStatistik ist ein Standard für die amtliche Statistik und wurde
gemäß den Konformitätskriterien für XÖV-Standards neu entwickelt. Die Notwendigkeit hierfür
erwuchs aus der Veröffentlichung des XÖV-Handbuches und der damit verbundenen Zertifzierung
zur qualitativen Bewertung der Datenaustauschformate.
Die Struktur der in der Spezifikation beschriebenen Rohdatenmeldung entspricht dabei
vollständig dem bisherigen Standard DatML/RAW 2.0. Jede von DatML/RAW 2.0 validierte XMLInstanz wird auch von XStatistik validiert.
Neu hinzugekommen ist die Definition der Empfangsbestätigung, die bislang unter der
Bezeichnung DatML/RES 1.0 separat entwickelt wurde. Auch diese Struktur wurde gegenüber
dem Originalformat nicht geändert, um die Abwärtskompatibilität zu wahren.
x
1
Kapitel 1. Einleitung
1.1. Die amtliche Statistik
Die amtliche Statistik führt ca. 400 Bundesstatistiken durch. Bei der Mehrzahl dieser Statistiken
müssen die Befragten, wie Unternehmen und Behörden, die erforderlichen statistischen Daten
an die statistischen Ämter übermitteln.
XStatistik ist Bestandteil von eSTATISTIK, einem eGovernment-Initiativprogramm der
Statistischen Ämter des Bundes und der Länder, mit dem elektronische,
medienbruchfreie Produktionsprozesse verwirklicht werden. In XStatistik sind einheitliche,
verfahrensübergreifende XML Nachrichten für die Kommunikation zwischen der amtlichen
Statistik und den Meldern definiert. Sie finden flächendeckend Verwendung in den OnlineMeldeverfahren IDEV und eSTATISTIK.core, in verfahrensspezifischen Dateneingängen wie denen
der Außenhandelsstatistik, sowie zunehmend in der Übernahme von Daten aus der Beleglesung.
Mit eSTATISTIK.core, einem innovativen Online-Meldeverfahren, das gemeinsam mit der
Arbeitsgemeinschaft für wirtschaftliche Verwaltung e.V. (AWV) entwickelt worden ist, werden
die von der Statistik erfragten Daten automatisiert aus dem betrieblichen Rechnungswesen
oder aus anderen elektronisch auswertbaren Unternehmensunterlagen gewonnen. Die Daten
werden im Format XStatistik in verschlüsselter Form über das Internet an eine gemeinsame
Dateneingangsstelle der amtlichen Statistik übermittelt, unabhängig davon, für welche Erhebung
und welches statistische Amt die Lieferung bestimmt ist. Es erfolgt eine Kontrolle der
statistischen Daten durch den Empfänger auf Basis von fachlichen Vorgaben im XMLFormat(Erhebungsbeschreibung). So ist sichergestellt, dass die Datenlieferung vollständig
und korrekt ist. Von dort werden sie an die jeweils zuständige Empfangsstelle, i.d.R. der
Berichtsempfänger, verteilt.
eSTATISTIK.core zielt als Teil der Deutschland-Online-Initiative der Bundesregierung vor allem auf
die Entlastung der Wirtschaft bei der Mitwirkung an statistischen Erhebungen ab und ist bereits
mehrfach national und international ausgezeichnet worden.
1.2. Entwicklung von XStatistik
Als Standard und Grundlage für die Automatisierung der Aufbereitungsprozesse wurden u.
a. die XML-basierten DatML-Formate zur Beschreibung der Daten entwickelt. Sie unterstützen
den gesamten statistischen Produktionsprozess von der Erhebung der Daten über ihre
Plausibilisierung bis zur eigentlichen Verarbeitung und Archivierung. Die direkt mit der
Konzeption, Erhebung, Aufbereitung und Ergebniskommunikation verbundenen Prozesse werden
zusammenfassend Leistungsprozesse genannt.
Abbildung 1.1. Die Leistungsprozesse der Statistikproduktion. Quelle: Statistisches Bundesamt,
Strategie- und Programmplan 2009–2013. [http://www.destatis.de/jetspeed/portal/cms/
Sites/destatis/Internet/DE/Content/Service/UeberUns/Ziele/
StrategieProgrammplan,property=file.pdf]
Aufbau der Spezifikation
2
Den unterschiedlichen Anforderungen im Laufe des Produktionsprozesses entspricht die
Unterteilung des Dokumententyps in eine Reihe von Unterformaten, die untereinander eine
konsistente Metadatenhaltung ermöglichen.
Das Datenaustauschformat für statistische Rohdaten wird inzwischen seit fast 10 Jahren
entwickelt. Damals wie heute wird für dieses Format die Bezeichnung DatML/RAW verwendet.
Die aktuelle Version 2.0 des Formats DatML/RAW [http://www.statspez.de/service/downloads/
DatML/raw/v2_0/datml-raw-2_0-spezifikation.pdf] wird bereits seit 2006 im produktiven Betrieb
eingesetzt. Mit dem Beginn der XÖV-Initiative wurde die Bezeichnung XStatistik eingeführt,
um einerseits die Nähe zu den übrigen XÖV-Vorhaben zu verdeutlichen und andererseits die
verschiedenen Nachrichten für den innerbehördlichen Nachrichtenaustausch XÖV-konform in
einem einheitlichen Schema zu bündeln. Mit der vorliegenden Version 2.0.1 enthält der Standard
XStatistik sowohl die Rohdatenmeldung (DatML/RAW 2.0) als auch die Empfangsbestätigung
(DatML/RES 1.0).
1.3. Aufbau der Spezifikation
Im zweiten Kapitel werden die Teilprozesse der Datenerhebung beschrieben, die von XStatistik
derzeit unterstützt werden. Dabei werden die beteiligten Akteure und Anwendungsfälle
in Form von UML-Aktivitätsdiagrammen dargestellt. Eine detaillierte Beschreibung des
Informationsmodells ist Bestandteil des dritten Kapitels.
3
Kapitel 2. Datenerhebung
In der Datenerhebung können folgende Akteure und Anwendungsfälle identifiziert werden,
die am Nachrichtenaustausch beteiligt sind. Nicht für alle Anwendungsfälle existieren dabei
spezifische Nachrichten in XStatistik, dies trifft nur auf die Anwendungsfälle "Rohdaten melden"
und "Datenempfang bestätigen" zu. Die übrigen Anwendungsfälle werden an dieser Stelle
jedoch aufgeführt und beschrieben, um das komplexe Umfeld des Nachrichtenformats zu
veranschaulichen.
Abbildung 2.1. Übersicht der XStatistik-Anwendungsfälle für die Datenerhebung. Für die
Anwendungsfälle "Rohdaten melden" und "Empfangsbestätigung" sind in XStatistik die
Nachrichten DatML-RAW-D bzw. DatML-RES-D definiert.
2.1. Akteure
Ein Berichtspflichtiger im Sinne der amtlichen Statistik ist eine Person oder Firma, die verpflichtet
ist, bestimmte Daten an ein Statistisches Amt zu melden. Sowohl der Umfang der zu erhebenden
Daten als auch die Periodizität der Erhebungen sind gesetzlich verankert.
Neben dem Berichtspflichtigen definiert XStatistik die Rolle des Melders. Dieser kann von
einem oder mehreren Berichtspflichtigen beauftragt werden, die statistischen Daten an den
Berichtsempfänger zu senden. Diese Rolle kann aber auch vom Berichtspflichtigen selbst
wahrgenommen werden.
Datengewinnung vorbereiten
4
Jede Rohdatenmeldung enthält mindestens eine Angabe zum Empfänger. Im zentralen
Dateneingang des Online-Meldeverfahrens eSTATISTIK.core werden alle eintreffenden
Rohdatenmeldungen entgegengenommen und an einen oder mehrere Berichtsempfänger
weitergeleitet. Der Empfänger prüft die eintreffende Nachricht auf Wohlgeformtheit und Gültigkeit
gegenüber der Erhebungsbeschreibung, die eine Beschreibung der zu liefernden Meldedaten
in der erwarteten Qualität beinhaltet, und bestätigt dem Absender den Empfang der Nachricht.
Enthält die Rohdatenmeldung nur den Empfänger ist dieser gleichzeitig der Berichtsempfänger.
Der Berichtsempfänger ist i.d.R. ein Statistisches Landesamt oder das Statistische Bundesamt,
also die Daten erhebende Behörde.
2.2. Datengewinnung vorbereiten
Dieser Anwendungsfall dient der Veranschaulichung des Zusammenhanges zwischen der
generischen Rohdatenmeldung und einer konkreten Erhebung. Ziel dieses Teilprozesses
ist die Konfiguration der Unternehmenssoftware bzw. der Software CORE.reporter [http://
www.statspez.de/core/reporter.html] hinsichtlich der Spezifizierung der zu meldenden Daten.
Eine Datenerhebung in der amtlichen Statistik hat immer eine gesetzliche Grundlage. Die
zu erhebenden Merkmale und deren Ausprägungen werden im Fachverfahren festgelegt und
in einem fachlichen Modell, der sog. Liefervereinbarung, beschrieben. Aus diesem Modell
wiederum wird eine generische Erhebungsbeschreibung im Format DatML/SDF erzeugt. Als
internes Metadatenformat ist es nicht in XStatistik enthalten.
Bestandteil der Erhebungsbeschreibung sind die einzelnen Merkmale und Merkmalsgruppen,
ein Datenmodell zur technischen Definition des logischen Modells, die verwendeten
Klassifikationen, sowie Qualitätsanforderungen.
Die Lieferung von statistischen Rohdaten für eine bestimmte Erhebung mit ihrem definierten
Umfang statistischer Merkmale ist eine konkrete Anwendung des generischen Dokumententyps.
Dienstleister für
Datenmeldung beauftragen
5
Abbildung 2.2. Anwendungsfall: Datengewinnung vorbereiten
2.3. Dienstleister für Datenmeldung beauftragen
Nimmt ein Dienstleister die Rolle des Melders wahr, kann dieser statistische Daten im
Auftrag des Berichtspflichtigen an den Berichtsempfänger übermitteln. Die übermittelte
Rohdatenmeldung ist dabei so ausgelegt, dass Daten mehrerer Berichtspflichtiger und jeweils
mehrerer Berichtszeiträume enthalten sein können.
Wird ein Dienstleister beauftragt, hat das Auswirkungen auf die Rohdatenmeldung. Als
Absender der Nachricht vom Typ DatML-RAW-D tritt der Dienstleister auf, während die
einzelnen Berichtspflichtigen innerhalb des Elementes Nachricht bzw. Segment angegeben
werden. Liefert der Berichtspflichtige hingegen die Daten selbst an die amtliche Statistik, wird
lediglich einmal der Absender angegeben.
Rohdaten melden
6
Abbildung 2.3. Anwendungsfall: Dienstleister für Datenmeldung beauftragen
2.4. Rohdaten melden
Die Rohdatenmeldung DatML-RAW-D ist das zentrale Element dieses Anwendungsfalls
und wird verwendet unabhängig davon, ob der Berichtspflichtige selbst meldet oder einen
Dienstleister beauftragt. Aus fachlicher Sicht ist es ein generischer Dokumententyp, da
er erhebungsübergreifend verwendet werden kann. Seine Struktur ist auf größtmögliche
Flexibilität ausgelegt und erlaubt die Lieferung von Daten für beliebige und beliebig viele
Erhebungen, für unterschiedliche Berichtszeiträume, von unterschiedlichen Berichtspflichtigen
und für unterschiedliche Berichtsempfänger in einem Dokument. Das Schema ist sowohl
absender- wie auch empfängerseitig mandantenfähig. Desweiteren werden Zusatzfunktionen wie
Testunterstützung, Adressänderung und Empfangsbestätigung unterstützt.
Einzelmeldung weiterleiten
7
Abbildung 2.4. Anwendungsfall: Rohdaten melden
2.5. Einzelmeldung weiterleiten
Die flexible Struktur der Rohdatenmeldung erlaubt es, mehrere Einzelmeldungen in einer
Rohdatenmeldung zu kapseln, die für verschiedene Berichtsempfänger bestimmt sind. Die
vollständige Rohdatenmeldung wird im zentralen Dateneingang von eSTATISTIK.core geprüft und
in Einzelmeldungen zerlegt. Die Einzelmeldungen werden im nächsten Schritt an die zuständigen
Berichtsempfänger weitergeleitet.
Datenempfang bestätigen
8
Abbildung 2.5. Anwendungsfall: Einzelmeldung weiterleiten
2.6. Datenempfang bestätigen
Der Empfang einer Rohdatenmeldung wird dem Absender in Form einer Nachricht im DatMLRES-D-Format bestätigt. Sind während der Prüfung Fehler aufgetreten, erhält der Absender vom
Empfänger mit dem Prüfprotokoll eine Liste aller Fehlermeldungen.
Bitte beachten: Die derzeit übermittelten Prüfprotokolle verwenden aus Gründen der
Abwärtskompatibilität einen anderen Namensraum als XStatistik und können daher nur dann
gegen das XML Schema validiert werden, wenn dieser in den empfangenen XML-Dokumenten
angepasst wird. Die Struktur des Schemas entspricht jedoch der des Originalformates DatML/RES
1.0.
Datenempfang bestätigen
9
Abbildung 2.6. Anwendungsfall: Datenempfang bestätigen
10
11
Kapitel 3. Informationsmodell
3.1. Übersicht der Hauptgruppen
Es existieren die folgenden Hauptgruppen im Modell:
Hauptgruppe
Datenerhebung
3.2. Hauptgruppe: Datenerhebung
3.2.1. Übersicht zum Schema
Hauptgruppe zur Beschreibung von globalen Elementen zur Unterstützung der Datenerhebung.
XML-Schema: xstatistik-nachrichten.xsd
Eigenschaft Wert
Version 2.0.1
Namensraum http://www.destatis.de/schema/datml-raw/2.0/de
Präfix xst
URL des Schemas http://www.statspez.de/service/downloads/XStatistik/v2_0_1/
xstatistik-nachrichten.xsd
Inkludierte Schemata - Baukasten,
Importierte Schemata - XOEV-Basisdatentypen (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd, Präfix: xoev-dt)
3.2.2. Nachrichten der Hauptgruppe
Übersicht der Nachrichten
Es existieren die folgenden Nachrichten in der Hauptgruppe Datenerhebung:
Nr. Nachricht
- DatML-RAW-D
- DatML-RES-D
DatML-RAW-D
Bitte beachten: Im XÖV-Kontext wird die Bezeichnung "Nachricht" verwendet, um die vollständige
Informationseinheit zu beschreiben, die im Rahmen des Datenaustauschs versendet wird.
Innerhalb dieser Spezifikation wird der Begriff "Nachricht" – sofern nicht anders angegeben –
jedoch verwendet, um ein Element vom Typ Nachricht zu beschreiben. Dieses stellt einen
Bestandteil einer Rohdatenmeldung dar. Innerhalb der Empfangsbestätigung vom Typ DatMLRES-D wiederum wird die Bezeichnung "Prüfnachricht" verwendet, um einen Bestandteil des
Prüfprotokolls zu beschreiben.
Der Nachrichtentyp DatML-RAW-D wird zur Meldung von statistischen Rohdaten (siehe auch
Kapitel 2, Datenerhebung) verwendet. Eine Rohdatenmeldung enthält genau einen Absender,
genau einen Empfänger und mindestens ein Element vom Typ Nachricht. Optional sind ein
Kommentar, Verarbeitungsoptionen (Optionen), Protokolldaten und zu Kontrollzwecken die
Anzahl der Nachrichten. Das Suffix'-D' zeigt die deutsche Version des Dokumententyps an.
Nachrichten der Hauptgruppe
12
Das Datenformat erlaubt die gleichzeitige Übertragung beliebig vieler statistischer
Einzelmeldungen. Diese können ohne Einschränkung bezüglich des fachlichen Kontextes
kombiniert werden.
Als Ergänzung bietet der Nachrichtentyp Mechanismen für die sinnvolle und redundanzfreie
Strukturierung von Mengen von Einzelmeldungen: die Verwendung mehrerer Elemente vom
Typ Nachricht und die Segmentierung von Nachrichten (Segment). Während es zwischen
zwei Nachrichten keinen Bezug gibt, können Metadaten wie Erhebung, Berichtszeitraum und
Berichtspflichtiger von mehreren Segmenten gemeinsam genutzt werden. Hierzu werden die
Segmente hierarchisch angeordnet, wodurch die Metadaten entlang dieser Baumstruktur – von
einem Element Nachricht ausgehend, über mehrere Segmente bis hin zu den Elementen des
Typs Datensegment – verteilt werden.
Beide Mechanismen erlauben Meldern eine Ihren Bedürfnissen angepasste Konstruktion der
Dokumente.
DatML-RAW-D
type = < anonymous>
attribute s
version
me mo
type = xoev-dt:String.Latin
0..1
optione n
type = xst:Optionen
0..1
protokoll
type = xst:Protokoll
0..1
abs e nde r
type = xst:Absender
e mpfae ng e r
type = xst:Empfaenger
nachricht
type = xst:Nachricht
1..*
anzahl
type = xs:positiveInteger
0..1
Abbildung 3.1. xst:DatML-RAW-D
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema DatML-RAW-D (globales Element)
Nachrichten der Hauptgruppe
13
Eigenschaft Wert
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Sender (allgemein) -
Empfänger (allgemein) -
Rechtsgrundlagen - Bundesstatistikgesetz
Elemente
Element: nachricht
Eigenschaft Wert
Name im XML-Schema nachricht
Beschreibung Nachrichten enthalten statistische Rohdaten sowie Metadaten,
die den statistischen Kontext einer Rohdatenmeldung
(StatistischerKontext) beschreiben. Die optionale
Segmentierung einer Nachricht erlaubt es, beliebig viele
Rohdatenmeldungen mit unterschiedlichem statistischen Kontext in
einer Nachricht zu übermitteln und die Metadaten redundanzfrei
abzuspeichern. Mit dem Element nachrichtenID kann einer
Nachricht ein Identifikator zugeordnet werden.
Implementierungshinweis -
Typ xst:Nachricht
Häufigkeit 1 .. *
Default -
Nil-Wert möglich? nein
Form qualified
Element: anzahl
Eigenschaft Wert
Name im XML-Schema anzahl
Beschreibung Optionales Element zur Angabe der im Dokument übermittelten
Nachrichten.
Implementierungshinweis -
Typ xs:positiveInteger (http://www.w3.org/2001/XMLSchema.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Attribute
Attribut: version
Eigenschaft Wert
Name im XML-Schema version
Nachrichten der Hauptgruppe
14
Attribut: version
Eigenschaft Wert
Beschreibung Hilfstyp zur Einschränkung der für eine Nachricht vom Typ DatMLRAW-D gültigen Versionsnummer. Derzeit ist ausschließlich die
Version 2.0 gültig.
Implementierungshinweis -
Typ xst:Token.Version.DatML-RAW-D
Optional nein
Default -
Lokale Strukturen
Name in der Spezifikation
Nachrichtenkopf
DatML-RES-D
Die Nachricht DatML-RES-D ist komplementär zu DatML-RAW-D. Mit DatML-RES-D werden
Prüfprotokolle von den erhebenden Stelle an den Melder versendet, um Auskunft über die
Qualität der eingegangen Meldungen zu geben.
Nachrichtentyp zur Meldung von statistischen Rohdaten (siehe auch Kapitel 2, Datenerhebung).
Eine Nachricht enthält genau einen Absender, genau einen Empfänger und mindestens
ein Prüfprotokoll. Optional sind ein Kommentar, Verarbeitungsoptionen (Optionen) und
Protokolldaten. Das Suffix'-D' zeigt die deutsche Version des Dokumententyps an.
In Bezug auf eine vorausgegangene Rohdatenmeldung sind die Rollen von Absender und
Empfänger vertauscht. Wurde die Rohdatenmeldung über einen zentralen Erhebungsserver
verschickt, der eine Verteilung vornimmt, und wird das Prüfprotokoll nicht durch jenen Server,
sondern erst beim Berichtsempfänger erstellt und dann direkt zum ursprünglichen Absender
übertragen, nimmt der Berichtsempfänger die Rolle des Absenders ein.
Nachrichten der Hauptgruppe
15
DatML-RES-D
type = < anonymous>
attribute s
version
me mo
type = xoev-dt:String.Latin
0..1
optione n
type = xst:Optionen
0..1
protokoll
type = xst:Protokoll
0..1
abs e nde r
type = xst:Absender
e mpfae ng e r
type = xst:Empfaenger
prue fprotokoll
type = xst:Pruefprotokoll
Abbildung 3.2. xst:DatML-RES-D
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema DatML-RES-D (globales Element)
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Sender (allgemein) -
Empfänger (allgemein) -
Rechtsgrundlagen - Bundesstatistikgesetz
Elemente
Element: pruefprotokoll
Eigenschaft Wert
Name im XML-Schema pruefprotokoll
Beschreibung Ein Prüfprotokoll enthält die Prüfergebnisse für eine
Rohdatenmeldung. Die Ergebnisse sind analog zur logischen
Struktur einer Meldung im DatML-RAW-D-Format unterteilt in die
Ebenen Prüfdokument, Nachricht und Meldung. Der Umfang
der Prüfungen und damit des Prüfprotokolls kann in Abhängigkeit
des Meldungsformates und der Prüfverfahren variieren und ist
entsprechend zu dokumentieren.
Spezifische Typen der Hauptgruppe
16
Element: pruefprotokoll
Eigenschaft Wert
Implementierungshinweis -
Typ xst:Pruefprotokoll
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Attribute
Attribut: version
Eigenschaft Wert
Name im XML-Schema version
Beschreibung Hilfstyp zur Einschränkung der für eine Nachricht vom Typ DatMLRES-D gültigen Versionsnummer. Derzeit ist ausschließlich die
Version 1.0 gültig.
Implementierungshinweis -
Typ xst:Token.Version.DatML-RES-D
Optional nein
Default -
Lokale Strukturen
Name in der Spezifikation
Nachrichtenkopf
3.2.3. Spezifische Typen der Hauptgruppe
Übersicht der hauptgruppenspezifischen Typen
Es existieren keine spezifischen Typen für die Hauptgruppe.
3.3. Allgemeine Typen
3.3.1. Baukasten
Übersicht zum Schema
XML-Schema: xstatistik-baukasten.xsd
Eigenschaft Wert
Version 2.0.1
Namensraum http://www.destatis.de/schema/datml-raw/2.0/de
Präfix xst
URL des Schemas http://www.statspez.de/service/downloads/XStatistik/v2_0_1/
xstatistik-baukasten.xsd
Inkludierte Schemata - Basisdatentypen,
Importierte Schemata - XOEV-Basisdatentypen (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd, Präfix: xoev-dt)
Baukasten
17
Übersicht der Typen
Es existieren die folgenden Typen für den Baukasten:
Name in der Spezifikation Name im XML-Schema
Absender Absender
AnforderungEmpfangsbestaetigung AnforderungEmpfangsbestaetigung
Anschrift Anschrift
Anwendung Anwendung
Berichtszeitraum Berichtszeitraum
Berichtszeitraum.Sequence Berichtszeitraum.Sequence
Berichtszeitraumdatum Berichtszeitraumdatum
Berichtszeitraumdatum.Choice Berichtszeitraumdatum.Choice
Berichtszeitraumdatum.Choice.Sequence Berichtszeitraumdatum.Choice.Sequence
Datei Datei
Datei.Choice Datei.Choice
Datenattribute Datenattribute
Dateneingang Dateneingang
Dateneingang.Choice Dateneingang.Choice
Datensegment Datensegment
Datensegment.Choice Datensegment.Choice
Dokumententyp Dokumententyp
Dokumentinstanz Dokumentinstanz
Empfaenger Empfaenger
Erhebung Erhebung
Fehler Fehler
Formular Formular
Funktionselement Funktionselement
Hilfsmerkmal Hilfsmerkmal
Identitaet Identitaet
Kontakt Kontakt
Kontakt.Sequence Kontakt.Sequence
Korrektur Korrektur
Material Material
Meldungsart Meldungsart
Merkmal Merkmal
Merkmal.Choice Merkmal.Choice
Merkmalsgruppe Merkmalsgruppe
Merkmalsgruppe.Choice Merkmalsgruppe.Choice
Nachricht Nachricht
Nachrichtenkopf Nachrichtenkopf
Optionen Optionen
Ordnungsmerkmal Ordnungsmerkmal
Baukasten
18
Name in der Spezifikation Name im XML-Schema
Ordnungsmerkmal.Sequence Ordnungsmerkmal.Sequence
Ordnungsmerkmal.Sequence.Choice Ordnungsmerkmal.Sequence.Choice
Organisation Organisation
Person Person
Protokoll Protokoll
Pruefdokument Pruefdokument
Pruefmeldung Pruefmeldung
Pruefnachricht Pruefnachricht
Pruefprotokoll Pruefprotokoll
Pruefstatus Pruefstatus
Pruefung Pruefung
Satz Satz
Satz.Choice Satz.Choice
Segment Segment
StatistischerKontext StatistischerKontext
StatistischerKontext.Choice StatistischerKontext.Choice
Test Test
Absender
Der Absender versendet das Dokument. Handelt es sich um eine Rohdatenmeldung, kann er
selbst Berichtspflichtiger sein und/oder für Dritte berichten. Eine Empfangsbestätigung wird
i.d.R. von einem Statistischen Landesamt oder dem Statistischen Bundesamt versendet.
Für eine Rohdatenmeldung steht zur Änderung der Adress- und Kontaktinformationen das
Element Korrektur zur Verfügung. Es ist anwendungsspezifisch festzulgegen, welche Daten zu
Verifikation der Identität des Absenders herangezogen werden.
Baukasten
19
Abs e nde r
ke nnung
type = xst:String.TextKlasse
be re chtig ung
type = xst:String.TextKlasse
0..1
ide ntifikation
type = xst:Kontakt
0..1
e xte rne Ide ntifikation
type = xst:String.TextKlasse
0..1
kontakt
type = xst:Kontakt
0..1
korre ktur
type = xst:Korrektur
0..1
me mo
type = xoev-dt:String.Latin
0..1
Abbildung 3.3. xst:Absender
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Absender
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Nachrichtenkopf,
- xst:Pruefmeldung,
- xst:StatistischerKontext,
Elemente
Element: kennung
Eigenschaft Wert
Name im XML-Schema kennung
Baukasten
20
Element: kennung
Eigenschaft Wert
Beschreibung Erweiterung des Typs String.Latin um ein Attribut klasse
zur Beschreibung von Zeichenketten. Im Gegensatz zum Typ
String.TextKlasseNoDefault wird für das Attribut klasse
der Standardwert default gesetzt.
Implementierungshinweis -
Typ xst:String.TextKlasse
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: berechtigung
Eigenschaft Wert
Name im XML-Schema berechtigung
Beschreibung Das Element berechtigung kann für den Berechtigungsnachweis
des Absenders zur Teilnahme an einem Lieferverfahren verwendet
werden. Da ein Berechtigungsschlüssel erhebungsabhängig sein
kann, ist er auch im Typ Erhebung zulässig.
Ist ein Berechtigungsschlüssel für einen Berichtspflichtigen über
alle Erhebungen einheitlich, ist es ausreichend, den Schlüssel im
Typ Absender anzugeben.
Ist der Berechtigungsschlüssel zusätzlich erhebungsspezifisch,
muss er im Typ Erhebung angegeben werden, falls ein
Berichtspflichtiger für mehr als eine Erhebung meldet. Dies ist
nicht notwendig, wenn die Metadaten derart organisiert sind,
dass keine strukturelle Unterordnung der Erhebung unter den
Berichtspflichtigen existiert.
Implementierungshinweis -
Typ xst:String.TextKlasse
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: identifikation
Eigenschaft Wert
Name im XML-Schema identifikation
Beschreibung Die Klasse Kontakt enthält Elemente zur Beschreibung von
Kontaktdaten. Zur Beschreibung der Kontaktdaten stehen ein
strukturiertes (Kontakt.Sequence) und ein zeilenbasiertes
Inhaltsmodell (Element: zeile) zur Verfügung.
Anmerkung
Die Klasse Kontakt wird bei den verschiedenen Akteuren
sowohl für das Element identifikation als auch für
Baukasten
21
Element: identifikation
Eigenschaft Wert
kontakt verwendet. Das Element identifikation
ergänzt die Pflichtangabe kennung des Akteurs um
zusätzliche Adressangaben. Das Element kontakt
hingegen ermöglicht die Angabe eines zusätzlichen
Ansprachpartners, z. B. bei fachlichen Rückfragen.
Implementierungshinweis -
Typ xst:Kontakt
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: externeIdentifikation
Eigenschaft Wert
Name im XML-Schema externeIdentifikation
Beschreibung Das Element externeIdentifikation erlaubt es
Dienstleistern, die für ihre Kunden DatML-RAW-D-Nachrichten
erzeugen, ein eigenes Identifikationsmerkmal – z. B. eine
Kundennummer – anzugeben.
Implementierungshinweis -
Typ xst:String.TextKlasse
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: kontakt
Eigenschaft Wert
Name im XML-Schema kontakt
Beschreibung Die Klasse Kontakt enthält Elemente zur Beschreibung von
Kontaktdaten. Zur Beschreibung der Kontaktdaten stehen ein
strukturiertes (Kontakt.Sequence) und ein zeilenbasiertes
Inhaltsmodell (Element: zeile) zur Verfügung.
Anmerkung
Die Klasse Kontakt wird bei den verschiedenen Akteuren
sowohl für das Element identifikation als auch für
kontakt verwendet. Das Element identifikation
ergänzt die Pflichtangabe kennung des Akteurs um
zusätzliche Adressangaben. Das Element kontakt
hingegen ermöglicht die Angabe eines zusätzlichen
Ansprachpartners, z. B. bei fachlichen Rückfragen.
Implementierungshinweis -
Typ xst:Kontakt
Häufigkeit 0 .. 1
Default -
Baukasten
22
Element: kontakt
Eigenschaft Wert
Nil-Wert möglich? nein
Form qualified
Element: korrektur
Eigenschaft Wert
Name im XML-Schema korrektur
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht nicht
definiert.
Implementierungshinweis -
Typ xst:Korrektur
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: memo
Eigenschaft Wert
Name im XML-Schema memo
Beschreibung Das Feld memo ermöglicht die Angabe eines zusätzlichen
Kommentars.
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
AnforderungEmpfangsbestaetigung
Das Element AnforderungEmpfangsbestätigung erlaubt die Anforderung einer
Empfangsbestätigung. Optionale Attribute bestimmen Versandart, Format und eine
Betreffangabe.
Anforde rung Empfang s be s tae tig ung
attribute s
betreff
format
versandart
Abbildung 3.4. xst:AnforderungEmpfangsbestaetigung
Baukasten
23
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema AnforderungEmpfangsbestaetigung
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Optionen,
Attribute
Attribut: betreff
Eigenschaft Wert
Name im XML-Schema betreff
Beschreibung Diese optionale Angabe wird als Betreff in die angeforderte
Empfangsbestätigung eingefügt.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Attribut: format
Eigenschaft Wert
Name im XML-Schema format
Beschreibung Mit dem Attribut format kann das Datenformat der angeforderten
Empfangsbestätigung spezifiziert werden. Neben einer Textdatei
kann die Ausgabe als DatML-RES-D-Nachricht übermittelt
werden.
Implementierungshinweis -
Typ xst:Token.FormatEmpfangsbestaetigung
Optional ja
Default default
Attribut: versandart
Eigenschaft Wert
Name im XML-Schema versandart
Beschreibung Mit diesem Attribut kann die Versandart angegeben werden, mit der
die angeforderte Empfangsbestätigung an den Auskunftgebenden
versendet werden soll.
Implementierungshinweis -
Typ xst:Token.Versandart
Optional ja
Default default
Anschrift
Der Typ Anschrift bezeichnet eine postalische Adresse, erweitert um die Möglichkeit, Kreis und
Bundesland anzugeben. Diese für deutsche Adressen unüblichen Feldern wurden zugunsten der
Symmetrie zur geplanten englischen Version des Nachrichtentyps hinzugefügt.
Baukasten
24
Ans chrift
s tras s e
type = xst:String.TextZeileHTML
0..1
haus numme r
type = xst:String.TextZeileHTML
0..1
pos tfach
type = xst:String.TextZeileHTML
0..1
pos tfachle itzahl
type = xst:String.TextZeileHTML
0..1
pos tfachort
type = xst:String.TextZeileHTML
0..1
pos tle itzahl
type = xst:String.TextZeileHTML
ort
type = xst:String.TextZeileHTML
kre is
type = xst:String.TextZeileHTML
0..1
bunde s land
type = xst:String.TextZeileHTML
0..1
land
type = xst:String.TextZeileHTML
0..1
zus atz
type = xst:String.TextZeileHTML
0..1
Abbildung 3.5. xst:Anschrift
Baukasten
25
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Anschrift
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Kontakt.Sequence,
Elemente
Element: strasse
Eigenschaft Wert
Name im XML-Schema strasse
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: hausnummer
Eigenschaft Wert
Name im XML-Schema hausnummer
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: postfach
Eigenschaft Wert
Name im XML-Schema postfach
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Baukasten
26
Element: postfach
Eigenschaft Wert
Nil-Wert möglich? nein
Form qualified
Element: postfachleitzahl
Eigenschaft Wert
Name im XML-Schema postfachleitzahl
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: postfachort
Eigenschaft Wert
Name im XML-Schema postfachort
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: postleitzahl
Eigenschaft Wert
Name im XML-Schema postleitzahl
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: ort
Eigenschaft Wert
Name im XML-Schema ort
Baukasten
27
Element: ort
Eigenschaft Wert
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: kreis
Eigenschaft Wert
Name im XML-Schema kreis
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: bundesland
Eigenschaft Wert
Name im XML-Schema bundesland
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: land
Eigenschaft Wert
Name im XML-Schema land
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Baukasten
28
Element: land
Eigenschaft Wert
Default -
Nil-Wert möglich? nein
Form qualified
Element: zusatz
Eigenschaft Wert
Name im XML-Schema zusatz
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Anwendung
Dieses Element beinhaltet Informationen über die Anwendung, von der die Nachricht erzeugt
wurde.
Anw e ndung
anw e ndung s name
type = xst:String.TextZeileHTML
ve rs ion
type = xoev-dt:String.Latin
0..1
s e rve r
type = xoev-dt:String.Latin
0..1
he rs te lle r
type = xoev-dt:String.Latin
0..1
ze rtifikat
type = xst:String.TextKlasseNoDefault
0..1
Abbildung 3.6. xst:Anwendung
Baukasten
29
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Anwendung
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Datei,
- xst:Dateneingang,
- xst:Dokumentinstanz,
Elemente
Element: anwendungsname
Eigenschaft Wert
Name im XML-Schema anwendungsname
Beschreibung Der Name der Anwendung.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: version
Eigenschaft Wert
Name im XML-Schema version
Beschreibung Die verwendete Version der Anwendung.
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: server
Eigenschaft Wert
Name im XML-Schema server
Beschreibung Details zum Server, auf dem die Nachricht generiert wurden.
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Baukasten
30
Element: server
Eigenschaft Wert
Default -
Nil-Wert möglich? nein
Form qualified
Element: hersteller
Eigenschaft Wert
Name im XML-Schema hersteller
Beschreibung Der Name des Herstellers der Anwendung.
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: zertifikat
Eigenschaft Wert
Name im XML-Schema zertifikat
Beschreibung Falls die Anwendung die Angabe eines Zertifikatschlüssels
vorschreibt, kann dieser im Element zertifikat abgelegt
werden.
Implementierungshinweis -
Typ xst:String.TextKlasseNoDefault
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Berichtszeitraum
Der Typ Berichtszeitraum gibt den Berichtszeitraum der gelieferten statistischen Daten an. Dabei
handelt es sich entweder um ein Einzeldatum, beginnend mit der obligatorischen Angabe des
Jahres, oder um zwei Einzeldaten, die Beginn und Ende des Berichtszeitraumes markieren. Die
Angaben sind einschließende Werte. In Spannen sind verschiedene Zeiträume für Beginn und
Ende möglich, z.B. „zweites Halbjahr 1999 bis einschließlich drittes Quartal 2000“.
Baukasten
31
Be richts ze itraum
s tring
type = xst:String.Formatiert
jahr
type = xst:PositiveInteger.Jahr
0..1
halbjahr
type = xst:PositiveInteger.Halbjahr
s e me s te r
type = xst:PositiveInteger.Halbjahr
quartal
type = xst:PositiveInteger.Quartal
w oche
type = xst:PositiveInteger.Woche
monat
type = xst:PositiveInteger.Monat
tag
type = xst:PositiveInteger.Tag
0..1
be g inn
type = xst:Berichtszeitraumdatum
e nde
type = xst:Berichtszeitraumdatum
Abbildung 3.7. xst:Berichtszeitraum
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Berichtszeitraum
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Choice
Verwendet in - xst:Pruefmeldung,
- xst:StatistischerKontext,
Elemente
Element: string
Eigenschaft Wert
Name im XML-Schema string
Baukasten
32
Element: string
Eigenschaft Wert
Beschreibung Der Berichtszeitraum kann auch eine formatierte Zeichenkette
(String.Formatiert) sein. Die Festlegungen zulässiger
Datumsangaben und weitere Regeln erfolgen in der Anwendung.
Implementierungshinweis -
Typ xst:String.Formatiert
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Lokale Strukturen
Name in der Spezifikation
Berichtszeitraumdatum
Berichtszeitraum.Sequence
Berichtszeitraum.Sequence
Lokaler Hilfstyp zur abwärtskompatiblen Modellierung der übergeordneten Klasse.
Be richts ze itraum.Se que nce
be g inn
type = xst:Berichtszeitraumdatum
e nde
type = xst:Berichtszeitraumdatum
Abbildung 3.8. xst:Berichtszeitraum.Sequence
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Berichtszeitraum.Sequence
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Berichtszeitraum,
Elemente
Element: beginn
Eigenschaft Wert
Name im XML-Schema beginn
Baukasten
33
Element: beginn
Eigenschaft Wert
Beschreibung Beginn eines Zeitraumes in Form eines Kalender-, Halbjahres-,
Vierteljahres-, Wochendatums oder Semesters.
Implementierungshinweis -
Typ xst:Berichtszeitraumdatum
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: ende
Eigenschaft Wert
Name im XML-Schema ende
Beschreibung Ende eines Zeitraumes in Form eines Kalender-, Halbjahres-,
Vierteljahres-, Wochendatums oder Semesters.
Implementierungshinweis -
Typ xst:Berichtszeitraumdatum
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Berichtszeitraumdatum
Baukasten
34
Be richts ze itraumdatum
jahr
type = xst:PositiveInteger.Jahr
0..1
halbjahr
type = xst:PositiveInteger.Halbjahr
s e me s te r
type = xst:PositiveInteger.Halbjahr
quartal
type = xst:PositiveInteger.Quartal
w oche
type = xst:PositiveInteger.Woche
monat
type = xst:PositiveInteger.Monat
tag
type = xst:PositiveInteger.Tag
0..1
Abbildung 3.9. xst:Berichtszeitraumdatum
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Berichtszeitraumdatum
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Berichtszeitraum,
- xst:Berichtszeitraum.Sequence,
Elemente
Element: jahr
Eigenschaft Wert
Name im XML-Schema jahr
Beschreibung Datentyp für die Angabe des Jahres des Berichtszeitraumes.
Implementierungshinweis -
Typ xst:PositiveInteger.Jahr
Häufigkeit 1
Baukasten
35
Element: jahr
Eigenschaft Wert
Default -
Nil-Wert möglich? nein
Form qualified
Lokale Strukturen
Name in der Spezifikation
Berichtszeitraumdatum.Choice
Berichtszeitraumdatum.Choice
Lokaler Hilfstyp zur abwärtskompatiblen Modellierung der übergeordneten Klasse.
Be richts ze itraumdatum.Choice
halbjahr
type = xst:PositiveInteger.Halbjahr
s e me s te r
type = xst:PositiveInteger.Halbjahr
quartal
type = xst:PositiveInteger.Quartal
w oche
type = xst:PositiveInteger.Woche
monat
type = xst:PositiveInteger.Monat
tag
type = xst:PositiveInteger.Tag
0..1
Abbildung 3.10. xst:Berichtszeitraumdatum.Choice
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Berichtszeitraumdatum.Choice
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Choice
Baukasten
36
Eigenschaft Wert
Verwendet in - xst:Berichtszeitraumdatum,
Elemente
Element: halbjahr
Eigenschaft Wert
Name im XML-Schema halbjahr
Beschreibung Datentyp für die Angabe des Halbjahres des Berichtszeitraumes.
Dieser Datentyp wird intern auch für die Angabe des Semesters
verwendet (siehe auch Token.Formatklasse).
Implementierungshinweis -
Typ xst:PositiveInteger.Halbjahr
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: semester
Eigenschaft Wert
Name im XML-Schema semester
Beschreibung Datentyp für die Angabe des Halbjahres des Berichtszeitraumes.
Dieser Datentyp wird intern auch für die Angabe des Semesters
verwendet (siehe auch Token.Formatklasse).
Implementierungshinweis -
Typ xst:PositiveInteger.Halbjahr
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: quartal
Eigenschaft Wert
Name im XML-Schema quartal
Beschreibung Datentyp für die Angabe des Quartals des Berichtszeitraumes.
Implementierungshinweis -
Typ xst:PositiveInteger.Quartal
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: woche
Eigenschaft Wert
Name im XML-Schema woche
Baukasten
37
Element: woche
Eigenschaft Wert
Beschreibung Datentyp für die Angabe der Kalenderwoche des
Berichtszeitraumes.
Implementierungshinweis -
Typ xst:PositiveInteger.Woche
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Lokale Strukturen
Name in der Spezifikation
Berichtszeitraumdatum.Choice.Sequence
Berichtszeitraumdatum.Choice.Sequence
Lokaler Hilfstyp zur abwärtskompatiblen Modellierung der übergeordneten Klasse. Ein Tag kann
nur in Verbindung mit einem Monat angegeben werden.
Be richts ze itraumdatum.Choice .Se que nce
monat
type = xst:PositiveInteger.Monat
tag
type = xst:PositiveInteger.Tag
0..1
Abbildung 3.11. xst:Berichtszeitraumdatum.Choice.Sequence
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Berichtszeitraumdatum.Choice.Sequence
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Berichtszeitraumdatum.Choice,
Elemente
Element: monat
Eigenschaft Wert
Name im XML-Schema monat
Baukasten
38
Element: monat
Eigenschaft Wert
Beschreibung Datentyp für die Angabe des Monats des Berichtszeitraumes.
Implementierungshinweis -
Typ xst:PositiveInteger.Monat
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: tag
Eigenschaft Wert
Name im XML-Schema tag
Beschreibung Datentyp für die Angabe des Tages im Monat des
Berichtszeitraumes.
Implementierungshinweis -
Typ xst:PositiveInteger.Tag
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Datei
Der Typ datei enthält Angaben zur Dokumentation der Datenlieferung in Dateiform. Es können
die Datei selbst (Dateiname), Datum und Uhrzeit ihrer Erzeugung, die Anwendung, welche die
Lieferdatei erzeugt hat (Anwendung) angegeben werden.
Weiterhin, sofern bekannt, kann ein mit der Datei gelieferter Identifikator (DokumentID), das
Datenformat und der Lieferweg (Datenträger bzw. Upload) beschrieben werden.
Enthält die DatML-RAW-D-Nachricht ein Element Dokumentinstanz, werden – falls
vorhanden – dessen Kindelemente dateiname, datum, uhrzeit, dokumentID und
anwendung in das Element datei übernommen.
Baukasten
39
Date i
date iname
type = xoev-dt:String.Latin
0..1
datum
type = xst:String.Datum
0..1
uhrze it
type = xst:String.Uhrzeit
0..1
anw e ndung
type = xst:Anwendung
0..1
dokume ntID
type = xst:String.TextKlasseNoDefault
0..1
date nformat
type = xst:String.Datenformat
0..1
0..1
date ntrae g e r
type = xst:String.Datentraeger
upload
type = xst:Leertyp
Abbildung 3.12. xst:Datei
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Datei
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Dateneingang.Choice,
Baukasten
40
Elemente
Element: dateiname
Eigenschaft Wert
Name im XML-Schema dateiname
Beschreibung Einschränkung auf alle lateinischen Zeichen innerhalb Unicode (vgl.
XÖV-Handbuch).
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: datum
Eigenschaft Wert
Name im XML-Schema datum
Beschreibung Erweiterung des Typs String.Latin zur Beschreibung formatierter
Zeichenketten mit einem speziellen Formatschema für eine
Datumsangabe (siehe auch String.Formatiert).
Implementierungshinweis -
Typ xst:String.Datum
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: uhrzeit
Eigenschaft Wert
Name im XML-Schema uhrzeit
Beschreibung Erweiterung des Typs String.Latin zur Beschreibung formatierter
Zeichenketten mit einem speziellen Formatschema für eine
Uhrzeitangabe (siehe auch String.Formatiert.
Eine Uhrzeit in Form eines Strings; Formatschema und Formatklasse
sind fest vor-gegeben (2.5.7.1). Wird die Uhrzeit nicht sekundenoder sogar minutengenau ange-geben, sind die entsprechenden
Felder mit Nullen zu belegen.
Implementierungshinweis -
Typ xst:String.Uhrzeit
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Baukasten
41
Element: anwendung
Eigenschaft Wert
Name im XML-Schema anwendung
Beschreibung Dieses Element beinhaltet Informationen über die Anwendung, von
der die Nachricht erzeugt wurde.
Implementierungshinweis -
Typ xst:Anwendung
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: dokumentID
Eigenschaft Wert
Name im XML-Schema dokumentID
Beschreibung Erweiterung des Typs String.Latin um ein Attribut klasse
zur Beschreibung von Zeichenketten. Im Gegensatz zum Typ
String.TextKlasse wird für das Attribut klasse kein
Standardwert vorgegeben.
Implementierungshinweis -
Typ xst:String.TextKlasseNoDefault
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: datenformat
Eigenschaft Wert
Name im XML-Schema datenformat
Beschreibung Die Lieferung einer DatML-RAW-D-Nachricht wird im Element
Datenformat durch Eintrag des Wertes "datml" dokumentiert.
Enthält die Nachricht ein Element Dokumentinstanz, werden –
sofern vorhanden – dessen Kindelemente dateiname, datum,
uhrzeit, dokumentID und anwendung in das Element datei
übernommen.
Implementierungshinweis -
Typ xst:String.Datenformat
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Lokale Strukturen
Name in der Spezifikation
Datei.Choice
Baukasten
42
Datei.Choice
Lokaler Hilfstyp zur abwärtskompatiblen Modellierung der übergeordneten Klasse.
Date i.Choice
date ntrae g e r
type = xst:String.Datentraeger
upload
type = xst:Leertyp
Abbildung 3.13. xst:Datei.Choice
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Datei.Choice
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Choice
Verwendet in - xst:Datei,
Elemente
Element: datentraeger
Eigenschaft Wert
Name im XML-Schema datentraeger
Beschreibung Erweiterung des Typs String.Latin um ein Attribut typ zur
Beschreibung des Datenträgers, auf dem die Rohdaten ausgeliefert
wurden (siehe auch Token.Datentraeger).
Implementierungshinweis -
Typ xst:String.Datentraeger
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: upload
Eigenschaft Wert
Name im XML-Schema upload
Beschreibung Die Verwendung dieses Elementes zeigt an, dass eine Datei per
Upload geliefert wurde. Eine gesonderte Protokollierung von Datum
und Uhrzeit des absenderseitigen Uploads ist nicht vorgesehen.
Stattdessen sollen im Element dateneingang Datum und Uhrzeit des
empfängerseitigen Dateieingangs dokumentiert werden.
Implementierungshinweis -
Typ xst:Leertyp
Baukasten
43
Element: upload
Eigenschaft Wert
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Datenattribute
Der Typ Datenattribute beschreibt allgemeine Eigenschaften von Werten in einfachen
und Ordnungsmerkmalen. Für numerische Werte können Dezimalzeichen und TausenderTrennzeichen abweichend vom Default bestimmt werden.
Date nattribute
attribute s
dezimalzeichen
tausender-trennzeichen
Abbildung 3.14. xst:Datenattribute
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Datenattribute
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:StatistischerKontext,
Attribute
Attribut: dezimalzeichen
Eigenschaft Wert
Name im XML-Schema dezimalzeichen
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default ,
Attribut: tausender-trennzeichen
Eigenschaft Wert
Name im XML-Schema tausender-trennzeichen
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Baukasten
44
Attribut: tausender-trennzeichen
Eigenschaft Wert
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default .
Dateneingang
Dieses Element beschreibt die Details des Dateneingangs. Es können Datum und Uhrzeit
des Dateneingangs, ein vergebener Eingangstempel und die den Dateneingang verarbeitende
Anwendung dokumentiert werden. Weiterhin kann die Form des Dateneingangs angegeben
werden, z. B. "Papierformular" für den Fall, dass ein Belegleser die DatML-RAW-D-Nachricht
erzeugt hat.
Date ne ing ang
datum
type = xst:String.Datum
uhrze it
type = xst:String.Uhrzeit
e ing ang s s te mpe l
type = xst:String.TextKlasseNoDefault
anw e ndung
type = xst:Anwendung
0..1
papie rformular
type = xst:Formular
online formular
type = xst:Formular
date i
type = xst:Datei
Abbildung 3.15. xst:Dateneingang
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Dateneingang
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Baukasten
45
Eigenschaft Wert
Verwendet in - xst:Protokoll,
- xst:Pruefdokument,
Elemente
Element: datum
Eigenschaft Wert
Name im XML-Schema datum
Beschreibung Datum des Dateneingangs.
Implementierungshinweis -
Typ xst:String.Datum
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: uhrzeit
Eigenschaft Wert
Name im XML-Schema uhrzeit
Beschreibung Uhrzeit des Dateneingangs
Implementierungshinweis -
Typ xst:String.Uhrzeit
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: eingangsstempel
Eigenschaft Wert
Name im XML-Schema eingangsstempel
Beschreibung Erweiterung des Typs String.Latin um ein Attribut klasse
zur Beschreibung von Zeichenketten. Im Gegensatz zum Typ
String.TextKlasse wird für das Attribut klasse kein
Standardwert vorgegeben.
Implementierungshinweis -
Typ xst:String.TextKlasseNoDefault
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: anwendung
Eigenschaft Wert
Name im XML-Schema anwendung
Baukasten
46
Element: anwendung
Eigenschaft Wert
Beschreibung Dieses Element beinhaltet Informationen über die Anwendung, von
der die Nachricht erzeugt wurde.
Implementierungshinweis -
Typ xst:Anwendung
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Lokale Strukturen
Name in der Spezifikation
Dateneingang.Choice
Dateneingang.Choice
Lokaler Hilfstyp zur abwärtskompatiblen Modellierung der übergeordneten Klasse.
Date ne ing ang .Choice
papie rformular
type = xst:Formular
online formular
type = xst:Formular
date i
type = xst:Datei
Abbildung 3.16. xst:Dateneingang.Choice
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Dateneingang.Choice
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Choice
Verwendet in - xst:Dateneingang,
Elemente
Element: papierformular
Eigenschaft Wert
Name im XML-Schema papierformular
Baukasten
47
Element: papierformular
Eigenschaft Wert
Beschreibung Die Auswahl "papierformular" zeigt an, dass die Rohdaten auf
einem Papierformular geliefert wurden. Hat das Formular einen
Namen, kann dieser mit dem Element formularname angegeben
werden. Für die Identifizierung eines einzelnen Formulars oder
einer Serie von Formularen (z.B. für einen Berichtszeitraum einer
Erhebung) steht das Element formularID zur Verfügung.
Implementierungshinweis -
Typ xst:Formular
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: onlineformular
Eigenschaft Wert
Name im XML-Schema onlineformular
Beschreibung Die Auswahl "onlineformular" zeigt an, dass die Rohdaten mit einem
Online-Formular (z.B. im HTML-Format) geliefert wurden. Hat das
Formular einen Namen, kann dieser mit dem Element formularname
angegeben werden. Für die Identifizierung eines einzelnen Beleges
oder einer Serie von Formularen (z.B. für einen Berichtszeitraum
einer Erhebung) steht das Element formularID zur Verfügung.
Implementierungshinweis -
Typ xst:Formular
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: datei
Eigenschaft Wert
Name im XML-Schema datei
Beschreibung Der Typ datei enthält Angaben zur Dokumentation der
Datenlieferung in Dateiform. Es können die Datei selbst
(Dateiname), Datum und Uhrzeit ihrer Erzeugung, die Anwendung,
welche die Lieferdatei erzeugt hat (Anwendung) angegeben
werden.
Weiterhin, sofern bekannt, kann ein mit der Datei gelieferter
Identifikator (DokumentID), das Datenformat und der
Lieferweg (Datenträger bzw. Upload) beschrieben werden.
Enthält die DatML-RAW-D-Nachricht ein Element
Dokumentinstanz, werden – falls vorhanden – dessen
Kindelemente dateiname, datum, uhrzeit, dokumentID und
anwendung in das Element datei übernommen.
Implementierungshinweis -
Baukasten
48
Element: datei
Eigenschaft Wert
Typ xst:Datei
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Datensegment
Ein Datensegment ist derjenige Abschnitt eines Segmentes, der die Meldungsdatensätze vom
Typ Satz enthält, die wiederum Ordnungsmerkmale enthalten können. Innerhalb eines
Datensegmentes haben alle Daten denselben statistischen Kontext.
Der Begriff Meldung wird somit definiert als Einheit bestehend aus einem Datensegment und
den Metadaten, die sich auf dem Segmentpfad zum übergeordneten Nachrichtenelement
befinden, einschließlich den Angaben Berichtspflichtiger und Berichtsempfänger.
Die Metadaten des statistischen Kontextes erlauben es, in jedem Datensegment einen in sich
abgeschlossenen Rohdatenbestand zu liefern. Grundsätzlich entspricht daher ein Datensegment
einer Rohdatenmeldung.
Anmerkung
Es ist nicht ausgeschlossen, dass in einer DatML-RAW-D-Instanz zwei oder mehr
Datensegmente – ggf. in verschiedenen Nachrichten – den selben statistischen Kontext
besitzen.
Date ns e g me nt
me ldung s ID
type = xst:String.TextKlasseNoDefault
0..1
me ldung s art
type = xst:Meldungsart
0..1
omm
type = xst:Ordnungsmerkmal
s atz
type = xst:Satz
1..*
Abbildung 3.17. xst:Datensegment
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Datensegment
Baukasten
49
Eigenschaft Wert
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:StatistischerKontext.Choice,
Elemente
Element: meldungsID
Eigenschaft Wert
Name im XML-Schema meldungsID
Beschreibung Mit dem Element meldungsID kann einer Meldung ein Identifikator
zugeordnet werden. Das Element wird in einem Datensegment
gesetzt,da dort eine Meldung in der Segmenthierachie eindeutig ist.
Implementierungshinweis -
Typ xst:String.TextKlasseNoDefault
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: meldungsart
Eigenschaft Wert
Name im XML-Schema meldungsart
Beschreibung Mit der Meldungsart wird angegeben, für welchen Zweck die
Meldung erfolgt. Mit Ausnahme der Originallieferungen von Daten
sind dies z.B. Korrekturen und Löschungen. Der Zweck einer
Meldung wird durch das Element meldungsart ausgedrückt, das ein
entsprechendes Funktionselement enthält. Ist ein Bezug zu einer
vorausgegangenen Meldung notwendig oder möglich, erfolgt dieser
in Form der meldungsID, die dem Funktionselement nachgeordnet
ist. Das Funktionselement nil unterdrückt die Verarbeitung einer
Meldung.
Implementierungshinweis -
Typ xst:Meldungsart
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Lokale Strukturen
Name in der Spezifikation
Datensegment.Choice
Datensegment.Choice
Lokaler Hilfstyp zur abwärtskompatiblen Modellierung der übergeordneten Klasse.
Baukasten
50
Date ns e g me nt.Choice
omm
type = xst:Ordnungsmerkmal
s atz
type = xst:Satz
1..*
Abbildung 3.18. xst:Datensegment.Choice
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Datensegment.Choice
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Choice
Verwendet in - xst:Datensegment,
Elemente
Element: omm
Eigenschaft Wert
Name im XML-Schema omm
Beschreibung Ordnungsmerkmale haben wie einfache Merkmale einen Namen
und einen Wert, der jedoch nicht fehlen und nicht leer sein darf.
Im Gegensatz zu einfachen Merkmalen handels es sich dabei
um Merkmale, die eine systematische, bzw. ordnende, Aussage
haben. In Verzeichnissen geführte Merkmale wie Länderschlüssel
und Betriebsnummern sind typische Ordnungsmerkmale.
Mit Ordnungsmerkmalen können Gruppen von Datensätzen
gebildet werden, die alle den selben Wert für ein bestimmtes
Ordnungsmerkmal aufweisen. Dieses Ordnungsmerkmal ist in der
Dokumentstruktur nicht Bestandteil der Datensätze, sondern den
Datensätzen übergeordnet. Eine Folge von Datensätzen wird jeweils
genau einem Wert eines Ordnungsmerkmals zugeorgndet. Eine
sortierte Ablage der Datensätze wird dadurch nicht erzwungen.
Ordnungsmerkmale sind dennoch, wie einfache Merkmale, Teil
der statistischen Information. Aus fachlicher Sicht spielt es keine
Rolle, ob ein Merkmal als Ordnungs- oder als einfaches Merkmal
übermittelt wird. Hauptzweck von Ordnungsmerkmalen ist die
Redundanzverringerung, vor allem bei der Lieferung mittlerer und
großer Datenmengen.
Innerhalb eines Datensegmentes müssen Ordnungsmerkmale stets
gleich tief geschachtelt sein. Ordnungsmerkmale der gleichen
Hierarchiestufe müssen immer den gleichen Namen haben, also das
selbe Ordnungskriterium beschreiben. Die Anwendung muss die
Baukasten
51
Element: omm
Eigenschaft Wert
Einhaltung dieser Einschränkung prüfen, da sie nicht über ein XML
Schema definierbar ist.
Anmerkung
Enthält ein Datensegment Ordnungsmerkmale, so muss
über alle Datensätze hiweg ihre Reihenfolge in der
hierarchischen Anordnung unverändert bleiben.
Implementierungshinweis -
Typ xst:Ordnungsmerkmal
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: satz
Eigenschaft Wert
Name im XML-Schema satz
Beschreibung Ein statistischer Datensatz stellt eine Informationseinheit dar, die
zusammenhängende Daten über ein Erhebungsobjekt enthält. Ein
Satz besteht aus mindestens einem (Wert-)Merkmal und einer
optionalen Anzahlangabe für Kontrollzwecke.
Implementierungshinweis -
Typ xst:Satz
Häufigkeit 1 .. *
Default -
Nil-Wert möglich? nein
Form qualified
Dokumententyp
Diese Klasse gibt den Namen und optional die Version des zur Prüfung verwendeten
Dokumententyps an.
Dokume nte ntyp
name
type = xoev-dt:String.Latin
ve rs ion
type = xoev-dt:String.Latin
0..1
Abbildung 3.19. xst:Dokumententyp
Baukasten
52
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Dokumententyp
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Pruefung,
Elemente
Element: name
Eigenschaft Wert
Name im XML-Schema name
Beschreibung Einschränkung auf alle lateinischen Zeichen innerhalb Unicode (vgl.
XÖV-Handbuch).
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: version
Eigenschaft Wert
Name im XML-Schema version
Beschreibung Einschränkung auf alle lateinischen Zeichen innerhalb Unicode (vgl.
XÖV-Handbuch).
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Dokumentinstanz
Im Protokoll können mehrere Dokumentinstanzen gespeichert werden, die jeweiils einen
Zwischenstand der Verarbeitung der Originalnachricht repräsentieren. Es können eine DokumentID, die erzeugte Datei sowie die erzeugende Anwendung angegeben werden.
Baukasten
53
Dokume ntins tanz
date iname
type = xoev-dt:String.Latin
0..1
datum
type = xst:String.Datum
uhrze it
type = xst:String.Uhrzeit
anw e ndung
type = xst:Anwendung
0..1
dokume ntID
type = xst:String.TextKlasseNoDefault
0..1
re s s ource ID
type = xst:String.TextKlasseNoDefault
0..*
Abbildung 3.20. xst:Dokumentinstanz
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Dokumentinstanz
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Protokoll,
Elemente
Element: dateiname
Eigenschaft Wert
Name im XML-Schema dateiname
Beschreibung Einschränkung auf alle lateinischen Zeichen innerhalb Unicode (vgl.
XÖV-Handbuch).
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Baukasten
54
Element: dateiname
Eigenschaft Wert
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: datum
Eigenschaft Wert
Name im XML-Schema datum
Beschreibung Erweiterung des Typs String.Latin zur Beschreibung formatierter
Zeichenketten mit einem speziellen Formatschema für eine
Datumsangabe (siehe auch String.Formatiert).
Implementierungshinweis -
Typ xst:String.Datum
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: uhrzeit
Eigenschaft Wert
Name im XML-Schema uhrzeit
Beschreibung Erweiterung des Typs String.Latin zur Beschreibung formatierter
Zeichenketten mit einem speziellen Formatschema für eine
Uhrzeitangabe (siehe auch String.Formatiert.
Eine Uhrzeit in Form eines Strings; Formatschema und Formatklasse
sind fest vor-gegeben (2.5.7.1). Wird die Uhrzeit nicht sekundenoder sogar minutengenau ange-geben, sind die entsprechenden
Felder mit Nullen zu belegen.
Implementierungshinweis -
Typ xst:String.Uhrzeit
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: anwendung
Eigenschaft Wert
Name im XML-Schema anwendung
Beschreibung Dieses Element enthält Informationen zur Anwendung, die das
Dokument erzeugt hat. Die dokumenterzeugende Anwendung
kann die von ihr verwendeten Ressourcen, wie etwa ein DatML/
SDF-Dokument mit einer Erhebungsbeschreibung, mit Hilfe des
Elementes ressourceID dokumentieren.
Baukasten
55
Element: anwendung
Eigenschaft Wert
Implementierungshinweis -
Typ xst:Anwendung
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: dokumentID
Eigenschaft Wert
Name im XML-Schema dokumentID
Beschreibung Dieses Element enthält eine Angabe für die (eindeutige)
Identifizierung einer Dokumentinstanz.
Implementierungshinweis -
Typ xst:String.TextKlasseNoDefault
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: ressourceID
Eigenschaft Wert
Name im XML-Schema ressourceID
Beschreibung Dieses Element enthält die Kennzeichnung einer für die
Dokumentgenerierung verwendeten Ressource.
Implementierungshinweis -
Typ xst:String.TextKlasseNoDefault
Häufigkeit 0 .. *
Default -
Nil-Wert möglich? nein
Form qualified
Empfaenger
Der Empfänger einer Rohdatenmeldung ist i.d.R. ein Statistisches Landesamt oder das
Statistische Bundesamt. Der Berichtsempfänger muss in der Lage sein, sich selbst als Adressaten
zu bestätigen und benötigt deshalb eine Angabe zu seiner Identifikation. Standardmäßig ist
der Berichtsempfänger mit dem Empfänger des Dokumentes identisch. Eine externe (i.d.R. vom
Absender verwendete) Angabe für die Identifikation eines Verfahrensbeteiligten.
Baukasten
56
Empfae ng e r
ke nnung
type = xst:String.TextKlasse
0..1
ide ntifikation
type = xst:Kontakt
0..1
e xte rne Ide ntifikation
type = xst:String.TextKlasse
0..1
kontakt
type = xst:Kontakt
0..1
me mo
type = xoev-dt:String.Latin
0..1
Abbildung 3.21. xst:Empfaenger
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Empfaenger
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Nachrichtenkopf,
- xst:Pruefmeldung,
- xst:StatistischerKontext,
Elemente
Element: kennung
Eigenschaft Wert
Name im XML-Schema kennung
Beschreibung Erweiterung des Typs String.Latin um ein Attribut klasse
zur Beschreibung von Zeichenketten. Im Gegensatz zum Typ
String.TextKlasseNoDefault wird für das Attribut klasse
der Standardwert default gesetzt.
Implementierungshinweis -
Typ xst:String.TextKlasse
Häufigkeit 0 .. 1
Default -
Baukasten
57
Element: kennung
Eigenschaft Wert
Nil-Wert möglich? nein
Form qualified
Element: identifikation
Eigenschaft Wert
Name im XML-Schema identifikation
Beschreibung Die Klasse Kontakt enthält Elemente zur Beschreibung von
Kontaktdaten. Zur Beschreibung der Kontaktdaten stehen ein
strukturiertes (Kontakt.Sequence) und ein zeilenbasiertes
Inhaltsmodell (Element: zeile) zur Verfügung.
Anmerkung
Die Klasse Kontakt wird bei den verschiedenen Akteuren
sowohl für das Element identifikation als auch für
kontakt verwendet. Das Element identifikation
ergänzt die Pflichtangabe kennung des Akteurs um
zusätzliche Adressangaben. Das Element kontakt
hingegen ermöglicht die Angabe eines zusätzlichen
Ansprachpartners, z. B. bei fachlichen Rückfragen.
Implementierungshinweis -
Typ xst:Kontakt
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: externeIdentifikation
Eigenschaft Wert
Name im XML-Schema externeIdentifikation
Beschreibung Das Element externeIdentifikation erlaubt es
Dienstleistern, die für ihre Kunden DatML-RAW-D-Nachrichten
erzeugen, ein eigenes Identifikationsmerkmal – z. B. eine
Kundennummer – anzugeben.
Implementierungshinweis -
Typ xst:String.TextKlasse
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: kontakt
Eigenschaft Wert
Name im XML-Schema kontakt
Beschreibung Die Klasse Kontakt enthält Elemente zur Beschreibung von
Kontaktdaten. Zur Beschreibung der Kontaktdaten stehen ein
Baukasten
58
Element: kontakt
Eigenschaft Wert
strukturiertes (Kontakt.Sequence) und ein zeilenbasiertes
Inhaltsmodell (Element: zeile) zur Verfügung.
Anmerkung
Die Klasse Kontakt wird bei den verschiedenen Akteuren
sowohl für das Element identifikation als auch für
kontakt verwendet. Das Element identifikation
ergänzt die Pflichtangabe kennung des Akteurs um
zusätzliche Adressangaben. Das Element kontakt
hingegen ermöglicht die Angabe eines zusätzlichen
Ansprachpartners, z. B. bei fachlichen Rückfragen.
Implementierungshinweis -
Typ xst:Kontakt
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: memo
Eigenschaft Wert
Name im XML-Schema memo
Beschreibung Das Feld memo ermöglicht die Angabe eines zusätzlichen
Kommentars.
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Erhebung
Eine Erhebungsangabe hat eine Kennung und einen optionalen Namen. Stammt die Kennung aus
einer Klassifikation oder Systematik, kann diese mit dem Attribut klasse des Elementes kennung
angegeben werden. Es ist ausserdem möglich, eine Authentifizierungsangabe (berechtigung)
abzulegen, da diese erhebungsabhängig sein kann.
Baukasten
59
Erhe bung
ke nnung
type = xst:String.TextKlasse
te xt
type = xoev-dt:String.Latin
0..1
be re chtig ung
type = xst:String.TextKlasse
0..1
Abbildung 3.22. xst:Erhebung
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Erhebung
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Pruefmeldung,
- xst:StatistischerKontext,
Elemente
Element: kennung
Eigenschaft Wert
Name im XML-Schema kennung
Beschreibung Erweiterung des Typs String.Latin um ein Attribut klasse
zur Beschreibung von Zeichenketten. Im Gegensatz zum Typ
String.TextKlasseNoDefault wird für das Attribut klasse
der Standardwert default gesetzt.
Implementierungshinweis -
Typ xst:String.TextKlasse
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: text
Eigenschaft Wert
Name im XML-Schema text
Baukasten
60
Element: text
Eigenschaft Wert
Beschreibung Einschränkung auf alle lateinischen Zeichen innerhalb Unicode (vgl.
XÖV-Handbuch).
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: berechtigung
Eigenschaft Wert
Name im XML-Schema berechtigung
Beschreibung Das Element berechtigung kann für den Berechtigungsnachweis
des Absenders zur Teilnahme an einem Lieferverfahren verwendet
werden. Da ein Berechtigungsschlüssel erhebungsabhängig sein
kann, ist er auch im Typ Erhebung zulässig.
Ist ein Berechtigungsschlüssel für einen Berichtspflichtigen über
alle Erhebungen einheitlich, ist es ausreichend, den Schlüssel im
Typ Absender anzugeben.
Ist der Berechtigungsschlüssel zusätzlich erhebungsspezifisch,
muss er im Typ Erhebung angegeben werden, falls ein
Berichtspflichtiger für mehr als eine Erhebung meldet. Dies ist
nicht notwendig, wenn die Metadaten derart organisiert sind,
dass keine strukturelle Unterordnung der Erhebung unter den
Berichtspflichtigen existiert.
Implementierungshinweis -
Typ xst:String.TextKlasse
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Fehler
Diese Klasse beschreibt einen Fehler mit Schlüssel, Gewicht Text und Position und ggf. dem
Merkmal, auf das er sich bezieht. Die Verwendung dieser Elemente und ihre Inhalte sind
verfahrensspezifisch festzulegen.
Für den gesamten Fehler, den Schlüssel, das Gewicht und den Text bietet jeweils das Attribut
klasse die Möglichkeit, die Inhalte einer Klassifikation oder sonstigen formalen Definition
zuzuordnen.
Baukasten
61
Fe hle r
attribute s
klasse
s chlue s s e l
type = xst:String.SchluesselGewicht
0..1
g e w icht
type = xst:String.SchluesselGewicht
0..1
te xt
type = xst:String.TextKlasseNoDefault
0..1
pos ition
type = xst:String.Position
0..1
me rkmal
type = xst:StringLatin.NormalizedString
0..1
Abbildung 3.23. xst:Fehler
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Fehler
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Pruefdokument,
- xst:Pruefmeldung,
- xst:Pruefnachricht,
Elemente
Element: schluessel
Eigenschaft Wert
Name im XML-Schema schluessel
Beschreibung Erweiterung des Typs String.Latin zur Beschreibung des
Fehlerschlüssels und -gewichts. Die zulässigen Werte sind
verfahrensspezifisch.
Baukasten
62
Element: schluessel
Eigenschaft Wert
Implementierungshinweis -
Typ xst:String.SchluesselGewicht
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: gewicht
Eigenschaft Wert
Name im XML-Schema gewicht
Beschreibung Erweiterung des Typs String.Latin zur Beschreibung des
Fehlerschlüssels und -gewichts. Die zulässigen Werte sind
verfahrensspezifisch.
Implementierungshinweis -
Typ xst:String.SchluesselGewicht
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: text
Eigenschaft Wert
Name im XML-Schema text
Beschreibung Erweiterung des Typs String.Latin um ein Attribut klasse
zur Beschreibung von Zeichenketten. Im Gegensatz zum Typ
String.TextKlasse wird für das Attribut klasse kein
Standardwert vorgegeben.
Implementierungshinweis -
Typ xst:String.TextKlasseNoDefault
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: position
Eigenschaft Wert
Name im XML-Schema position
Beschreibung Die Position der fehlerverursachenden Stelle im
Meldungsdokument. Die Stelle kann auf verschiedene Weise
angegeben werden (siehe auch Token.FormatPosition).
Beispiele:
X-Path Ausdruck: <position>satz/mm[5]/wert</
position>
Baukasten
63
Element: position
Eigenschaft Wert
byte: <position format=’byte’>2691</position>
char: <position format=’char’>2691</position>
Name des Fehler verursachenden Feldes:<position
format=’name’>Alter in Jahren</position>
Satz und Offset:<position format=’satz’>8,25</
position< (Fehler in Satz 8, Position 25)
Implementierungshinweis -
Typ xst:String.Position
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: merkmal
Eigenschaft Wert
Name im XML-Schema merkmal
Beschreibung Bezieht sich der Fehler auf ein Merkmal, sollte der Name des
Merkmals in dieses Element geschrieben werden.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Attribute
Attribut: klasse
Eigenschaft Wert
Name im XML-Schema klasse
Beschreibung Einschränkung auf alle lateinischen Zeichen innerhalb Unicode (vgl.
XÖV-Handbuch).
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Optional ja
Default -
Formular
Generischer Typ zur Beschreibung von Formularen (z. B. Papier- und Onlineformulare).
Baukasten
64
Formular
formularID
type = xst:String.TextKlasseNoDefault
0..1
formularname
type = xst:String.TextKlasseNoDefault
0..1
Abbildung 3.24. xst:Formular
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Formular
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Dateneingang.Choice,
Elemente
Element: formularID
Eigenschaft Wert
Name im XML-Schema formularID
Beschreibung Dieses Attribut enthält eine Angabe für die Identifizierung eines
einzelnen oder einer zusammenhängenden Menge von Online- bzw.
Papierformularen, etwa für einen Berichtszeitraum einer Erhebung.
Es kann z.B. den Barcode eines Papierformulars enthalten.
Implementierungshinweis -
Typ xst:String.TextKlasseNoDefault
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: formularname
Eigenschaft Wert
Name im XML-Schema formularname
Beschreibung Dieses Element enthält den Namen eines Online- bzw.
Papierformulars. Für die Identifizierung eines einzelnen oder einer
Serie von Formularen sollte das Element formularID verwendet
werden.
Implementierungshinweis -
Typ xst:String.TextKlasseNoDefault
Baukasten
65
Element: formularname
Eigenschaft Wert
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Funktionselement
Funktions e le me nt
me ldung s ID
type = xst:String.TextKlasseNoDefault
Abbildung 3.25. xst:Funktionselement
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Funktionselement
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Meldungsart,
Elemente
Element: meldungsID
Eigenschaft Wert
Name im XML-Schema meldungsID
Beschreibung Erweiterung des Typs String.Latin um ein Attribut klasse
zur Beschreibung von Zeichenketten. Im Gegensatz zum Typ
String.TextKlasse wird für das Attribut klasse kein
Standardwert vorgegeben.
Implementierungshinweis -
Typ xst:String.TextKlasseNoDefault
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Hilfsmerkmal
Hilfsmerkmale sind Merkmale, die häufig zur Erhebung meldungsglobaler Zusatzinformationen
verwendet werden. Oft dienen sie auch zu organisatorischen und Verfahrenszwecken. Wie
Ordnungsmerkmale haben sie einen Namen und einen Wert, der nicht leer sein darf.
Hilfsmerkmale sind in den Elementen Nachricht und Segment erlaubt.
Baukasten
66
Hilfs me rkmal
attribute s
html-name
klasse
name
text
me mo
type = xoev-dt:String.Latin
0..1
w e rt
type = xst:String.Wert
Abbildung 3.26. xst:Hilfsmerkmal
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Hilfsmerkmal
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:StatistischerKontext,
Elemente
Element: memo
Eigenschaft Wert
Name im XML-Schema memo
Beschreibung Das Feld memo ermöglicht die Angabe eines zusätzlichen
Kommentars.
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: wert
Eigenschaft Wert
Name im XML-Schema wert
Baukasten
67
Element: wert
Eigenschaft Wert
Beschreibung Erweiterung des Typs String zur Beschreibung von Merkmalswerten.
Die Maßeinheit eines Wertes kann bei Bedarf mit dem
Attribut einheit angegeben werden. Das Attribut faktor bietet
die Möglichkeit, einen Wert als n-faches bzw. n-ten Bruchteil
der Maßeinheit anzugeben. Gibt es für die Maßeinheit eine
Klassifikation, z. B. eine ISO-Norm, kann diese mit dem Attribut
klasse angegeben werden.
Grundsätzlich ist die Angabe von Maßeinheiten und Faktoren nur
in Ausnahmefällen sinnvoll. Werte sollten bereits in der für die
Erhebung festgelegten Maßeinheit geliefert werden. Davon sollte
nur abgewichen werden, wenn dies ausdrücklich erlaubt ist, da
dann eine Umrechnung erfolgen muss; dies wird jedoch in den
allermeisten Fällen nicht vorgesehen sein.
Implementierungshinweis -
Typ xst:String.Wert
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Attribute
Attribut: html-name
Eigenschaft Wert
Name im XML-Schema html-name
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Attribut: klasse
Eigenschaft Wert
Name im XML-Schema klasse
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Attribut: name
Eigenschaft Wert
Name im XML-Schema name
Baukasten
68
Attribut: name
Eigenschaft Wert
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional nein
Default -
Attribut: text
Eigenschaft Wert
Name im XML-Schema text
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Identitaet
Ide ntitae t
org anis ation
type = xst:Organisation
0..1
pe rs on
type = xst:Person
0..1
Abbildung 3.27. xst:Identitaet
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Identitaet
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Kontakt.Sequence,
Elemente
Element: organisation
Eigenschaft Wert
Name im XML-Schema organisation
Baukasten
69
Element: organisation
Eigenschaft Wert
Beschreibung Der Typ Organisation beschreibt eine juristische, wirtschaftliche,
politische oder sonstige Organisationseinheit, etwa eine Firma, eine
Behörde oder eine internationale Institution (im Gegensatz zu einer
natürlichen Person).
Implementierungshinweis -
Typ xst:Organisation
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: person
Eigenschaft Wert
Name im XML-Schema person
Beschreibung Eine Person, die mindestens durch ihre(n) Nachnamen identifiziert
wird.
Implementierungshinweis -
Typ xst:Person
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Kontakt
Die Klasse Kontakt enthält Elemente zur Beschreibung von Kontaktdaten. Zur Beschreibung
der Kontaktdaten stehen ein strukturiertes (Kontakt.Sequence) und ein zeilenbasiertes
Inhaltsmodell (Element: zeile) zur Verfügung.
Anmerkung
Die Klasse Kontakt wird bei den verschiedenen Akteuren sowohl für das Element
identifikation als auch für kontakt verwendet. Das Element identifikation
ergänzt die Pflichtangabe kennung des Akteurs um zusätzliche Adressangaben.
Das Element kontakt hingegen ermöglicht die Angabe eines zusätzlichen
Ansprachpartners, z. B. bei fachlichen Rückfragen.
Baukasten
70
Kontakt
ze ile
type = xst:String.TextZeileHTML
1..*
ide ntitae t
type = xst:Identitaet
0..1
adre s s e
type = xst:Anschrift
0..1
te le fon
type = xst:String.TextZeileHTML
0..1
e mail
type = xst:String.TextZeileHTML
0..1
fax
type = xst:String.TextZeileHTML
0..1
url
type = xst:String.TextZeileHTML
0..1
Abbildung 3.28. xst:Kontakt
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Kontakt
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Choice
Verwendet in - xst:Absender,
- xst:Empfaenger,
- xst:Korrektur,
Baukasten
71
Elemente
Element: zeile
Eigenschaft Wert
Name im XML-Schema zeile
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 1 .. *
Default -
Nil-Wert möglich? nein
Form qualified
Lokale Strukturen
Name in der Spezifikation
Kontakt.Sequence
Kontakt.Sequence
Lokaler Hilfstyp zur abwärtskompatiblen Modellierung der übergeordneten Klasse.
Baukasten
72
Kontakt.Se que nce
ide ntitae t
type = xst:Identitaet
0..1
adre s s e
type = xst:Anschrift
0..1
te le fon
type = xst:String.TextZeileHTML
0..1
e mail
type = xst:String.TextZeileHTML
0..1
fax
type = xst:String.TextZeileHTML
0..1
url
type = xst:String.TextZeileHTML
0..1
Abbildung 3.29. xst:Kontakt.Sequence
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Kontakt.Sequence
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Kontakt,
Elemente
Element: identitaet
Eigenschaft Wert
Name im XML-Schema identitaet
Beschreibung
Implementierungshinweis -
Typ xst:Identitaet
Häufigkeit 0 .. 1
Baukasten
73
Element: identitaet
Eigenschaft Wert
Default -
Nil-Wert möglich? nein
Form qualified
Element: adresse
Eigenschaft Wert
Name im XML-Schema adresse
Beschreibung Der Typ Anschrift bezeichnet eine postalische Adresse, erweitert
um die Möglichkeit, Kreis und Bundesland anzugeben. Diese für
deutsche Adressen unüblichen Feldern wurden zugunsten der
Symmetrie zur geplanten englischen Version des Nachrichtentyps
hinzugefügt.
Implementierungshinweis -
Typ xst:Anschrift
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: telefon
Eigenschaft Wert
Name im XML-Schema telefon
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: email
Eigenschaft Wert
Name im XML-Schema email
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Baukasten
74
Element: fax
Eigenschaft Wert
Name im XML-Schema fax
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: url
Eigenschaft Wert
Name im XML-Schema url
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Korrektur
Identifikations. und Kontaktinformationen eines Absenders oder Berichtspflichtigen können
über dieses Element aktualisiert werden. Die Details eines Korrekturverfahrens sind
anwendungsabhängig.
Das Element Korrektur erlaubt die Übermittlung von Korrekturdaten für die Identifikation
und Kontaktdaten von Absender und Berichtspflichtigen.
Dieses Element steht in der Empfangsbestätigung nicht zur Verfügung!
Korre ktur
ide ntifikation
type = xst:Kontakt
0..1
kontakt
type = xst:Kontakt
0..1
Abbildung 3.30. xst:Korrektur
Baukasten
75
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Korrektur
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Absender,
Elemente
Element: identifikation
Eigenschaft Wert
Name im XML-Schema identifikation
Beschreibung Die Klasse Kontakt enthält Elemente zur Beschreibung von
Kontaktdaten. Zur Beschreibung der Kontaktdaten stehen ein
strukturiertes (Kontakt.Sequence) und ein zeilenbasiertes
Inhaltsmodell (Element: zeile) zur Verfügung.
Anmerkung
Die Klasse Kontakt wird bei den verschiedenen Akteuren
sowohl für das Element identifikation als auch für
kontakt verwendet. Das Element identifikation
ergänzt die Pflichtangabe kennung des Akteurs um
zusätzliche Adressangaben. Das Element kontakt
hingegen ermöglicht die Angabe eines zusätzlichen
Ansprachpartners, z. B. bei fachlichen Rückfragen.
Implementierungshinweis -
Typ xst:Kontakt
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: kontakt
Eigenschaft Wert
Name im XML-Schema kontakt
Beschreibung Die Klasse Kontakt enthält Elemente zur Beschreibung von
Kontaktdaten. Zur Beschreibung der Kontaktdaten stehen ein
strukturiertes (Kontakt.Sequence) und ein zeilenbasiertes
Inhaltsmodell (Element: zeile) zur Verfügung.
Anmerkung
Die Klasse Kontakt wird bei den verschiedenen Akteuren
sowohl für das Element identifikation als auch für
kontakt verwendet. Das Element identifikation
ergänzt die Pflichtangabe kennung des Akteurs um
zusätzliche Adressangaben. Das Element kontakt
Baukasten
76
Element: kontakt
Eigenschaft Wert
hingegen ermöglicht die Angabe eines zusätzlichen
Ansprachpartners, z. B. bei fachlichen Rückfragen.
Implementierungshinweis -
Typ xst:Kontakt
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Material
Bezeichnung und Version des Liefermaterials.
Mate rial
name
type = xst:String.TextZeileHTML
0..1
ke nnung
type = xst:String.TextKlasse
0..1
ve rs ion
type = xoev-dt:String.Latin
0..1
Abbildung 3.31. xst:Material
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Material
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:StatistischerKontext,
Elemente
Element: name
Eigenschaft Wert
Name im XML-Schema name
Baukasten
77
Element: name
Eigenschaft Wert
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: kennung
Eigenschaft Wert
Name im XML-Schema kennung
Beschreibung Erweiterung des Typs String.Latin um ein Attribut klasse
zur Beschreibung von Zeichenketten. Im Gegensatz zum Typ
String.TextKlasseNoDefault wird für das Attribut klasse
der Standardwert default gesetzt.
Implementierungshinweis -
Typ xst:String.TextKlasse
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: version
Eigenschaft Wert
Name im XML-Schema version
Beschreibung Einschränkung auf alle lateinischen Zeichen innerhalb Unicode (vgl.
XÖV-Handbuch).
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Meldungsart
Mit der Meldungsart wird angegeben, für welchen Zweck die Meldung erfolgt. Mit Ausnahme
der Originallieferungen von Daten sind dies z.B. Korrekturen und Löschungen. Der Zweck
einer Meldung wird durch das Element meldungsart ausgedrückt, das ein entsprechendes
Funktionselement enthält. Ist ein Bezug zu einer vorausgegangenen Meldung notwendig oder
möglich, erfolgt dieser in Form der meldungsID, die dem Funktionselement nachgeordnet ist. Das
Funktionselement nil unterdrückt die Verarbeitung einer Meldung.
Baukasten
78
Me ldung s art
orig inal
type = xst:Leertyp
be richtig ung
type = xst:Funktionselement
nachme ldung
type = xst:Funktionselement
aus taus ch
type = xst:Funktionselement
loe s chung
type = xst:Funktionselement
nil
type = xst:Leertyp
Abbildung 3.32. xst:Meldungsart
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Meldungsart
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Choice
Verwendet in - xst:Datensegment,
- xst:Pruefmeldung,
Elemente
Element: original
Eigenschaft Wert
Name im XML-Schema original
Beschreibung Leerer Datentyp für die Beschreibung leerer Elemente.
Implementierungshinweis -
Typ xst:Leertyp
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Baukasten
79
Element: berichtigung
Eigenschaft Wert
Name im XML-Schema berichtigung
Beschreibung -
Implementierungshinweis -
Typ xst:Funktionselement
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: nachmeldung
Eigenschaft Wert
Name im XML-Schema nachmeldung
Beschreibung -
Implementierungshinweis -
Typ xst:Funktionselement
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: austausch
Eigenschaft Wert
Name im XML-Schema austausch
Beschreibung -
Implementierungshinweis -
Typ xst:Funktionselement
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: loeschung
Eigenschaft Wert
Name im XML-Schema loeschung
Beschreibung -
Implementierungshinweis -
Typ xst:Funktionselement
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Baukasten
80
Element: nil
Eigenschaft Wert
Name im XML-Schema nil
Beschreibung Leerer Datentyp für die Beschreibung leerer Elemente.
Implementierungshinweis -
Typ xst:Leertyp
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Merkmal
Der Typ Merkmal beschreibt ein statistisches Merkmal, das mit einem Wert oder einer expliziten
Nichtantwort verbunden ist. Das Attribut name identifiziert das Merkmal und muss immer
angegeben werden. Das Attribut text erlaubt eine textuelle Merkmalsbeschreibung.
Me rkmal
attribute s
html-name
klasse
name
text
me mo
type = xoev-dt:String.Latin
0..1
w e rt
type = xst:String.Wert
na
type = xst:StringLatin.NormalizedString
Abbildung 3.33. xst:Merkmal
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Merkmal
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Baukasten
81
Eigenschaft Wert
Elementmodell Sequenz
Verwendet in - xst:Merkmalsgruppe.Choice,
- xst:Satz.Choice,
Elemente
Element: memo
Eigenschaft Wert
Name im XML-Schema memo
Beschreibung Das Feld memo ermöglicht die Angabe eines zusätzlichen
Kommentars.
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Attribute
Attribut: html-name
Eigenschaft Wert
Name im XML-Schema html-name
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Attribut: klasse
Eigenschaft Wert
Name im XML-Schema klasse
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Attribut: name
Eigenschaft Wert
Name im XML-Schema name
Baukasten
82
Attribut: name
Eigenschaft Wert
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional nein
Default -
Attribut: text
Eigenschaft Wert
Name im XML-Schema text
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Lokale Strukturen
Name in der Spezifikation
Merkmal.Choice
Merkmal.Choice
Lokaler Hilfstyp zur abwärtskompatiblen Modellierung der übergeordneten Klasse.
Me rkmal.Choice
w e rt
type = xst:String.Wert
na
type = xst:StringLatin.NormalizedString
Abbildung 3.34. xst:Merkmal.Choice
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Merkmal.Choice
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Baukasten
83
Eigenschaft Wert
Elementmodell Choice
Verwendet in - xst:Merkmal,
Elemente
Element: wert
Eigenschaft Wert
Name im XML-Schema wert
Beschreibung Der Wert, der einem statistischen Merkmal zugeordnet wurde.
Implementierungshinweis -
Typ xst:String.Wert
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: na
Eigenschaft Wert
Name im XML-Schema na
Beschreibung Das Element nasteht für eine explizite Nichtantwort. Der
Elementinhalt darf beliebigen Text enthalten.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Merkmalsgruppe
Ein einfaches Merkmal darf in einem Satz grundsätzlich genau einmal vorkommen. Es ist
jedoch möglich, dass für ein Erhebungsobjekt mehrere Ausprägungen eines Merkmals existieren,
die alle dem gleichen Erhebungskontext und -objekt zugeordnet sind. Oft handelt es sich dabei
um mehrere Merkmale, die eine zusammenhängende, wiederholbare Struktur (in der amtlichen
Statistik "wiederholte Feldgruppe" genannt) bilden.
Merkmale müssen innerhalb einer Merkmalsgruppe eindeutig sein. Es können aber in einem
Datensatz beliebig viele Instanzen einer Merkmalsgruppe enthalten sein. Merkmalsgruppen
können wiederum weitere Merkmalsgruppen enthalten.
Einfache Merkmale und Merkmalsgruppen selbst können zu einer wiederhol- und indizierbaren
Merkmalsgruppe zusammengefasst werden. Das Attribut name identifiziert die Merkmalsgruppe
und muss immer angegeben werden. Das Attribut text erlaubt eine zusätzliche textuelle
Beschreibung.
Baukasten
84
Me rkmals g ruppe
attribute s
html-name
index
klasse
name
text
1..*
mm
type = xst:Merkmal
mmg r
type = xst:Merkmalsgruppe
Abbildung 3.35. xst:Merkmalsgruppe
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Merkmalsgruppe
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Merkmalsgruppe.Choice,
- xst:Satz.Choice,
Attribute
Attribut: html-name
Eigenschaft Wert
Name im XML-Schema html-name
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Attribut: index
Eigenschaft Wert
Name im XML-Schema index
Baukasten
85
Attribut: index
Eigenschaft Wert
Beschreibung Dieses Element definiert den Modus der Indexgewinnung.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Attribut: klasse
Eigenschaft Wert
Name im XML-Schema klasse
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Attribut: name
Eigenschaft Wert
Name im XML-Schema name
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional nein
Default -
Attribut: text
Eigenschaft Wert
Name im XML-Schema text
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Lokale Strukturen
Name in der Spezifikation
Merkmalsgruppe.Choice
Merkmalsgruppe.Choice
Lokaler Hilfstyp zur abwärtskompatiblen Modellierung der übergeordneten Klasse.
Baukasten
86
Me rkmals g ruppe .Choice
mm
type = xst:Merkmal
mmg r
type = xst:Merkmalsgruppe
Abbildung 3.36. xst:Merkmalsgruppe.Choice
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Merkmalsgruppe.Choice
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Choice
Verwendet in - xst:Merkmalsgruppe,
Elemente
Element: mm
Eigenschaft Wert
Name im XML-Schema mm
Beschreibung Der Typ Merkmal beschreibt ein statistisches Merkmal, das mit
einem Wert oder einer expliziten Nichtantwort verbunden ist.
Das Attribut name identifiziert das Merkmal und muss immer
angegeben werden. Das Attribut text erlaubt eine textuelle
Merkmalsbeschreibung.
Implementierungshinweis -
Typ xst:Merkmal
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: mmgr
Eigenschaft Wert
Name im XML-Schema mmgr
Beschreibung Ein einfaches Merkmal darf in einem Satz grundsätzlich
genau einmal vorkommen. Es ist jedoch möglich, dass für
ein Erhebungsobjekt mehrere Ausprägungen eines Merkmals
existieren, die alle dem gleichen Erhebungskontext und -objekt
zugeordnet sind. Oft handelt es sich dabei um mehrere Merkmale,
die eine zusammenhängende, wiederholbare Struktur (in der
amtlichen Statistik "wiederholte Feldgruppe" genannt) bilden.
Baukasten
87
Element: mmgr
Eigenschaft Wert
Merkmale müssen innerhalb einer Merkmalsgruppe eindeutig sein.
Es können aber in einem Datensatz beliebig viele Instanzen
einer Merkmalsgruppe enthalten sein. Merkmalsgruppen können
wiederum weitere Merkmalsgruppen enthalten.
Einfache Merkmale und Merkmalsgruppen selbst können zu einer
wiederhol- und indizierbaren Merkmalsgruppe zusammengefasst
werden. Das Attribut name identifiziert die Merkmalsgruppe und
muss immer angegeben werden. Das Attribut text erlaubt eine
zusätzliche textuelle Beschreibung.
Implementierungshinweis -
Typ xst:Merkmalsgruppe
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Nachricht
Nachrichten enthalten statistische Rohdaten sowie Metadaten, die den statistischen
Kontext einer Rohdatenmeldung (StatistischerKontext) beschreiben. Die optionale
Segmentierung einer Nachricht erlaubt es, beliebig viele Rohdatenmeldungen mit
unterschiedlichem statistischen Kontext in einer Nachricht zu übermitteln und die Metadaten
redundanzfrei abzuspeichern. Mit dem Element nachrichtenID kann einer Nachricht ein
Identifikator zugeordnet werden.
Baukasten
88
Nachricht
me mo
type = xoev-dt:String.Latin
0..1
nachrichte nID
type = xst:String.TextKlasseNoDefault
0..1
e rhe bung
type = xst:Erhebung
0..1
be richts ze itraum
type = xst:Berichtszeitraum
0..1
be richts pflichtig e r
type = xst:Absender
0..1
be richts e mpfae ng e r
type = xst:Empfaenger
0..1
mate rial
type = xst:Material
0..1
date nattribute
type = xst:Datenattribute
0..1
hmm
type = xst:Hilfsmerkmal
0..*
date ns e g me nt
type = xst:Datensegment
s e g me nt
type = xst:Segment
1..*
Abbildung 3.37. xst:Nachricht
Baukasten
89
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Nachricht
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:DatML-RAW-D (globales Element),
Elemente
Element: memo
Eigenschaft Wert
Name im XML-Schema memo
Beschreibung Das Feld memo ermöglicht die Angabe eines zusätzlichen
Kommentars.
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: nachrichtenID
Eigenschaft Wert
Name im XML-Schema nachrichtenID
Beschreibung Mit dem Element nachrichtenID kann einer Nachricht ein
Identifikator zugeordnet werden.
Implementierungshinweis -
Typ xst:String.TextKlasseNoDefault
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Lokale Strukturen
Name in der Spezifikation
StatistischerKontext
Nachrichtenkopf
Im Nachrichtenkopf werden die gemeinsamen Elemente der Rohdatenmeldung und
der Empfangsbestätigung beschrieben. Einige Unterelemente sind lediglich für die
Rohdatenmeldung, nicht jedoch in der Empfangsbestätigung definiert. In der Spezifikation der
betroffenen Elemente ist dies jeweils angegeben.
Baukasten
90
Nachrichte nkopf
me mo
type = xoev-dt:String.Latin
0..1
optione n
type = xst:Optionen
0..1
protokoll
type = xst:Protokoll
0..1
abs e nde r
type = xst:Absender
e mpfae ng e r
type = xst:Empfaenger
Abbildung 3.38. xst:Nachrichtenkopf
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Nachrichtenkopf
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:DatML-RAW-D (globales Element),
- xst:DatML-RES-D (globales Element),
Elemente
Element: memo
Eigenschaft Wert
Name im XML-Schema memo
Beschreibung Das Feld memo ermöglicht die Angabe eines zusätzlichen
Kommentars.
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Baukasten
91
Element: optionen
Eigenschaft Wert
Name im XML-Schema optionen
Beschreibung Verarbeitungsoptionen geben dem Absender einer Nachricht
die Möglichkeit, die Verarbeitung in bestimmter Weise zu
beeinflussen. Diese Funktionen werden in der jeweiligen
Anwendung implementiert und sind nicht Gegenstand dieses
Nachrichtenformates.
Jede Option ist ein nachgeordnetes Element des Typs Optionen.
Implementierungshinweis -
Typ xst:Optionen
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: protokoll
Eigenschaft Wert
Name im XML-Schema protokoll
Beschreibung In diesem Element werden Informationen abgelegt, die im Rahmen
der Verarbeitung einer DatML-RAW-D-Nachricht innerhalb des
statistischen Verbunds entstehen und sind lediglich zur Wahrung
der Abwärtskompatibilität mit der Vorgängerversion DatML/
RAW 2.0 weiterhin in XStatistik enthalten. Die Informationen
in diesem Element sind für den Nachrichtenaustausch zwischen
Berichtspflichtigen und der amtlichen Statistik daher nicht relevant.
Die Protokollinformationen dienen dazu, Lieferwege und
Verarbeitungsstufen einer Nachricht zu dokumentieren. Der Eingang
der Rohdaten (Dateneingang) und die Dokumentinstanzen
werden separat protokolliert.
Implementierungshinweis -
Typ xst:Protokoll
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: absender
Eigenschaft Wert
Name im XML-Schema absender
Beschreibung Der Absender versendet das Dokument. Handelt es sich um eine
Rohdatenmeldung, kann er selbst Berichtspflichtiger sein und/
oder für Dritte berichten. Eine Empfangsbestätigung wird i.d.R. von
einem Statistischen Landesamt oder dem Statistischen Bundesamt
versendet.
Für eine Rohdatenmeldung steht zur Änderung der Adress- und
Kontaktinformationen das Element Korrektur zur Verfügung.
Baukasten
92
Element: absender
Eigenschaft Wert
Es ist anwendungsspezifisch festzulgegen, welche Daten zu
Verifikation der Identität des Absenders herangezogen werden.
Implementierungshinweis -
Typ xst:Absender
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: empfaenger
Eigenschaft Wert
Name im XML-Schema empfaenger
Beschreibung Der Empfänger einer Rohdatenmeldung ist i.d.R. ein
Statistisches Landesamt oder das Statistische Bundesamt. Der
Berichtsempfänger muss in der Lage sein, sich selbst als
Adressaten zu bestätigen und benötigt deshalb eine Angabe zu
seiner Identifikation. Standardmäßig ist der Berichtsempfänger mit
dem Empfänger des Dokumentes identisch. Eine externe (i.d.R.
vom Absender verwendete) Angabe für die Identifikation eines
Verfahrensbeteiligten.
Implementierungshinweis -
Typ xst:Empfaenger
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Optionen
Verarbeitungsoptionen geben dem Absender einer Nachricht die Möglichkeit, die Verarbeitung
in bestimmter Weise zu beeinflussen. Diese Funktionen werden in der jeweiligen Anwendung
implementiert und sind nicht Gegenstand dieses Nachrichtenformates.
Jede Option ist ein nachgeordnetes Element des Typs Optionen.
Optione n
te s t
type = xst:Test
0..1
e mpfang s be s tae tig ung
type = xst:AnforderungEmpfangsbestaetigung
0..1
Abbildung 3.39. xst:Optionen
Baukasten
93
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Optionen
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Nachrichtenkopf,
Elemente
Element: test
Eigenschaft Wert
Name im XML-Schema test
Beschreibung Das Element Test zeigt an, dass die Nachricht nur zu Testzwecken
versendet wurde. Das Attribut kennung erlaubt eine beliebige
Angabe, z.B. für die Steuerung und Kontrolle von Testserien.
Implementierungshinweis -
Typ xst:Test
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: empfangsbestaetigung
Eigenschaft Wert
Name im XML-Schema empfangsbestaetigung
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht nicht
definiert.
Implementierungshinweis -
Typ xst:AnforderungEmpfangsbestaetigung
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Ordnungsmerkmal
Ordnungsmerkmale haben wie einfache Merkmale einen Namen und einen Wert, der jedoch
nicht fehlen und nicht leer sein darf. Im Gegensatz zu einfachen Merkmalen handels
es sich dabei um Merkmale, die eine systematische, bzw. ordnende, Aussage haben. In
Verzeichnissen geführte Merkmale wie Länderschlüssel und Betriebsnummern sind typische
Ordnungsmerkmale.
Mit Ordnungsmerkmalen können Gruppen von Datensätzen gebildet werden, die alle den selben
Wert für ein bestimmtes Ordnungsmerkmal aufweisen. Dieses Ordnungsmerkmal ist in der
Dokumentstruktur nicht Bestandteil der Datensätze, sondern den Datensätzen übergeordnet.
Eine Folge von Datensätzen wird jeweils genau einem Wert eines Ordnungsmerkmals
zugeorgndet. Eine sortierte Ablage der Datensätze wird dadurch nicht erzwungen.
Baukasten
94
Ordnungsmerkmale sind dennoch, wie einfache Merkmale, Teil der statistischen Information. Aus
fachlicher Sicht spielt es keine Rolle, ob ein Merkmal als Ordnungs- oder als einfaches Merkmal
übermittelt wird. Hauptzweck von Ordnungsmerkmalen ist die Redundanzverringerung, vor allem
bei der Lieferung mittlerer und großer Datenmengen.
Innerhalb eines Datensegmentes müssen Ordnungsmerkmale stets gleich tief geschachtelt sein.
Ordnungsmerkmale der gleichen Hierarchiestufe müssen immer den gleichen Namen haben,
also das selbe Ordnungskriterium beschreiben. Die Anwendung muss die Einhaltung dieser
Einschränkung prüfen, da sie nicht über ein XML Schema definierbar ist.
Anmerkung
Enthält ein Datensegment Ordnungsmerkmale, so muss über alle Datensätze hiweg ihre
Reihenfolge in der hierarchischen Anordnung unverändert bleiben.
Ordnung s me rkmal
attribute s
html-name
klasse
name
text
me mo
type = xoev-dt:String.Latin
0..1
1..*
w e rt
type = xst:String.Wert
omm
type = xst:Ordnungsmerkmal
s atz
type = xst:Satz
1..*
Abbildung 3.40. xst:Ordnungsmerkmal
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Ordnungsmerkmal
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Baukasten
95
Eigenschaft Wert
Verwendet in - xst:Datensegment.Choice,
- xst:Ordnungsmerkmal.Sequence.Choice,
Elemente
Element: memo
Eigenschaft Wert
Name im XML-Schema memo
Beschreibung Das Feld memo ermöglicht die Angabe eines zusätzlichen
Kommentars.
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Attribute
Attribut: html-name
Eigenschaft Wert
Name im XML-Schema html-name
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Attribut: klasse
Eigenschaft Wert
Name im XML-Schema klasse
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Attribut: name
Eigenschaft Wert
Name im XML-Schema name
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Baukasten
96
Attribut: name
Eigenschaft Wert
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional nein
Default -
Attribut: text
Eigenschaft Wert
Name im XML-Schema text
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Lokale Strukturen
Name in der Spezifikation
Ordnungsmerkmal.Sequence
Ordnungsmerkmal.Sequence
Lokaler Hilfstyp zur abwärtskompatiblen Modellierung der übergeordneten Klasse.
Ordnung s me rkmal.Se que nce
w e rt
type = xst:String.Wert
omm
type = xst:Ordnungsmerkmal
s atz
type = xst:Satz
1..*
Abbildung 3.41. xst:Ordnungsmerkmal.Sequence
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Ordnungsmerkmal.Sequence
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Baukasten
97
Eigenschaft Wert
Elementmodell Sequenz
Verwendet in - xst:Ordnungsmerkmal,
Elemente
Element: wert
Eigenschaft Wert
Name im XML-Schema wert
Beschreibung Erweiterung des Typs String zur Beschreibung von Merkmalswerten.
Die Maßeinheit eines Wertes kann bei Bedarf mit dem
Attribut einheit angegeben werden. Das Attribut faktor bietet
die Möglichkeit, einen Wert als n-faches bzw. n-ten Bruchteil
der Maßeinheit anzugeben. Gibt es für die Maßeinheit eine
Klassifikation, z. B. eine ISO-Norm, kann diese mit dem Attribut
klasse angegeben werden.
Grundsätzlich ist die Angabe von Maßeinheiten und Faktoren nur
in Ausnahmefällen sinnvoll. Werte sollten bereits in der für die
Erhebung festgelegten Maßeinheit geliefert werden. Davon sollte
nur abgewichen werden, wenn dies ausdrücklich erlaubt ist, da
dann eine Umrechnung erfolgen muss; dies wird jedoch in den
allermeisten Fällen nicht vorgesehen sein.
Implementierungshinweis -
Typ xst:String.Wert
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Lokale Strukturen
Name in der Spezifikation
Ordnungsmerkmal.Sequence.Choice
Ordnungsmerkmal.Sequence.Choice
Lokaler Hilfstyp zur abwärtskompatiblen Modellierung der übergeordneten Klasse.
Ordnung s me rkmal.Se que nce .Choice
omm
type = xst:Ordnungsmerkmal
s atz
type = xst:Satz
1..*
Abbildung 3.42. xst:Ordnungsmerkmal.Sequence.Choice
Baukasten
98
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Ordnungsmerkmal.Sequence.Choice
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Choice
Verwendet in - xst:Ordnungsmerkmal.Sequence,
Elemente
Element: omm
Eigenschaft Wert
Name im XML-Schema omm
Beschreibung Ordnungsmerkmale haben wie einfache Merkmale einen Namen
und einen Wert, der jedoch nicht fehlen und nicht leer sein darf.
Im Gegensatz zu einfachen Merkmalen handels es sich dabei
um Merkmale, die eine systematische, bzw. ordnende, Aussage
haben. In Verzeichnissen geführte Merkmale wie Länderschlüssel
und Betriebsnummern sind typische Ordnungsmerkmale.
Mit Ordnungsmerkmalen können Gruppen von Datensätzen
gebildet werden, die alle den selben Wert für ein bestimmtes
Ordnungsmerkmal aufweisen. Dieses Ordnungsmerkmal ist in der
Dokumentstruktur nicht Bestandteil der Datensätze, sondern den
Datensätzen übergeordnet. Eine Folge von Datensätzen wird jeweils
genau einem Wert eines Ordnungsmerkmals zugeorgndet. Eine
sortierte Ablage der Datensätze wird dadurch nicht erzwungen.
Ordnungsmerkmale sind dennoch, wie einfache Merkmale, Teil
der statistischen Information. Aus fachlicher Sicht spielt es keine
Rolle, ob ein Merkmal als Ordnungs- oder als einfaches Merkmal
übermittelt wird. Hauptzweck von Ordnungsmerkmalen ist die
Redundanzverringerung, vor allem bei der Lieferung mittlerer und
großer Datenmengen.
Innerhalb eines Datensegmentes müssen Ordnungsmerkmale stets
gleich tief geschachtelt sein. Ordnungsmerkmale der gleichen
Hierarchiestufe müssen immer den gleichen Namen haben, also das
selbe Ordnungskriterium beschreiben. Die Anwendung muss die
Einhaltung dieser Einschränkung prüfen, da sie nicht über ein XML
Schema definierbar ist.
Anmerkung
Enthält ein Datensegment Ordnungsmerkmale, so muss
über alle Datensätze hiweg ihre Reihenfolge in der
hierarchischen Anordnung unverändert bleiben.
Implementierungshinweis -
Typ xst:Ordnungsmerkmal
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Baukasten
99
Element: omm
Eigenschaft Wert
Form qualified
Element: satz
Eigenschaft Wert
Name im XML-Schema satz
Beschreibung Ein statistischer Datensatz stellt eine Informationseinheit dar, die
zusammenhängende Daten über ein Erhebungsobjekt enthält. Ein
Satz besteht aus mindestens einem (Wert-)Merkmal und einer
optionalen Anzahlangabe für Kontrollzwecke.
Implementierungshinweis -
Typ xst:Satz
Häufigkeit 1 .. *
Default -
Nil-Wert möglich? nein
Form qualified
Organisation
Der Typ Organisation beschreibt eine juristische, wirtschaftliche, politische oder sonstige
Organisationseinheit, etwa eine Firma, eine Behörde oder eine internationale Institution (im
Gegensatz zu einer natürlichen Person).
Org anis ation
name
type = xst:String.TextZeileHTML
nie de rlas s ung
type = xst:String.TextZeileHTML
0..1
zus atz
type = xst:String.TextZeileHTML
0..1
Abbildung 3.43. xst:Organisation
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Organisation
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Baukasten
100
Eigenschaft Wert
Elementmodell Sequenz
Verwendet in - xst:Identitaet,
Elemente
Element: name
Eigenschaft Wert
Name im XML-Schema name
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: niederlassung
Eigenschaft Wert
Name im XML-Schema niederlassung
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: zusatz
Eigenschaft Wert
Name im XML-Schema zusatz
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Person
Eine Person, die mindestens durch ihre(n) Nachnamen identifiziert wird.
Baukasten
101
Pe rs on
anre de
type = xst:String.TextZeileHTML
0..1
tite l
type = xst:String.TextZeileHTML
0..1
vorname
type = xst:String.TextZeileHTML
0..1
nachname
type = xst:String.TextZeileHTML
zus atz
type = xst:String.TextZeileHTML
0..1
Abbildung 3.44. xst:Person
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Person
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Identitaet,
Elemente
Element: anrede
Eigenschaft Wert
Name im XML-Schema anrede
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Baukasten
102
Element: anrede
Eigenschaft Wert
Form qualified
Element: titel
Eigenschaft Wert
Name im XML-Schema titel
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: vorname
Eigenschaft Wert
Name im XML-Schema vorname
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: nachname
Eigenschaft Wert
Name im XML-Schema nachname
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: zusatz
Eigenschaft Wert
Name im XML-Schema zusatz
Baukasten
103
Element: zusatz
Eigenschaft Wert
Beschreibung Dieses Element ist in einer DatML-RES-D-Nachricht ohne die
Attribute zeilennummer und html-name definiert.
Implementierungshinweis -
Typ xst:String.TextZeileHTML
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Protokoll
In diesem Element werden Informationen abgelegt, die im Rahmen der Verarbeitung einer
DatML-RAW-D-Nachricht innerhalb des statistischen Verbunds entstehen und sind lediglich zur
Wahrung der Abwärtskompatibilität mit der Vorgängerversion DatML/RAW 2.0 weiterhin in
XStatistik enthalten. Die Informationen in diesem Element sind für den Nachrichtenaustausch
zwischen Berichtspflichtigen und der amtlichen Statistik daher nicht relevant.
Die Protokollinformationen dienen dazu, Lieferwege und Verarbeitungsstufen einer Nachricht zu
dokumentieren. Der Eingang der Rohdaten (Dateneingang) und die Dokumentinstanzen
werden separat protokolliert.
Protokoll
date ne ing ang
type = xst:Dateneingang
0..1
dokume ntins tanz
type = xst:Dokumentinstanz
0..*
Abbildung 3.45. xst:Protokoll
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Protokoll
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Nachrichtenkopf,
Elemente
Element: dateneingang
Eigenschaft Wert
Name im XML-Schema dateneingang
Baukasten
104
Element: dateneingang
Eigenschaft Wert
Beschreibung Für den Dateneingang können Details wie Lieferweg, -datenträger
und -format angegeben werden. Auf diese Weise kann zwischen
Onlinemeldungen per HTML-Formular, Papiermeldungen, dem
Upload von Dateien und Datenträgerlieferungen unterschieden
werden.
Dieses Element ist in einer DatML-RES-D-Nachricht nicht
definiert.
Implementierungshinweis -
Typ xst:Dateneingang
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: dokumentinstanz
Eigenschaft Wert
Name im XML-Schema dokumentinstanz
Beschreibung Im Protokoll können mehrere Dokumentinstanzen gespeichert
werden, die jeweiils einen Zwischenstand der Verarbeitung der
Originalnachricht repräsentieren. Es können eine Dokument-ID,
die erzeugte Datei sowie die erzeugende Anwendung angegeben
werden.
Implementierungshinweis -
Typ xst:Dokumentinstanz
Häufigkeit 0 .. *
Default -
Nil-Wert möglich? nein
Form qualified
Pruefdokument
Diese Klasse enthält die Prüfergebnisse für die gesamte Rohdatenmeldung und den
auf der Dokumentenebene aufgetretenen Fehlern. Auf dieser Prüfebene werden alle
anderen (in der Klasse Prüfung definierten) Prüfebenen zusammen gefasst. Mit dem
Attribut dokumentstatus wird zusätzlich angegeben, ob das Dokument als Ganzes
ungeprüft ist, akzeptiert oder abgewiesen wurde. Wie Prüfstatus und dokumentstatus
zusammenhängen ist verfahrensspezifisch.
Baukasten
105
Prue fdokume nt
attribute s
dokumentstatus
pruefstatus
date ne ing ang
type = xst:Dateneingang
0..1
fe hle r
type = xst:Fehler
0..*
nachricht
type = xst:Pruefnachricht
0..*
Abbildung 3.46. xst:Pruefdokument
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Pruefdokument
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Pruefprotokoll,
Elemente
Element: dateneingang
Eigenschaft Wert
Name im XML-Schema dateneingang
Beschreibung Dieses Element beschreibt die Details des Dateneingangs. Es
können Datum und Uhrzeit des Dateneingangs, ein vergebener
Eingangstempel und die den Dateneingang verarbeitende
Anwendung dokumentiert werden. Weiterhin kann die Form des
Dateneingangs angegeben werden, z. B. "Papierformular" für den
Fall, dass ein Belegleser die DatML-RAW-D-Nachricht erzeugt hat.
Implementierungshinweis -
Typ xst:Dateneingang
Häufigkeit 0 .. 1
Default -
Baukasten
106
Element: dateneingang
Eigenschaft Wert
Nil-Wert möglich? nein
Form qualified
Element: fehler
Eigenschaft Wert
Name im XML-Schema fehler
Beschreibung Diese Klasse beschreibt einen Fehler mit Schlüssel, Gewicht
Text und Position und ggf. dem Merkmal, auf das er sich
bezieht. Die Verwendung dieser Elemente und ihre Inhalte sind
verfahrensspezifisch festzulegen.
Für den gesamten Fehler, den Schlüssel, das Gewicht und den Text
bietet jeweils das Attribut klasse die Möglichkeit, die Inhalte einer
Klassifikation oder sonstigen formalen Definition zuzuordnen.
Implementierungshinweis -
Typ xst:Fehler
Häufigkeit 0 .. *
Default -
Nil-Wert möglich? nein
Form qualified
Element: nachricht
Eigenschaft Wert
Name im XML-Schema nachricht
Beschreibung In dieser Klasse werden die Ergebnisse der Prüfung der einzelnen
Nachrichten der Rohdatenmeldung gespeichert.
Implementierungshinweis -
Typ xst:Pruefnachricht
Häufigkeit 0 .. *
Default -
Nil-Wert möglich? nein
Form qualified
Attribute
Attribut: dokumentstatus
Eigenschaft Wert
Name im XML-Schema dokumentstatus
Beschreibung Einschränkung des Typs Token zur Beschreibung des
Dokumentenstatus.
Implementierungshinweis -
Typ xst:Token.Dokumentstatus
Optional nein
Baukasten
107
Attribut: dokumentstatus
Eigenschaft Wert
Default -
Attribut: pruefstatus
Eigenschaft Wert
Name im XML-Schema pruefstatus
Beschreibung Einschränkung des Basistyps Token zur Beschreibung der
verschiedenen Prüfzustände. Dieser Typ findet auf verschiedenen
Ebenen des Prüfprotokolls Anwendung.
Implementierungshinweis -
Typ xst:Token.Pruefstatus
Optional nein
Default -
Pruefmeldung
In dieser Klasse werden die Informationen der Prüfungen der einzelnen Meldungen einer
Rohdatenmeldung (entspricht den Datensegmenten mit den zugehörigen Metadaten)
protokolliert.
Werden die Meldungen in der Rohdatenmeldung mit einer Kennung eindeutig identifizierbar
gemacht, ist diese Kennung hier zu übernehmen und im Element meldungsID abzulegen. Die
Meldungsart gibt den Verwendungszweck der Meldung an, z.B. Korrektur oder Löschung.
Erhebung und Berichtszeitraum sind vollständig anzugeben, Berichtspflichtiger und -empfänger
soweit sie nicht mit dem Empfänger bzw. dem Absender des Prüfprotokolls identisch sind. Alle
gleichnamigen Elemente können aus einer Rohdatenmeldung (DatML-RAW-D) kopiert werden.
Baukasten
108
Prue fme ldung
attribute s
pruefstatus
me ldung s ID
type = xst:String.TextKlasseNoDefault
0..1
me ldung s art
type = xst:Meldungsart
0..1
e rhe bung
type = xst:Erhebung
be richts ze itraum
type = xst:Berichtszeitraum
be richts pflichtig e r
type = xst:Absender
0..1
be richts e mpfae ng e r
type = xst:Empfaenger
0..1
fe hle r
type = xst:Fehler
0..*
Abbildung 3.47. xst:Pruefmeldung
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Pruefmeldung
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Pruefnachricht,
Baukasten
109
Elemente
Element: meldungsID
Eigenschaft Wert
Name im XML-Schema meldungsID
Beschreibung Erweiterung des Typs String.Latin um ein Attribut klasse
zur Beschreibung von Zeichenketten. Im Gegensatz zum Typ
String.TextKlasse wird für das Attribut klasse kein
Standardwert vorgegeben.
Implementierungshinweis -
Typ xst:String.TextKlasseNoDefault
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: meldungsart
Eigenschaft Wert
Name im XML-Schema meldungsart
Beschreibung Mit der Meldungsart wird angegeben, für welchen Zweck die
Meldung erfolgt. Mit Ausnahme der Originallieferungen von Daten
sind dies z.B. Korrekturen und Löschungen. Der Zweck einer
Meldung wird durch das Element meldungsart ausgedrückt, das ein
entsprechendes Funktionselement enthält. Ist ein Bezug zu einer
vorausgegangenen Meldung notwendig oder möglich, erfolgt dieser
in Form der meldungsID, die dem Funktionselement nachgeordnet
ist. Das Funktionselement nil unterdrückt die Verarbeitung einer
Meldung.
Implementierungshinweis -
Typ xst:Meldungsart
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: erhebung
Eigenschaft Wert
Name im XML-Schema erhebung
Beschreibung Eine Erhebungsangabe hat eine Kennung und einen optionalen
Namen. Stammt die Kennung aus einer Klassifikation oder
Systematik, kann diese mit dem Attribut klasse des Elementes
kennung angegeben werden. Es ist ausserdem möglich, eine
Authentifizierungsangabe (berechtigung) abzulegen, da diese
erhebungsabhängig sein kann.
Implementierungshinweis -
Typ xst:Erhebung
Häufigkeit 1
Baukasten
110
Element: erhebung
Eigenschaft Wert
Default -
Nil-Wert möglich? nein
Form qualified
Element: berichtszeitraum
Eigenschaft Wert
Name im XML-Schema berichtszeitraum
Beschreibung Der Typ Berichtszeitraum gibt den Berichtszeitraum der gelieferten
statistischen Daten an. Dabei handelt es sich entweder um
ein Einzeldatum, beginnend mit der obligatorischen Angabe des
Jahres, oder um zwei Einzeldaten, die Beginn und Ende des
Berichtszeitraumes markieren. Die Angaben sind einschließende
Werte. In Spannen sind verschiedene Zeiträume für Beginn und
Ende möglich, z.B. „zweites Halbjahr 1999 bis einschließlich drittes
Quartal 2000“.
Implementierungshinweis -
Typ xst:Berichtszeitraum
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: berichtspflichtiger
Eigenschaft Wert
Name im XML-Schema berichtspflichtiger
Beschreibung Der Absender versendet das Dokument. Handelt es sich um eine
Rohdatenmeldung, kann er selbst Berichtspflichtiger sein und/
oder für Dritte berichten. Eine Empfangsbestätigung wird i.d.R. von
einem Statistischen Landesamt oder dem Statistischen Bundesamt
versendet.
Für eine Rohdatenmeldung steht zur Änderung der Adress- und
Kontaktinformationen das Element Korrektur zur Verfügung.
Es ist anwendungsspezifisch festzulgegen, welche Daten zu
Verifikation der Identität des Absenders herangezogen werden.
Implementierungshinweis -
Typ xst:Absender
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: berichtsempfaenger
Eigenschaft Wert
Name im XML-Schema berichtsempfaenger
Baukasten
111
Element: berichtsempfaenger
Eigenschaft Wert
Beschreibung Der Empfänger einer Rohdatenmeldung ist i.d.R. ein
Statistisches Landesamt oder das Statistische Bundesamt. Der
Berichtsempfänger muss in der Lage sein, sich selbst als
Adressaten zu bestätigen und benötigt deshalb eine Angabe zu
seiner Identifikation. Standardmäßig ist der Berichtsempfänger mit
dem Empfänger des Dokumentes identisch. Eine externe (i.d.R.
vom Absender verwendete) Angabe für die Identifikation eines
Verfahrensbeteiligten.
Implementierungshinweis -
Typ xst:Empfaenger
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: fehler
Eigenschaft Wert
Name im XML-Schema fehler
Beschreibung Diese Klasse beschreibt einen Fehler mit Schlüssel, Gewicht
Text und Position und ggf. dem Merkmal, auf das er sich
bezieht. Die Verwendung dieser Elemente und ihre Inhalte sind
verfahrensspezifisch festzulegen.
Für den gesamten Fehler, den Schlüssel, das Gewicht und den Text
bietet jeweils das Attribut klasse die Möglichkeit, die Inhalte einer
Klassifikation oder sonstigen formalen Definition zuzuordnen.
Implementierungshinweis -
Typ xst:Fehler
Häufigkeit 0 .. *
Default -
Nil-Wert möglich? nein
Form qualified
Attribute
Attribut: pruefstatus
Eigenschaft Wert
Name im XML-Schema pruefstatus
Beschreibung Einschränkung des Basistyps Token zur Beschreibung der
verschiedenen Prüfzustände. Dieser Typ findet auf verschiedenen
Ebenen des Prüfprotokolls Anwendung.
Implementierungshinweis -
Typ xst:Token.Pruefstatus
Optional nein
Default -
Baukasten
112
Pruefnachricht
In dieser Klasse werden die Ergebnisse der Prüfung der einzelnen Nachrichten der
Rohdatenmeldung gespeichert.
Prue fnachricht
attribute s
pruefstatus
nachrichte nID
type = xst:String.TextKlasseNoDefault
0..1
fe hle r
type = xst:Fehler
0..*
me ldung
type = xst:Pruefmeldung
0..*
Abbildung 3.48. xst:Pruefnachricht
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Pruefnachricht
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Pruefdokument,
Elemente
Element: nachrichtenID
Eigenschaft Wert
Name im XML-Schema nachrichtenID
Beschreibung Erweiterung des Typs String.Latin um ein Attribut klasse
zur Beschreibung von Zeichenketten. Im Gegensatz zum Typ
String.TextKlasse wird für das Attribut klasse kein
Standardwert vorgegeben.
Implementierungshinweis -
Typ xst:String.TextKlasseNoDefault
Häufigkeit 0 .. 1
Baukasten
113
Element: nachrichtenID
Eigenschaft Wert
Default -
Nil-Wert möglich? nein
Form qualified
Element: fehler
Eigenschaft Wert
Name im XML-Schema fehler
Beschreibung Diese Klasse beschreibt einen Fehler mit Schlüssel, Gewicht
Text und Position und ggf. dem Merkmal, auf das er sich
bezieht. Die Verwendung dieser Elemente und ihre Inhalte sind
verfahrensspezifisch festzulegen.
Für den gesamten Fehler, den Schlüssel, das Gewicht und den Text
bietet jeweils das Attribut klasse die Möglichkeit, die Inhalte einer
Klassifikation oder sonstigen formalen Definition zuzuordnen.
Implementierungshinweis -
Typ xst:Fehler
Häufigkeit 0 .. *
Default -
Nil-Wert möglich? nein
Form qualified
Element: meldung
Eigenschaft Wert
Name im XML-Schema meldung
Beschreibung In dieser Klasse werden die Informationen der Prüfungen der
einzelnen Meldungen einer Rohdatenmeldung (entspricht den
Datensegmenten mit den zugehörigen Metadaten) protokolliert.
Werden die Meldungen in der Rohdatenmeldung mit einer
Kennung eindeutig identifizierbar gemacht, ist diese Kennung
hier zu übernehmen und im Element meldungsID abzulegen. Die
Meldungsart gibt den Verwendungszweck der Meldung an, z.B.
Korrektur oder Löschung.
Erhebung und Berichtszeitraum sind vollständig anzugeben,
Berichtspflichtiger und -empfänger soweit sie nicht mit dem
Empfänger bzw. dem Absender des Prüfprotokolls identisch sind.
Alle gleichnamigen Elemente können aus einer Rohdatenmeldung
(DatML-RAW-D) kopiert werden.
Implementierungshinweis -
Typ xst:Pruefmeldung
Häufigkeit 0 .. *
Default -
Nil-Wert möglich? nein
Form qualified
Baukasten
114
Attribute
Attribut: pruefstatus
Eigenschaft Wert
Name im XML-Schema pruefstatus
Beschreibung Einschränkung des Basistyps Token zur Beschreibung der
verschiedenen Prüfzustände. Dieser Typ findet auf verschiedenen
Ebenen des Prüfprotokolls Anwendung.
Implementierungshinweis -
Typ xst:Token.Pruefstatus
Optional nein
Default -
Pruefprotokoll
Ein Prüfprotokoll enthält die Prüfergebnisse für eine Rohdatenmeldung. Die Ergebnisse
sind analog zur logischen Struktur einer Meldung im DatML-RAW-D-Format unterteilt in die
Ebenen Prüfdokument, Nachricht und Meldung. Der Umfang der Prüfungen und damit des
Prüfprotokolls kann in Abhängigkeit des Meldungsformates und der Prüfverfahren variieren und
ist entsprechend zu dokumentieren.
Prue fprotokoll
prue fung
type = xst:Pruefung
dokume nt
type = xst:Pruefdokument
Abbildung 3.49. xst:Pruefprotokoll
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Pruefprotokoll
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:DatML-RES-D (globales Element),
Elemente
Element: pruefung
Eigenschaft Wert
Name im XML-Schema pruefung
Beschreibung Es sind fünf generische Prüfebenen definiert, die verschiedenen
formalen und inhaltlichen Aspekten entsprechen, nach denen
eine Rohdatenmeldung geprüft werden kann: Syntax, Semantik,
Autorisierung, Daten und Dokument. Für jede Prüfebene kann der
Prüfstatus angegeben werden.
Baukasten
115
Element: pruefung
Eigenschaft Wert
Implementierungshinweis -
Typ xst:Pruefung
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: dokument
Eigenschaft Wert
Name im XML-Schema dokument
Beschreibung Diese Klasse enthält die Prüfergebnisse für die gesamte
Rohdatenmeldung und den auf der Dokumentenebene
aufgetretenen Fehlern. Auf dieser Prüfebene werden alle anderen (in
der Klasse Prüfung definierten) Prüfebenen zusammen gefasst.
Mit dem Attribut dokumentstatus wird zusätzlich angegeben,
ob das Dokument als Ganzes ungeprüft ist, akzeptiert oder
abgewiesen wurde. Wie Prüfstatus und dokumentstatus
zusammenhängen ist verfahrensspezifisch.
Implementierungshinweis -
Typ xst:Pruefdokument
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Pruefstatus
Mit dem Attribut pruefstatus wird der Status (ungeprüft, fehlerhaft, fehlerfrei) der einzelnen
Prüfungen angegeben.
Prue fs tatus
attribute s
pruefstatus
Abbildung 3.50. xst:Pruefstatus
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Pruefstatus
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Pruefung,
Baukasten
116
Attribute
Attribut: pruefstatus
Eigenschaft Wert
Name im XML-Schema pruefstatus
Beschreibung Einschränkung des Basistyps Token zur Beschreibung der
verschiedenen Prüfzustände. Dieser Typ findet auf verschiedenen
Ebenen des Prüfprotokolls Anwendung.
Implementierungshinweis -
Typ xst:Token.Pruefstatus
Optional nein
Default -
Pruefung
Es sind fünf generische Prüfebenen definiert, die verschiedenen formalen und inhaltlichen
Aspekten entsprechen, nach denen eine Rohdatenmeldung geprüft werden kann: Syntax,
Semantik, Autorisierung, Daten und Dokument. Für jede Prüfebene kann der Prüfstatus
angegeben werden.
Prue fung
prue fs tufe
type = xst:Pruefstufe
0..1
dokume nttyp
type = xst:Dokumententyp
0..1
s yntax
type = xst:Pruefstatus
0..1
s e mantik
type = xst:Pruefstatus
0..1
autoris ie rung
type = xst:Pruefstatus
0..1
date n
type = xst:Pruefstatus
0..1
Abbildung 3.51. xst:Pruefung
Baukasten
117
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Pruefung
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Pruefprotokoll,
Elemente
Element: pruefstufe
Eigenschaft Wert
Name im XML-Schema pruefstufe
Beschreibung Datentyp für die Angabe der Prüfstufe innerhalb des
Prüfprotokolls.
In vielen Fällen ist es aus verfahrenstechnischen oder fachlichen
Gründen nicht möglich, ein Meldungsdokument vollständig in
einem einzigen Schritt zu prüfen. Stattdessen werden zwei
oder mehr Prüfungen durchlaufen, die jeweils unterschiedliche
Aspekte eines Dokumentes prüfen oder in der Tiefe variieren.
Prüfprotokolle können daher Zwischenergebnisse enthalten, und es
kann vorkommen, dass ein Dokument so fehlerhaft ist, dass es nicht
alle Prüfschritte durchlaufen kann.
Mit dem Typ Pruefstufe können in einem Prüfprotokoll
Informationen hinterlegt werden, die den Umfang der
vorgenommenen Prüfungen ausdrückt:
1) Konformität mit der Dokumententypdefinition (XML
Schema):Geprüft wird auf Wohlgeformtheit (Syntax) und Validität
(Semantik).
2) Semantik: Soweit sie nicht durch die Dokumententypdefinition
abgedeckt ist (z. B. Eindeutigkeit der Metadaten im Segmentpfad).
Beinhaltet 1).
3) Einhaltung weiterer, nicht statistikspezifischer Vorgaben, wie
Güötigkeit der Empfänger- und Absenderangaben. Beinhaltet 1) und
2).
4) Einhaltung der Vorgaben der der Erhebungsbeschreibung, z.
B. Namen und Anzahl der Merkmale und Merkmalsgruppen,
Vollständigkeit der obligatorischen Merkmale, Datentypen,
Berichtszeitraum und Erhebung. Beinhaltet 1) und 2).
5) Vollständige Prüfung. Beinhaltet 1), 2), 3) und 4).
Implementierungshinweis -
Typ xst:Pruefstufe
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Baukasten
118
Element: dokumenttyp
Eigenschaft Wert
Name im XML-Schema dokumenttyp
Beschreibung Diese Klasse gibt den Namen und optional die Version des zur
Prüfung verwendeten Dokumententyps an.
Implementierungshinweis -
Typ xst:Dokumententyp
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: syntax
Eigenschaft Wert
Name im XML-Schema syntax
Beschreibung Diese Prüfebene entspricht einer reinen Syntaxprüfung. Ein XMLbasiertes Dokument ist syntaktisch korrekt, wenn es den XMLSyntaxregeln folgt.
Implementierungshinweis -
Typ xst:Pruefstatus
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: semantik
Eigenschaft Wert
Name im XML-Schema semantik
Beschreibung Diese Prüfebene entspricht einer reinen Semantikprüfung.Ein
XML-Dokument ist aus XML-Sicht semantisch korrekt, wenn
es gegen eine Dokumententypdefinition validierbar ist. Es
kann aber semantische Regeln geben, die nicht durch einen
Dokumententyp dargestellt werden können. In solchen Fällen wird
die semantische Prüfung dieser Regeln durch eine spezifische
Anwendung unterstützt. In den Bereich der Semantikprüfung fallen
auch solche Daten, die formale Aspekte der Meldung betreffen
oder rein funktionaler, nichtstatistischer Art sind (z.B. Anzahl der
Datensätze oder Testindikatoren).
Implementierungshinweis -
Typ xst:Pruefstatus
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Baukasten
119
Element: autorisierung
Eigenschaft Wert
Name im XML-Schema autorisierung
Beschreibung Diese Prüfebene umfasst die Prüfung der Angaben zur Identifikation
und Autorisierung der Verfahrensteilnehmer.
Implementierungshinweis -
Typ xst:Pruefstatus
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: daten
Eigenschaft Wert
Name im XML-Schema daten
Beschreibung Auf dieser Prüfebene werden alle statistischen Rohdaten und
Metadaten geprüft.
Implementierungshinweis -
Typ xst:Pruefstatus
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Satz
Ein statistischer Datensatz stellt eine Informationseinheit dar, die zusammenhängende Daten
über ein Erhebungsobjekt enthält. Ein Satz besteht aus mindestens einem (Wert-)Merkmal und
einer optionalen Anzahlangabe für Kontrollzwecke.
Baukasten
120
Satz
attribute s
kennung
1..*
mm
type = xst:Merkmal
mmg r
type = xst:Merkmalsgruppe
anzahl
type = xs:positiveInteger
0..1
Abbildung 3.52. xst:Satz
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Satz
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Datensegment.Choice,
- xst:Ordnungsmerkmal.Sequence.Choice,
Elemente
Element: anzahl
Eigenschaft Wert
Name im XML-Schema anzahl
Beschreibung -
Implementierungshinweis -
Typ xs:positiveInteger (http://www.w3.org/2001/XMLSchema.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Attribute
Attribut: kennung
Eigenschaft Wert
Name im XML-Schema kennung
Baukasten
121
Attribut: kennung
Eigenschaft Wert
Beschreibung Das Attribut kennung ist eine Möglichkeit, Sätze unterschiedlichen
Typs in Bezug auf Inhalt und Aufbau zu kennzeichnen.
Anwendungsentwicklern steht es frei, auch andere Mechanismen
der Satztyperkennung zu implementieren.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Lokale Strukturen
Name in der Spezifikation
Satz.Choice
Satz.Choice
Lokaler Hilfstyp zur abwärtskompatiblen Modellierung der übergeordneten Klasse.
Satz.Choice
mm
type = xst:Merkmal
mmg r
type = xst:Merkmalsgruppe
Abbildung 3.53. xst:Satz.Choice
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Satz.Choice
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Choice
Verwendet in - xst:Satz,
Elemente
Element: mm
Eigenschaft Wert
Name im XML-Schema mm
Beschreibung Der Typ Merkmal beschreibt ein statistisches Merkmal, das mit
einem Wert oder einer expliziten Nichtantwort verbunden ist.
Baukasten
122
Element: mm
Eigenschaft Wert
Das Attribut name identifiziert das Merkmal und muss immer
angegeben werden. Das Attribut text erlaubt eine textuelle
Merkmalsbeschreibung.
Implementierungshinweis -
Typ xst:Merkmal
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: mmgr
Eigenschaft Wert
Name im XML-Schema mmgr
Beschreibung Ein einfaches Merkmal darf in einem Satz grundsätzlich
genau einmal vorkommen. Es ist jedoch möglich, dass für
ein Erhebungsobjekt mehrere Ausprägungen eines Merkmals
existieren, die alle dem gleichen Erhebungskontext und -objekt
zugeordnet sind. Oft handelt es sich dabei um mehrere Merkmale,
die eine zusammenhängende, wiederholbare Struktur (in der
amtlichen Statistik "wiederholte Feldgruppe" genannt) bilden.
Merkmale müssen innerhalb einer Merkmalsgruppe eindeutig sein.
Es können aber in einem Datensatz beliebig viele Instanzen
einer Merkmalsgruppe enthalten sein. Merkmalsgruppen können
wiederum weitere Merkmalsgruppen enthalten.
Einfache Merkmale und Merkmalsgruppen selbst können zu einer
wiederhol- und indizierbaren Merkmalsgruppe zusammengefasst
werden. Das Attribut name identifiziert die Merkmalsgruppe und
muss immer angegeben werden. Das Attribut text erlaubt eine
zusätzliche textuelle Beschreibung.
Implementierungshinweis -
Typ xst:Merkmalsgruppe
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Segment
Ein Segment besteht aus einem optionalen Kommentar und mindestens einem Metadatum zum
statistischen Kontext (StatistischerKontext), gefolgt von einem Datensegment oder
einer Folge von Segmenten, die wiederum weitere Segmente enthalten können.
Baukasten
123
Se g me nt
me mo
type = xoev-dt:String.Latin
0..1
e rhe bung
type = xst:Erhebung
0..1
be richts ze itraum
type = xst:Berichtszeitraum
0..1
be richts pflichtig e r
type = xst:Absender
0..1
be richts e mpfae ng e r
type = xst:Empfaenger
0..1
mate rial
type = xst:Material
0..1
date nattribute
type = xst:Datenattribute
0..1
hmm
type = xst:Hilfsmerkmal
0..*
date ns e g me nt
type = xst:Datensegment
s e g me nt
type = xst:Segment
1..*
Abbildung 3.54. xst:Segment
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Segment
Baukasten
124
Eigenschaft Wert
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:StatistischerKontext.Choice,
Elemente
Element: memo
Eigenschaft Wert
Name im XML-Schema memo
Beschreibung Das Feld memo ermöglicht die Angabe eines zusätzlichen
Kommentars.
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Lokale Strukturen
Name in der Spezifikation
StatistischerKontext
StatistischerKontext
Hilfsklasse zur Modellierung der gemeinsamen Strukturen der Elemente Nachricht und
Segment.
Sowohl Nachricht als auch Segment enthalten einen optionalen Kommentar und
verschiedene optionale Metadaten, gefolgt von entweder einem Datensegment, das
die Meldungsdaten enthält, oder einer Folge von Segmenten, die wiederum weitere
Segmente enthalten können. Durch die hierarchische Anordnung von Segmenten entsteht ein
Segmentbaum. Die Wurzel des Segmentbaumes ist das Element Nachricht, das die gleichen
Eigenschaften besitzt wie ein Segment. Das Nachrichtenelement kann daher logisch wie ein
Segment behandelt werden.
Die Blätter des Segmentbaumes sind diejenigen Segmente, die statt weiterer Segmente ein
Datensegment enthalten. In unsegmentierten Nachrichten besteht der Segmentbaum nur aus
dem Nachrichtenelement.
Jedes Metadatum darf auf einem Segmentpfad nur einmal vorkommen. Dabei spielt es
keine Rolle, ob es sich in einem Nachrichten- oder einem Segmentelement befindet.
Hilfsmerkmale dürfen beliebig oft erscheinen, doch muss jedes einen eindeutigen Namen
haben.
Baukasten
125
Statis tis che rKonte xt
e rhe bung
type = xst:Erhebung
0..1
be richts ze itraum
type = xst:Berichtszeitraum
0..1
be richts pflichtig e r
type = xst:Absender
0..1
be richts e mpfae ng e r
type = xst:Empfaenger
0..1
mate rial
type = xst:Material
0..1
date nattribute
type = xst:Datenattribute
0..1
hmm
type = xst:Hilfsmerkmal
0..*
date ns e g me nt
type = xst:Datensegment
s e g me nt
type = xst:Segment
1..*
Abbildung 3.55. xst:StatistischerKontext
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema StatistischerKontext
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Nachricht,
Baukasten
126
Eigenschaft Wert
- xst:Segment,
Elemente
Element: erhebung
Eigenschaft Wert
Name im XML-Schema erhebung
Beschreibung Eine Erhebungsangabe hat eine Kennung und einen optionalen
Namen. Stammt die Kennung aus einer Klassifikation oder
Systematik, kann diese mit dem Attribut klasse des Elementes
kennung angegeben werden. Es ist ausserdem möglich, eine
Authentifizierungsangabe (berechtigung) abzulegen, da diese
erhebungsabhängig sein kann.
Implementierungshinweis -
Typ xst:Erhebung
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: berichtszeitraum
Eigenschaft Wert
Name im XML-Schema berichtszeitraum
Beschreibung Der Typ Berichtszeitraum gibt den Berichtszeitraum der gelieferten
statistischen Daten an. Dabei handelt es sich entweder um
ein Einzeldatum, beginnend mit der obligatorischen Angabe des
Jahres, oder um zwei Einzeldaten, die Beginn und Ende des
Berichtszeitraumes markieren. Die Angaben sind einschließende
Werte. In Spannen sind verschiedene Zeiträume für Beginn und
Ende möglich, z.B. „zweites Halbjahr 1999 bis einschließlich drittes
Quartal 2000“.
Implementierungshinweis -
Typ xst:Berichtszeitraum
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: berichtspflichtiger
Eigenschaft Wert
Name im XML-Schema berichtspflichtiger
Beschreibung Es können Daten beliebig vieler Berichtspflichtiger an beliebig viele
Berichtsempfänger in einer DatML-RAW-D-Nachricht übermittelt
werden. Standardmäßig ist der Berichtspflichtige mit dem
Absender identisch. Ein berichtspflichtiger muss daher nur
angegeben werden, wenn er nicht mit dem Absender der DatMLRAW-D-Nachricht übereinstimmt (siehe auch Abschnitt  2.1,
„Akteure“). Für Änderungen der Adres- und Kontaktinformationen
Baukasten
127
Element: berichtspflichtiger
Eigenschaft Wert
eines Berichtspflichtigen kann das Element Korrektur verwendet
werden.
Implementierungshinweis -
Typ xst:Absender
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: berichtsempfaenger
Eigenschaft Wert
Name im XML-Schema berichtsempfaenger
Beschreibung Es können Daten beliebig vieler Berichtspflichtiger an beliebig viele
Berichtsempfänger in einer DatML-RAW-D-Nachricht übermittelt
werden. Standardmäßig ist der Berichtsempfänger mit dem
Empfänger identisch. Ein Berichtsempfänger muss daher nur
angegeben werden, wenn er nicht mit dem Empfänger der DatMLRAW-D-Nachricht übereinstimmt (siehe auch Abschnitt  2.1,
„Akteure“).
Implementierungshinweis -
Typ xst:Empfaenger
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: material
Eigenschaft Wert
Name im XML-Schema material
Beschreibung Bezeichnung und Version des Liefermaterials.
Implementierungshinweis -
Typ xst:Material
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: datenattribute
Eigenschaft Wert
Name im XML-Schema datenattribute
Beschreibung Der Typ Datenattribute beschreibt allgemeine Eigenschaften
von Werten in einfachen und Ordnungsmerkmalen. Für numerische
Werte können Dezimalzeichen und Tausender-Trennzeichen
abweichend vom Default bestimmt werden.
Baukasten
128
Element: datenattribute
Eigenschaft Wert
Implementierungshinweis -
Typ xst:Datenattribute
Häufigkeit 0 .. 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: hmm
Eigenschaft Wert
Name im XML-Schema hmm
Beschreibung Hilfsmerkmale sind Merkmale, die häufig zur Erhebung
meldungsglobaler Zusatzinformationen verwendet werden. Oft
dienen sie auch zu organisatorischen und Verfahrenszwecken. Wie
Ordnungsmerkmale haben sie einen Namen und einen Wert,
der nicht leer sein darf. Hilfsmerkmale sind in den Elementen
Nachricht und Segment erlaubt.
Implementierungshinweis -
Typ xst:Hilfsmerkmal
Häufigkeit 0 .. *
Default -
Nil-Wert möglich? nein
Form qualified
Lokale Strukturen
Name in der Spezifikation
StatistischerKontext.Choice
StatistischerKontext.Choice
Lokaler Hilfstyp zur abwärtskompatiblen Modellierung der übergeordneten Klasse.
Statis tis che rKonte xt.Choice
date ns e g me nt
type = xst:Datensegment
s e g me nt
type = xst:Segment
1..*
Abbildung 3.56. xst:StatistischerKontext.Choice
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema StatistischerKontext.Choice
Baukasten
129
Eigenschaft Wert
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Choice
Verwendet in - xst:StatistischerKontext,
Elemente
Element: datensegment
Eigenschaft Wert
Name im XML-Schema datensegment
Beschreibung Ein Datensegment ist derjenige Abschnitt eines Segmentes,
der die Meldungsdatensätze vom Typ Satz enthält, die
wiederum Ordnungsmerkmale enthalten können. Innerhalb
eines Datensegmentes haben alle Daten denselben statistischen
Kontext.
Der Begriff Meldung wird somit definiert als Einheit bestehend
aus einem Datensegment und den Metadaten, die sich auf
dem Segmentpfad zum übergeordneten Nachrichtenelement
befinden, einschließlich den Angaben Berichtspflichtiger
und Berichtsempfänger.
Die Metadaten des statistischen Kontextes erlauben es, in jedem
Datensegment einen in sich abgeschlossenen Rohdatenbestand
zu liefern. Grundsätzlich entspricht daher ein Datensegment einer
Rohdatenmeldung.
Anmerkung
Es ist nicht ausgeschlossen, dass in einer DatMLRAW-D-Instanz zwei oder mehr Datensegmente – ggf.
in verschiedenen Nachrichten – den selben statistischen
Kontext besitzen.
Implementierungshinweis -
Typ xst:Datensegment
Häufigkeit 1
Default -
Nil-Wert möglich? nein
Form qualified
Element: segment
Eigenschaft Wert
Name im XML-Schema segment
Beschreibung Ein Segment besteht aus einem optionalen Kommentar
und mindestens einem Metadatum zum statistischen Kontext
(StatistischerKontext), gefolgt von einem Datensegment
oder einer Folge von Segmenten, die wiederum weitere Segmente
enthalten können.
Implementierungshinweis -
Typ xst:Segment
Basisdatentypen
130
Element: segment
Eigenschaft Wert
Häufigkeit 1 .. *
Default -
Nil-Wert möglich? nein
Form qualified
Test
Das Element Test zeigt an, dass die Nachricht nur zu Testzwecken versendet wurde. Das Attribut
kennung erlaubt eine beliebige Angabe, z.B. für die Steuerung und Kontrolle von Testserien.
Te s t
attribute s
kennung
Abbildung 3.57. xst:Test
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Test
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Optionen,
Attribute
Attribut: kennung
Eigenschaft Wert
Name im XML-Schema kennung
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
3.3.2. Basisdatentypen
Übersicht zum Schema
Sammlung von technischen Datentypen, z.B. Einschränkungen von W3C-Datentypen.
Basisdatentypen
131
XML-Schema: xstatistik-basistypen.xsd
Eigenschaft Wert
Version 2.0.1
Namensraum http://www.destatis.de/schema/datml-raw/2.0/de
Präfix xst
URL des Schemas http://www.statspez.de/service/downloads/XStatistik/v2_0_1/
xstatistik-basistypen.xsd
Inkludierte Schemata -
Importierte Schemata - XOEV-Basisdatentypen (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd, Präfix: xoev-dt)
Übersicht der Typen
Es existieren die folgenden Basisdatentypen:
Name in der Spezifikation Name im XML-Schema
Leertyp Leertyp
PositiveInteger.Halbjahr PositiveInteger.Halbjahr
PositiveInteger.Jahr PositiveInteger.Jahr
PositiveInteger.Monat PositiveInteger.Monat
PositiveInteger.Pruefstufe PositiveInteger.Pruefstufe
PositiveInteger.Quartal PositiveInteger.Quartal
PositiveInteger.Tag PositiveInteger.Tag
PositiveInteger.Woche PositiveInteger.Woche
Pruefstufe Pruefstufe
String.Datenformat String.Datenformat
String.Datentraeger String.Datentraeger
String.Datum String.Datum
String.Formatiert String.Formatiert
String.Position String.Position
String.SchluesselGewicht String.SchluesselGewicht
String.TextKlasse String.TextKlasse
String.TextKlasseNoDefault String.TextKlasseNoDefault
String.TextZeileHTML String.TextZeileHTML
String.Uhrzeit String.Uhrzeit
String.Wert String.Wert
StringLatin.NormalizedString StringLatin.NormalizedString
StringLatin.Token StringLatin.Token
Token.Datenformat Token.Datenformat
Token.Datentraeger Token.Datentraeger
Token.Dokumentstatus Token.Dokumentstatus
Token.FormatEmpfangsbestaetigung Token.FormatEmpfangsbestaetigung
Token.FormatPosition Token.FormatPosition
Token.Formatklasse Token.Formatklasse
Basisdatentypen
132
Name in der Spezifikation Name im XML-Schema
Token.Pruefstatus Token.Pruefstatus
Token.Versandart Token.Versandart
Token.Version.DatML-RAW-D Token.Version.DatML-RAW-D
Token.Version.DatML-RES-D Token.Version.DatML-RES-D
Leertyp
Leerer Datentyp für die Beschreibung leerer Elemente.
Abbildung 3.58. xst:Leertyp
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Leertyp
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Verwendet in - xst:Datei.Choice,
- xst:Meldungsart,
PositiveInteger.Halbjahr
Datentyp für die Angabe des Halbjahres des Berichtszeitraumes. Dieser Datentyp wird intern auch
für die Angabe des Semesters verwendet (siehe auch Token.Formatklasse).
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema PositiveInteger.Halbjahr
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xs:positiveInteger (http://www.w3.org/2001/XMLSchema.xsd)
Verwendet in - xst:Berichtszeitraumdatum.Choice,
Einschränkungen
Einschränkungstyp Wert
maxInclusive 2
minInclusive 1
PositiveInteger.Jahr
Datentyp für die Angabe des Jahres des Berichtszeitraumes.
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema PositiveInteger.Jahr
Basisdatentypen
133
Eigenschaft Wert
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xs:positiveInteger (http://www.w3.org/2001/XMLSchema.xsd)
Verwendet in - xst:Berichtszeitraumdatum,
Einschränkungen
Einschränkungstyp Wert
maxInclusive 9999
minInclusive 0001
PositiveInteger.Monat
Datentyp für die Angabe des Monats des Berichtszeitraumes.
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema PositiveInteger.Monat
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xs:positiveInteger (http://www.w3.org/2001/XMLSchema.xsd)
Verwendet in - xst:Berichtszeitraumdatum.Choice.Sequence,
Einschränkungen
Einschränkungstyp Wert
maxInclusive 12
minInclusive 1
PositiveInteger.Pruefstufe
Datentyp für die Angabe der Prüfstufe innerhalb des Prüfprotokolls.
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema PositiveInteger.Pruefstufe
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xs:positiveInteger (http://www.w3.org/2001/XMLSchema.xsd)
Zur Ableitung genutzt von - xst:Pruefstufe,
Einschränkungen
Einschränkungstyp Wert
maxInclusive 5
Basisdatentypen
134
Einschränkungstyp Wert
minInclusive 1
PositiveInteger.Quartal
Datentyp für die Angabe des Quartals des Berichtszeitraumes.
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema PositiveInteger.Quartal
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xs:positiveInteger (http://www.w3.org/2001/XMLSchema.xsd)
Verwendet in - xst:Berichtszeitraumdatum.Choice,
Einschränkungen
Einschränkungstyp Wert
maxInclusive 4
minInclusive 1
PositiveInteger.Tag
Datentyp für die Angabe des Tages im Monat des Berichtszeitraumes.
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema PositiveInteger.Tag
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xs:positiveInteger (http://www.w3.org/2001/XMLSchema.xsd)
Verwendet in - xst:Berichtszeitraumdatum.Choice.Sequence,
Einschränkungen
Einschränkungstyp Wert
maxInclusive 31
minInclusive 1
PositiveInteger.Woche
Datentyp für die Angabe der Kalenderwoche des Berichtszeitraumes.
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema PositiveInteger.Woche
Basisdatentypen
135
Eigenschaft Wert
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xs:positiveInteger (http://www.w3.org/2001/XMLSchema.xsd)
Verwendet in - xst:Berichtszeitraumdatum.Choice,
Einschränkungen
Einschränkungstyp Wert
maxInclusive 53
minInclusive 1
Pruefstufe
Datentyp für die Angabe der Prüfstufe innerhalb des Prüfprotokolls.
In vielen Fällen ist es aus verfahrenstechnischen oder fachlichen Gründen nicht möglich, ein
Meldungsdokument vollständig in einem einzigen Schritt zu prüfen. Stattdessen werden zwei
oder mehr Prüfungen durchlaufen, die jeweils unterschiedliche Aspekte eines Dokumentes
prüfen oder in der Tiefe variieren. Prüfprotokolle können daher Zwischenergebnisse enthalten,
und es kann vorkommen, dass ein Dokument so fehlerhaft ist, dass es nicht alle Prüfschritte
durchlaufen kann.
Mit dem Typ Pruefstufe können in einem Prüfprotokoll Informationen hinterlegt werden, die
den Umfang der vorgenommenen Prüfungen ausdrückt:
1) Konformität mit der Dokumententypdefinition (XML Schema):Geprüft wird auf Wohlgeformtheit
(Syntax) und Validität (Semantik).
2) Semantik: Soweit sie nicht durch die Dokumententypdefinition abgedeckt ist (z. B.
Eindeutigkeit der Metadaten im Segmentpfad). Beinhaltet 1).
3) Einhaltung weiterer, nicht statistikspezifischer Vorgaben, wie Güötigkeit der Empfänger- und
Absenderangaben. Beinhaltet 1) und 2).
4) Einhaltung der Vorgaben der der Erhebungsbeschreibung, z. B. Namen und Anzahl der
Merkmale und Merkmalsgruppen, Vollständigkeit der obligatorischen Merkmale, Datentypen,
Berichtszeitraum und Erhebung. Beinhaltet 1) und 2).
5) Vollständige Prüfung. Beinhaltet 1), 2), 3) und 4).
Prue fs tufe
attribute s
klasse
Abbildung 3.59. xst:Pruefstufe
Basisdatentypen
136
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Pruefstufe
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Erweiterung von xst:PositiveInteger.Pruefstufe,
Verwendet in - xst:Pruefung,
Attribute
Attribut: klasse
Eigenschaft Wert
Name im XML-Schema klasse
Beschreibung Einschränkung auf alle lateinischen Zeichen innerhalb Unicode (vgl.
XÖV-Handbuch).
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Optional ja
Default -
String.Datenformat
Erweiterung des Typs String.Latin um ein Attribut typ zur Beschreibung des Datenformats der
Rohdaten (siehe auch Token.Datenformat).
String .Date nformat
attribute s
typ
Abbildung 3.60. xst:String.Datenformat
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema String.Datenformat
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Erweiterung von xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Basisdatentypen
137
Eigenschaft Wert
Verwendet in - xst:Datei,
Attribute
Attribut: typ
Eigenschaft Wert
Name im XML-Schema typ
Beschreibung Hilfstyp zur Einschränkung der für eine Datenlieferung möglichen
Datenformate (undefiniert, datml, xml, datensatz, edifact). Der Wert
datml zeigt an, dass eine DatML/RAW-Instanz geliefert wurde (siehe
auch String.Datenformat).
Implementierungshinweis -
Typ xst:Token.Datenformat
Optional ja
Default -
String.Datentraeger
Erweiterung des Typs String.Latin um ein Attribut typ zur Beschreibung des Datenträgers, auf dem
die Rohdaten ausgeliefert wurden (siehe auch Token.Datentraeger).
String .Date ntrae g e r
attribute s
typ
Abbildung 3.61. xst:String.Datentraeger
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema String.Datentraeger
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Erweiterung von xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Verwendet in - xst:Datei.Choice,
Attribute
Attribut: typ
Eigenschaft Wert
Name im XML-Schema typ
Basisdatentypen
138
Attribut: typ
Eigenschaft Wert
Beschreibung Hilfstyp zur Einschränkung der Werte für Datenträger, mit der
eine Datenlieferung erfolgt ist (undefiniert, diskettel, cdrom, dvd,
kassette, magnetband) (siehe auch String.Datentraeger ).
Implementierungshinweis -
Typ xst:Token.Datentraeger
Optional ja
Default -
String.Datum
Erweiterung des Typs String.Latin zur Beschreibung formatierter Zeichenketten mit einem
speziellen Formatschema für eine Datumsangabe (siehe auch String.Formatiert).
String .Datum
attribute s
format
klasse
Abbildung 3.62. xst:String.Datum
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema String.Datum
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Erweiterung von xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Verwendet in - xst:Datei,
- xst:Dateneingang,
- xst:Dokumentinstanz,
Attribute
Attribut: format
Eigenschaft Wert
Name im XML-Schema format
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Basisdatentypen
139
Attribut: format
Eigenschaft Wert
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default jjjjmmtt (fix)
Attribut: klasse
Eigenschaft Wert
Name im XML-Schema klasse
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default datum (fix)
String.Formatiert
Erweiterung des Typs String.Latin zur Beschreibung formatierter Zeichenketten. Die erforderlichen
Attribute format und klasse liefern ein Formatschema und die Klasse des Formatschemas.
Aufgrund des Klassennamens (derzeit ausschließlich datum) kann das Formatschema
interpretiert werden.
String .Formatie rt
attribute s
format
klasse
Abbildung 3.63. xst:String.Formatiert
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema String.Formatiert
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Erweiterung von xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Basisdatentypen
140
Eigenschaft Wert
Verwendet in - xst:Berichtszeitraum,
Attribute
Attribut: format
Eigenschaft Wert
Name im XML-Schema format
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional nein
Default
Attribut: klasse
Eigenschaft Wert
Name im XML-Schema klasse
Beschreibung Datentyp zur Angabe der Formatklasse (siehe auch
String.Formatiert). Formatklasse datum: Beschreibung eines
Einzeldatums oder einer Zeitspanne aus zwei Einzeldaten nach
folgendem Formatschema:
datum[-datum]
datum: j4|[{h|hh}|{q|qq}|{s|ss}|{w|ww}|
monat[tag[std[min[sek]]]]
j4: jjjj, Jahr vierstellig
h: h, Halbjahr i.d.F. hn|Hn|n, n=1..2
hh: hh, Halbjahr i.d.F. nn, nn=01..02
q: q, Quartal i.d.F. qn|Qn|n, n=1..4
qq: qq, Quartal i.d.F. nn, nn=01..04
s: s, Semester i.d.F. sn|Sn|n, n=1..2
(1=Sommersemester, 2=Wintersemester)
ss: ss, Semester i.d.F. nn, nn=01..02
monat: mm, Monat zweistellig
w: w, Woche i.d.F. wnn|Wnn|nn, nn=01..53
ww: ww, Woche i.d.F. nn, nn=01..53
tag: tt, Tag zweistellig
std: hh, Stunde zweistellig
min: mm, Minute zweistellig
sek: ss, Sekunde zweistellig
Hinweise:
• Das Jahr ist stets vierstellig und obligatorisch.
• Auf das Jahr folgt entweder ein Monat, ein Quartal, ein Halbjahr
oder eine Woche (von 01-53).
Basisdatentypen
141
Attribut: klasse
Eigenschaft Wert
• Die Kennzeichnung eines Halbjahres, eines Semesters, eines
Quartals und einer Woche im Datum (nicht im Format) durch
einen Buchstaben ist optional; so kann das erste Halbjahr 2002
wahlweise als 2002H1 und als 20021 angegeben werden.
• Ein Tag darf nur auf einen Monat folgen.
• Eine Uhrzeit darf nur auf einen Tag folgen.
Formatschema Werte Bedeutung
jjjjmm 200205 Jahr und Monat
jjjj-jjjj 2001-2002 Jahresspanne
jjjjq 2002Q2, 20022 Jahr und zweites Quartal
jjjjqq 200202 Jahr und zweites Quartal
jjjjh 2002H1, 20021 Jahr und erstes Halbjahr
jjjjhh 200201 Jahr und erstes Halbjahr
jjjjs 20021, 2002S1 Jahr und Sommersemester
jjjjss 200202 Jahr und Wintersemester
Implementierungshinweis -
Typ xst:Token.Formatklasse
Optional nein
Default
String.Position
Die Position der fehlerverursachenden Stelle im Meldungsdokument. Die Stelle kann auf
verschiedene Weise angegeben werden (siehe auch Token.FormatPosition). Beispiele:
X-Path Ausdruck: <position>satz/mm[5]/wert</position>
byte: <position format=’byte’>2691</position>
char: <position format=’char’>2691</position>
Name des Fehler verursachenden Feldes:<position format=’name’>Alter in
Jahren</position>
Satz und Offset:<position format=’satz’>8,25</position< (Fehler in Satz 8,
Position 25)
String .Pos ition
attribute s
format
Abbildung 3.64. xst:String.Position
Basisdatentypen
142
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema String.Position
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Erweiterung von xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Verwendet in - xst:Fehler,
Attribute
Attribut: format
Eigenschaft Wert
Name im XML-Schema format
Beschreibung Einschränkung des Typs Token zur Beschreibung der verschiedenen
Möglichkeiten, um Fehlerpositionen anzugeben (siehe auch
String.Position)
Implementierungshinweis -
Typ xst:Token.FormatPosition
Optional ja
Default -
String.SchluesselGewicht
Erweiterung des Typs String.Latin zur Beschreibung des Fehlerschlüssels und -gewichts. Die
zulässigen Werte sind verfahrensspezifisch.
String .Schlue s s e lGe w icht
attribute s
klasse
Abbildung 3.65. xst:String.SchluesselGewicht
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema String.SchluesselGewicht
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Basisdatentypen
143
Eigenschaft Wert
Erweiterung von xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Verwendet in - xst:Fehler,
Attribute
Attribut: klasse
Eigenschaft Wert
Name im XML-Schema klasse
Beschreibung Einschränkung auf alle lateinischen Zeichen innerhalb Unicode (vgl.
XÖV-Handbuch).
Implementierungshinweis -
Typ xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Optional ja
Default -
String.TextKlasse
Erweiterung des Typs String.Latin um ein Attribut klasse zur Beschreibung von Zeichenketten.
Im Gegensatz zum Typ String.TextKlasseNoDefault wird für das Attribut klasse der
Standardwert default gesetzt.
String .Te xtKlas s e
attribute s
klasse
Abbildung 3.66. xst:String.TextKlasse
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema String.TextKlasse
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Erweiterung von xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Verwendet in - xst:Absender,
- xst:Empfaenger,
- xst:Erhebung,
Basisdatentypen
144
Eigenschaft Wert
- xst:Material,
Attribute
Attribut: klasse
Eigenschaft Wert
Name im XML-Schema klasse
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default default
String.TextKlasseNoDefault
Erweiterung des Typs String.Latin um ein Attribut klasse zur Beschreibung von Zeichenketten.
Im Gegensatz zum Typ String.TextKlasse wird für das Attribut klasse kein Standardwert
vorgegeben.
String .Te xtKlas s e NoDe fault
attribute s
klasse
Abbildung 3.67. xst:String.TextKlasseNoDefault
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema String.TextKlasseNoDefault
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Erweiterung von xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Verwendet in - xst:Anwendung,
- xst:Datei,
- xst:Dateneingang,
- xst:Datensegment,
- xst:Dokumentinstanz,
- xst:Fehler,
- xst:Formular,
- xst:Funktionselement,
Basisdatentypen
145
Eigenschaft Wert
- xst:Nachricht,
- xst:Pruefmeldung,
- xst:Pruefnachricht,
Attribute
Attribut: klasse
Eigenschaft Wert
Name im XML-Schema klasse
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
String.TextZeileHTML
Erweiterung des Typs xs:string zur Beschreibung von Zeichenketten. Die zusätzlichen Attribute
dienten in früheren Versionen von DatML/RAW zur Dokumentation von Informationen aus OnlineErhebungen. In einem zeilenbasierten Datenmodell kann die Zeilennummer der Information
angegeben werden. Der Name des Formularfeldes, in das die Information eingegeben wurde,
kann mit dem Attribut html-name spezifiziert werden.
String .Te xtZe ile HTML
attribute s
html-name
zeilennummer
Abbildung 3.68. xst:String.TextZeileHTML
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema String.TextZeileHTML
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Erweiterung von xs:string (http://www.w3.org/2001/XMLSchema.xsd)
Verwendet in - xst:Anschrift,
- xst:Anwendung,
- xst:Kontakt,
Basisdatentypen
146
Eigenschaft Wert
- xst:Kontakt.Sequence,
- xst:Material,
- xst:Organisation,
- xst:Person,
Attribute
Attribut: html-name
Eigenschaft Wert
Name im XML-Schema html-name
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Attribut: zeilennummer
Eigenschaft Wert
Name im XML-Schema zeilennummer
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
String.Uhrzeit
Erweiterung des Typs String.Latin zur Beschreibung formatierter Zeichenketten mit einem
speziellen Formatschema für eine Uhrzeitangabe (siehe auch String.Formatiert.
Eine Uhrzeit in Form eines Strings; Formatschema und Formatklasse sind fest vor-gegeben
(2.5.7.1). Wird die Uhrzeit nicht sekunden- oder sogar minutengenau ange-geben, sind die
entsprechenden Felder mit Nullen zu belegen.
String .Uhrze it
attribute s
format
klasse
Abbildung 3.69. xst:String.Uhrzeit
Basisdatentypen
147
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema String.Uhrzeit
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Erweiterung von xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Verwendet in - xst:Datei,
- xst:Dateneingang,
- xst:Dokumentinstanz,
Attribute
Attribut: format
Eigenschaft Wert
Name im XML-Schema format
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default hhmmss (fix)
Attribut: klasse
Eigenschaft Wert
Name im XML-Schema klasse
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default datum (fix)
String.Wert
Erweiterung des Typs String zur Beschreibung von Merkmalswerten.
Die Maßeinheit eines Wertes kann bei Bedarf mit dem Attribut einheit angegeben werden. Das
Attribut faktor bietet die Möglichkeit, einen Wert als n-faches bzw. n-ten Bruchteil der Maßeinheit
anzugeben. Gibt es für die Maßeinheit eine Klassifikation, z. B. eine ISO-Norm, kann diese mit
dem Attribut klasse angegeben werden.
Grundsätzlich ist die Angabe von Maßeinheiten und Faktoren nur in Ausnahmefällen sinnvoll.
Werte sollten bereits in der für die Erhebung festgelegten Maßeinheit geliefert werden. Davon
sollte nur abgewichen werden, wenn dies ausdrücklich erlaubt ist, da dann eine Umrechnung
erfolgen muss; dies wird jedoch in den allermeisten Fällen nicht vorgesehen sein.
Basisdatentypen
148
String .We rt
attribute s
einheit
faktor
klasse
Abbildung 3.70. xst:String.Wert
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema String.Wert
Implementierungshinweis -
Inhaltsmodell komplexer Typ
Elementmodell Sequenz
Erweiterung von xs:string (http://www.w3.org/2001/XMLSchema.xsd)
Verwendet in - xst:Hilfsmerkmal,
- xst:Merkmal.Choice,
- xst:Ordnungsmerkmal.Sequence,
Attribute
Attribut: einheit
Eigenschaft Wert
Name im XML-Schema einheit
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
Attribut: faktor
Eigenschaft Wert
Name im XML-Schema faktor
Beschreibung -
Implementierungshinweis -
Typ xs:positiveInteger (http://www.w3.org/2001/XMLSchema.xsd)
Optional ja
Basisdatentypen
149
Attribut: faktor
Eigenschaft Wert
Default 1
Attribut: klasse
Eigenschaft Wert
Name im XML-Schema klasse
Beschreibung Einschränkung von String.Latin zur Erzeugung eines Datentyps mit
den Eigenschaften von xs:normalizedstring.
Implementierungshinweis -
Typ xst:StringLatin.NormalizedString
Optional ja
Default -
StringLatin.NormalizedString
Einschränkung von String.Latin zur Erzeugung eines Datentyps mit den Eigenschaften von
xs:normalizedstring.
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema StringLatin.NormalizedString
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xoev-dt:String.Latin (http://xoev.de/schemata/
basisdatentypen/1_0//xoev-basisdatentypen.xsd)
Verwendet in - xst:AnforderungEmpfangsbestaetigung,
- xst:Datenattribute,
- xst:Fehler,
- xst:Hilfsmerkmal,
- xst:Merkmal,
- xst:Merkmal.Choice,
- xst:Merkmalsgruppe,
- xst:Ordnungsmerkmal,
- xst:Satz,
- xst:String.Datum,
- xst:String.Formatiert,
- xst:String.TextKlasse,
- xst:String.TextKlasseNoDefault,
- xst:String.TextZeileHTML,
- xst:String.Uhrzeit,
- xst:String.Wert,
- xst:Test,
Zur Ableitung genutzt von - xst:StringLatin.Token,
Einschränkungen
Einschränkungstyp Wert
whiteSpace replace
Basisdatentypen
150
StringLatin.Token
Einschränkung von StringLatin.NormalizedString zur Erzeugung eines Datentyps mit den
Eigenschaften von xs:token.
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema StringLatin.Token
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xst:StringLatin.NormalizedString,
Zur Ableitung genutzt von - xst:Token.FormatEmpfangsbestaetigung,
- xst:Token.Datentraeger,
- xst:Token.Dokumentstatus,
- xst:Token.Version.DatML-RAW-D,
- xst:Token.Version.DatML-RES-D,
- xst:Token.Datenformat,
- xst:Token.Pruefstatus,
- xst:Token.Formatklasse,
- xst:Token.Versandart,
- xst:Token.FormatPosition,
Einschränkungen
Einschränkungstyp Wert
whiteSpace collapse
Token.Datenformat
Hilfstyp zur Einschränkung der für eine Datenlieferung möglichen Datenformate (undefiniert,
datml, xml, datensatz, edifact). Der Wert datml zeigt an, dass eine DatML/RAW-Instanz geliefert
wurde (siehe auch String.Datenformat).
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Token.Datenformat
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xst:StringLatin.Token,
Verwendet in - xst:String.Datenformat,
Einschränkungen
Einschränkungstyp Wert
pattern undefiniert|datml|xml|datensatz|csv|edifact
Token.Datentraeger
Hilfstyp zur Einschränkung der Werte für Datenträger, mit der eine Datenlieferung
erfolgt ist (undefiniert, diskettel, cdrom, dvd, kassette, magnetband) (siehe auch
String.Datentraeger ).
Basisdatentypen
151
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Token.Datentraeger
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xst:StringLatin.Token,
Verwendet in - xst:String.Datentraeger,
Einschränkungen
Einschränkungstyp Wert
pattern undefiniert|diskette|cdrom|dvd|kassette|magnetband
Token.Dokumentstatus
Einschränkung des Typs Token zur Beschreibung des Dokumentenstatus.
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Token.Dokumentstatus
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xst:StringLatin.Token,
Verwendet in - xst:Pruefdokument,
Einschränkungen
Einschränkungstyp Wert
pattern akzeptiert|abgewiesen
Token.FormatEmpfangsbestaetigung
Hilfstyp zur Einschränkung der für eine Empfangsbestaetigung; (siehe auch
AnforderungEmpfangsbestätigung) möglichen Datenformate (default, xml, text).
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Token.FormatEmpfangsbestaetigung
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xst:StringLatin.Token,
Verwendet in - xst:AnforderungEmpfangsbestaetigung,
Einschränkungen
Einschränkungstyp Wert
pattern default|text|xml
Basisdatentypen
152
Token.FormatPosition
Einschränkung des Typs Token zur Beschreibung der verschiedenen Möglichkeiten, um
Fehlerpositionen anzugeben (siehe auch String.Position)
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Token.FormatPosition
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xst:StringLatin.Token,
Verwendet in - xst:String.Position,
Einschränkungen
Einschränkungstyp Wert
pattern xpath|byte|char|satz|name
Token.Formatklasse
Datentyp zur Angabe der Formatklasse (siehe auch String.Formatiert). Formatklasse
datum: Beschreibung eines Einzeldatums oder einer Zeitspanne aus zwei Einzeldaten nach
folgendem Formatschema:
datum[-datum]
datum: j4|[{h|hh}|{q|qq}|{s|ss}|{w|ww}|
monat[tag[std[min[sek]]]]
j4: jjjj, Jahr vierstellig
h: h, Halbjahr i.d.F. hn|Hn|n, n=1..2
hh: hh, Halbjahr i.d.F. nn, nn=01..02
q: q, Quartal i.d.F. qn|Qn|n, n=1..4
qq: qq, Quartal i.d.F. nn, nn=01..04
s: s, Semester i.d.F. sn|Sn|n, n=1..2
(1=Sommersemester, 2=Wintersemester)
ss: ss, Semester i.d.F. nn, nn=01..02
monat: mm, Monat zweistellig
w: w, Woche i.d.F. wnn|Wnn|nn, nn=01..53
ww: ww, Woche i.d.F. nn, nn=01..53
tag: tt, Tag zweistellig
std: hh, Stunde zweistellig
min: mm, Minute zweistellig
sek: ss, Sekunde zweistellig
Hinweise:
• Das Jahr ist stets vierstellig und obligatorisch.
• Auf das Jahr folgt entweder ein Monat, ein Quartal, ein Halbjahr oder eine Woche (von 01-53).
• Die Kennzeichnung eines Halbjahres, eines Semesters, eines Quartals und einer Woche im
Datum (nicht im Format) durch einen Buchstaben ist optional; so kann das erste Halbjahr 2002
wahlweise als 2002H1 und als 20021 angegeben werden.
Basisdatentypen
153
• Ein Tag darf nur auf einen Monat folgen.
• Eine Uhrzeit darf nur auf einen Tag folgen.
Formatschema Werte Bedeutung
jjjjmm 200205 Jahr und Monat
jjjj-jjjj 2001-2002 Jahresspanne
jjjjq 2002Q2, 20022 Jahr und zweites Quartal
jjjjqq 200202 Jahr und zweites Quartal
jjjjh 2002H1, 20021 Jahr und erstes Halbjahr
jjjjhh 200201 Jahr und erstes Halbjahr
jjjjs 20021, 2002S1 Jahr und Sommersemester
jjjjss 200202 Jahr und Wintersemester
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Token.Formatklasse
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xst:StringLatin.Token,
Verwendet in - xst:String.Formatiert,
Einschränkungen
Einschränkungstyp Wert
pattern undefiniert|datum
Token.Pruefstatus
Einschränkung des Basistyps Token zur Beschreibung der verschiedenen Prüfzustände. Dieser
Typ findet auf verschiedenen Ebenen des Prüfprotokolls Anwendung.
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Token.Pruefstatus
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xst:StringLatin.Token,
Verwendet in - xst:Pruefdokument,
- xst:Pruefmeldung,
- xst:Pruefnachricht,
- xst:Pruefstatus,
Einschränkungen
Einschränkungstyp Wert
pattern ungeprueft|fehlerfrei|fehlerhaft
Basisdatentypen
154
Token.Versandart
Hilfstyp zur Einschränkung der für eine Empfangsbestätigung möglichen Versandart (default,
email, post, download) (siehe auch AnforderungEmpfangsbestätigung).
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Token.Versandart
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xst:StringLatin.Token,
Verwendet in - xst:AnforderungEmpfangsbestaetigung,
Einschränkungen
Einschränkungstyp Wert
pattern default|email|post|download
Token.Version.DatML-RAW-D
Hilfstyp zur Einschränkung der für eine Nachricht vom Typ DatML-RAW-D gültigen
Versionsnummer. Derzeit ist ausschließlich die Version 2.0 gültig.
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Token.Version.DatML-RAW-D
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xst:StringLatin.Token,
Verwendet in - xst:DatML-RAW-D (globales Element),
Einschränkungen
Einschränkungstyp Wert
pattern 2.0
Token.Version.DatML-RES-D
Hilfstyp zur Einschränkung der für eine Nachricht vom Typ DatML-RES-D gültigen
Versionsnummer. Derzeit ist ausschließlich die Version 1.0 gültig.
Allgemeine Eigenschaften
Eigenschaft Wert
Name im XML-Schema Token.Version.DatML-RES-D
Implementierungshinweis -
Inhaltsmodell einfacher Typ
Abgeleitet von xst:StringLatin.Token,
Verwendet in - xst:DatML-RES-D (globales Element),
Basisdatentypen
155
Einschränkungen
Einschränkungstyp Wert
pattern 1.0
156