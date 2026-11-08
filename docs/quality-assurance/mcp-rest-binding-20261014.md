---
title: MCP-Lesevertraege gegen produktive REST-Schemas
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-14
---

# P0: Echte REST-Parameterbindung

Das neue Gate scripts/check_mcp_rest_bindings.py erzeugt standardmaessig die OpenAPI der produktiven main-App und prueft die elf GET-/HEAD-Bindungen des Process-Kernel-Katalogs. Es verlangt vorhandene Operation und Operation-ID, bekannte Parameter, vollstaendige Pflichtparameter, kompatible Typen/Enums und nicht schwaechere numerische Grenzen. --spec erlaubt eine ausdrueckliche Offline-Spec; CI verwendet den Live-Generator. Das Gate schreibt keine OpenAPI-Datei und bewahrt fremde alte Arbeitskopien. Es laeuft im bestehenden OpenAPI-Drift-Workflow mit dessen vorhandener Datenbank.

Settlement-Filter verwenden nun campaign_id/supplier_id und die echten Statuswerte; Kampagnenvorlagen haben keinen Typfilter. AP-Listen verwenden supplier_id/query/skip/limit; offene Posten die REST-Konten-/Status-/Suchfilter mit begrenztem limit. Das historisch instance_status benannte Werkzeug beschreibt nun korrekt Workflow-Definitionsversionen und deren Filter: der vorhandene REST-Weg liefert keinen Instanzstatus. Seine drei Brokerverwendungen fuer Ausnahme-/Liefer-/Freigabekontext brauchen weiterhin einen eigenen fachlichen Ersatz; Definitionslisten sind kein Nachweis dieser Sachverhalte. Die Neuro-Ausfuehrung sperrt deshalb dieses irrefuehrende Werkzeug vor HTTP mit workflow_instance_contract_not_implemented. Ein zusaetzlicher Transport-Negativtest sichert das ab.

Qualitaetsprotokollfreigabe und Mahnlauf veraendern Geschaeftsdaten. Ihre bisherigen Kategorien VALIDIEREN/BERECHNEN wurden auf SCHREIBEN mit Freigabehinweis korrigiert. Die bestehende Neuro-Ausfuehrung lehnt sie damit vor Transport als write_capability_not_approved ab. Dies schaltet keine andere Domain-API ab und erteilt keine neuen Rechte. Die sieben veraenderten Vertraege tragen schema_version 2; der unveraenderte Registry-Umschlag bleibt Version 1.

Abnahme: vierzehn neue Faelle pruefen positive Bindung, fehlenden Pfad/Operation-ID, unbekannte/fehlende/falsch typisierte Parameter, schwaechere Grenzen, Enumverlust, Dubletten und nullable Schema-Referenzen sowie die beiden Write-Sperren. Gegen die eingecheckte Produktions-OpenAPI bestehen elf Bindungen. Auch der frisch erzeugte Produktions-OpenAPI-Abgleich besteht mit elf Bindungen; der Generator meldet vorbestehende doppelte Operation-IDs ausserhalb dieses Slices. 127 bestehende Agentenmanifest-/MCP-/Ausfuehrungs-/Brokerfaelle und 14 neue Gate-/Sperr-/Versionsfaelle bestanden. Die lokalen HTTP-Regressionen liefen ausserhalb der Sandbox; die neuen reinen Vertragsfaelle benoetigen keine DB.

Liefergrenze: Dieses Gate beweist REST-Leseparameterkompatibilitaet, keine gleiche Fachsemantik oder vollstaendige Rechte-/POST-/CLI-Gleichwertigkeit. Offene P0-Arbeit: ERP-Katalog und POST-Transformationen, kanonische freigegebene Capability-Version und Artefaktsnapshots. P1: Historienanzeige, Prozesssimulation und technische STUDIO-RELEASE-001-Sperre. Keine neue Datenbank, kein Reset, keine Migration.
