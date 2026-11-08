/**
 * Drift-Gate: Adaptive Fachaktionen YAML ↔ TS-Alias-Spiegel ↔ Registry-Felder.
 *
 * Source of Truth: config/adaptive_workspace_fachaktionen.yaml
 * Spiegel: FACHAKTION_CATALOG_ALIASES in fachaktion-resolve.ts
 * Registry: WORKSPACE_FACHAKTIONEN.catalogId → route / scope / screenId
 *
 * Keine Schein-Asserts: Mengen, Mengen-Gleichheit und Feldwerte werden
 * gegen den geparsten Katalog geprueft (analog YAML↔screenIds Composition-Gate).
 */
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { load as loadYaml } from 'js-yaml'
import { describe, expect, it } from 'vitest'
import { WORKSPACE_FACHAKTIONEN } from '@/workspace'
import { FACHAKTION_CATALOG_ALIASES } from '@/workspace/fachaktion-resolve'

const HERE = dirname(fileURLToPath(import.meta.url))
const YAML_PATH = resolve(HERE, '../../../../../config/adaptive_workspace_fachaktionen.yaml')

type YamlAction = {
  action_id: string
  aliases?: string[] | null
  route_path?: string | null
  screen_id?: string | null
  permission?: { scope?: string | null } | null
}

type YamlCatalog = {
  actions: YamlAction[]
}

function loadCatalog(): YamlCatalog {
  const catalog = loadYaml(readFileSync(YAML_PATH, 'utf8')) as YamlCatalog
  expect(Array.isArray(catalog.actions), 'YAML actions[]').toBe(true)
  expect(catalog.actions.length).toBeGreaterThan(0)
  return catalog
}

function sorted(values: Iterable<string>): string[] {
  return [...values].sort((a, b) => a.localeCompare(b))
}

describe('fachaktion alias parity YAML↔TS', () => {
  it('FACHAKTION_CATALOG_ALIASES spiegelt YAML action_id und aliases 1:1', () => {
    const catalog = loadCatalog()
    const yamlById = new Map(
      catalog.actions.map((action) => [action.action_id, [...(action.aliases ?? [])]] as const),
    )
    const tsIds = sorted(Object.keys(FACHAKTION_CATALOG_ALIASES))
    const yamlIds = sorted(yamlById.keys())

    expect(tsIds, 'Alias-Keys vs YAML action_ids').toEqual(yamlIds)
    expect(tsIds.length).toBe(yamlIds.length)
    expect(tsIds.length).toBeGreaterThanOrEqual(15)

    for (const actionId of yamlIds) {
      const yamlAliases = yamlById.get(actionId) ?? []
      const tsAliases = [...(FACHAKTION_CATALOG_ALIASES[actionId] ?? [])]
      expect(tsAliases, `aliases fuer ${actionId}`).toEqual(yamlAliases)
      expect(new Set(tsAliases).size, `keine Duplikat-Aliase in TS fuer ${actionId}`).toBe(
        tsAliases.length,
      )
      expect(new Set(yamlAliases).size, `keine Duplikat-Aliase in YAML fuer ${actionId}`).toBe(
        yamlAliases.length,
      )
    }
  })

  it('Registry catalogId hat YAML action_id mit route_path, screen_id und permission.scope', () => {
    const catalog = loadCatalog()
    const yamlById = new Map(catalog.actions.map((action) => [action.action_id, action] as const))

    const withCatalog = WORKSPACE_FACHAKTIONEN.filter((action) => Boolean(action.catalogId))
    expect(withCatalog.length).toBe(WORKSPACE_FACHAKTIONEN.length)
    expect(withCatalog.length).toBeGreaterThanOrEqual(10)

    for (const action of withCatalog) {
      const catalogId = action.catalogId as string
      const yamlAction = yamlById.get(catalogId)
      expect(yamlAction, `Registry catalogId ${catalogId} fehlt in YAML`).toBeTruthy()
      expect(action.target.route, catalogId).toBe(yamlAction?.route_path)
      expect(action.target.screenId, catalogId).toBe(yamlAction?.screen_id)
      expect(action.requiredScopes, catalogId).toEqual([yamlAction?.permission?.scope])
      expect(action.target.route?.startsWith('/'), catalogId).toBe(true)
      expect(action.target.route?.includes('/api/'), catalogId).toBe(false)
    }
  })

  it('kein Alias kollidiert ueber action_ids hinweg (YAML und TS)', () => {
    const catalog = loadCatalog()
    const owners = new Map<string, string>()

    for (const action of catalog.actions) {
      for (const alias of action.aliases ?? []) {
        const key = alias.trim().toLowerCase()
        expect(key.length, `leerer Alias bei ${action.action_id}`).toBeGreaterThan(0)
        const previous = owners.get(key)
        expect(previous, `Alias-Kollision '${alias}' (${previous} vs ${action.action_id})`).toBeUndefined()
        owners.set(key, action.action_id)
      }
    }

    const tsOwners = new Map<string, string>()
    for (const [actionId, aliases] of Object.entries(FACHAKTION_CATALOG_ALIASES)) {
      for (const alias of aliases) {
        const key = alias.trim().toLowerCase()
        const previous = tsOwners.get(key)
        expect(previous, `TS Alias-Kollision '${alias}' (${previous} vs ${actionId})`).toBeUndefined()
        tsOwners.set(key, actionId)
      }
    }

    expect(sorted(owners.keys())).toEqual(sorted(tsOwners.keys()))
  })
})
