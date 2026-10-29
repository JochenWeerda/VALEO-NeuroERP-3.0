import { describe, expect, it, vi, beforeEach } from 'vitest'
import {
  ARTICLE_CREATE_PATH,
  ARTICLE_CREATE_REQUIRED_WITHOUT_DEFAULT,
  ARTICLE_INBOX_DEFAULTS,
  LIEFERANT_CREATE_PATH,
  articleCreateBlockedReason,
  articleCreateFromInboxSupported,
  buildArticleCreateBody,
  buildLieferantCreateBody,
  createArticleFromProposal,
  createLieferantFromProposal,
  enrichArticleImageAfterCreate,
  supplierCreateBlockedReason,
} from '@/components/adaptive-workspace/inbox/master-data-create'
import type { InboxMasterDataProposal } from '@/components/adaptive-workspace/inbox/types'

const postMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: { post: postMock },
  getAxiosErrorMessage: (error: unknown) =>
    error instanceof Error ? error.message : 'Unbekannter Fehler.',
}))

function supplier(
  payload: Record<string, string | null | undefined>,
  gaps: string[] = [],
): NonNullable<InboxMasterDataProposal['supplier']> {
  return {
    kind: 'supplier_create',
    status: 'propose',
    booking: false,
    executable: false,
    domain_api: 'POST /api/v1/einkauf/lieferanten',
    target_route: '/einkauf/lieferanten',
    reason: 'test',
    payload,
    gaps,
  }
}

function articlePropose(
  payload: Record<string, string | null | undefined>,
  gaps: string[] = [],
): NonNullable<InboxMasterDataProposal['articles']>[number] {
  return {
    kind: 'article_create',
    status: 'propose',
    booking: false,
    executable: false,
    domain_api: 'POST /api/v1/articles/',
    target_route: '/artikel/neu',
    payload,
    gaps,
    image_research: {
      status: 'propose',
      executed: false,
      booking: false,
      service: 'app.services.article_image_enrichment.resolve_image_for_article',
      api: 'POST /api/v1/articles/enrich-images',
      reason: 'test',
    },
  }
}

describe('master-data-create', () => {
  beforeEach(() => {
    postMock.mockReset()
  })

  it('maps propose payload to LieferantCreate body without inventing numbers', () => {
    const body = buildLieferantCreateBody(
      supplier({
        firmenname: 'Neue Muehle GmbH',
        lieferantennummer: 'L-NEU-9',
        strasse: 'Hofweg 1',
        plz: '26789',
        ort: 'Leer',
      }),
    )
    expect(body).toEqual({
      firmenname: 'Neue Muehle GmbH',
      lieferantennummer: 'L-NEU-9',
      land: 'Deutschland',
      strasse: 'Hofweg 1',
      plz: '26789',
      ort: 'Leer',
    })
  })

  it('blocks create when lieferantennummer is missing', () => {
    const row = supplier(
      { firmenname: 'Ohne Nummer', lieferantennummer: null },
      ['lieferantennummer_fehlt_im_extrakt'],
    )
    expect(buildLieferantCreateBody(row)).toBeNull()
    expect(supplierCreateBlockedReason(row)).toMatch(/Lieferantennummer fehlt/)
  })

  it('posts only to the authorized lieferanten endpoint', async () => {
    postMock.mockResolvedValue({ data: { id: 'lf-1' } })
    const result = await createLieferantFromProposal(
      supplier({ firmenname: 'Nordkorn', lieferantennummer: 'L-22' }),
    )
    expect(result).toEqual({ ok: true, id: 'lf-1' })
    expect(postMock).toHaveBeenCalledWith(LIEFERANT_CREATE_PATH, {
      firmenname: 'Nordkorn',
      lieferantennummer: 'L-22',
      land: 'Deutschland',
    })
  })

  it('treats HTTP 409 as idempotent Lieferant-Create success (DEMO-GAP Rerun)', async () => {
    postMock.mockRejectedValue({ response: { status: 409, statusText: 'Conflict' } })
    const result = await createLieferantFromProposal(
      supplier({
        firmenname: 'Nordkorn Handelsgesellschaft Demo OHG',
        lieferantennummer: 'DEMO-LF-GAP',
      }),
    )
    expect(result).toEqual({
      ok: true,
      alreadyExists: true,
      id: 'DEMO-LF-GAP',
    })
    expect(postMock).toHaveBeenCalledWith(LIEFERANT_CREATE_PATH, {
      firmenname: 'Nordkorn Handelsgesellschaft Demo OHG',
      lieferantennummer: 'DEMO-LF-GAP',
      land: 'Deutschland',
    })
  })

  it('applies Artikelstamm defaults for unit/category/sales_price=0', () => {
    expect(ARTICLE_CREATE_REQUIRED_WITHOUT_DEFAULT).toEqual([
      'article_number',
      'name',
      'unit',
      'category',
      'sales_price',
    ])
    expect(ARTICLE_INBOX_DEFAULTS).toEqual({
      unit: 't',
      category: 'Sonstige',
      sales_price: 0,
    })
    const body = buildArticleCreateBody(
      articlePropose({
        name: 'Winterweizen A',
        article_number: 'WW-1',
        ean_code: '4006381333931',
      }),
    )
    expect(body).toEqual({
      article_number: 'WW-1',
      name: 'Winterweizen A',
      unit: 't',
      category: 'Sonstige',
      sales_price: 0,
      ean_code: '4006381333931',
      barcode: '4006381333931',
    })
    expect(
      articleCreateFromInboxSupported([
        articlePropose({ name: 'Weizen', article_number: 'WW-1', unit_hint: 'kg' }),
      ]),
    ).toBe(true)
  })

  it('prefers unit_hint over stamm default unit', () => {
    const body = buildArticleCreateBody(
      articlePropose({ name: 'Weizen', article_number: 'WW-1', unit_hint: 'kg' }),
    )
    expect(body?.unit).toBe('kg')
    expect(body?.sales_price).toBe(0)
  })

  it('blocks article create when article_number missing', () => {
    const row = articlePropose(
      { name: 'Ohne Nummer', article_number: null },
      ['artikelnummer_fehlt_im_extrakt'],
    )
    expect(buildArticleCreateBody(row)).toBeNull()
    expect(articleCreateBlockedReason(row)).toMatch(/Artikelnummer fehlt/)
    expect(articleCreateFromInboxSupported([row])).toBe(false)
  })

  it('posts article to authorized endpoint then fetch-image', async () => {
    postMock
      .mockResolvedValueOnce({ data: { id: 'art-9' } })
      .mockResolvedValueOnce({ data: { image_url: 'https://example.test/w.jpg' } })
    const row = articlePropose({ name: 'Weizen', article_number: 'WW-1' })
    const created = await createArticleFromProposal(row)
    expect(created).toEqual({ ok: true, id: 'art-9' })
    expect(postMock).toHaveBeenCalledWith(ARTICLE_CREATE_PATH, {
      article_number: 'WW-1',
      name: 'Weizen',
      unit: 't',
      category: 'Sonstige',
      sales_price: 0,
    })
    const enrich = await enrichArticleImageAfterCreate('art-9', row)
    expect(enrich).toEqual({ ok: true, image_url: 'https://example.test/w.jpg' })
    expect(postMock).toHaveBeenCalledWith('/api/v1/articles/art-9/fetch-image')
  })
})
