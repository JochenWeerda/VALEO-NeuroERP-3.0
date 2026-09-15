import type { ScreenFloorplan } from './schema'

/** One vocabulary for page purpose; navigation columns are an independent axis. */
export const FLOORPLAN_RULES: Record<ScreenFloorplan, { label: string; purpose: string; allowsColumns: boolean }> = {
  worklist: { label: 'Arbeitsliste', purpose: 'Suchen, filtern, auswählen und bearbeiten', allowsColumns: true },
  objectPage: { label: 'Objektseite', purpose: 'Objekt und zugehörige Unterobjekte bearbeiten', allowsColumns: true },
  transaction: { label: 'Transaktion', purpose: 'Einen fachlichen Vorgang prüfen und ausdrücklich abschließen', allowsColumns: false },
  cockpit: { label: 'Cockpit', purpose: 'Überblick, Ausnahmen und nächste Schritte', allowsColumns: false },
  wizard: { label: 'Assistent', purpose: 'Geführte Schritte mit Abschlussprüfung', allowsColumns: false },
  analyticalList: { label: 'Analytische Liste', purpose: 'Kennzahlen und dazugehörige Datensätze gemeinsam untersuchen', allowsColumns: true },
}

export const FLOORPLAN_IDS = Object.keys(FLOORPLAN_RULES) as ScreenFloorplan[]
