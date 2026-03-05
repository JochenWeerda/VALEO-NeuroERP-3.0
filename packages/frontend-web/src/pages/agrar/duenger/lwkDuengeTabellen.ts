/**
 * LWK-Hinweisdienste: Tab. 1/2 Wintergetreide/Raps, Tab. 3a/3b Grünland.
 * Bezirksstelle Ostfriesland/Oldenburg-Nord (Nr. 2/18.02.2026, Nr. 05/03.03.2026).
 */

/** Tab. 1 Marsch – 1. N-Gabe (kg N/ha). Jahres-N darf Düngebedarfsermittlung nicht überschreiten. */
export type Bestandstyp = 'normal' | 'ueppig' | 'duenn'

export const TAB1_MARSCH: Record<string, { min: number; max: number }> = {
  weizen_normal: { min: 100, max: 120 },
  weizen_ueppig: { min: 80, max: 100 },
  weizen_raps_duenn: { min: 120, max: 140 },
  raps_normal: { min: 100, max: 120 },
}

/** Tab. 2 Geest – 1. N-Gabe (kg N/ha). */
export const TAB2_GEEST: Record<string, { min: number; max: number }> = {
  getreide_normal: { min: 60, max: 80 },
  getreide_ueppig: { min: 50, max: 60 },
  raps: { min: 100, max: 100 },
}

/** Wintergerste: 20 kg unter Getreide (Tab. 1). */
export const WINTERGERSTE_OFFSET_KG = 20

/** Schwefel: Raps 30–40 kg S/ha; Getreide Marsch 15–20 kg S/ha bei schwachen Beständen/leichten Böden. */
export const SCHWEFEL_RAPS_KG_HA = { min: 30, max: 40 }
export const SCHWEFEL_GETREIDE_MARSCH_KG_HA = { min: 15, max: 20 }

// --- Grünland Tab. 3a (ohne Vorjahres-org. Düngung): N-Düngebedarf + N-Gaben pro Aufwuchs (1.–6.) ---
export type GruenlandNutzung =
  | 'standweide_extensiv'
  | 'intensiv_vollweide_leg'
  | 'intensiv_vollweide_ohne'
  | 'maehweide_80'
  | 'maehweide_60'
  | 'maehweide_40'
  | 'maehweide_20'
  | 'schnitt_3'
  | 'schnitt_4'
  | 'schnitt_5'
  | 'schnitt_6'

export type StandortTyp = 'mineral' | 'hochmoor' | 'niedermoor'

export type GruenlandZeile = {
  nBedarfPflanze: number
  nDuengebedarf: number
  gaben: number[] // 1.–6. Aufwuchs, kg N/ha
}

/** Tab. 3a Mineralboden (0–8 % Humus; bei >8 % Humus −20 kg N-Düngebedarf). */
export const TAB3A_MINERAL: Record<GruenlandNutzung, GruenlandZeile> = {
  standweide_extensiv: { nBedarfPflanze: 65, nDuengebedarf: 55, gaben: [15, 0, 0, 0, 0, 0] },
  intensiv_vollweide_leg: { nBedarfPflanze: 110, nDuengebedarf: 100, gaben: [60, 30, 30, 0, 0, 0] },
  intensiv_vollweide_ohne: { nBedarfPflanze: 130, nDuengebedarf: 120, gaben: [80, 50, 30, 0, 0, 0] },
  maehweide_80: { nBedarfPflanze: 150, nDuengebedarf: 140, gaben: [100, 70, 30, 0, 0, 0] },
  maehweide_60: { nBedarfPflanze: 190, nDuengebedarf: 180, gaben: [140, 70, 40, 30, 0, 0] },
  maehweide_40: { nBedarfPflanze: 220, nDuengebedarf: 210, gaben: [170, 100, 40, 30, 0, 0] },
  maehweide_20: { nBedarfPflanze: 245, nDuengebedarf: 235, gaben: [195, 100, 60, 35, 0, 0] },
  schnitt_3: { nBedarfPflanze: 190, nDuengebedarf: 180, gaben: [140, 70, 40, 30, 0, 0] },
  schnitt_4: { nBedarfPflanze: 245, nDuengebedarf: 235, gaben: [195, 100, 60, 35, 0, 0] },
  schnitt_5: { nBedarfPflanze: 310, nDuengebedarf: 300, gaben: [260, 100, 60, 50, 50, 0] },
  schnitt_6: { nBedarfPflanze: 350, nDuengebedarf: 340, gaben: [260, 100, 80, 80, 50, 30] },
}

