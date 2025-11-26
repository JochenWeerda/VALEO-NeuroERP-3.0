import { create } from 'zustand'

type SalesDoc = { id: string; number: string; status: string; total?: number; updatedAt: number }
type InventoryEvent = { sku: string; delta: number; qty: number; ts: number }
type PolicyAlert = { id: string; title: string; message: string; severity: 'warn' | 'crit'; ts: number }
type WorkflowEvent = { domain: string; number: string; from: string; to: string; action: string; ts: number }

type LiveState = {
  sales: Record<string, SalesDoc>
  inventory: Record<string, InventoryEvent>
  policy: PolicyAlert[]
  workflow: Record<string, WorkflowEvent>
  setSalesDoc: (_d: SalesDoc) => void
  setInventoryEvt: (_e: InventoryEvent) => void
  pushPolicy: (_a: PolicyAlert) => void
  sweepPolicy: (_ttlMs: number) => void
  setWorkflowEvent: (_e: WorkflowEvent) => void
}

const POLICY_HISTORY_LIMIT = 100

export const useLive = create<LiveState>((set) => ({
  sales: {},
  inventory: {},
  policy: [],
  workflow: {},
  setSalesDoc: (doc: SalesDoc): void => {
    set((_state) => ({
      sales: {
        ..._state.sales,
        [doc.id]: doc,
      },
    }))
  },
  setInventoryEvt: (event: InventoryEvent): void => {
    set((_state) => ({
      inventory: {
        ..._state.inventory,
        [event.sku]: event,
      },
    }))
  },
  pushPolicy: (alert: PolicyAlert): void => {
    set((state) => {
      const alreadyKnown = state.policy.some((item) => item.id === alert.id)
      if (alreadyKnown) {
        return { policy: state.policy }
      }
      return {
        policy: [alert, ...state.policy].slice(0, POLICY_HISTORY_LIMIT),
      }
    })
  },
  sweepPolicy: (_ttlMs: number): void => {
    set((_state) => ({
      policy: _state.policy.filter((item) => Date.now() - item.ts < _ttlMs),
    }))
  },
  setWorkflowEvent: (event: WorkflowEvent): void => {
    set((_state) => ({
      workflow: {
        ..._state.workflow,
        [`${event.domain}:${event.number}`]: event,
      },
    }))
  },
}))
