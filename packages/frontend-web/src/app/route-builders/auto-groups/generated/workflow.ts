import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  { "module": "@/pages/workflow/workflow-monitoring", "path": "workflow-monitoring" },
  { "module": "@/pages/workflow/workflow-regeln", "path": "workflow-regeln" },
  { "module": "@/pages/workflow/workflow-sandbox", "path": "workflow-sandbox" },
  { "module": "@/pages/workflow/flow-spine-studio", "path": "flow-spine-studio" },
  { "module": "@/pages/workflow/flow-spine-order-to-cash", "path": "flow-spine-order-to-cash" },
  { "module": "@/pages/workflow/flow-spine-procure-to-pay", "path": "flow-spine-procure-to-pay" },
  { "module": "@/pages/workflow/flow-spine-inventory-to-settlement", "path": "flow-spine-inventory-to-settlement" },
  { "module": "@/pages/workflow/flow-spine-harvest-to-settlement", "path": "flow-spine-harvest-to-settlement" },
  { "module": "@/pages/workflow/flow-spine-contract-to-settlement", "path": "flow-spine-contract-to-settlement" },
  { "module": "@/pages/workflow/flow-spine-complaint-to-resolution", "path": "flow-spine-complaint-to-resolution" },
  { "module": "@/pages/workflow/flow-spine-service-to-customer", "path": "flow-spine-service-to-customer" },
  { "module": "@/pages/workflow/flow-spine-finance-to-close", "path": "flow-spine-finance-to-close" },
  { "module": "@/pages/workflow/flow-spine-compliance-to-report", "path": "flow-spine-compliance-to-report" },
]