/** Tab. 3a Hochmoor (Mindestabzug 50 kg N/ha). */
export const TAB3A_HOCHMOOR: Record<GruenlandNutzung, GruenlandZeile> = {
  standweide_extensiv: { nBedarfPflanze: 65, nDuengebedarf: 65, gaben: [0, 0, 0, 0, 0, 0] },
  intensiv_vollweide_leg: { nBedarfPflanze: 110, nDuengebedarf: 110, gaben: [30, 30, 0, 0, 0, 0] },
  intensiv_vollweide_ohne: { nBedarfPflanze: 130, nDuengebedarf: 130, gaben: [50, 50, 0, 0, 0, 0] },
  maehweide_80: { nBedarfPflanze: 150, nDuengebedarf: 150, gaben: [70, 70, 0, 0, 0, 0] },
  maehweide_60: { nBedarfPflanze: 190, nDuengebedarf: 190, gaben: [110, 70, 40, 0, 0, 0] },
  maehweide_40: { nBedarfPflanze: 220, nDuengebedarf: 220, gaben: [140, 70, 40, 30, 0, 0] },
  maehweide_20: { nBedarfPflanze: 245, nDuengebedarf: 245, gaben: [165, 80, 50, 35, 0, 0] },
  schnitt_3: { nBedarfPflanze: 190, nDuengebedarf: 190, gaben: [110, 70, 40, 0, 0, 0] },
  schnitt_4: { nBedarfPflanze: 245, nDuengebedarf: 245, gaben: [165, 80, 50, 35, 0, 0] },
  schnitt_5: { nBedarfPflanze: 310, nDuengebedarf: 310, gaben: [230, 100, 60, 40, 30, 0] },
  schnitt_6: { nBedarfPflanze: 350, nDuengebedarf: 340, gaben: [260, 100, 80, 80, 50, 30] },
}

/** Tab. 3a Niedermoor (Mindestabzug 80 kg N/ha; frühjahrsbetont). */
export const TAB3A_NEDERMOOR: Record<GruenlandNutzung, GruenlandZeile> = {
  standweide_extensiv: { nBedarfPflanze: 65, nDuengebedarf: 55, gaben: [30, 25, 0, 0, 0, 0] },
  intensiv_vollweide_leg: { nBedarfPflanze: 110, nDuengebedarf: 100, gaben: [60, 40, 0, 0, 0, 0] },
  intensiv_vollweide_ohne: { nBedarfPflanze: 130, nDuengebedarf: 120, gaben: [60, 30, 30, 0, 0, 0] },
  maehweide_80: { nBedarfPflanze: 150, nDuengebedarf: 140, gaben: [80, 30, 30, 0, 0, 0] },
  maehweide_60: { nBedarfPflanze: 190, nDuengebedarf: 180, gaben: [90, 60, 30, 0, 0, 0] },
  maehweide_40: { nBedarfPflanze: 220, nDuengebedarf: 210, gaben: [100, 70, 40, 0, 0, 0] },
  maehweide_20: { nBedarfPflanze: 245, nDuengebedarf: 235, gaben: [100, 60, 45, 30, 0, 0] },
  schnitt_3: { nBedarfPflanze: 190, nDuengebedarf: 180, gaben: [100, 50, 30, 0, 0, 0] },
  schnitt_4: { nBedarfPflanze: 245, nDuengebedarf: 235, gaben: [100, 60, 45, 30, 0, 0] },
  schnitt_5: { nBedarfPflanze: 310, nDuengebedarf: 300, gaben: [100, 60, 60, 50, 30, 0] },
  schnitt_6: { nBedarfPflanze: 350, nDuengebedarf: 340, gaben: [100, 80, 80, 50, 30, 0] },
}

