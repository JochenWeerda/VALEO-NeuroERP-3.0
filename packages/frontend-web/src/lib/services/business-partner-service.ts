import { apiClient } from '@/lib/api-client'

export type BusinessPartnerEnvelope = {
  business_partner: {
    core_identity: {
      partner_id?: string
      partner_number: string
      matchcode?: string | null
      name_1: string
      name_2?: string | null
      legal_form?: string | null
      street?: string | null
      house_number?: string | null
      postal_code?: string | null
      city?: string | null
      country?: string | null
      state?: string | null
      language?: string | null
      status: 'active' | 'inactive' | 'blocked'
    }
    roles: {
      is_customer: boolean
      is_supplier: boolean
      is_carrier: boolean
      is_employee: boolean
      is_service_provider: boolean
    }
    contact_data: {
      phone?: string | null
      mobile?: string | null
      email?: string | null
      website?: string | null
      fax?: string | null
    }
    banking: {
      iban?: string | null
      bic?: string | null
      bank_name?: string | null
      sepa_mandate_reference?: string | null
      sepa_mandate_signed_at?: string | null
    }
    finance: {
      debtor_account?: string | null
      creditor_account?: string | null
      tax_number?: string | null
      vat_id?: string | null
      tax_type?: string | null
      payment_terms_id?: string | null
      credit_limit?: number | null
      dunning_level?: number | null
      blocked_for_delivery: boolean
      blocked_for_invoice: boolean
    }
    agrar_extension: Record<string, unknown>
    logistics: Record<string, unknown>
    marketing_consent: Record<string, unknown>
    gdpr: Record<string, unknown>
    legacy_customer_fields?: Record<string, unknown>
    audit: {
      created_at?: string | null
      created_by?: string | null
      updated_at?: string | null
      updated_by?: string | null
    }
  }
}

