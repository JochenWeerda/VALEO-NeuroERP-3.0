import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { AgrarWorkbench } from '@/components/mask-builder/specialized/agrar/agrar-workbench'
import { LagerWorkbench } from '@/components/mask-builder/specialized/lager/lager-workbench'
import { FleetWorkbench } from '@/components/mask-builder/specialized/fleet/fleet-workbench'
import { PricingWorkbench } from '@/components/mask-builder/specialized/pricing/pricing-workbench'
import type { RenderPlan } from '@/components/mask-builder/render-plan/types'

vi.mock('@/components/mask-builder/specialized/intake/domain-runtime', () => ({
  DomainContractBoundary: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))
vi.mock('@/components/mask-builder/specialized/agrar/schlagkartei-surface', () => ({ default: () => <div>Schlagkartei</div> }))
vi.mock('@/components/mask-builder/specialized/agrar/milchvieh-karte-surface', () => ({ default: () => <div>Milchvieh</div> }))
vi.mock('@/components/mask-builder/specialized/agrar/ernte-annahme-surface', () => ({ default: () => <div>ErnteAnnahme</div> }))
vi.mock('@/components/mask-builder/specialized/agrar/abrechnung-surface', () => ({ default: () => <div>Abrechnung</div> }))
vi.mock('@/components/mask-builder/specialized/lager/materialfluss-surface', () => ({ default: () => <div>Materialfluss</div> }))
vi.mock('@/components/mask-builder/specialized/fleet/fahrzeug-vertiefung-surface', () => ({ default: () => <div>FahrzeugVertiefung</div> }))
vi.mock('@/components/mask-builder/specialized/pricing/konditionssystem-surface', () => ({ default: () => <div>Konditionssystem</div> }))

function plan(type: string, id: string): RenderPlan {
  return { screenId: id, specialized: { type, id } } as RenderPlan
}

describe('domain workbenches', () => {
  it('rejects invalid agrar contracts and routes known ones', async () => {
    render(<AgrarWorkbench contract={{ id: 'agrar/x' } as never} plan={plan('agrar_workbench', 'agrar/x')} />)
    expect(screen.getByRole('alert')).toHaveTextContent('Agrar-Arbeitsplatz ist nicht verfügbar')
    render(
      <AgrarWorkbench
        contract={{ id: 'agrar/kunden-schlagkartei' } as never}
        plan={plan('agrar_workbench', 'agrar/kunden-schlagkartei')}
      />,
    )
    expect(await screen.findByText('Schlagkartei')).toBeTruthy()
  })

  it('routes lager/fleet/pricing contracts', async () => {
    render(
      <LagerWorkbench
        contract={{ id: 'lager/materialfluss' } as never}
        plan={plan('lager_workbench', 'lager/materialfluss')}
      />,
    )
    expect(await screen.findByText('Materialfluss')).toBeTruthy()

    render(
      <FleetWorkbench
        contract={{ id: 'fuhrpark/fahrzeug-vertiefung' } as never}
        plan={plan('fleet_workbench', 'fuhrpark/fahrzeug-vertiefung')}
      />,
    )
    expect(await screen.findByText('FahrzeugVertiefung')).toBeTruthy()

    render(
      <PricingWorkbench
        contract={{ id: 'konditionen/konditionssystem' } as never}
        plan={plan('pricing_workbench', 'konditionen/konditionssystem')}
      />,
    )
    expect(await screen.findByText('Konditionssystem')).toBeTruthy()
  })
})
