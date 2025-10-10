export const nfDE = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 3 })

export function formatDE(n: number | null | undefined): string {
  if (typeof n !== 'number' || Number.isNaN(n)) return ''
  return nfDE.format(n)
}

export function parseDE(input: string): number {
  const s = (input ?? '').trim()
  if (!s) return 0
  const normalized = s.replace(/\./g, '').replace(',', '.')
  const n = Number(normalized)
  return Number.isFinite(n) ? n : 0
}