/** Tab. 3b Mineral (mit Vorjahres-org. Düngung; 10 % Abschlag). N-Düngebedarf und Aufteilung org./min. zusammengefasst. */
export const TAB3B_MINERAL: Record<GruenlandNutzung, GruenlandZeile> = {
  standweide_extensiv: { nBedarfPflanze: 65, nDuengebedarf: 55, gaben: [30, 25, 0, 0, 0, 0] },
  intensiv_vollweide_leg: { nBedarfPflanze: 110, nDuengebedarf: 100, gaben: [60, 40, 0, 0, 0, 0] },
  intensiv_vollweide_ohne: { nBedarfPflanze: 130, nDuengebedarf: 120, gaben: [60, 30, 30, 0, 0, 0] },
  maehweide_80: { nBedarfPflanze: 150, nDuengebedarf: 134, gaben: [80, 30, 24, 0, 0, 0] },
  maehweide_60: { nBedarfPflanze: 190, nDuengebedarf: 168, gaben: [90, 55, 23, 0, 0, 0] },
  maehweide_40: { nBedarfPflanze: 220, nDuengebedarf: 196, gaben: [100, 50, 16, 0, 0, 0] },
  maehweide_20: { nBedarfPflanze: 245, nDuengebedarf: 219, gaben: [100, 60, 30, 29, 0, 0] },
  schnitt_3: { nBedarfPflanze: 190, nDuengebedarf: 164, gaben: [90, 74, 39, 0, 0, 0] },
  schnitt_4: { nBedarfPflanze: 245, nDuengebedarf: 218, gaben: [100, 65, 30, 23, 0, 0] },
  schnitt_5: { nBedarfPflanze: 310, nDuengebedarf: 283, gaben: [100, 65, 60, 30, 28, 0] },
  schnitt_6: { nBedarfPflanze: 350, nDuengebedarf: 323, gaben: [100, 80, 75, 30, 33, 0] },
}

/** Tab. 3b Hochmoor (mit Vorjahres-org. Düngung). */
export const TAB3B_HOCHMOOR: Record<GruenlandNutzung, GruenlandZeile> = {
  standweide_extensiv: { nBedarfPflanze: 65, nDuengebedarf: 65, gaben: [0, 0, 0, 0, 0, 0] },
  intensiv_vollweide_leg: { nBedarfPflanze: 110, nDuengebedarf: 110, gaben: [30, 30, 0, 0, 0, 0] },
  intensiv_vollweide_ohne: { nBedarfPflanze: 130, nDuengebedarf: 130, gaben: [50, 50, 0, 0, 0, 0] },
  maehweide_80: { nBedarfPflanze: 150, nDuengebedarf: 150, gaben: [70, 24, 0, 0, 0, 0] },
  maehweide_60: { nBedarfPflanze: 190, nDuengebedarf: 190, gaben: [70, 28, 0, 0, 0, 0] },
  maehweide_40: { nBedarfPflanze: 220, nDuengebedarf: 220, gaben: [80, 41, 0, 0, 0, 0] },
  maehweide_20: { nBedarfPflanze: 245, nDuengebedarf: 245, gaben: [85, 30, 23, 0, 0, 0] },
  schnitt_3: { nBedarfPflanze: 190, nDuengebedarf: 190, gaben: [89, 0, 0, 0, 0, 0] },
  schnitt_4: { nBedarfPflanze: 245, nDuengebedarf: 245, gaben: [85, 30, 23, 0, 0, 0] },
  schnitt_5: { nBedarfPflanze: 310, nDuengebedarf: 310, gaben: [100, 40, 38, 0, 0, 0] },
  schnitt_6: { nBedarfPflanze: 350, nDuengebedarf: 340, gaben: [260, 100, 80, 80, 50, 30] },
}