export type DiscountItem = {
  id: string
  partner_id: string
  article_number: string
  description?: string | null
  discount_percent: number
  valid_from?: string | null
  valid_to?: string | null
  discount_list_number?: string | null
  source_type?: 'import' | 'batch' | 'internal' | null
  created_by?: string | null
  updated_by?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export type DiscountItemPayload = {
  article_number: string
  description?: string | null
  discount_percent: number
  valid_from?: string | null
  valid_to?: string | null
  discount_list_number?: string | null
  source_type?: 'import' | 'batch' | 'internal' | null
  created_by?: string | null
  updated_by?: string | null
}

export type PriceAgreement = {
  id: string
  partner_id: string
  article_number: string
  description?: string | null
  valid_from?: string | null
  valid_to?: string | null
  price_net?: number | null
  price_incl_freight?: number | null
  price_unit?: string | null
  discount_allowed: boolean
  special_freight?: number | null
  payment_condition?: string | null
  source_type?: 'import' | 'batch' | 'internal' | null
  operator_name?: string | null
  operator_date?: string | null
  created_by?: string | null
  updated_by?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export type PriceAgreementPayload = {
  article_number: string
  description?: string | null
  valid_from?: string | null
  valid_to?: string | null
  price_net?: number | null
  price_incl_freight?: number | null
  price_unit?: string | null
  discount_allowed: boolean
  special_freight?: number | null
  payment_condition?: string | null
  source_type?: 'import' | 'batch' | 'internal' | null
  operator_name?: string | null
  operator_date?: string | null
  created_by?: string | null
  updated_by?: string | null
}

export type Instruction = {
  id: string
  partner_id: string
  instruction_text: string
  instruction_priority: 'low' | 'normal' | 'high' | 'critical'
  valid_from?: string | null
  valid_to?: string | null
  created_by?: string | null
  updated_by?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export type Address = {
  id: string
  partner_id: string
  address_type: 'customer' | 'invoice' | 'shipping' | 'postal'
  name_1?: string | null
  name_2?: string | null
  name_3?: string | null
  street?: string | null
  house_number?: string | null
  country?: string | null
  postal_code?: string | null
  city?: string | null
  po_box?: string | null
  po_box_postal_code?: string | null
  po_box_city?: string | null
  phone?: string | null
  fax?: string | null
  email?: string | null
  website?: string | null
  salutation?: string | null
  brief_salutation?: string | null
  free_field_1?: string | null
  free_field_2?: string | null
  free_field_3?: string | null
  area_code?: string | null
  is_default: boolean
  created_by?: string | null
  updated_by?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export type AddressPayload = Omit<Address, 'id' | 'partner_id' | 'created_at' | 'updated_at'>

export type BillingConfig = {
  id: string
  partner_id: string
  customer_group?: string | null
  customer_type?: 'standard' | 'organ' | 'group_internal' | null
  account_statement_print: boolean
  account_statement_separate: boolean
  account_statement_reprint: boolean
  last_account_statement_number?: number | null
  last_account_statement_date?: string | null
  account_balance?: number | null
  print_ad_text: boolean
  shipping_expenses_enabled: boolean
  settlement_mode?: 'single' | 'collective' | null
  admin_overhead_surcharge_percent?: number | null
  invoice_number_range?: string | null
  bonus_eligible: boolean
  self_billing_sales: boolean
  self_billing_purchase: boolean
  remarkable_claim: boolean
  vat_optimizer: boolean
  created_by?: string | null
  updated_by?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export type BillingConfigPayload = Omit<BillingConfig, 'id' | 'partner_id' | 'created_at' | 'updated_at'>

export type CpdAccount = {
  id: string
  partner_id: string
  cpd_customer_number: string
  debtor_account?: string | null
  search_term?: string | null
  name_1: string
  name_2?: string | null
  name_3?: string | null
  street?: string | null
  house_number?: string | null
  country?: string | null
  postal_code?: string | null
  city?: string | null
  po_box?: string | null
  po_box_city?: string | null
  phone_1?: string | null
  phone_2?: string | null
  fax?: string | null
  salutation?: string | null
  brief_salutation?: string | null
  email?: string | null
  website?: string | null
  branch_office?: string | null
  cost_center?: string | null
  invoice_type?: string | null
  collective_invoice: boolean
  invoice_form_template?: string | null
  sales_representative?: string | null
  area_code?: string | null
  cash_discount_percent?: number | null
  cash_discount_days?: number | null
  payment_target_days?: number | null
  created_by?: string | null
  updated_by?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export type CpdAccountPayload = Omit<CpdAccount, 'id' | 'partner_id' | 'created_at' | 'updated_at'>

export const businessPartnerService = {
  async list(params?: { search?: string; status?: string }) {
    const response = await apiClient.get<BusinessPartnerEnvelope[]>('/api/v1/crm/business-partners/', {
      params,
    })
    return response.data
  },

  async get(partnerId: string) {
    const response = await apiClient.get<BusinessPartnerEnvelope>(`/api/v1/crm/business-partners/${partnerId}`)
    return response.data
  },

  async create(payload: BusinessPartnerEnvelope) {
    const response = await apiClient.post<BusinessPartnerEnvelope>('/api/v1/crm/business-partners/', payload)
    return response.data
  },

  async update(partnerId: string, payload: BusinessPartnerEnvelope) {
    const response = await apiClient.put<BusinessPartnerEnvelope>(
      `/api/v1/crm/business-partners/${partnerId}`,
      payload,
    )
    return response.data
  },

  async listDiscountItems(partnerId: string) {
    const response = await apiClient.get<DiscountItem[]>(`/api/v1/crm/business-partners/${partnerId}/discount-items`)
    return response.data
  },

  async createDiscountItem(partnerId: string, payload: DiscountItemPayload) {
    const response = await apiClient.post<DiscountItem>(
      `/api/v1/crm/business-partners/${partnerId}/discount-items`,
      payload,
    )
    return response.data
  },

  async updateDiscountItem(partnerId: string, itemId: string, payload: DiscountItemPayload) {
    const response = await apiClient.put<DiscountItem>(
      `/api/v1/crm/business-partners/${partnerId}/discount-items/${itemId}`,
      payload,
    )
    return response.data
  },

  async deleteDiscountItem(partnerId: string, itemId: string) {
    await apiClient.delete(`/api/v1/crm/business-partners/${partnerId}/discount-items/${itemId}`)
  },

  async listPriceAgreements(partnerId: string) {
    const response = await apiClient.get<PriceAgreement[]>(`/api/v1/crm/business-partners/${partnerId}/price-agreements`)
    return response.data
  },

  async createPriceAgreement(partnerId: string, payload: PriceAgreementPayload) {
    const response = await apiClient.post<PriceAgreement>(
      `/api/v1/crm/business-partners/${partnerId}/price-agreements`,
      payload,
    )
    return response.data
  },

  async updatePriceAgreement(partnerId: string, agreementId: string, payload: PriceAgreementPayload) {
    const response = await apiClient.put<PriceAgreement>(
      `/api/v1/crm/business-partners/${partnerId}/price-agreements/${agreementId}`,
      payload,
    )
    return response.data
  },

  async deletePriceAgreement(partnerId: string, agreementId: string) {
    await apiClient.delete(`/api/v1/crm/business-partners/${partnerId}/price-agreements/${agreementId}`)
  },

  async listInstructions(partnerId: string) {
    const response = await apiClient.get<Instruction[]>(`/api/v1/crm/business-partners/${partnerId}/instructions`)
    return response.data
  },

  async listAddresses(partnerId: string) {
    const response = await apiClient.get<Address[]>(`/api/v1/crm/business-partners/${partnerId}/addresses`)
    return response.data
  },

  async createAddress(partnerId: string, payload: AddressPayload) {
    const response = await apiClient.post<Address>(`/api/v1/crm/business-partners/${partnerId}/addresses`, payload)
    return response.data
  },

  async updateAddress(partnerId: string, addressId: string, payload: AddressPayload) {
    const response = await apiClient.put<Address>(
      `/api/v1/crm/business-partners/${partnerId}/addresses/${addressId}`,
      payload,
    )
    return response.data
  },

  async deleteAddress(partnerId: string, addressId: string) {
    await apiClient.delete(`/api/v1/crm/business-partners/${partnerId}/addresses/${addressId}`)
  },

  async getBillingConfig(partnerId: string) {
    const response = await apiClient.get<BillingConfig>(`/api/v1/crm/business-partners/${partnerId}/billing-config`)
    return response.data
  },

  async putBillingConfig(partnerId: string, payload: BillingConfigPayload) {
    const response = await apiClient.put<BillingConfig>(
      `/api/v1/crm/business-partners/${partnerId}/billing-config`,
      payload,
    )
    return response.data
  },

  async patchBillingConfig(partnerId: string, payload: Partial<BillingConfigPayload>) {
    const response = await apiClient.patch<BillingConfig>(
      `/api/v1/crm/business-partners/${partnerId}/billing-config`,
      payload,
    )
    return response.data
  },

  async listCpdAccounts(partnerId: string) {
    const response = await apiClient.get<CpdAccount[]>(`/api/v1/crm/business-partners/${partnerId}/cpd-accounts`)
    return response.data
  },

  async createCpdAccount(partnerId: string, payload: CpdAccountPayload) {
    const response = await apiClient.post<CpdAccount>(`/api/v1/crm/business-partners/${partnerId}/cpd-accounts`, payload)
    return response.data
  },

  async updateCpdAccount(partnerId: string, accountId: string, payload: CpdAccountPayload) {
    const response = await apiClient.put<CpdAccount>(
      `/api/v1/crm/business-partners/${partnerId}/cpd-accounts/${accountId}`,
      payload,
    )
    return response.data
  },

  async deleteCpdAccount(partnerId: string, accountId: string) {
    await apiClient.delete(`/api/v1/crm/business-partners/${partnerId}/cpd-accounts/${accountId}`)
  },
}
