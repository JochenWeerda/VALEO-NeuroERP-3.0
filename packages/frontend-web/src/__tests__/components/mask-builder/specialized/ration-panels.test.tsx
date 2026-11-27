import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import {
  ForagePerformancePanel,
  RationBlocksPanel,
  epBalanceWithinGuidance,
  getMilkEpExcessKg,
} from '@/components/mask-builder/specialized/feed/ration-optimization-surface'
import type { OptimizationResult, RationBlocks } from '@/lib/api/rations-optimization'

const emptyBlock = {
  dmi_kg: 12.5,
  dmi_share_pct: 50,
  cost_eur_day: 0,
  me_mj: 0,
  sidp_g: 0,
  cp_g: 0,
  items: [],
}

const blocks: RationBlocks = {
  feeding_system: {
    system: 'PMR',
    concentrate_distribution: 'transponder',
    concentrate_max_per_serving_kg: null,
    concentrate_servings_per_day: null,
    concentrate_max_per_day_kg: null,
    auto_promoted_from_tmr: true,
  },
  tmr_block: { ...emptyBlock, dmi_kg: 12.5, dmi_share_pct: 50 },
  pasture_block: { ...emptyBlock, dmi_kg: 4, dmi_share_pct: 16 },
  concentrate_staged_block: { ...emptyBlock, dmi_kg: 8.5, dmi_share_pct: 34 },
}

const forageResult = {
  forage_performance: {
    feeding_type: 'TMR',
    target_milk_kg: 32,
    forage_only: {
      milk_from_energy_kg: 28,
      milk_from_protein_kg: 31,
      limiting_milk_kg: 28,
    },
    supplemented: {
      milk_from_energy_kg: 32,
      milk_from_protein_kg: 33,
      limiting_milk_kg: 32,
      concentrate_dmi_kg: 6.2,
      forage_displacement_dmi_kg: 1.1,
    },
  },
} as OptimizationResult

describe('ration panels (new-code coverage buffer)', () => {
  it('deckt EP-Hilfsfunktionen und null-Guards ab', () => {
    expect(RationBlocksPanel({ blocks: null })).toBeNull()
    expect(ForagePerformancePanel({ result: null })).toBeNull()
    expect(ForagePerformancePanel({ result: {} as OptimizationResult })).toBeNull()
    const ex = getMilkEpExcessKg(forageResult.forage_performance!)
    expect(ex.ist).toBe(3)
    expect(ex.neu).toBe(1)
    expect(epBalanceWithinGuidance(2)).toBe(true)
    expect(epBalanceWithinGuidance(2.5)).toBe(false)
  })

  it('rendert Fütterungsblöcke inkl. Auto-Promotion', () => {
    render(<RationBlocksPanel blocks={blocks} />)
    expect(screen.getByText(/Fütterungssystem & Blöcke/)).toBeTruthy()
    expect(screen.getByText(/PMR · transponder/)).toBeTruthy()
    expect(screen.getByText(/Automatisch von TMR auf PMR\+Weide/)).toBeTruthy()
    expect(screen.getByText(/TMR \/ Mischwagen/)).toBeTruthy()
    expect(screen.getByText(/^Weide$/)).toBeTruthy()
    expect(screen.getByText(/Kraftfutter gestaffelt/)).toBeTruthy()
  })

  it('rendert Grundfutterleistungs-Panel inkl. compact-Variante', () => {
    const { rerender } = render(<ForagePerformancePanel result={forageResult} />)
    expect(screen.getByText(/Grundfutterleistung TMR/)).toBeTruthy()
    expect(screen.getByText(/Milch aus Energie Grundfutter/)).toBeTruthy()
    expect(screen.getByText(/Kraftfutter:/)).toBeTruthy()
    expect(screen.getByText(/Priorität:/)).toBeTruthy()

    rerender(<ForagePerformancePanel result={forageResult} compact />)
    expect(screen.getByText(/E\/P-Abgleich/)).toBeTruthy()
  })
})
