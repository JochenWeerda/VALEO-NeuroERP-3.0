/**
 * Stammdaten-Anlage aus Inbox-Vorschlaegen.
 * Schreibt nur ueber autorisierte Domänen-APIs (kein Inbox-Approve, kein Direct-SQL).
 */

import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import type { InboxMasterDataProposal } from './types'

export const LIEFERANT_CREATE_PATH = '/api/v1/einkauf/lieferanten'
export const ARTICLE_CREATE_PATH = '/api/v1/articles/'
export const ARTICLE_FETCH_IMAGE_PATH = (articleId: string) =>
  `/api/v1/articles/${encodeURIComponent(articleId)}/fetch-image`

/**
 * Domänen-UI-Defaults aus Artikelstamm (`stamm-legacy` DEFAULT_ARTIKEL /
 * kategorieOptions / einheitOptions). Keine Fantasiewerte:
 * - unit: 't' (Masken-Default fuer Neuanlage)
 * - category: 'Sonstige' (letzte Option / Fallback mapApiToForm)
 * - sales_price: 0 (vkPreis Default; API ArticleBase sales_price ge=0)
 */
export const ARTICLE_INBOX_DEFAULTS = {
  unit: 't',
  category: 'Sonstige',
  sales_price: 0,
} as const

export type LieferantCreateBody = {
  firmenname: string
  lieferantennummer: string
  strasse?: string
  plz?: string
  ort?: string
  land?: string
  email?: string
  telefon?: string
  ust_id?: string
}

export type ArticleCreateBody = {
  article_number: string
  name: string
  unit: string
  category: string
  sales_price: number
  ean_code?: string
  barcode?: string
}

export type ArticleProposalRow = NonNullable<InboxMasterDataProposal['articles']>[number]

function clean(value: unknown): string | undefined {
  if (typeof value !== 'string') return undefined
  const trimmed = value.trim()
  return trimmed.length > 0 ? trimmed : undefined
}

/** Baut den POST-Body fuer LieferantCreate; null wenn Pflichtfelder fehlen. */
export function buildLieferantCreateBody(
  supplier: NonNullable<InboxMasterDataProposal['supplier']>,
): LieferantCreateBody | null {
  if (supplier.status !== 'propose' || supplier.kind !== 'supplier_create') return null
  const payload = supplier.payload ?? {}
  const firmenname = clean(payload.firmenname)
  const lieferantennummer = clean(payload.lieferantennummer)
  if (!firmenname || !lieferantennummer) return null
  const body: LieferantCreateBody = {
    firmenname,
    lieferantennummer,
    land: clean(payload.land) || 'Deutschland',
  }
  const strasse = clean(payload.strasse)
  const plz = clean(payload.plz)
  const ort = clean(payload.ort)
  const email = clean(payload.email)
  const telefon = clean(payload.telefon)
  const ustId = clean(payload.ust_id)
  if (strasse) body.strasse = strasse
  if (plz) body.plz = plz
  if (ort) body.ort = ort
  if (email) body.email = email
  if (telefon) body.telefon = telefon
  if (ustId) body.ust_id = ustId
  return body
}

export function supplierCreateBlockedReason(
  supplier: NonNullable<InboxMasterDataProposal['supplier']> | null | undefined,
): string | null {
  if (!supplier || supplier.status !== 'propose') return 'Kein Lieferant-Vorschlag.'
  if (buildLieferantCreateBody(supplier)) return null
  const gaps = supplier.gaps ?? []
  if (gaps.includes('lieferantennummer_fehlt_im_extrakt') || !clean(supplier.payload?.lieferantennummer)) {
    return 'Lieferantennummer fehlt im Extrakt — Anlage ueber die Maske.'
  }
  if (!clean(supplier.payload?.firmenname)) {
    return 'Firmenname fehlt im Extrakt — Anlage ueber die Maske.'
  }
  return 'Lieferant-Vorschlag unvollstaendig fuer POST /api/v1/einkauf/lieferanten.'
}

function axiosStatus(cause: unknown): number | undefined {
  if (cause && typeof cause === 'object' && 'response' in cause) {
    const response = (cause as { response?: { status?: number } }).response
    return typeof response?.status === 'number' ? response.status : undefined
  }
  return undefined
}

export async function createLieferantFromProposal(
  supplier: NonNullable<InboxMasterDataProposal['supplier']>,
): Promise<
  { ok: true; id?: string; alreadyExists?: boolean } | { ok: false; message: string }
