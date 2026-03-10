import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

export type SupplierRating = {
  supplierId: string
  supplier: string
  onTimeDelivery: number
  qualityScore: number
  priceScore: number
  serviceScore: number
  overallScore: number
  totalOrders: number
  updatedAt?: string
}

export type ServiceEntrySheet = {
  id: string
  number: string
  supplierId?: string
  purchaseOrderId?: string
  serviceDate: string
  description: string
  quantity: number
  unitPrice: number
  amount: number
  status: string
  createdAt?: string
  updatedAt?: string
}

export type EdiMessage = {
  id: string
  number: string
  direction: 'inbound' | 'outbound' | string
  partner: string
  messageType: string
  status: string
  payload: Record<string, unknown>
  createdAt?: string
  ackAt?: string
}

export type SupplierDocument = {
  id: string
  name: string
  typ: string
  kategorie: string
  groesse: number
  hochgeladenAm?: string
  beschreibung?: string
}

export type PoCommunication = {
  id: string
  channel: 'email' | 'portal' | string
  subject: string
  message?: string
  recipient?: string
  status: string
  createdAt?: string
}

export type EinkaufAuditTrail = {
  documentType: string
  documentId: string
  events: Array<Record<string, unknown>>
  total: number
}

const EMPTY_SUPPLIER_RATINGS: SupplierRating[] = []
const EMPTY_SUPPLIER_DOCUMENTS: SupplierDocument[] = []
const EMPTY_PO_COMMUNICATIONS: PoCommunication[] = []
const EMPTY_SERVICE_ENTRY_SHEETS: ServiceEntrySheet[] = []
const EMPTY_EDI_MESSAGES: EdiMessage[] = []

export const procurementPlusKeys = {
  all: ['procurement-plus'] as const,
  supplierRatings: () => [...procurementPlusKeys.all, 'supplier-ratings'] as const,
  supplierDocuments: (supplierId: string) => [...procurementPlusKeys.all, 'supplier-documents', supplierId] as const,
  poCommunications: (poId: string) => [...procurementPlusKeys.all, 'po-communications', poId] as const,
  auditTrail: (docType: string, docId: string) => [...procurementPlusKeys.all, 'audit-trail', docType, docId] as const,
  serviceEntrySheets: () => [...procurementPlusKeys.all, 'service-entry-sheets'] as const,
  ediMessages: () => [...procurementPlusKeys.all, 'edi-messages'] as const,
}

export function useSupplierRatings() {
  return useQuery({
    queryKey: procurementPlusKeys.supplierRatings(),
    queryFn: async () => (await apiClient.get<{ items: SupplierRating[] }>('/api/v1/einkauf/supplier-ratings')).data.items,
    initialData: EMPTY_SUPPLIER_RATINGS,
    staleTime: 2 * 60 * 1000,
  })
}

export function useSaveSupplierRating() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: SupplierRating) =>
      (await apiClient.post<SupplierRating>(`/api/v1/einkauf/supplier-ratings/${encodeURIComponent(data.supplierId)}`, data)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: procurementPlusKeys.supplierRatings() }),
  })
}

export function useSupplierDocuments(supplierId: string) {
  return useQuery({
    queryKey: procurementPlusKeys.supplierDocuments(supplierId),
    queryFn: async () =>
      (await apiClient.get<SupplierDocument[]>(`/api/v1/einkauf/suppliers/${encodeURIComponent(supplierId)}/documents`)).data,
    enabled: !!supplierId,
    initialData: EMPTY_SUPPLIER_DOCUMENTS,
    staleTime: 30 * 1000,
  })
}

export function useCreateSupplierDocument(supplierId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: Partial<SupplierDocument>) =>
      (await apiClient.post(`/api/v1/einkauf/suppliers/${encodeURIComponent(supplierId)}/documents`, data)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: procurementPlusKeys.supplierDocuments(supplierId) }),
  })
}

export function useDeleteSupplierDocument(supplierId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (docId: string) =>
      (await apiClient.delete(`/api/v1/einkauf/suppliers/${encodeURIComponent(supplierId)}/documents/${encodeURIComponent(docId)}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: procurementPlusKeys.supplierDocuments(supplierId) }),
  })
}

export function usePoCommunications(poId: string) {
  return useQuery({
    queryKey: procurementPlusKeys.poCommunications(poId),
    queryFn: async () =>
      (await apiClient.get<PoCommunication[]>(`/api/v1/purchase-orders/${encodeURIComponent(poId)}/communications`)).data,
    enabled: !!poId,
    initialData: EMPTY_PO_COMMUNICATIONS,
    staleTime: 10 * 1000,
  })
}

export function useSendPoCommunication(poId: string, channel: 'email' | 'portal') {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: { subject?: string; message?: string; recipient?: string }) =>
      (
        await apiClient.post<PoCommunication>(
          `/api/v1/purchase-orders/${encodeURIComponent(poId)}/communications/${channel}`,
          data,
        )
      ).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: procurementPlusKeys.poCommunications(poId) }),
  })
}

export function useEinkaufAuditTrail(docType: string, docId: string) {
  return useQuery({
    queryKey: procurementPlusKeys.auditTrail(docType, docId),
    queryFn: async () =>
      (await apiClient.get<EinkaufAuditTrail>(`/api/v1/einkauf/audit-trail/${encodeURIComponent(docType)}/${encodeURIComponent(docId)}`)).data,
    enabled: !!docType && !!docId,
    initialData: null,
    staleTime: 10 * 1000,
  })
}

export function useServiceEntrySheets() {
  return useQuery({
    queryKey: procurementPlusKeys.serviceEntrySheets(),
    queryFn: async () =>
      (await apiClient.get<{ items: ServiceEntrySheet[] }>('/api/v1/einkauf/service-entry-sheets')).data.items,
    initialData: EMPTY_SERVICE_ENTRY_SHEETS,
    staleTime: 2 * 60 * 1000,
  })
}

export function useCreateServiceEntrySheet() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: Partial<ServiceEntrySheet>) =>
      (await apiClient.post<ServiceEntrySheet>('/api/v1/einkauf/service-entry-sheets', data)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: procurementPlusKeys.serviceEntrySheets() }),
  })
}

export function useUpdateServiceEntrySheet() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<ServiceEntrySheet> }) =>
      (await apiClient.patch<ServiceEntrySheet>(`/api/v1/einkauf/service-entry-sheets/${encodeURIComponent(id)}`, data)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: procurementPlusKeys.serviceEntrySheets() }),
  })
}

export function useEdiMessages() {
  return useQuery({
    queryKey: procurementPlusKeys.ediMessages(),
    queryFn: async () => (await apiClient.get<{ items: EdiMessage[] }>('/api/v1/einkauf/edi/messages')).data.items,
    initialData: EMPTY_EDI_MESSAGES,
    staleTime: 30 * 1000,
  })
}

export function useCreateEdiMessage() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: Partial<EdiMessage>) =>
      (await apiClient.post<EdiMessage>('/api/v1/einkauf/edi/messages', data)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: procurementPlusKeys.ediMessages() }),
  })
}

export function useAckEdiMessage() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) =>
      (await apiClient.post<EdiMessage>(`/api/v1/einkauf/edi/messages/${encodeURIComponent(id)}/ack`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: procurementPlusKeys.ediMessages() }),
  })
}
