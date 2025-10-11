import { type ReactNode, useMemo, useState } from 'react'
import { PageToolbar, type ToolbarAction } from '@/components/navigation/PageToolbar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'

export interface ObjectPageSection {
  id: string
  label: string
  icon?: ReactNode
  badge?: ReactNode
  content: ReactNode
}

export interface ObjectPageProps {
  title: string
  subtitle?: string
  keyInfo?: ReactNode
  sections: ObjectPageSection[]
  initialSectionId?: string
  onSectionChange?: (sectionId: string) => void
  primaryActions?: ToolbarAction[]
  overflowActions?: ToolbarAction[]
  editMode?: boolean
  onEdit?: () => void
  onSave?: () => void
  onCancel?: () => void
  mcpContext?: {
    pageDomain: string
    entityType: string
    documentId?: string
  }
}

export const objectPageMCP = createMCPMetadata('ObjectPage', 'detail', {
  accessibility: {
    role: 'main',
    ariaLabel: 'Object detail view with sections',
  },
  intent: {
    purpose: 'Inspect and edit a business object',
    userActions: ['navigate-section', 'edit', 'save', 'cancel'],
    dataContext: ['business-object', 'section'],
  },
  mcpHints: {
    autoFillable: true,
    explainable: true,
    testable: true,
  },
})

const defaultActions = (
  editMode: boolean,
  onEdit?: () => void,
  onSave?: () => void,
  onCancel?: () => void,
): ToolbarAction[] => {
  if (editMode) {
    const actions: ToolbarAction[] = []
    if (typeof onSave === 'function') {
      actions.push({
        id: 'object-save',
        label: 'Speichern',
        onClick: onSave,
        variant: 'default',
        mcp: { intent: 'save-object' },
      })
    }
    if (typeof onCancel === 'function') {
      actions.push({
        id: 'object-cancel',
        label: 'Abbrechen',
        onClick: onCancel,
        variant: 'secondary',
        mcp: { intent: 'cancel-edit' },
      })
    }
    return actions
  }

  if (typeof onEdit === 'function') {
    return [
      {
        id: 'object-edit',
        label: 'Bearbeiten',
        onClick: onEdit,
        variant: 'outline',
        mcp: { intent: 'edit-object' },
      },
    ]
  }

  return []
}

export function ObjectPage({
  title,
  subtitle,
  keyInfo,
  sections,
  initialSectionId,
  onSectionChange,
  primaryActions,
  overflowActions,
  editMode = false,
  onEdit,
  onSave,
  onCancel,
  mcpContext,
}: ObjectPageProps): JSX.Element {
  const safeSections = useMemo(() => sections.filter((section) => section != null), [sections])

  const initialSection = useMemo(() => {
    if (typeof initialSectionId === 'string') {
      const explicit = safeSections.find((section) => section.id === initialSectionId)
      if (explicit) {
        return explicit.id
      }
    }
    return safeSections[0]?.id ?? ''
  }, [initialSectionId, safeSections])

  const [activeSection, setActiveSection] = useState<string>(initialSection)

  const computedActions = useMemo<ToolbarAction[]>(() => {
    if (Array.isArray(primaryActions) && primaryActions.length > 0) {
      return primaryActions
    }
    return defaultActions(editMode, onEdit, onSave, onCancel)
  }, [editMode, onCancel, onEdit, onSave, primaryActions])

  const handleSectionChange = (value: string): void => {
    setActiveSection(value)
    if (typeof onSectionChange === 'function') {
      onSectionChange(value)
    }
  }

  return (
    <div
      className="flex h-full flex-col"
      data-mcp-pattern="object-page"
      data-mcp-entity={mcpContext?.entityType}
      data-mcp-document-id={mcpContext?.documentId}
    >
      <PageToolbar
        title={title}
        subtitle={subtitle}
        primaryActions={computedActions}
        overflowActions={overflowActions}
        mcpContext={
          mcpContext
            ? {
                pageDomain: mcpContext.pageDomain,
                currentDocument: mcpContext.documentId,
                availableActions: computedActions.map((action) => action.id),
              }
            : undefined
        }
      />

      <div className="flex-1 space-y-6 overflow-y-auto p-6">
        {keyInfo !== undefined && keyInfo !== null ? (
          <div className="rounded-lg border bg-muted/40 p-4" data-mcp-slot="key-info">
            {keyInfo}
          </div>
        ) : null}

        {safeSections.length > 0 ? (
          <Tabs value={activeSection} onValueChange={handleSectionChange} className="space-y-4">
            <TabsList className="w-full justify-start overflow-x-auto">
              {safeSections.map((section) => (
                <TabsTrigger
                  key={section.id}
                  value={section.id}
                  className="group relative data-[state=active]:bg-primary/10 data-[state=active]:text-primary"
                >
                  {section.icon !== undefined && section.icon !== null ? (
                    <span className="mr-2 inline-flex h-4 w-4 items-center">{section.icon}</span>
                  ) : null}
                  <span>{section.label}</span>
                  {section.badge !== undefined && section.badge !== null ? (
                    <span className="ml-2 text-xs text-muted-foreground">{section.badge}</span>
                  ) : null}
                </TabsTrigger>
              ))}
            </TabsList>

            {safeSections.map((section) => (
              <TabsContent
                key={section.id}
                value={section.id}
                className={cn(
                  'rounded-lg border bg-card p-6 shadow-sm',
                  section.id === activeSection ? 'block' : 'hidden',
                )}
              >
                <div data-mcp-section={section.id}>{section.content}</div>
              </TabsContent>
            ))}
          </Tabs>
        ) : (
          <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
            Keine Abschnitte vorhanden.
          </div>
        )}
      </div>
    </div>
  )
}
