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
  setSalesDoc: (d: SalesDoc) => void
  setInventoryEvt: (e: InventoryEvent) => void
  pushPolicy: (a: PolicyAlert) => void
  sweepPolicy: (ttlMs: number) => void
  setWorkflowEvent: (e: WorkflowEvent) => void
}

const POLICY_HISTORY_LIMIT = 100

export const useLive = create<LiveState>((set) => ({
  sales: {},
  inventory: {},
  policy: [],
  workflow: {},
  setSalesDoc: (doc: SalesDoc): void => {
    set((state) => ({
      sales: {
        ...state.sales,
        [doc.id]: doc,
      },
    }))
  },
  setInventoryEvt: (event: InventoryEvent): void => {
    set((state) => ({
      inventory: {
        ...state.inventory,
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
  sweepPolicy: (ttlMs: number): void => {
    set((state) => ({
      policy: state.policy.filter((item) => Date.now() - item.ts < ttlMs),
    }))
  },
  setWorkflowEvent: (event: WorkflowEvent): void => {
    set((state) => ({
      workflow: {
        ...state.workflow,
        [`${event.domain}:${event.number}`]: event,
      },
    }))
  },
}))
