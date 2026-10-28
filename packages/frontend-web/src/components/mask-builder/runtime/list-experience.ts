import type { ListExperience } from '../schema'

type Row = Record<string, unknown>
export function evaluateListExperience(experience: ListExperience, rows: Row[]) {
  const counts: Record<string, number> = Object.create(null)
  for (const aggregate of experience.aggregates) {
    counts[aggregate.key] = rows.filter(row => aggregate.conditions.every(condition => {
      const equal = String(row[condition.field] ?? '') === condition.value
      return condition.op === 'eq' ? equal : !equal
    })).length
  }
  const interpolate = (text: string) => text.replace(/\{([^{}]+)\}/g, (match, key: string) => Object.prototype.hasOwnProperty.call(counts, key) ? String(counts[key]) : match)
  const notice = experience.notice && (counts[experience.notice.aggregate] ?? 0) > 0 ? interpolate(experience.notice.text) : undefined
  const insights = (experience.insightLines ?? []).flatMap(line => {
    const variant = line.variants.find(v => !v.when || (counts[v.when.aggregate] ?? 0) > v.when.value)
    return variant ? [{ label: line.label, text: interpolate(variant.text) }] : []
  })
  return { counts, notice, insights }
}
