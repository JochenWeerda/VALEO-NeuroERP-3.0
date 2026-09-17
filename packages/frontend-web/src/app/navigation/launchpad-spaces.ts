import type { NavItem } from '@/app/navigation/types'

type LaunchpadText = {
  de: string
  en: string
}

export type LaunchpadPageDef = {
  id: string
  label: LaunchpadText
  sectionId?: string
  tileItemIds?: string[]
  extraTiles?: Array<{
    id: string
    label: LaunchpadText
    path: string
    description?: LaunchpadText
    kind?: LaunchpadTileKind
  }>
}

export type LaunchpadSpaceDef = {
  id: string
  label: LaunchpadText
  pages: LaunchpadPageDef[]
}

export type LaunchpadTileKind = 'app' | 'task' | 'kpi' | 'alert'

export type LaunchpadAppTile = {
  id: string
  label: string
  path: string
  description?: string
  keywords?: string[]
  kind?: LaunchpadTileKind
}

export type LaunchpadPageOrigin = 'catalog' | 'custom'

export type LaunchpadPage = {
  id: string
  label: string
  tiles: LaunchpadAppTile[]
  origin: LaunchpadPageOrigin
  locked: boolean
  hidden?: boolean
}

export type LaunchpadSpace = {
  id: string
  label: string
  pages: LaunchpadPage[]
}

const MAX_PAGE_TILES = 10
const TASK_TILE_IDS = new Set(['kim-cockpit', 'meine-aufgaben', 'aktivitaeten'])
const ALERT_TILE_IDS = new Set(['leitstand', 'qs-leitstand'])

export function launchpadTileKind(id: string): LaunchpadTileKind {
  if (ALERT_TILE_IDS.has(id)) {
    return 'alert'
  }
  return TASK_TILE_IDS.has(id) ? 'task' : 'app'
}

export function matchesLaunchpadCatalogQuery(tile: LaunchpadAppTile, query: string): boolean {
  const needle = query.trim().toLowerCase()
  if (!needle) {
    return true
  }
  const pathHaystack = tile.path.toLowerCase().replaceAll('/', ' ')
  return (
    tile.label.toLowerCase().includes(needle) ||
    (tile.description ?? '').toLowerCase().includes(needle) ||
    pathHaystack.includes(needle) ||
    (tile.keywords ?? []).some((keyword) => keyword.toLowerCase().includes(needle))
  )
}

/**
 * Frühere Space-IDs bleiben lesbar, damit ein gespeicherter Tab nicht ins Leere fällt.
 */
export const LAUNCHPAD_SPACE_ALIASES: Record<string, string> = {
  erfassung: 'ernte',
  maerkte: 'handel',
  organisation: 'steuerung',
}

export function canonicalizeLaunchpadSpaceId(spaceId: string | undefined): string | undefined {
  if (!spaceId) {
    return undefined
  }
  return LAUNCHPAD_SPACE_ALIASES[spaceId] ?? spaceId
}

/**
 * Arbeitswelten, nicht Module. Dieselbe Entität darf in mehreren Spaces liegen
 * (Kontrakt in Handel und Ernte, Kunde in CRM, Debitoren und Disposition).
 * Flow-Spine-Prozessräume gehören nicht auf die Startseite.
 */
