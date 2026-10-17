# Eine Studio-Belegmaske mit versionierten Standardvarianten

Stand: 17.10.2026. Verbindliches Ziel des Auftraggebers: eine gemeinsame Maskenfamilie, keine getrennten Maskenimplementierungen je Belegfall. Die aktuelle kanonische Familie hat neun Varianten; die rund 14 bisherigen Einstiege sind keine 14 eigenstaendigen Fachmodelle.

## Kanonische Varianten

| Richtung | Variante | Fachfall |
|---|---|---|
| ausgehend | sales_offer | Verkaufsangebot |
| ausgehend | sales_order | Verkaufsauftrag |
| ausgehend | sales_delivery | Verkaufslieferschein |
| ausgehend | sales_invoice | Ausgangsrechnung |
| ausgehend | sales_credit_memo | Verkaufsgutschrift |
| eingehend | purchase_order | Bestellung beim Lieferanten |
| eingehend | goods_receipt | Wareneingang / Einkaufslieferschein |
| eingehend | purchase_invoice | Eingangsrechnung |
| eingehend | purchase_credit_memo | Einkaufsgutschrift |

Bestellung und Verkaufsauftrag sind hier nach ihrem Einkaufs-/Verkaufsbereich eingeordnet; die Richtung ist keine Aussage ueber den technischen E-Mail-Eingang. Weitere echte Fachfaelle werden als registrierte, versionierte Variante derselben Familie hinzugefuegt, sobald Datenvertrag und Fachwirkung nachgewiesen sind. Eine Belastung wird nicht allein wegen eines aehnlichen Layouts als Gutschrift behandelt.

## Zuordnung der bisherigen Einstiege

| Bisheriger Einstieg | Zielvariante | Abloesebedingung |
|---|---|---|
| sales/angebot-erstellen | sales_offer | Kopf, Positionen, Sonderfelder und Folgeauftrag abnehmen |
| sales/order-editor, neu | sales_order | Anlage und alle Auftragsfelder abnehmen |
| sales/order-editor, vorhanden | sales_order | Bestehende Fachdaten und Belegkette erhalten |
| verkauf/lieferschein-erfassung | sales_delivery | Lager-/Lieferdaten, Mengenrechte und Kette abnehmen |
| sales/invoice-editor | sales_invoice | Anlage, Bearbeitung, Steuer und Kontierung abnehmen |
| verkauf/rechnung | sales_invoice | Anzeige, Druck, Freigabe und Buchungsnachweis abnehmen |
| sales/credit-note-editor | sales_credit_memo | Gutschrift, OP-Wirkung und zulaessige Korrektur abnehmen |
| einkauf/bestellungen/neu | purchase_order | Anlage und Bestellsonderfelder abnehmen |
| einkauf/bestellung-stamm | purchase_order | Bestehende Bestellungen und Teilmengen erhalten |
| einkauf/lieferschein-erfassung | goods_receipt | Lager-/Chargen-/Mengenwirkung abnehmen |
| einkauf/rechnung-eingang-erfassung | purchase_invoice | Steuer, Kontierung, Freigabe und Journal abnehmen |
| einkauf/gutschriften-belastungen | purchase_credit_memo fuer echte Gutschriften | Belastungen bleiben ein eigener offener Fachfall |
| finance/invoice-form | sales_invoice fuer Waren-/Leistungsrechnungen | Reine Finanzrechnung gesondert fachlich klassifizieren |
| finance/ap-invoice-form / finance/ap-invoice | purchase_invoice fuer Waren-/Leistungsrechnungen | Reine Finanzrechnung gesondert fachlich klassifizieren |

Diese Matrix beschreibt den Zielweg, keine bereits erfolgte Umleitung oder Datenmigration. Alte Wege werden erst nach nachgewiesener Funktionsparitaet entfernt.

## Gemeinsame Implementierung und Fassung

Fuehrend ist screen_definitions_beleg.py: ein Builder, ein Register mit unveraenderlichen Basis-/Variantenfassungen, eine zentrale Renderkette. Version 1.1.0 ergaenzt die Bearbeitungsaktion fuer bestehende Entwuerfe in allen neun Varianten. Historische 1.0.0-Fassungen bleiben unveraendert aufloesbar. Studio kann die registrierte Ausgangsfassung uebernehmen; das ersetzt keine Freigabe eines veraenderten Studio-Entwurfs.

Bearbeitung laedt den vollstaendigen kanonischen DocFlow-Beleg, nicht die erste Seite des Positionsregisters. Version, Identitaet, Belegart und Status werden vor dem Dialog geprueft. Wiederholungsschutz und Transaktion liegen im vorhandenen Domain-Command. Sichtbare Spalten folgen der Variante; bestehende nicht angezeigte Positionsangaben bleiben im Eingabekontext erhalten. Gesperrte Belege und schreibende Agenten werden dadurch nicht freigeschaltet.

## Noch erforderliche Paritaet

Die neue Entwurfsbearbeitung ist kein Nachweis vollstaendiger Kopf-/Sonderfeldparitaet. Partnerauswahl, Neuanlage, Liefer-/Zahlungs-/Kontraktbausteine, gezielte Aenderung verknuepfter Positionen, Mengenbearbeitung ohne Preisleserecht, unabhaengige Variantenfreigaben, reale Fachkettenprofile und Browserabnahme jedes abgeloesten Einstiegs bleiben gesonderte Abnahmen. Insbesondere darf ein Vollersatz keine vorhandenen Positionsverknuepfungen beseitigen. Bis zur jeweiligen Abnahme bleiben die bisherigen Fachwege erhalten.
