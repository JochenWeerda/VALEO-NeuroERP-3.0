/**
 * Slice-006: E-Rechnung XRechnung/ZUGFeRD Export für B2B-Verkaufsrechnungen.
 *
 * Schließt die E-Rechnung-2025-Pflichtumfang-Lücke für reguläre SalesInvoice.
 * Backend: app/api/v1/endpoints/sales_invoice_einvoice.py
 */
import { apiClient } from '@/lib/api-client'

export type EInvoiceFormat = 'xrechnung' | 'zugferd'

export interface EInvoicePartyOverride {
  name?: string
  street?: string
  postal_code?: string
  city?: string
  country_code?: string
  vat_id?: string
  email?: string
}

export interface EInvoiceExportRequest {
  supplier?: EInvoicePartyOverride
  customer?: EInvoicePartyOverride
  buyer_reference?: string
  payment_terms_text?: string
  payment_due_date?: string
}

async function postBlob(url: string, body: EInvoiceExportRequest): Promise<Blob> {
  const response = await apiClient.post(url, body ?? {}, { responseType: 'blob' })
  return response.data as Blob
}

export async function generateXRechnung(
  invoiceNumber: string,
  options: EInvoiceExportRequest = {}
): Promise<Blob> {
  return postBlob(
    `/api/v1/sales/invoices/${encodeURIComponent(invoiceNumber)}/einvoice/xrechnung`,
    options
  )
}

export async function generateZugferd(
  invoiceNumber: string,
  options: EInvoiceExportRequest = {}
): Promise<Blob> {
  return postBlob(
    `/api/v1/sales/invoices/${encodeURIComponent(invoiceNumber)}/einvoice/zugferd`,
    options
  )
}

export async function downloadXRechnung(
  invoiceNumber: string,
  options?: EInvoiceExportRequest
): Promise<void> {
  const blob = await generateXRechnung(invoiceNumber, options)
  triggerDownload(blob, `xrechnung-${invoiceNumber}.xml`)
}

export async function downloadZugferd(
  invoiceNumber: string,
  options?: EInvoiceExportRequest
): Promise<void> {
  const blob = await generateZugferd(invoiceNumber, options)
  triggerDownload(blob, `zugferd-${invoiceNumber}.pdf`)
}

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  document.body.removeChild(anchor)
  URL.revokeObjectURL(url)
}
