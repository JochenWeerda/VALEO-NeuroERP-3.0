#!/usr/bin/env npx ts-node
/**
 * Wave 30 — prueft Generator-Performance-Vertrag fuer mask_registry Metadaten.
 */

import { execSync } from 'node:child_process'

type MaskEntry = {
  mask_id: string
  generator_ready?: boolean
  requires_lazy_tabs?: boolean
  requires_virtual_tables?: boolean
  lookup_min_chars?: number
  initial_payload_budget_kb?: number
}

type RegistryPayload = {
  masks?: MaskEntry[]
}

function loadRegistry(): RegistryPayload {
  const raw = execSync(
    'python -c "from app.core.mask_classification import build_mask_registry; import json; print(json.dumps(build_mask_registry().model_dump(mode=\'json\')))"',
    { encoding: 'utf8' },
  )
  return JSON.parse(raw) as RegistryPayload
}

function main(): void {
  const registry = loadRegistry()
  const masks = registry.masks ?? []
  const generatorMasks = masks.filter((mask) => mask.generator_ready)
  const violations: string[] = []

  if (generatorMasks.length === 0) {
    violations.push('Keine generator_ready Masken im Registry gefunden.')
  }

  for (const mask of generatorMasks) {
    if (!mask.requires_lazy_tabs) {
      violations.push(`${mask.mask_id}: requires_lazy_tabs muss true sein`)
    }
    if ((mask.lookup_min_chars ?? 0) < 2) {
      violations.push(`${mask.mask_id}: lookup_min_chars muss >= 2 sein`)
    }
    if ((mask.initial_payload_budget_kb ?? 0) <= 0) {
      violations.push(`${mask.mask_id}: initial_payload_budget_kb muss > 0 sein`)
    }
  }

  if (violations.length > 0) {
    console.error('Mask performance contract violations:')
    for (const violation of violations) {
      console.error(`- ${violation}`)
    }
    process.exit(1)
  }

  console.log(`Mask performance contract OK (${generatorMasks.length} generator mask(s)).`)
}

main()