/** Tab. 3b Niedermoor (mit Vorjahres-org. Düngung). */
export const TAB3B_NEDERMOOR: Record<GruenlandNutzung, GruenlandZeile> = {
  standweide_extensiv: { nBedarfPflanze: 65, nDuengebedarf: 55, gaben: [30, 25, 0, 0, 0, 0] },
  intensiv_vollweide_leg: { nBedarfPflanze: 110, nDuengebedarf: 100, gaben: [60, 40, 0, 0, 0, 0] },
  intensiv_vollweide_ohne: { nBedarfPflanze: 130, nDuengebedarf: 120, gaben: [60, 30, 30, 0, 0, 0] },
  maehweide_80: { nBedarfPflanze: 150, nDuengebedarf: 140, gaben: [66, 46, 0, 0, 0, 0] },
  maehweide_60: { nBedarfPflanze: 190, nDuengebedarf: 180, gaben: [102, 40, 22, 0, 0, 0] },
  maehweide_40: { nBedarfPflanze: 220, nDuengebedarf: 210, gaben: [132, 60, 32, 0, 0, 0] },
  maehweide_20: { nBedarfPflanze: 245, nDuengebedarf: 235, gaben: [148, 50, 35, 28, 0, 0] },
  schnitt_3: { nBedarfPflanze: 190, nDuengebedarf: 180, gaben: [96, 46, 30, 0, 0, 0] },
  schnitt_4: { nBedarfPflanze: 245, nDuengebedarf: 235, gaben: [148, 35, 28, 0, 0, 0] },
  schnitt_5: { nBedarfPflanze: 310, nDuengebedarf: 300, gaben: [213, 40, 30, 28, 0, 0] },
  schnitt_6: { nBedarfPflanze: 350, nDuengebedarf: 340, gaben: [100, 80, 80, 50, 30, 0] },
}

export function getGruenlandTabelle(
  standort: StandortTyp,
  mitVorjahresOrgDungung: boolean
): Record<GruenlandNutzung, GruenlandZeile> {
  if (mitVorjahresOrgDungung) {
    if (standort === 'mineral') return TAB3B_MINERAL
    if (standort === 'hochmoor') return TAB3B_HOCHMOOR
    return TAB3B_NEDERMOOR
  }
  if (standort === 'mineral') return TAB3A_MINERAL
  if (standort === 'hochmoor') return TAB3A_HOCHMOOR
  return TAB3A_NEDERMOOR
}

export const GRUENLAND_NUTZUNG_LABELS: Record<GruenlandNutzung, string> = {
  standweide_extensiv: 'Standweide, extensiv',
  intensiv_vollweide_leg: 'Intensiv-Vollweide (5–10 % Leguminosen)',
  intensiv_vollweide_ohne: 'Intensiv-Vollweide (ohne Leguminosen)',
  maehweide_80: 'Mähweide 80 % (1 Schnitt, 4× Weide)',
  maehweide_60: 'Mähweide 60 % (2 Schnitte, 3× Weide)',
  maehweide_40: 'Mähweide 40 % (3 Schnitte, 2× Weide)',
  maehweide_20: 'Mähweide 20 % (4 Schnitte, 1× Weide)',
  schnitt_3: '3-Schnittnutzung (80 dt TM/ha)',
  schnitt_4: '4-Schnittnutzung (90 dt TM/ha)',
  schnitt_5: '5-Schnittnutzung (110 dt TM/ha)',
  schnitt_6: '6-Schnittnutzung (120 dt TM/ha)',
}
