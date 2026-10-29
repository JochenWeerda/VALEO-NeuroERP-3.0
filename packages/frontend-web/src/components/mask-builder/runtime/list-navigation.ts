import { readWorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'
import type { ListExperience } from '../schema'

type Row = Record<string, unknown>
export function listNavigationTarget(targetPath: string, query: URLSearchParams,
  resume: ListExperience['workflowResume'], create: boolean) {
  if (!targetPath.startsWith('/') || targetPath.startsWith('//') || targetPath.includes('\\')) {
    throw new Error('Navigation muss innerhalb der Anwendung bleiben.')
  }
  const context = readWorkflowEntryContext(query)
  const target = new URL(targetPath, 'http://valeo.invalid')
  if (context) query.forEach((value, key) => target.searchParams.set(key, value))
  const url = target.pathname + target.search + target.hash
  return {
    url,
    checkpoint: context?.process && context.instanceId && resume ? {
      process: context.process,
      instanceId: context.instanceId,
      payload: {
        resume_node_id: resume.resumeNodeId,
        resume_route: url,
        resume_payload: { screen: create ? resume.createScreen : resume.detailScreen,
          targetPath, workflowCase: context.caseNumber || undefined },
        business_status: resume.businessStatus,
        action_label: resume.actionLabelPrefix + targetPath,
      },
    } : undefined,
  }
}

/** Export the complete filtered client result, never silently refetch unfiltered rows. */
export function listCSV(rows: Row[], columns: { key: string; label: string }[], delimiter = ';'): string {
  const escape = (value: unknown) => {
    let text = String(value ?? '')
    if (typeof value === 'string' && /^[=+\-@\t\r]/.test(text)) text = `'${  text}`
    return `"${  text.replace(/"/g, '""')  }"`
  }
  return [columns.map(column => escape(column.label)).join(delimiter),
    ...rows.map(row => columns.map(column => escape(row[column.key])).join(delimiter))].join('\n')
}
