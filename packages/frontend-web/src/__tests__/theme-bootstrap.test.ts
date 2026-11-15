import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { act, renderHook } from '@testing-library/react'

const firstPaint = vi.hoisted(() => ({ dark: null as boolean | null, render: vi.fn() }))
vi.mock('react-dom/client', () => ({ default: { createRoot: () => ({
  render: () => {
    firstPaint.dark = document.documentElement.classList.contains('dark')
    firstPaint.render()
  },
}) } }))

beforeEach(() => {
  vi.resetModules()
  localStorage.clear()
  document.documentElement.className = ''
  document.documentElement.setAttribute('data-theme', 'meridian')
  document.body.innerHTML = '<div id="root"></div>'
  firstPaint.dark = null
  firstPaint.render.mockClear()
})
afterEach(() => {
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
  document.body.innerHTML = ''
  document.documentElement.className = ''
})

describe('theme before the shared renderer first mounts', () => {
  it.each([
    { stored: 'dark', systemDark: false, expected: true },
    { stored: 'light', systemDark: true, expected: false },
    { stored: null, systemDark: true, expected: true },
    { stored: 'invalid', systemDark: true, expected: true },
    { stored: null, systemDark: false, expected: false },
  ])('applies $stored with OS dark=$systemDark before first paint', async ({ stored, systemDark, expected }) => {
    if (stored !== null) localStorage.setItem('theme', stored)
    vi.stubGlobal('matchMedia', vi.fn(() => ({ matches: systemDark })))
    await import('../main')
    expect(firstPaint.render).toHaveBeenCalledOnce()
    expect(firstPaint.dark).toBe(expected)
    expect(document.documentElement.getAttribute('data-theme')).toBe('meridian')
  })

  it('uses the OS preference when browser storage is blocked', async () => {
    vi.stubGlobal('matchMedia', vi.fn(() => ({ matches: true })))
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => { throw new DOMException('Storage blocked', 'SecurityError') })
    await import('../main')
    expect(firstPaint.dark).toBe(true)
    expect(firstPaint.render).toHaveBeenCalledOnce()
  })

  it('removes a stale dark root class for a stored light preference', async () => {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'light')
    vi.stubGlobal('matchMedia', vi.fn(() => ({ matches: true })))
    await import('../main')
    expect(firstPaint.dark).toBe(false)
  })

  it('keeps theme switching usable when persistence is blocked', async () => {
    vi.stubGlobal('matchMedia', vi.fn(() => ({ matches: false })))
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new DOMException('Storage blocked', 'SecurityError') })
    const { useTheme } = await import('../hooks/useTheme')
    const { result, unmount } = renderHook(() => useTheme())
    act(() => result.current.toggleTheme())
    expect(result.current.isDark).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    unmount()
  })
})
