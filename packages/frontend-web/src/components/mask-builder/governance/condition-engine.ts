import type { ScreenCondition } from '../schema'

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

/** Liest `tour.canCreate` zuerst als flachen Schlüssel, dann als Pfad. */
export function readPath(root: Record<string, unknown>, path: string): unknown {
  if (Object.prototype.hasOwnProperty.call(root, path)) return root[path]
  let current: unknown = root
  for (const segment of path.split('.')) {
    if (!isRecord(current) || !Object.prototype.hasOwnProperty.call(current, segment)) return undefined
    current = current[segment]
  }
  return current
}

function isPresent(value: unknown): boolean {
  return value != null && value !== '' && value !== false
}

export function evaluateCondition(condition: ScreenCondition, root: Record<string, unknown>): boolean {
  if (typeof condition === 'string') return isPresent(readPath(root, condition))
  if ('all' in condition) return condition.all.every((entry) => evaluateCondition(entry, root))
  if ('any' in condition) return condition.any.some((entry) => evaluateCondition(entry, root))
  if ('not' in condition) return !evaluateCondition(condition.not, root)
  const value = readPath(root, condition.path)
  if (condition.exists === true && !isPresent(value)) return false
  if (condition.exists === false && isPresent(value)) return false
  if ('equals' in condition && value !== condition.equals) return false
  if ('notEquals' in condition && value === condition.notEquals) return false
  if (condition.exists == null && !('equals' in condition) && !('notEquals' in condition)) return isPresent(value)
  return true
}

export function matchesValueList(
  row: Record<string, unknown>,
  rule?: { field: string; values: Array<string | number | boolean> },
): boolean {
  if (!rule) return true
  return rule.values.includes(row[rule.field] as string | number | boolean)
}
