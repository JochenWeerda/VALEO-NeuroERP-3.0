# Spuelcharge als physische Umlagerung

Nutzerentscheid 22.10.2026: Spuelmenge von der Quelle abbuchen und dem Ziel zubuchen. Kein reiner Reinigungsnachweis ohne Bestandswirkung.

Kanonischer Dienst delegiert in einen kleinen SQL-Helfer. Beide aktiven Zellen werden im angeforderten Lager/Mandanten in stabiler Reihenfolge gesperrt. Endliche positive Menge, verschiedener Ursprung/Ziel, Mandantenmaterial, freie Zellen, vorhandenes Material, Quellbestand und Zielkapazitaet werden geprueft. Zwei Bewegungen mit erlaubtem Eigentumstyp owned sowie vorherigem/neuem Bestand und beide Zellbestaende werden gemeinsam geschrieben. Eine vollstaendige gerichtete Route ist erforderlich; nur deren Kanten werden als gespuelt markiert. Eingebettete Routenpruefung darf nicht vorzeitig committen. Fehler rollen die Buchung zurueck.

Elf echte SQL-Faelle auf dem vorhandenen valeo_probe:100/20kg werden70/50kg, beide vollstaendigen Bewegungen, keine Aenderung einer abzweigenden Kante; Ueberziehung, Kapazitaet, Lager, Mandant, identische Zelle, NaN, fehlendes Material und gesperrte Zelle; Rueckrollen bei spaetem Auditfehler und bei aktiver Routenprotokollierung. Ausschliesslich eigene synthetische Daten in rueckgerollter Aussentransaktion. Kein Reset/Migration/Container. Der alte Mock erlaubte200kg Abgang aus einer leeren Quelle; er wurde durch diese staerkere SQL-Abnahme ersetzt. Gemeinsam mit bestehenden Materialfluss- und Coverage-Vertraegen40 bestanden.

Offen bleiben separate Transfer-/Lot-Link-SQL-Snapshots, dauerhafte Wiederholungssicherung, Herkunft/Chargen-/Fremdeigentumsbehandlung und die bisherige allgemeine best-effort/asynchrone Outbox. Diese Abnahme behauptet keine vollstaendige transaktionale Zustellgarantie oder Gesamt-WMS-Freigabe. Kein Browser-/PLC-Nachweis.
