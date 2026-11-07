# MCP-Zeilencommands: unabhaengige Freigabepruefung

Der laufende Arbeitsstand ist noch nicht abgenommen. Zwei konkrete Sicherheitsbefunde muessen vor Freigabe geschlossen werden:

1. Der generische Maskenadapter muss unbekannte Schreibendpunkte standardmaessig ablehnen. Das globale masks:write und Rollen am Ziel ersetzen keine ausdrueckliche Capability-Freigabe. Registrierung, Endpunkt, Domain-Command und Version muessen eindeutig sein; unvollstaendige, doppelte oder deaktivierte Eintraege duerfen nicht freigeben.
2. Die Capability-Rollenpruefung muss am authentifizierten MCP-Dispatch vor jeder Weiterleitung greifen, auch wenn das weitergereichte Token eine menschliche Identitaet besitzt. Ein frei gesetzter Kanalheader ist kein vertrauenswuerdiger Nachweis. Direkte menschliche REST-Bedienung behaelt ihre bestehende Fachrollenpruefung; deklarierte Agenten werden zusaetzlich im Domain-Command kontrolliert.

Erforderliche Negativnachweise: unbekanntes Ziel, doppelte Registrierung, falsche Version, deaktivierte Freigabe, fehlende spezifische Rolle trotz globalem Scope und menschlichem Token. Jeder dieser Faelle muss vor HTTP-Weiterleitung abgewiesen werden. Lesende readView-Aktionen bleiben getrennt; widerspruechliche Schreib-/Lesedeklarationen sind bereits bei Definition/Validierung abzuweisen.

Dieser Bericht dokumentiert Reviewanforderungen und ist kein bestandener Ausfuehrungsnachweis. Der verantwortliche Slice ist MCP-ROW-COMMANDS-20261107; Implementierung und Tests laufen dort weiter.
