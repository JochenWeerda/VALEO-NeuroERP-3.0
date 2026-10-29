import type { ListExperience } from '../schema'

type Row = Record<string, unknown>
/** Exact cents for canonical two-decimal money. Never silently coerce missing data. */
function minorUnits(value: unknown): bigint {
  if ((typeof value !== 'string' && typeof value !== 'number') || typeof value === 'number' && !Number.isFinite(value)) throw new Error('Ungültiger Summenwert.')
  const match = /^(-?)([0-9]+)(?:\.([0-9]{1,2}))?$/.exec(String(value))
  if (!match) throw new Error('Ungültiger Summenwert.')
  return (match[1] ? -1n : 1n) * (BigInt(match[2]) * 100n + BigInt((match[3] ?? '').padEnd(2, '0')))
}

export function formatListAggregate(aggregate: ListExperience['aggregates'][number], value: number, currency = 'EUR'): string {
  return aggregate.format === 'currency' ? new Intl.NumberFormat('de-DE', { style: 'currency', currency }).format(value) : String(value)
}

export function evaluateListExperience(experience: ListExperience, rows: Row[]) {
  const counts: Record<string, number> = Object.create(null)
  const currencies: Record<string, string> = Object.create(null)
  for (const aggregate of experience.aggregates) {
    const selected = rows.filter(row => aggregate.conditions.every(condition => {
      const equal = String(row[condition.field] ?? '') === condition.value
      return condition.op === 'eq' ? equal : !equal
    }))
    if (aggregate.kind === 'sum') {
      if (!aggregate.field) throw new Error('Summenfeld fehlt.')
      const field = aggregate.field
      if (aggregate.currencyField) {
        const currencyField = aggregate.currencyField
        const codes = [...new Set(selected.map(row => row[currencyField]))]
        if (codes.length > 1 || codes.some(code => typeof code !== 'string' || !/^[A-Z]{3}$/.test(code))) throw new Error('Währungsübergreifende Summe ist gesperrt.')
        currencies[aggregate.key] = String(codes[0] ?? 'EUR')
      }
      const total = selected.reduce((sum, row) => sum + minorUnits(row[field]), 0n)
      if (total > 90071992547400n || total < -90071992547400n) throw new Error('Summenwert überschreitet den Anzeigevertrag.')
      counts[aggregate.key] = Number(total) / 100
    } else counts[aggregate.key] = selected.length
  }
  const interpolate = (text: string) => text.replace(/\{([^{}]+)\}/g, (match, key: string) => Object.prototype.hasOwnProperty.call(counts, key) ? String(counts[key]) : match)
  const notice = experience.notice && (counts[experience.notice.aggregate] ?? 0) > 0 ? interpolate(experience.notice.text) : undefined
  const insights = (experience.insightLines ?? []).flatMap(line => {
    const variant = line.variants.find(v => !v.when || (counts[v.when.aggregate] ?? 0) > v.when.value)
    return variant ? [{ label: line.label, text: interpolate(variant.text) }] : []
  })
  return { counts, notice, insights, ...(Object.keys(currencies).length ? { currencies } : {}) }
}
