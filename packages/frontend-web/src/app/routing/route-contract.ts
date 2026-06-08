import {
  generatedRouteInventory,
  generatedParamKeys,
  generatedSearchKeys,
} from '@/app/routing/route-tree.gen'

type InventoryPath = (typeof generatedRouteInventory)[number]['path']

export type AppRoutePath = InventoryPath extends infer TPath extends string
  ? TPath extends ''
    ? '/'
    : `/${TPath}`
  : never

type SegmentParam<TSegment extends string> =
  TSegment extends `:${infer TParam}` ? TParam : never

type PathParamNames<TPath extends string> =
  TPath extends `${infer TSegment}/${infer TRest}`
    ? SegmentParam<TSegment> | PathParamNames<TRest>
    : SegmentParam<TPath>

export type AppRouteParams<TPath extends AppRoutePath> = {
  [TParam in PathParamNames<TPath>]: string | number
}

export type AppRouteParamKey = (typeof generatedParamKeys)[number]
export type AppRouteHref = string

export type AppSearchKey = (typeof generatedSearchKeys)[number]
export type AppSearchValue = string | number | boolean | null | undefined
export type AppRouteSearch = Partial<Record<AppSearchKey, AppSearchValue | readonly AppSearchValue[]>>

type BuildRouteArguments<TPath extends AppRoutePath> =
  [PathParamNames<TPath>] extends [never]
    ? []
    : [params: AppRouteParams<TPath>]

export function buildRoute<TPath extends AppRoutePath>(
  path: TPath,
  ...[params]: BuildRouteArguments<TPath>
): string {
  const values = params as Record<string, string | number> | undefined
  return path.replace(/:([A-Za-z0-9_]+)/g, (_match, name: string) => {
    const value = values?.[name]
    if (value === undefined) {
      throw new Error(`Missing route parameter "${name}" for "${path}".`)
    }
    return encodeURIComponent(String(value))
  })
}

export function appendRouteSearch(route: string, search: AppRouteSearch): string {
  const query = new URLSearchParams()
  for (const [key, rawValue] of Object.entries(search)) {
    const values = Array.isArray(rawValue) ? rawValue : [rawValue]
    for (const value of values) {
      if (value !== undefined && value !== null) query.append(key, String(value))
    }
  }
  const queryString = query.toString()
  return queryString ? `${route}?${queryString}` : route
}
