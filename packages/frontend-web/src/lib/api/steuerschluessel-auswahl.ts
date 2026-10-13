/**
 * Die eine Steuerschluessel-Auswahl aller Masken — Backend: /api/v1/finance/tax-keys/auswahl.
 *
 * Belege und Stammdaten geben den Steuerschluessel an, nicht den Satz. Der Satz ist das Abbild des
 * Schluessels und kommt vom Server; keine Maske setzt einen Vorgabewert ein.
 */
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/** Verkaufsbelege nehmen Umsatzsteuer-, Eingangsbelege Vorsteuerschluessel; steuerfreie gelten fuer beide. */
export type Steuerrichtung = 'verkauf' | 'einkauf'

export type Schluesselwahl = {
  code: string
  bezeichnung: string
  steuersatz: number | string
  par_24_ustg?: boolean
  reverse_charge?: boolean
}

export async function ladeSchluesselAuswahl(richtung: Steuerrichtung): Promise<Schluesselwahl[]> {
  return (await apiClient.get<Schluesselwahl[]>('/api/v1/finance/tax-keys/auswahl', { params: { richtung } })).data
}

export function useSteuerschluesselAuswahl(richtung: Steuerrichtung) {
  return useQuery({
    queryKey: ['finance', 'tax-keys', 'auswahl', richtung],
    queryFn: () => ladeSchluesselAuswahl(richtung),
    staleTime: 5 * 60 * 1000,
  })
}

/** Der Satz des Schluessels in Prozent — oder `null`, wenn kein (gueltiger) Schluessel gewaehlt ist. */
export function satzVon(auswahl: Schluesselwahl[] | undefined, code: string | null | undefined): number | null {
  const wahl = code ? auswahl?.find((k) => k.code === code) : undefined
  return wahl ? Number(wahl.steuersatz) : null
}

export function schluesselText(auswahl: Schluesselwahl[] | undefined, code: string | null | undefined): string {
  if (!code) return 'kein Steuerschlüssel'
  const wahl = auswahl?.find((k) => k.code === code)
  return wahl
    ? `${wahl.code} – ${wahl.bezeichnung} (${Number(wahl.steuersatz).toLocaleString('de-DE')} %)`
    : `${code} – nicht (mehr) gültig`
}
