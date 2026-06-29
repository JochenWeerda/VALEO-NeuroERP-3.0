import { describe, expect, it } from 'vitest'
import { generateAgentMaskContract } from '@/components/mask-builder/runtime/generateAgentMaskContract'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const baseScreen: ScreenDefinition = {
  schemaVersion: 1,
  id: 'crm/customer-360',
  domain: 'crm',
  mode: 'detail',
  title: 'Kundenstamm',
  fields: [
    { key: 'name', label: 'Name', type: 'text', required: true },
    { key: 'iban', label: 'IBAN', type: 'text' },
    { key: 'email', label: 'E-Mail', type: 'text', readOnly: true },
  ],
  tabs: [
    {
      key: 'kontakt',
      label: 'Kontakt',
      fields: [{ key: 'phone', label: 'Telefon', type: 'text' }],
    },
  ],
  actions: [
    { key: 'freigeben', label: 'Freigeben', humanApprovalRequired: true, auditReasonRequired: true },
    { key: 'loeschen', label: 'Loeschen', dangerLevel: 'destructive', requiresConfirmation: true },
  ],
}

describe('generateAgentMaskContract', () => {
  it('derives screenId and domain correctly', () => {
    const contract = generateAgentMaskContract(baseScreen)
    expect(contract.screenId).toBe('crm/customer-360')
    expect(contract.domain).toBe('crm')
    expect(contract.contractVersion).toBe(1)
  })

  it('collects fields from root and tabs', () => {
    const contract = generateAgentMaskContract(baseScreen)
    expect(contract.readableFields).toContain('name')
    expect(contract.readableFields).toContain('iban')
    expect(contract.readableFields).toContain('phone')
  })

  it('excludes readOnly fields from editableFields', () => {
    const contract = generateAgentMaskContract(baseScreen)
    expect(contract.editableFields).toContain('name')
    expect(contract.editableFields).not.toContain('email')
  })

  it('detects sensitive fields by key pattern', () => {
    const contract = generateAgentMaskContract(baseScreen)
    expect(contract.sensitiveFields).toContain('iban')
    expect(contract.sensitiveFields).not.toContain('name')
  })

  it('creates blocking validation rules for required fields', () => {
    const contract = generateAgentMaskContract(baseScreen)
    const nameRule = contract.validationRules.find((r) => r.fieldKey === 'name')
    expect(nameRule).toBeDefined()
    expect(nameRule!.severity).toBe('blocking')
    expect(nameRule!.rule).toBe('required')
    // non-required fields should not have rules
    expect(contract.validationRules.find((r) => r.fieldKey === 'email')).toBeUndefined()
  })

  it('maps actions with humanApprovalRequired', () => {
    const contract = generateAgentMaskContract(baseScreen)
    const freigeben = contract.availableActions.find((a) => a.key === 'freigeben')
    expect(freigeben!.requiresHumanApproval).toBe(true)
    const loeschen = contract.availableActions.find((a) => a.key === 'loeschen')
    expect(loeschen!.dangerLevel).toBe('destructive')
    expect(loeschen!.requiresConfirmation).toBe(true)
  })

  it('generates auditRequirements for actions with auditReasonRequired', () => {
    const contract = generateAgentMaskContract(baseScreen)
    const audit = contract.auditRequirements.find((a) => a.actionKey === 'freigeben')
    expect(audit).toBeDefined()
    expect(audit!.requiresReason).toBe(true)
  })

  it('generates default testSelectors', () => {
    const contract = generateAgentMaskContract(baseScreen)
    expect(contract.testSelectors['screenRoot']).toBe('[data-testid="screen-crm/customer-360"]')
    expect(contract.testSelectors['submitButton']).toBe('[data-testid="form-submit-btn"]')
  })

  it('explicit agentContract overrides generated fields', () => {
    const screen: ScreenDefinition = {
      ...baseScreen,
      agentContract: {
        ...generateAgentMaskContract(baseScreen),
        businessPurpose: 'Explizit gesetzt',
        forbiddenAgentTasks: ['Kunden loeschen'],
        examplePrompts: ['Zeige alle Kunden aus Bayern'],
      },
    }
    const contract = generateAgentMaskContract(screen)
    expect(contract.businessPurpose).toBe('Explizit gesetzt')
    expect(contract.forbiddenAgentTasks).toContain('Kunden loeschen')
    expect(contract.examplePrompts).toContain('Zeige alle Kunden aus Bayern')
  })

  it('handles screen with no fields or tabs gracefully', () => {
    const empty: ScreenDefinition = {
      schemaVersion: 1,
      id: 'platform/empty',
      domain: 'platform',
      mode: 'list',
      title: 'Empty',
    }
    const contract = generateAgentMaskContract(empty)
    expect(contract.readableFields).toEqual([])
    expect(contract.validationRules).toEqual([])
    expect(contract.availableActions).toEqual([])
  })
})