export const LAUNCHPAD_SPACES: LaunchpadSpaceDef[] = [
  {
    id: 'handel',
    label: { de: 'Handel & CRM', en: 'Trade & CRM' },
    pages: [
      {
        id: 'kunden',
        label: { de: 'Meine Kunden', en: 'My customers' },
        tileItemIds: ['kunden', 'kim-cockpit'],
        extraTiles: [
          {
            id: 'meine-aufgaben',
            label: { de: 'Meine Aufgaben', en: 'My tasks' },
            path: '/crm/aktivitaeten',
            description: {
              de: 'Wiedervorlagen und offene Aktivitäten',
              en: 'Follow-ups and open activities',
            },
            kind: 'task',
          },
        ],
      },
      {
        id: 'aussendienst',
        label: { de: 'CRM & Außendienst', en: 'Field sales' },
        tileItemIds: ['aktivitaeten', 'vertreterstamm', 'betriebsprofile'],
      },
      {
        id: 'angebote-auftraege',
        label: { de: 'Angebote & Aufträge', en: 'Quotes & orders' },
        tileItemIds: ['angebot', 'auftrag', 'ausgehend-angebot', 'ausgehend-auftrag'],
      },
      {
        id: 'verkauf',
        label: { de: 'Verkauf', en: 'Sales' },
        tileItemIds: ['lieferung', 'rechnung', 'ausgehende-belege'],
      },
      {
        id: 'einkauf',
        label: { de: 'Einkauf', en: 'Procurement' },
        tileItemIds: ['bestellungen', 'wareneingang', 'eingehende-belege', 'rechnungseingaenge'],
      },
      {
        id: 'kontrakte',
        label: { de: 'Kontrakte', en: 'Contracts' },
        tileItemIds: ['kontrakt-uebersicht', 'kontrakt-erfuellung', 'kontrakt-settlement'],
      },
      {
        id: 'preise',
        label: { de: 'Preise & Konditionen', en: 'Pricing' },
        tileItemIds: ['preis-kalkulation', 'preis-konditionen', 'konditionssystem'],
      },
      {
        id: 'kasse',
        label: { de: 'Kasse', en: 'POS' },
        tileItemIds: ['pos-terminal', 'tagesabschluss'],
      },
    ],
  },
  {
    id: 'ernte',
    label: { de: 'Ernte & Warenannahme', en: 'Harvest & intake' },
    pages: [
      {
        id: 'waage',
        label: { de: 'Annahme & Waage', en: 'Receiving' },
        tileItemIds: ['warteschlange', 'wiegungen', 'hofliste'],
      },
      {
        id: 'erntekampagne',
        label: { de: 'Erntekampagne', en: 'Harvest campaign' },
        tileItemIds: ['ernte', 'ernte-annahme'],
      },
      {
        id: 'qualitaet',
        label: { de: 'Qualität & Labor', en: 'Quality' },
        tileItemIds: ['labor-auftraege', 'qm-dokumente', 'reklamationen'],
      },
      {
        id: 'proben',
        label: { de: 'Proben', en: 'Samples' },
        tileItemIds: ['bodenproben', 'labor-auftraege', 'annahme-qualitaets-check'],
      },
      {
        id: 'abrechnung',
        label: { de: 'Abrechnungsvorbereitung', en: 'Settlement prep' },
        tileItemIds: ['sammelabrechnung', 'annahme-abrechnung', 'kontrakt-settlement'],
      },
    ],
  },
  {
    id: 'logistik',
    label: { de: 'Lager & Logistik', en: 'Warehouse & logistics' },
    pages: [
      {
        id: 'lager-silo',
        label: { de: 'Lager & Silo', en: 'Warehouse & silo' },
        tileItemIds: ['silo-uebersicht', 'fremdware', 'lagerplaetze'],
      },
      {
        id: 'bestaende',
        label: { de: 'Bestände', en: 'Stock' },
        tileItemIds: ['bestandsuebersicht', 'lagerbewegungen'],
      },
      {
        id: 'disposition',
        label: { de: 'Tagesdisposition', en: 'Daily dispatch' },
        tileItemIds: ['tour-fracht-arbeitsraum', 'tourenplanung', 'kunden'],
      },
      {
        id: 'touren',
        label: { de: 'Touren & Fuhrpark', en: 'Tours & fleet' },
        tileItemIds: ['fuhrpark', 'frachtbriefe'],
      },
      {
        id: 'versand',
        label: { de: 'Versand', en: 'Shipping' },
        tileItemIds: ['versand-avis', 'versand-frachtdokumente'],
      },
      {
        id: 'umlagerungen',
        label: { de: 'Umlagerungen', en: 'Transfers' },
        tileItemIds: ['einlagerung', 'auslagerung'],
      },
      {
        id: 'inventur',
        label: { de: 'Inventur', en: 'Inventory count' },
        tileItemIds: ['inventur', 'permanente-inventur'],
      },
    ],
  },
  {
    id: 'betriebsmittel',
    label: { de: 'Betriebsmittel & Produktion', en: 'Inputs & production' },
    pages: [
      {
        id: 'duenger',
        label: { de: 'Dünger', en: 'Fertilizer' },
        tileItemIds: ['duenger-liste', 'duenger-bedarfsrechner', 'duenger-mischungen'],
      },
      {
        id: 'psm',
        label: { de: 'Pflanzenschutz', en: 'Crop protection' },
        tileItemIds: ['psm-liste', 'psm-applikation', 'psm-auflagen-manager'],
      },
      {
        id: 'saatgut',
        label: { de: 'Saatgut', en: 'Seed' },
        tileItemIds: ['saatgut-liste', 'saatgut-sortenregister', 'saatgut-bestellung'],
      },
      {
        id: 'futtermittel',
        label: { de: 'Futtermittel', en: 'Feed' },
        tileItemIds: ['einzelfuttermittel', 'mischfuttermittel', 'rationsoptimierung'],
      },
      {
        id: 'produktion',
        label: { de: 'Mischungen & Produktion', en: 'Blending & production' },
        tileItemIds: ['produktionsleitstand', 'rezepturgruppen', 'duenger-mischungen'],
      },
      {
        id: 'chargen',
        label: { de: 'Chargen', en: 'Lots' },
        tileItemIds: ['partiestamm', 'chargen-bearbeiten'],
      },
    ],
  },
  {
    id: 'finanzen',
    label: { de: 'Finanzen & Controlling', en: 'Finance & controlling' },
    pages: [
      {
        id: 'debitoren',
        label: { de: 'Debitoren', en: 'Receivables' },
        tileItemIds: ['op-verwaltung', 'mahnlauf', 'kunden'],
      },
      {
        id: 'kreditoren',
        label: { de: 'Kreditoren', en: 'Payables' },
        tileItemIds: ['op-kreditoren-finance', 'fibu-verbindlichkeiten'],
      },
      {
        id: 'zahlungen',
        label: { de: 'Zahlungen', en: 'Payments' },
        tileItemIds: ['zahlungslaeufe', 'zahlungseingang'],
      },
      {
        id: 'kontrolle',
        label: { de: 'Belegkontrolle', en: 'Document control' },
        tileItemIds: ['beleg-kontrolle', 'auftrags-kontrolle', 'lieferschein-kontrolle'],
      },
      {
        id: 'kosten',
        label: { de: 'Kostenrechnung', en: 'Cost accounting' },
        tileItemIds: ['kostenstellenrechnung'],
      },
      {
        id: 'controlling',
        label: { de: 'Controlling', en: 'Controlling' },
        tileItemIds: ['plan-ist', 'deckungsbeitrag', 'liquiditaet'],
      },
      {
        id: 'abschluss',
        label: { de: 'Abschluss', en: 'Close' },
        tileItemIds: ['periodenabschluss', 'datev-export'],
      },
    ],
  },
  {
    id: 'steuerung',
    label: { de: 'Steuerung & Compliance', en: 'Control & compliance' },
    pages: [
      {
        id: 'leitstand',
        label: { de: 'Leitstand', en: 'Control center' },
        extraTiles: [
          { id: 'leitstand', label: { de: 'Leitstand', en: 'Control center' }, path: '/workflow/leitstand', kind: 'alert' },
        ],
      },
      {
        id: 'aufgaben',
        label: { de: 'Aufgaben & Freigaben', en: 'Tasks & approvals' },
        extraTiles: [
          { id: 'freigaben', label: { de: 'Freigaben', en: 'Approvals' }, path: '/workflows/approval' },
        ],
      },
      {
        id: 'dokumente',
        label: { de: 'Dokumente', en: 'Documents' },
        tileItemIds: ['letzte-dokumente', 'dms-volltext'],
      },
      {
        id: 'qs',
        label: { de: 'QS', en: 'Quality system' },
        tileItemIds: ['qs-leitstand', 'qm-dokumente'],
      },
      {
        id: 'gmp',
        label: { de: 'GMP+', en: 'GMP+' },
        tileItemIds: ['qs-leitstand', 'zulassungen'],
      },
      {
        id: 'regulatory',
        label: { de: 'PSM & Zulassungen', en: 'Regulatory' },
        tileItemIds: ['psm-auflagen-manager', 'psm-sachkunde-register', 'zulassungen'],
      },
      {
        id: 'nachhaltigkeit',
        label: { de: 'Nachhaltigkeit & CBAM', en: 'Sustainability' },
        tileItemIds: ['eudr', 'esg-report', 'co2-bilanz'],
      },
      {
        id: 'audit',
        label: { de: 'Audit', en: 'Audit' },
        tileItemIds: ['audit-trails', 'audit-trail-finance'],
      },
    ],
  },
]

