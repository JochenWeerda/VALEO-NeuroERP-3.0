import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

export type PartyKind = 'lead' | 'customer'

const PARTY_SECTION_ALIASES: Record<string, string> = {
  chef: 'masterdata',
  chefanweisung: 'masterdata',
  notizen: 'masterdata',
  stamm: 'masterdata',
  stammdaten: 'masterdata',
  masterdata: 'masterdata',
  praesente: 'praesente',
  präsente: 'praesente',
  gifts: 'praesente',
  postfach: 'postfach',
  mailbox: 'postfach',
  mail: 'postfach',
  geo: 'address',
  karte: 'address',
  map: 'address',
  address: 'address',
  adresse: 'address',
  belege: 'auftraege',
  orders: 'auftraege',
  auftraege: 'auftraege',
  finanzen: 'finance',
  finance: 'finance',
  op: 'finance',
  dokumente: 'dokumente',
  aktivitaeten: 'aktivitaeten',
  activities: 'aktivitaeten',
  aufgaben: 'aufgaben',
  tasks: 'aufgaben',
  kontrakte: 'kontrakte',
  contacts: 'contacts',
  kontakte: 'contacts',
  angebote: 'angebote',
  quotes: 'angebote',
  offers: 'angebote',
  historie: 'historie',
  history: 'historie',
  timeline: 'historie',
  tab21: 'chefanweisungen',
  chefanweisungen: 'chefanweisungen',
  tab22: 'contacts',
  tab23: 'anschriften',
  anschriften: 'anschriften',
  addresses: 'anschriften',
  tab24: 'kontoauszug',
  kontoauszug: 'kontoauszug',
  tab25: 'cpd',
  cpd: 'cpd',
}

export function resolvePartyKind(kind: string | null | undefined, pathname?: string): PartyKind {
  if (kind === 'lead') return 'lead'
  if (kind === 'customer') return 'customer'
  if (pathname?.includes('/lead')) return 'lead'
  return 'customer'
}

export function readQueryParam(
  searchParams: { get: (key: string) => string | null },
  key: string,
): string | null {
  const fromRouter = searchParams.get(key)
  if (fromRouter) return fromRouter
  if (typeof window === 'undefined') return null
  return new URLSearchParams(window.location.search).get(key)
}

/** KIM and list deep-links (`?tab=chef`) land on ScreenDefinition section keys. */
export function resolvePartySectionKey(tab: string | null | undefined): string | undefined {
  const key = tab?.trim().toLowerCase()
  if (!key) return undefined
  return PARTY_SECTION_ALIASES[key] ?? key
}

export default function PartyNativePage({
  kind = 'customer',
  entityId,
  testId,
  requestedSectionKey,
}: {
  kind?: PartyKind
  entityId?: string
  testId?: string
  requestedSectionKey?: string
}): JSX.Element {
  const screenId = kind === 'lead' ? 'crm/lead' : 'crm/customer-360'
  return (
    <UniversalNativeDetailPage
      screenId={screenId}
      entityId={entityId}
      testId={testId ?? (kind === 'lead' ? 'crm-lead' : 'crm-customer-360')}
      requestedSectionKey={requestedSectionKey}
    />
  )
}
