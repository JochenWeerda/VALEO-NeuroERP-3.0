/**
 * Kontowahl im Portal (PORTAL-CONTEXT-001).
 *
 * - Genau ein zugeordnetes Konto: wird automatisch gewaehlt.
 * - Mehrere: Auswahl, bevor kundenbezogene Daten geladen werden; gewechselt wird nur zwischen zugeordneten Konten.
 * - Keines: Hinweis; ohne gueltige Zuordnung gibt es keine Kundendaten und keine Auftraege.
 * - Interne Betreuung (Innendienst ohne Zuordnung): waehlt einen Kunden des Mandanten; der Server prueft das.
 */
import { useEffect, type ReactNode } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Building2 } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { usePortalKonto, type PortalKundenkonto } from '@/lib/portal-konto'
import { CustomerCombobox, type CustomerLite } from '@/components/crm/CustomerCombobox'
import { Callout, CalloutDescription, CalloutTitle } from '@/components/ui/callout'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

export function usePortalKonten() {
  const { aktiv, waehle } = usePortalKonto()
  const queryClient = useQueryClient()
  const konten = useQuery<PortalKundenkonto[]>({
    queryKey: ['portal-kundenkonten'],
    queryFn: async () => (await apiClient.get<PortalKundenkonto[]>('/api/v1/portal/kundenkonten')).data,
    staleTime: 60_000,
  })
  const liste = konten.data ?? []

  useEffect(() => {
    if (!konten.data) return
    if (aktiv && aktiv.rolle !== 'intern' && !konten.data.some((k) => k.customer_id === aktiv.customer_id)) {
      waehle(null) // Zuordnung widerrufen: Wahl verfaellt
      return
    }
    if (!aktiv && konten.data.length === 1) waehle(konten.data[0])
  }, [konten.data, aktiv, waehle])

  const wechsle = (konto: PortalKundenkonto | null) => {
    if (konto?.customer_id === aktiv?.customer_id) return
    waehle(konto)
    // Alle Kundendaten gehoerten zum vorigen Konto.
    void queryClient.resetQueries({ predicate: (q) => q.queryKey[0] !== 'portal-kundenkonten' })
  }

  return { konten: liste, aktiv, wechsle, laedt: konten.isLoading, fehler: konten.isError }
}

function bezeichnung(k: PortalKundenkonto): string {
  return `${k.name ?? k.customer_id}${k.customer_number ? ` · ${k.customer_number}` : ''}`
}

/** Kopfzeile: aktives Konto, bei mehreren als Auswahl. */
export function PortalKontoWahl() {
  const { konten, aktiv, wechsle } = usePortalKonten()
  if (konten.length > 1) {
    return (
      <Select
        value={aktiv?.customer_id ?? ''}
        onValueChange={(id) => wechsle(konten.find((k) => k.customer_id === id) ?? null)}
      >
        <SelectTrigger className="h-9 w-56" aria-label="Aktiver Betrieb">
          <SelectValue placeholder="Betrieb wählen" />
        </SelectTrigger>
        <SelectContent>
          {konten.map((k) => (
            <SelectItem key={k.customer_id} value={k.customer_id}>
              {bezeichnung(k)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    )
  }
  if (!aktiv) return null
  return (
    <span className="hidden items-center gap-1.5 text-sm text-muted-foreground md:flex">
      <Building2 className="h-4 w-4" aria-hidden />
      {bezeichnung(aktiv)}
      {aktiv.rolle === 'intern' && (
        <Button variant="ghost" size="sm" onClick={() => wechsle(null)}>
          Kunde wechseln
        </Button>
      )}
    </span>
  )
}

/** Inhalt erst, wenn ein Konto gewaehlt ist. */
export function PortalKontoGate({ intern, children }: { intern: boolean; children: ReactNode }) {
  const { konten, aktiv, wechsle, laedt, fehler } = usePortalKonten()

  if (laedt) return <Skeleton className="h-24 w-full" />
  if (fehler) {
    return (
      <Callout variant="error">
        <CalloutTitle>Kundenkonten konnten nicht geladen werden</CalloutTitle>
        <CalloutDescription>Bitte später erneut versuchen.</CalloutDescription>
      </Callout>
    )
  }
  if (aktiv) return <>{children}</>

  if (konten.length > 1) {
    return (
      <div className="mx-auto max-w-xl space-y-3">
        <h2 className="text-lg font-semibold">Für welchen Betrieb möchten Sie arbeiten?</h2>
        {konten.map((k) => (
          <Button key={k.customer_id} variant="outline" className="w-full justify-start" onClick={() => wechsle(k)}>
            <Building2 className="mr-2 h-4 w-4" aria-hidden />
            {bezeichnung(k)}
          </Button>
        ))}
      </div>
    )
  }

  if (intern) {
    return (
      <div className="mx-auto max-w-xl space-y-3">
        <h2 className="text-lg font-semibold">Kunde für die Betreuung wählen</h2>
        <CustomerCombobox
          value={null}
          onChange={(kunde: CustomerLite | null) =>
            kunde &&
            wechsle({
              customer_id: kunde.id,
              customer_number: kunde.customer_number,
              name: kunde.company_name,
              rolle: 'intern',
              rechte: [],
            })
          }
        />
      </div>
    )
  }

  return (
    <Callout variant="info">
      <CalloutTitle>Kein Kundenkonto zugeordnet</CalloutTitle>
      <CalloutDescription>
        Ihre Anmeldung ist noch keinem Betrieb zugeordnet. Bitte wenden Sie sich an Ihren Ansprechpartner im Landhandel.
      </CalloutDescription>
    </Callout>
  )
}
