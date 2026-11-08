---
title: Kanonischer DQ-Objektvertrag fuer REST und MCP
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-14
---

# Datenqualitaet am ausdruecklichen Fachobjekt

Der Process-Kernel-DQ-Command verlangt jetzt entity_typ und datensatz als echtes Objekt sowie optional kontext_datensaetze. Der bisher deklarierte datensatz_json-Text wurde vom Adapter nie geparst: Stattdessen wurde die ganze Parameterhuelle geprueft. Dieses konkurrierende Eingabeformat ist entfernt. Fehlende Objekte und Zusatzfelder werden abgewiesen; Fachobjektwerte bleiben unveraendert.

REST und das MCP-Werkzeug Version 2 verwenden denselben DataQualityCheckIn-Validator. Bestehende Grenzen bleiben zentral erhalten: 50 Felder, 1000 Zeichen je direktem Stringwert, maximal 100 Vergleichsobjekte. FastAPI entfernt null-Default-Annotationen in OpenAPI; das gemeinsame Modell exportiert diese optionale-null-Darstellung auch fuer MCP, ohne den Gatevergleich anderer Defaults zu schwaechen. Die fachlichen DQ-Regeln bleiben im bestehenden Regelsetregister, kein zweites Rechtesystem und kein Schreibrecht.

Der interne Broker verpackt seine flachen Planattribute ausdruecklich als Fachobjekt. Supplier/customer/article/invoice werden auf die echten Regelsetnamen Lieferant/Debitor/Artikel/APRechnung abgebildet; vorherige KREDITOR/ARTIKEL-Namen trafen keine vorhandenen Regelsets. Bereits kanonische Planrequests werden weitergereicht. Fehlender Entitaetstyp bekommt keine erfundene Artikelvorgabe. Der Transport validiert vor HTTP und meldet sanitisiertes 422 ohne Eingabewerte; fremde Mandantenselektoren im Fachobjekt bleiben vor HTTP gesperrt.

127 bestehende MCP-/HTTP-/Broker-/Manifestfaelle bestanden, anschliessend 44 gezielte DQ-/Migrations-/Gatefaelle. Neue Faelle pruefen echte Objektweitergabe an den DQ-Pruefer, Objekt-/Feld-/Vergleichsgrenzen, fehlerhafte JSON-Text-Huellen, Schema-Drift, reale Regelsetnamen und fremde Selektoren. Isolierte Transport-Negativtests ersetzen die vorgelagerte JWT-Pruefung ausdruecklich und sind kein neuer Provider-Nachweis. Keine Datenbank oder Migration erforderlich.

OpenAPI wird nur fuer DQ-Eingabe/Beschreibung und die neue Komponente auf HEAD projiziert; fremde Arbeitskopien bleiben unangetastet. Das bestehende CI-Gate prueft nun elf GET-Bindungen und zwei kanonische POST-Eingaben. Andere POST-/Berechtigungs-/CLI-Vertraege, freigegebene Capability-Version und Artefaktsnapshots bleiben offen; ebenso Studio-Historienanzeige, vollstaendige Prozesssimulation und Release-Sperre. Keine Produktionsfreigabe aus einem DQ-Ergebnis ableiten.
