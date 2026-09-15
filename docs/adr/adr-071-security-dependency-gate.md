---
title: ADR-071 Security-Dependency-Gate statt automatischer Major-Upgrades
type: adr
audience: [architektur, entwickler, qa, sicherheit]
owner: architecture
status: accepted
last_reviewed: 2026-09-15
version: 1.0.0
---

# ADR-071 Security-Dependency-Gate statt automatischer Major-Upgrades

**Status:** Accepted

**Datum:** 2026-09-15

## Kontext

VALEO NeuroERP ist ein Microservice-/DDD-System mit vielen unabhängigen
Python- und Node-Manifesten. Scanner (Dependabot, pip-audit, npm-audit,
Grype, Trivy) liefern Rohbefunde. Ein ungefiltertes „immer auf die
Advisory-Fixversion heben“ zerstört funktionierende Dienste: Major-Sprünge
brechen APIs, und ein Paket-Fix kann ein anderes Manifest unauflösbar
machen. Lehrfall 2026-09-14: `transformers>=4.47` zieht `tokenizers>=0.22`,
`chromadb==0.5.23` verlangt `tokenizers<=0.20.3`. Die Advisory-Fixversion
4.57.6 ist deshalb kein zulässiger Automatik-Schritt.

GitHub dokumentiert Dependabot-Auto-Merge über Actions als optionales
Muster, nicht als Pflicht
([Automating Dependabot with GitHub Actions](https://docs.github.com/en/code-security/tutorials/secure-your-dependencies/automate-dependabot-with-actions)).
Für dieses ERP ist Auto-Merge unzulässig.

## Entscheidung

1. **Release-Invariante.** Keine bekannte, praktisch ausnutzbare kritische
   Schwachstelle darf unbehandelt in ein Release. „Unbehandelt“ heißt:
   weder Herstellerfix eingespielt noch dokumentierte, nachprüfbare
   Beherrschung (nicht erreichbar / nicht betroffen) mit Evidenz und
   Wiedervorlage.
2. **Alte Pins sind zulässig**, wenn das Risiko analysiert und beherrscht
   ist. Ein Scanner-Treffer ohne erreichbaren Angriffsweg ist kein
   automatischer Upgrade-Auftrag.
3. **Dependabot ist Sensor und PR-Erzeuger**, kein Merge-Bot. Es gibt
   keinen Workflow, der Dependabot-PRs per `gh pr merge --auto` oder
   Repository-Automerge übernimmt. Version-Update-PRs dürfen begrenzt oder
   unterdrückt werden; Security-Advisories und Alerts bleiben sichtbar.
4. **Vor jedem Release sitzt ein eigener Security-Dependency-Gate-Agent**
   zwischen Scanner und Merge. Der Gate ändert keine Dependencies und
   merget keine PRs. Er bewertet Rohbefunde gegen eine versionsscharfe
   Entscheidungsliste. Unbekannte, abgelaufene oder evidenzgeänderte
   Bewertungen blockieren. Pauschale Severity-Ausnahmen sind verboten.
5. **Major- und API-brechende Upgrades** erfolgen nur mit reproduzierbarem
   Nachweis (Resolver, Tests, betroffene Dienste), nie weil ein Advisory
   eine höhere Version nennt.

Die technische Umsetzung liegt im abgeschlossenen Slice
`SECURITY-DEPENDENCY-POLICY-20260915` (Codex):
`scripts/security_dependency_gate.py`,
`config/security/dependency-decisions.json`,
`.github/dependabot.yml` (`open-pull-requests-limit: 0` für pip/npm,
kein Auto-Merge). Bestehende Service-Pins bleiben im Dateibesitz der
Manifest-Slices. Operativer Nachweis:
[Policy-QA](../quality-assurance/security-dependency-policy-2026-09-15.md).

## Konsequenzen

Positiv:

- Releases orientieren sich an ausnutzbarem Risiko, nicht an Scanner-Zählern.
- Funktionierende Pins überleben, wenn der Angriffsweg nachweislich fehlt.
- Dependabot bleibt Frühwarnung, ohne das ERP durch Major-Bumps zu zerlegen.

Negativ:

- Jede Beherrschung braucht Evidenz, Owner und Wiedervorlage; das ist
  mehr Aufwand als Auto-Merge.
- Scanner-Jobs dürfen rot bleiben, während das Release-Gate nach
  dokumentierter Bewertung grün wird. Beide Signale müssen getrennt lesbar
  sein.
- Unbewertete Befunde (zum Beispiel transformers auf 4.46.3) bleiben
  blockierend, bis eine Entscheidung vorliegt.

## Referenzen

- [Ist-Stand 2026-09-15](../quality-assurance/security-dependency-status-2026-09-15.md)
- [Service-Security-Gates](../quality-assurance/service-security-gates-2026-09-14.md)
- [ADR-019 Sicherheitsmodell für externe Agenten](adr-019-sicherheitsmodell-externe-agenten-delegierte-aktionen.md)
- [GitHub: Dependabot mit Actions automatisieren](https://docs.github.com/en/code-security/tutorials/secure-your-dependencies/automate-dependabot-with-actions)
- Workboard: `SECURITY-DEPENDENCY-POLICY-20260915`
