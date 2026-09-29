import type { ScreenColumnNavigation, ScreenFloorplan, ScreenSectionNavigation } from './schema'

interface FloorplanRule {
  label: string
  purpose: string
  allowsColumns: boolean
  /** Belegseiten duerfen ihre Register als durchgehende Seite mit Sprungmarken zeigen. */
  allowsSectionAnchors: boolean
}

/** One vocabulary for page purpose; navigation columns are an independent axis. */
export const FLOORPLAN_RULES: Record<ScreenFloorplan, FloorplanRule> = {
  worklist: { label: 'Arbeitsliste', purpose: 'Suchen, filtern, auswählen und bearbeiten', allowsColumns: true, allowsSectionAnchors: false },
  objectPage: { label: 'Objektseite', purpose: 'Objekt und zugehörige Unterobjekte bearbeiten', allowsColumns: true, allowsSectionAnchors: true },
  transaction: { label: 'Transaktion', purpose: 'Einen fachlichen Vorgang prüfen und ausdrücklich abschließen', allowsColumns: false, allowsSectionAnchors: true },
  cockpit: { label: 'Cockpit', purpose: 'Überblick, Ausnahmen und nächste Schritte', allowsColumns: false, allowsSectionAnchors: false },
  wizard: { label: 'Assistent', purpose: 'Geführte Schritte mit Abschlussprüfung', allowsColumns: false, allowsSectionAnchors: false },
  analyticalList: { label: 'Analytische Liste', purpose: 'Kennzahlen und dazugehörige Datensätze gemeinsam untersuchen', allowsColumns: true, allowsSectionAnchors: false },
}

export const FLOORPLAN_IDS = Object.keys(FLOORPLAN_RULES) as ScreenFloorplan[]

const LIST_FLOORPLANS = new Set<ScreenFloorplan>(['worklist', 'analyticalList'])

/** Dense booking screens stay full width. List floors with tables open listDetail unless declared. */
export function defaultColumnNavigation(
  floorplan: ScreenFloorplan,
  hasTables: boolean,
  declared?: ScreenColumnNavigation,
): ScreenColumnNavigation {
  if (!FLOORPLAN_RULES[floorplan].allowsColumns) return 'single'
  if (declared) return declared
  if (LIST_FLOORPLANS.has(floorplan) && hasTables) return 'listDetail'
  return 'single'
}

/** Anchors only where the floorplan allows it and no column split competes for the page. */
export function resolveSectionNavigation(
  floorplan: ScreenFloorplan,
  columnNavigation: ScreenColumnNavigation,
  declared?: ScreenSectionNavigation,
): ScreenSectionNavigation {
  if (declared !== 'anchors') return 'tabs'
  if (!FLOORPLAN_RULES[floorplan].allowsSectionAnchors || columnNavigation !== 'single') return 'tabs'
  return 'anchors'
}
