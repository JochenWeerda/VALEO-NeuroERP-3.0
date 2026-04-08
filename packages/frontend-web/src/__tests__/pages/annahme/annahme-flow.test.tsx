/**
 * Annahme-Kernflow Tests (Wave 91)
 * Gap 002, 021, 023, 024
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'

// ============================================================
// Gruppe 1: useTouchDevice() Hook — JSDOM-Sicherheit
// ============================================================

describe('useTouchDeviceHook', () => {
  it('window.matchMedia ist in Testumgebung vorhanden (test-setup.ts Stub)', () => {
    expect(typeof window.matchMedia).toBe('function')
  })

  it('useTouchDevice() gibt false zurueck wenn matchMedia stub matches=false', async () => {
    const { useTouchDevice } = await import('@/hooks/useTouchDevice')
    expect(useTouchDevice()).toBe(false)
  })

  it('useTouchDevice() gibt false zurueck wenn matchMedia wirft', async () => {
    const original = window.matchMedia
    ;(window as any).matchMedia = () => { throw new Error('matchMedia not supported') }
    // Re-import forces re-evaluation of the module
    vi.resetModules()
    const { useTouchDevice } = await import('@/hooks/useTouchDevice')
    expect(useTouchDevice()).toBe(false)
    ;(window as any).matchMedia = original
  })
})

// ============================================================
// Gruppe 2: buildCoreMaskShortcuts — Shortcut-Definitionen
// ============================================================

describe('CoreMaskShortcuts', () => {
  it('buildCoreMaskShortcuts produziert Ctrl+S Shortcut', async () => {
    const { buildCoreMaskShortcuts } = await import('@/hooks/useKeyboardShortcuts')
    const onSave = vi.fn()
    const shortcuts = buildCoreMaskShortcuts({ onSave })
    const saveShortcut = shortcuts.find((s) => s.key === 's' && s.ctrl)
    expect(saveShortcut).toBeDefined()
    expect(saveShortcut?.label).toBe('Speichern')
  })

  it('buildCoreMaskShortcuts produziert Escape Shortcut', async () => {
    const { buildCoreMaskShortcuts } = await import('@/hooks/useKeyboardShortcuts')
    const shortcuts = buildCoreMaskShortcuts({ onCancel: vi.fn() })
    const escShortcut = shortcuts.find((s) => s.key === 'Escape')
    expect(escShortcut).toBeDefined()
    expect(escShortcut?.label).toBe('Abbrechen')
  })

  it('buildCoreMaskShortcuts disabled=true deaktiviert Speichern-Shortcut', async () => {
    const { buildCoreMaskShortcuts } = await import('@/hooks/useKeyboardShortcuts')
    const shortcuts = buildCoreMaskShortcuts({ onSave: vi.fn(), isSaveDisabled: true })
    const saveShortcut = shortcuts.find((s) => s.key === 's' && s.ctrl)
    expect(saveShortcut?.disabled).toBe(true)
  })

  it('formatShortcutLabel gibt String mit "S" zurueck fuer Ctrl+S', async () => {
    const { formatShortcutLabel } = await import('@/hooks/useKeyboardShortcuts')
    const label = formatShortcutLabel({ key: 's', ctrl: true })
    expect(typeof label).toBe('string')
    expect(label).toMatch(/S/)
  })
})

// ============================================================
// Gruppe 3: useTouchDevice re-export Kompatibilitaet
// ============================================================

describe('TouchFieldLayoutReexport', () => {
  it('useTouchDevice re-export aus TouchFieldLayout ist Funktion', async () => {
    const mod = await import('@/components/touch/TouchFieldLayout')
    expect(typeof mod.useTouchDevice).toBe('function')
  })

  it('useTouchDevice re-export gibt false zurueck im JSDOM', async () => {
    const mod = await import('@/components/touch/TouchFieldLayout')
    expect(mod.useTouchDevice()).toBe(false)
  })
})

// ============================================================
// Gruppe 4: useKeyboardShortcuts — Event-Listener
// ============================================================

describe('useKeyboardShortcutsListener', () => {
  it('useKeyboardShortcuts registriert keydown-Listener auf window', async () => {
    const addSpy = vi.spyOn(window, 'addEventListener')
    const { useKeyboardShortcuts } = await import('@/hooks/useKeyboardShortcuts')
    const TestComp = () => {
      useKeyboardShortcuts([{ key: 's', ctrl: true, label: 'Test', action: vi.fn() }])
      return <div />
    }
    render(<TestComp />)
    const keydownCalls = addSpy.mock.calls.filter((c) => c[0] === 'keydown')
    expect(keydownCalls.length).toBeGreaterThan(0)
    addSpy.mockRestore()
  })

  it('Ctrl+S Shortcut-Action wird aufgerufen', async () => {
    const { useKeyboardShortcuts } = await import('@/hooks/useKeyboardShortcuts')
    const onSave = vi.fn()
    const TestComp = () => {
      useKeyboardShortcuts([{ key: 's', ctrl: true, label: 'Speichern', action: onSave, allowInInputs: true }])
      return <div />
    }
    render(<TestComp />)
    fireEvent.keyDown(window, { key: 's', ctrlKey: true })
    expect(onSave).toHaveBeenCalledOnce()
  })
})

// ============================================================
// Gruppe 5: Annahme-Seiten existieren als Default-Exports
// ============================================================

vi.mock('@/lib/axios', () => ({
  api: { post: vi.fn().mockResolvedValue({ data: { id: 'att-1' } }) },
}))
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: vi.fn() }),
}))
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>()
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useLocation: () => ({ state: null, pathname: '/annahme', search: '', hash: '', key: 'default' }),
    useSearchParams: () => [new URLSearchParams(), vi.fn()],
  }
})
vi.mock('@/components/navigation/ModuleToolbar', () => ({
  ModuleToolbar: ({ title }: { title: string }) => React.createElement('div', { 'data-testid': 'module-toolbar' }, title),
}))
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: vi.fn().mockResolvedValue({ data: { id: 'qp-1', reference_context: null } }),
    get: vi.fn().mockResolvedValue({ data: [] }),
  },
}))
vi.mock('@/lib/api/inventory', () => ({
  useWarteschlangeEintrag: () => ({ data: null }),
  usePatchWarteschlangeStatus: () => ({ mutate: vi.fn() }),
}))
vi.mock('@/policy/decision-view', () => ({
  buildDecisionView: () => null,
}))
vi.mock('@/components/workflow/ProcessStatusPanel', () => ({
  ProcessStatusPanel: () => React.createElement('div', { 'data-testid': 'process-status-panel' }),
}))
vi.mock('@/components/workflow/CompactDecisionCard', () => ({
  CompactDecisionCard: () => React.createElement('div'),
}))
vi.mock('@/components/ErrorState', () => ({
  ErrorState: () => React.createElement('div', null, 'Fehler'),
}))
vi.mock('@/features/workflow/useApprovalDensityProfile', () => ({
  useApprovalDensityProfile: () => null,
}))
vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query')
  return {
    ...actual,
    useMutation: () => ({ mutate: vi.fn(), mutateAsync: vi.fn().mockResolvedValue({}), isPending: false, data: null }),
    useQuery: () => ({ data: null, isLoading: false, isError: false, refetch: vi.fn() }),
    useQueryClient: () => ({ invalidateQueries: vi.fn() }),
  }
})

describe('AnnahmeFlowSeiten', () => {
  it('lkw-registrierung exportiert default-Komponente', async () => {
    const mod = await import('@/pages/annahme/lkw-registrierung')
    expect(typeof mod.default).toBe('function')
  })

  it('qualitaets-check exportiert default-Komponente', async () => {
    const mod = await import('@/pages/annahme/qualitaets-check')
    expect(typeof mod.default).toBe('function')
  })

  it('abrechnung exportiert default-Komponente', async () => {
    const mod = await import('@/pages/annahme/abrechnung')
    expect(typeof mod.default).toBe('function')
  })

  it('LKWRegistrierungPage rendert ohne Fehler', async () => {
    const { default: Page } = await import('@/pages/annahme/lkw-registrierung')
    expect(() => render(React.createElement(Page))).not.toThrow()
  })

  it('QualitaetsCheckPage rendert ohne Fehler', async () => {
    const { default: Page } = await import('@/pages/annahme/qualitaets-check')
    expect(() => render(React.createElement(Page))).not.toThrow()
  })

  it('AnnahmeAbrechnungPage rendert ohne Fehler', async () => {
    const { default: Page } = await import('@/pages/annahme/abrechnung')
    expect(() => render(React.createElement(Page))).not.toThrow()
  })
})
