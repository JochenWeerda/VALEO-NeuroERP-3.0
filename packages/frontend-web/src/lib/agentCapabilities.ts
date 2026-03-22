/**
 * Agent Capability Registry — Frontend
 * Maps domain processes to NeuroASSIST capabilities.
 * Single source of truth for which agents handle which workflows.
 */

export type AgentCapabilityDef = {
  capability_key: string
  title: string
  domain: string
  description: string
  /** Which form fields this agent can provide suggestions for */
  suggestFields: string[]
  /** Readiness level for display/filtering */
  readiness: 'productive' | 'assisted' | 'prototype'
}

export const AGENT_CAPABILITIES: AgentCapabilityDef[] = [
  {
    capability_key: 'bestellvorschlag_assistant',
    title: 'Bestellvorschlag',
    domain: 'einkauf',
    description: 'Erzeugt Bestellvorschläge basierend auf Lagerbestand und Verkaufsplanung.',
    suggestFields: ['artikel', 'menge', 'lieferant'],
    readiness: 'productive',
  },
  {
    capability_key: 'rohware_annahme_assistant',
    title: 'Rohware-Annahme',
    domain: 'annahme',
    description: 'Schlägt Artikel und Lagerziel basierend auf Lieferant- und Fahrzeughistorie vor.',
    suggestFields: ['artikel', 'lagerZiel'],
    readiness: 'assisted',
  },
  {
    capability_key: 'auslagerung_assistant',
    title: 'Auslagerung',
    domain: 'lager',
    description: 'Empfiehlt Auslagerungsstrategie und Charge basierend auf FIFO/FEFO-Regeln.',
    suggestFields: ['strategie', 'chargenId'],
    readiness: 'assisted',
  },
  {
    capability_key: 'einlagerung_assistant',
    title: 'Einlagerung',
    domain: 'lager',
    description: 'Empfiehlt optimalen Lagerort basierend auf Artikel, Menge und Belegungsgrad.',
    suggestFields: ['lagerort'],
    readiness: 'assisted',
  },
  {
    capability_key: 'skonto_optimizer',
    title: 'Skonto-Optimierung',
    domain: 'finanzen',
    description: 'Analysiert offene Posten und empfiehlt Zahlungen mit maximalem Skontonutzen.',
    suggestFields: ['zahlungsbetrag', 'valutatag'],
    readiness: 'productive',
  },
  {
    capability_key: 'compliance_copilot',
    title: 'Compliance-Copilot',
    domain: 'compliance',
    description: 'Führt proaktive Compliance-Checks durch und identifiziert Abweichungen.',
    suggestFields: [],
    readiness: 'productive',
  },
  {
    capability_key: 'data_quality_assistant',
    title: 'Datenqualitäts-Assistent',
    domain: 'stammdaten',
    description: 'Erkennt Anomalien und Dubletten in Stammdaten und schlägt Korrekturen vor.',
    suggestFields: [],
    readiness: 'assisted',
  },
  {
    capability_key: 'operations_exception_assistant',
    title: 'Ausnahme-Assistent',
    domain: 'operations',
    description: 'Erkennt Ausnahmesituationen im Tagesgeschäft und schlägt Eskalationspfade vor.',
    suggestFields: [],
    readiness: 'assisted',
  },
]

export function getCapabilitiesForDomain(domain: string): AgentCapabilityDef[] {
  return AGENT_CAPABILITIES.filter((c) => c.domain === domain)
}

export function getCapabilityByKey(key: string): AgentCapabilityDef | undefined {
  return AGENT_CAPABILITIES.find((c) => c.capability_key === key)
}

export function getProductiveCapabilities(): AgentCapabilityDef[] {
  return AGENT_CAPABILITIES.filter((c) => c.readiness === 'productive')
}
