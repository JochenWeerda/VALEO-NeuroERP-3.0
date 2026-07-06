import type { ScreenDensity, ScreenLayoutMode } from '../schema'

export function renderValue(value: unknown): string {
  if (value == null) return ''
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  return JSON.stringify(value)
}

export function getValue(source: Record<string, unknown>, path: string): unknown {
  if (path in source) return source[path]
  return path.split('.').reduce<unknown>((current, segment) => {
    if (current === null || typeof current !== 'object') return undefined
    return (current as Record<string, unknown>)[segment]
  }, source)
}

export function layoutClasses(mode: ScreenLayoutMode | undefined, density: ScreenDensity = 'compact'): {
  root: string
  header: string
  fields: string
  touchTarget: string
} {
  const isExpert = density === 'expertDense'
  const isComfortable = density === 'comfortable'
  if (mode === 'mobileStack') {
    return {
      root: isExpert ? 'space-y-3 p-3 sm:p-4' : 'space-y-4 p-3 sm:p-4',
      header: 'flex flex-col gap-3 rounded-md border border-border bg-card p-4 shadow-sm',
      fields: 'grid gap-3 grid-cols-1',
      touchTarget: 'min-h-11',
    }
  }
  if (mode === 'tabletTouch') {
    return {
      root: isComfortable ? 'space-y-6 p-4 md:p-6' : 'space-y-5 p-4 md:p-6',
      header: 'flex flex-col gap-4 rounded-md border border-border bg-card p-5 shadow-sm lg:flex-row lg:items-center lg:justify-between',
      fields: 'grid gap-4 md:grid-cols-2',
      touchTarget: 'min-h-12',
    }
  }
  return {
    root: isExpert ? 'space-y-4 p-3 md:p-5' : isComfortable ? 'space-y-7 p-4 md:p-8' : 'space-y-5 p-4 md:p-6',
    header: isExpert
      ? 'flex flex-col gap-3 rounded-md border border-border bg-card p-4 shadow-sm md:flex-row md:items-center md:justify-between'
      : 'flex flex-col gap-4 rounded-md border border-border bg-card p-5 shadow-sm md:flex-row md:items-center md:justify-between',
    fields: isExpert ? 'grid gap-3 md:grid-cols-3 xl:grid-cols-4' : 'grid gap-4 md:grid-cols-2 xl:grid-cols-3',
    touchTarget: '',
  }
}
