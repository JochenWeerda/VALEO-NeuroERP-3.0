import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/agribusiness/farmers",
    "path": "farmers"
  },
  {
    "module": "@/pages/agribusiness/field-service-tasks",
    "path": "field-service-tasks"
  },
  {
    "module": "@/pages/agribusiness/field-service-task-neu",
    "path": "field-service-tasks/neu"
  },
  {
    "module": "@/pages/agribusiness/field-service-task-edit",
    "path": "field-service-tasks/:taskId/bearbeiten"
  }
]
