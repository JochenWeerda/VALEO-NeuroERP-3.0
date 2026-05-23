import { describe, expect, it } from 'vitest'
import { isTerraAgrarPortalPath, TERRA_AGRAR_PORTAL_PATHS } from '@/lib/portal-theme'

describe('portal-theme', () => {
  it('exports the three agrar portal routes', () => {
    expect(TERRA_AGRAR_PORTAL_PATHS).toEqual([
      '/portal/feldbuch',
      '/portal/naehrstoffbilanzen',
      '/portal/rationsoptimierung',
    ])
  })

  it('matches exact agrar portal paths', () => {
    for (const path of TERRA_AGRAR_PORTAL_PATHS) {
      expect(isTerraAgrarPortalPath(path)).toBe(true)
    }
  })

  it('matches nested agrar portal paths', () => {
    expect(isTerraAgrarPortalPath('/portal/feldbuch/schlag/1')).toBe(true)
  })

  it('does not match non-agrar portal paths', () => {
    expect(isTerraAgrarPortalPath('/portal')).toBe(false)
    expect(isTerraAgrarPortalPath('/portal/shop')).toBe(false)
    expect(isTerraAgrarPortalPath('/portal/dokumente')).toBe(false)
    expect(isTerraAgrarPortalPath('/agrar/ernte')).toBe(false)
  })
})