export function isLaunchpadHiddenNavId(id: string): boolean {
  return id.includes('flow-spine') || id === 'dashboard'
}

function normalizeLanguage(lang?: string): keyof LaunchpadText {
  const normalized = (lang ?? 'de').split('-')[0].toLowerCase()
  return normalized === 'en' ? 'en' : 'de'
}

function translate(text: LaunchpadText, lang?: string): string {
  return text[normalizeLanguage(lang)]
}

function indexNavItems(items: NavItem[], into = new Map<string, NavItem>()): Map<string, NavItem> {
  for (const item of items) {
    into.set(item.id, item)
    if (item.children?.length) {
      indexNavItems(item.children, into)
    }
  }
  return into
}

function routablePath(item: NavItem | undefined): string | undefined {
  if (!item?.path || item.path.includes(':')) {
    return undefined
  }
  return item.path
}

function fallbackTiles(section: NavItem | undefined): LaunchpadAppTile[] {
  if (!section?.children) {
    return []
  }
  return section.children
    .filter((child) => !isLaunchpadHiddenNavId(child.id))
    .flatMap((child) => {
      const path = routablePath(child)
      return path ? [{ id: child.id, label: child.label, path, keywords: child.keywords }] : []
    })
    .slice(0, MAX_PAGE_TILES)
}

