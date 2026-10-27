import { beforeEach, describe, expect, it } from 'vitest'

import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import {
  WORKSPACE_COMPOSITION_STORAGE_KEY,
  clearWorkspaceCompositionSession,
  initialWorkspaceCompositionDraft,
  isSpecializedKindEnabled,
  moveWorkspaceView,
  readWorkspaceCompositionSession,
  resolveComposableWorkspace,
  saveWorkspaceCompositionSession,
  workspaceCompositionStorageKey,
  setSpecializedKindEnabled,
} from '@/studio/workspace-composition-session'

function memoryStorage(seed: Record<string, string> = {}): Storage {
  const map = new Map(Object.entries(seed))
  return {
    get length() {
      return map.size
    },
    clear: () => map.clear(),
    getItem: (key: string) => map.get(key) ?? null,
    key: (index: number) => [...map.keys()][index] ?? null,
    removeItem: (key: string) => {
      map.delete(key)
    },
    setItem: (key: string, value: string) => {
      map.set(key, value)
    },
  }
}

describe('WorkspaceComposition Session Compose', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
  })

  it('speichert nur gültige Compositions unter valeo.workspace.composition in localStorage', () => {
    const ok = saveWorkspaceCompositionSession(WORKSPACE_COMPOSITION_FIXTURE)
    expect(ok.ok).toBe(true)
    expect(localStorage.getItem(WORKSPACE_COMPOSITION_STORAGE_KEY)).toContain(
      'workspace.disposition-und-inbox',
    )
  })

  it('speichert nur gültige Compositions unter valeo.workspace.composition', () => {
    const storage = memoryStorage()
    const ok = saveWorkspaceCompositionSession(WORKSPACE_COMPOSITION_FIXTURE, storage)
    expect(ok.ok).toBe(true)
    expect(storage.getItem(WORKSPACE_COMPOSITION_STORAGE_KEY)).toContain(
      'workspace.disposition-und-inbox',
    )

    const broken = {
      ...WORKSPACE_COMPOSITION_FIXTURE,
      specializedComponents: [
        {
          ...WORKSPACE_COMPOSITION_FIXTURE.specializedComponents[0],
          hostViewId: 'gibt-es-nicht',
        },
      ],
    }
    const rejected = saveWorkspaceCompositionSession(broken, storage)
    expect(rejected.ok).toBe(false)
    expect(storage.getItem(WORKSPACE_COMPOSITION_STORAGE_KEY)).toContain(
      'workspace.disposition-und-inbox',
    )
  })

  it('liest ungültige Session als invalid ohne stilles Mounten', () => {
    const storage = memoryStorage({
      [WORKSPACE_COMPOSITION_STORAGE_KEY]: JSON.stringify({
        ...WORKSPACE_COMPOSITION_FIXTURE,
        id: '',
      }),
    })
    const read = readWorkspaceCompositionSession(storage)
    expect(read.status).toBe('invalid')
    if (read.status !== 'invalid') return
    expect(read.issues.length).toBeGreaterThan(0)

    const initial = initialWorkspaceCompositionDraft(storage)
    expect(initial.mounted).toBeNull()
    expect(initial.issues.length).toBeGreaterThan(0)
    expect(initial.source).toBe('session-invalid')
  })

  it('schaltet inbox und disposition_board an und ab und hält Validator grün', () => {
    let draft = setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'inbox', false)
    expect(isSpecializedKindEnabled(draft, 'inbox')).toBe(false)
    expect(isSpecializedKindEnabled(draft, 'disposition_board')).toBe(true)
    expect(draft.fachaktionRefs.some((a) => a.specializedComponentId === 'slot-document-inbox')).toBe(
      false,
    )
    expect(resolveComposableWorkspace(draft).ok).toBe(true)

    draft = setSpecializedKindEnabled(draft, 'disposition_board', false)
    expect(draft.specializedComponents).toEqual([])
    expect(resolveComposableWorkspace(draft).ok).toBe(true)

    draft = setSpecializedKindEnabled(draft, 'inbox', true)
    expect(isSpecializedKindEnabled(draft, 'inbox')).toBe(true)
    expect(draft.fachaktionRefs.some((a) => a.id === 'action-open-inbox-item')).toBe(true)
    expect(resolveComposableWorkspace(draft).ok).toBe(true)
  })

  it('ändert die View-Reihenfolge deterministisch', () => {
    const moved = moveWorkspaceView(WORKSPACE_COMPOSITION_FIXTURE, 'beleg-inbox-host', 'up')
    expect(moved.views.map((v) => v.id)).toEqual(['beleg-inbox-host', 'dispo-cockpit'])
    expect(moved.views[0].order).toBe(10)
    expect(moved.views[1].order).toBe(20)
    expect(resolveComposableWorkspace(moved).ok).toBe(true)
  })

  it('clear entfernt den Session-Eintrag', () => {
    const storage = memoryStorage()
    saveWorkspaceCompositionSession(WORKSPACE_COMPOSITION_FIXTURE, storage)
    clearWorkspaceCompositionSession(storage)
    expect(readWorkspaceCompositionSession(storage).status).toBe('empty')
  })

  it('verwirft ungueltiges JSON und liest Default aus localStorage', () => {
    localStorage.setItem(WORKSPACE_COMPOSITION_STORAGE_KEY, '{nicht-json')
    const read = readWorkspaceCompositionSession()
    expect(read.status).toBe('invalid')
    if (read.status !== 'invalid') return
    expect(read.issues.some((i) => i.code === 'session_json')).toBe(true)
  })

  it('zieht fuer sessionStorage-Aufrufer auf localStorage nach wenn Key dort leer', () => {
    saveWorkspaceCompositionSession(WORKSPACE_COMPOSITION_FIXTURE)
    sessionStorage.removeItem(WORKSPACE_COMPOSITION_STORAGE_KEY)
    const read = readWorkspaceCompositionSession(sessionStorage)
    expect(read.status).toBe('ok')
    if (read.status !== 'ok') return
    expect(read.composition.id).toBe('workspace.disposition-und-inbox')
  })

  it('hängt sub an den Composition-Key und liest den globalen Key nur wenn der Nutzer-Key leer ist', () => {
    const subject = 'person-a'
    const userKey = workspaceCompositionStorageKey(subject)
    expect(workspaceCompositionStorageKey(null)).toBe(WORKSPACE_COMPOSITION_STORAGE_KEY)
    expect(userKey).toBe(`${WORKSPACE_COMPOSITION_STORAGE_KEY}.${subject}`)

    const storage = memoryStorage({
      [WORKSPACE_COMPOSITION_STORAGE_KEY]: JSON.stringify(WORKSPACE_COMPOSITION_FIXTURE),
    })
    const fallback = readWorkspaceCompositionSession(storage, subject)
    expect(fallback.status).toBe('ok')
    expect(storage.getItem(userKey)).toBeNull()

    const saved = saveWorkspaceCompositionSession(
      setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'inbox', false),
      storage,
      subject,
    )
    expect(saved.ok).toBe(true)
    expect(storage.getItem(userKey)).toContain('workspace.disposition-und-inbox')
    expect(storage.getItem(WORKSPACE_COMPOSITION_STORAGE_KEY)).toContain('"kind":"inbox"')
    const read = readWorkspaceCompositionSession(storage, subject)
    expect(read.status).toBe('ok')
    if (read.status !== 'ok') return
    expect(read.composition.specializedComponents.some((slot) => slot.kind === 'inbox')).toBe(false)

    storage.setItem(userKey, '{kein-json')
    expect(readWorkspaceCompositionSession(storage, subject).status).toBe('invalid')
  })

  it('hängt den Mandanten vor die sub und liest den nächst allgemeineren Key einmal', () => {
    const subject = 'person-a'
    const tenant = 'haus-a'
    const userKey = workspaceCompositionStorageKey(subject)
    const activeKey = workspaceCompositionStorageKey(subject, tenant)
    expect(workspaceCompositionStorageKey(subject, ' ')).toBe(userKey)
    expect(workspaceCompositionStorageKey(null, tenant)).toBe(WORKSPACE_COMPOSITION_STORAGE_KEY)
    expect(activeKey).toBe(`${WORKSPACE_COMPOSITION_STORAGE_KEY}.${tenant}.${subject}`)

    const userComposition = setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'inbox', false)
    const storage = memoryStorage({
      [WORKSPACE_COMPOSITION_STORAGE_KEY]: JSON.stringify(WORKSPACE_COMPOSITION_FIXTURE),
      [userKey]: JSON.stringify(userComposition),
    })
    const fromUser = readWorkspaceCompositionSession(storage, subject, tenant)
    expect(fromUser.status).toBe('ok')
    if (fromUser.status !== 'ok') return
    expect(fromUser.composition.specializedComponents.some((slot) => slot.kind === 'inbox')).toBe(false)

    storage.removeItem(userKey)
    const fromGlobal = readWorkspaceCompositionSession(storage, subject, tenant)
    expect(fromGlobal.status).toBe('ok')
    if (fromGlobal.status !== 'ok') return
    expect(fromGlobal.composition.specializedComponents.some((slot) => slot.kind === 'inbox')).toBe(true)

    const saved = saveWorkspaceCompositionSession(userComposition, storage, subject, tenant)
    expect(saved.ok).toBe(true)
    expect(storage.getItem(activeKey)).toContain('workspace.disposition-und-inbox')
    expect(storage.getItem(userKey)).toBeNull()
    expect(storage.getItem(WORKSPACE_COMPOSITION_STORAGE_KEY)).toContain('"kind":"inbox"')
    const read = readWorkspaceCompositionSession(storage, subject, tenant)
    expect(read.status).toBe('ok')
    if (read.status !== 'ok') return
    expect(read.composition.specializedComponents.some((slot) => slot.kind === 'inbox')).toBe(false)
  })
})