> {
  const body = buildLieferantCreateBody(supplier)
  if (!body) {
    return { ok: false, message: supplierCreateBlockedReason(supplier) ?? 'Payload unvollstaendig.' }
  }
  try {
    const response = await apiClient.post<{ id?: string }>(LIEFERANT_CREATE_PATH, body)
    return { ok: true, id: response.data?.id }
  } catch (cause) {
    // POST /einkauf/lieferanten: Dublette → 409 — Confirm erneut = idempotent ok.
    if (axiosStatus(cause) === 409) {
      return { ok: true, alreadyExists: true, id: body.lieferantennummer }
    }
    return { ok: false, message: getAxiosErrorMessage(cause) }
  }
}

/**
 * ArticleCreate aus Positions-Proposal + Domänen-Defaults.
 * Extrakt muss name + article_number liefern; unit/category/sales_price kommen
 * aus unit_hint bzw. ARTICLE_INBOX_DEFAULTS (kein Fantasiepreis).
 */
export function buildArticleCreateBody(article: ArticleProposalRow): ArticleCreateBody | null {
  if (article.kind !== 'article_create' || article.status !== 'propose') return null
  const payload = article.payload ?? {}
  const name = clean(payload.name)
  const articleNumber = clean(payload.article_number)
  if (!name || !articleNumber) return null
  const unitHint = clean(payload.unit_hint)
  const ean = clean(payload.ean_code)
  const body: ArticleCreateBody = {
    article_number: articleNumber,
    name,
    unit: unitHint || ARTICLE_INBOX_DEFAULTS.unit,
    category: ARTICLE_INBOX_DEFAULTS.category,
    sales_price: ARTICLE_INBOX_DEFAULTS.sales_price,
  }
  if (ean) {
    body.ean_code = ean
    body.barcode = ean
  }
  return body
}

export function articleCreateBlockedReason(article: ArticleProposalRow | null | undefined): string | null {
  if (!article || article.kind !== 'article_create') return 'Kein Artikel-Vorschlag.'
  if (article.status === 'blocked') {
    return article.detail ?? article.code ?? 'Artikel-Vorschlag blockiert (keine Positionszeilen).'
  }
  if (article.status !== 'propose') return 'Kein Artikel-Vorschlag zum Anlegen.'
  if (buildArticleCreateBody(article)) return null
  const gaps = article.gaps ?? []
  if (gaps.includes('artikelnummer_fehlt_im_extrakt') || !clean(article.payload?.article_number)) {
    return 'Artikelnummer fehlt im Extrakt — Anlage ueber die Maske.'
  }
  if (gaps.includes('artikelname_fehlt_im_extrakt') || !clean(article.payload?.name)) {
    return 'Artikelname fehlt im Extrakt — Anlage ueber die Maske.'
  }
  return 'Artikel-Vorschlag unvollstaendig fuer POST /api/v1/articles/.'
}

/** True wenn mindestens ein propose-Artikel mit name+number POST-faehig ist. */
export function articleCreateFromInboxSupported(
  articles: InboxMasterDataProposal['articles'] | undefined,
): boolean {
  if (!articles?.length) return false
  return articles.some((row) => buildArticleCreateBody(row) !== null)
}

/** Documentiert die ArticleCreate-Pflichtfelder; Defaults siehe ARTICLE_INBOX_DEFAULTS. */
export const ARTICLE_CREATE_REQUIRED_WITHOUT_DEFAULT = [
  'article_number',
  'name',
  'unit',
  'category',
  'sales_price',
] as const

export async function createArticleFromProposal(
  article: ArticleProposalRow,
): Promise<{ ok: true; id?: string } | { ok: false; message: string }> {
  const body = buildArticleCreateBody(article)
  if (!body) {
    return { ok: false, message: articleCreateBlockedReason(article) ?? 'Payload unvollstaendig.' }
  }
  try {
    const response = await apiClient.post<{ id?: string }>(ARTICLE_CREATE_PATH, body)
    return { ok: true, id: response.data?.id }
  } catch (cause) {
    return { ok: false, message: getAxiosErrorMessage(cause) }
  }
}

/**
 * Nach Artikelanlage: vorhandenes fetch-image (braucht article_id).
 * Ohne ID oder ohne name/ean im Slot: kein Call.
 */
export async function enrichArticleImageAfterCreate(
  articleId: string,
  article: ArticleProposalRow,
): Promise<{ ok: true; image_url?: string | null } | { ok: false; message: string }> {
  const research = article.image_research
  if (!research || research.status !== 'propose') {
    return { ok: false, message: 'Kein Bild-Research-Slot (EAN/Name).' }
  }
  if (!clean(articleId)) {
    return { ok: false, message: 'article_id fehlt nach Create — Enrich-API braucht ID.' }
  }
  try {
    const response = await apiClient.post<{ image_url?: string | null }>(
      ARTICLE_FETCH_IMAGE_PATH(articleId),
    )
    return { ok: true, image_url: response.data?.image_url }
  } catch (cause) {
    return { ok: false, message: getAxiosErrorMessage(cause) }
  }
}
