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

export const useLive = create<LiveState>((set) => ({
  sales: {},
  inventory: {},
  policy: [],
  workflow: {},
  setSalesDoc: (d) => set(s => ({ sales: { ...s.sales, [d.id]: d } })),
  setInventoryEvt: (e) => set(s => ({ inventory: { ...s.inventory, [e.sku]: e } })),
  pushPolicy: (a) => set(s => {
    const seen = new Set(s.policy.map(p => p.id))
    if (seen.has(a.id)) return s
    return { policy: [a, ...s.policy].slice(0, 100) }
  }),
  sweepPolicy: (ttlMs) => set(s => ({ policy: s.policy.filter(p => Date.now() - p.ts < ttlMs) })),
  setWorkflowEvent: (e) => set(s => ({
    workflow: { ...s.workflow, [`${e.domain}:${e.number}`]: e }
  })),
}))