export function resolveLaunchpadSpaces(sections: NavItem[], lang?: string): LaunchpadSpace[] {
  const byId = indexNavItems(sections)

  return LAUNCHPAD_SPACES.map((space) => {
    const pages = space.pages
      .map((page): LaunchpadPage | null => {
        const tiles: LaunchpadAppTile[] = []
        const seen = new Set<string>()

        const pushTile = (tile: LaunchpadAppTile) => {
          if (seen.has(tile.id) || isLaunchpadHiddenNavId(tile.id)) {
            return
          }
          seen.add(tile.id)
          tiles.push({ ...tile, kind: tile.kind ?? launchpadTileKind(tile.id) })
        }

        const section = page.sectionId ? byId.get(page.sectionId) : undefined
        if (page.tileItemIds?.length) {
          for (const itemId of page.tileItemIds) {
            const item = byId.get(itemId)
            const path = routablePath(item)
            if (item && path) {
              pushTile({ id: item.id, label: item.label, path, keywords: item.keywords })
            }
          }
        } else if (section) {
          for (const tile of fallbackTiles(section)) {
            pushTile(tile)
          }
        }

        const allowExtras = (page.tileItemIds?.length ?? 0) === 0 || tiles.length > 0
        if (allowExtras) {
          for (const extra of page.extraTiles ?? []) {
            pushTile({
              id: extra.id,
              label: translate(extra.label, lang),
              path: extra.path,
              description: extra.description ? translate(extra.description, lang) : undefined,
              kind: extra.kind ?? launchpadTileKind(extra.id),
            })
          }
        }

        if (tiles.length === 0) {
          return null
        }

        return {
          id: page.id,
          label: translate(page.label, lang),
          tiles: tiles.slice(0, MAX_PAGE_TILES),
          origin: 'catalog',
          locked: false,
        }
      })
      .filter((page): page is LaunchpadPage => page !== null)

    return {
      id: space.id,
      label: translate(space.label, lang),
      pages: pages.map((page, index) => ({ ...page, locked: index === 0 })),
    }
  }).filter((space) => space.pages.length > 0)
}

export function flattenLaunchpadTiles(
  spaces: LaunchpadSpace[],
): Array<LaunchpadAppTile & { spaceId: string; spaceLabel: string; pageId: string; pageLabel: string }> {
  return spaces.flatMap((space) =>
    space.pages.flatMap((page) =>
      page.tiles.map((tile) => ({
        ...tile,
        spaceId: space.id,
        spaceLabel: space.label,
        pageId: page.id,
        pageLabel: page.label,
      })),
    ),
  )
}

function launchpadTileSlot(key: string | number): number {
  if (typeof key === 'number') {
    return key
  }
  let hash = 0
  for (let index = 0; index < key.length; index += 1) {
    hash = (hash * 31 + key.charCodeAt(index)) | 0
  }
  return Math.abs(hash) % 6
}

/** Kachelfläche aus Chart-Slots — keine SAP-Palette, keine Status-Grün/Rot-Semantik. */
export function launchpadTileSurface(
  key: string | number,
  kind: LaunchpadTileKind = 'app',
): {
  backgroundColor: string
  borderColor: string
  borderLeftColor: string
} {
  const slot = launchpadTileSlot(key)
  const token = slot >= 0 && slot < 6 ? `--chart-${slot + 1}-hsl` : '--chart-other-hsl'
  const fill = kind === 'task' || kind === 'kpi' || kind === 'alert' ? 0.4 : 0.28
  return {
    backgroundColor: `hsl(var(${token}) / ${fill})`,
    borderColor: `hsl(var(${token}) / 0.7)`,
    borderLeftColor: `hsl(var(${token}))`,
  }
}
