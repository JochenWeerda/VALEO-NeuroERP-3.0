# MCP-Abfrageimport: manipulierte Signatur

Zwei isolierte Tests pruefen dryRun und execute mit echter HMAC-Signaturpruefung des QueryCenterService. Ein korrekt signiertes synthetisches Paket wird nachtraeglich veraendert. Der MCP-Command antwortet mit 422, ruft Import, Audit und Replay-Speicherung nicht auf, committet nicht und rollt zurueck. Kein Datenbankzugriff, keine produktiven Schluessel. Zwei Tests bestanden. Dies ist kein HTTP-/Rollen- oder PostgreSQL-Nachweis; die echte Signaturpruefung und der Adapterfehlerpfad werden abgedeckt.
