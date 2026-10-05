import { renderHook } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { useActionRuntime } from '@/components/mask-builder/runtime/useActionRuntime'
import { apiClient } from '@/lib/api-client'
import type { ScreenActionDefinition } from '@/components/mask-builder/schema'

vi.mock('@/lib/api-client', () => ({ apiClient: { request: vi.fn() } }))

describe('human input flow dispatch', () => {
  const action: ScreenActionDefinition = {
    key: 'calculate', label: 'Berechnen', forbiddenForAgents: true,
    inputFlow: { kind: 'humanForm', submitEndpoint: '/api/v1/bonus', method: 'POST' },
  }
  it.each(['execute', 'dryRun', 'validate', 'propose'] as const)(
    'does not submit a human form through %s', async (mode) => {
      const { result } = renderHook(() => useActionRuntime([action], { screenId: 'test', permissions: [] }))
      const response = await result.current.executeAction({ actionKey: 'calculate', mode })
      expect(response.success).toBe(false)
      expect(response.error).toContain('Eingabe')
      expect(apiClient.request).not.toHaveBeenCalled()
    },
  )
  it('retains the explicit agent prohibition even when an endpoint is present', async () => {
    const { result } = renderHook(() => useActionRuntime([
      { key: 'pay', label: 'Zahlen', forbiddenForAgents: true, commandEndpoint: '/api/v1/pay' },
    ], { screenId: 'test', permissions: [], isAgentCaller: true }))
    const response = await result.current.executeAction({ actionKey: 'pay', mode: 'execute' })
    expect(response.success).toBe(false)
    expect(response.error).toContain('gesperrt')
    expect(apiClient.request).not.toHaveBeenCalled()
  })
})
