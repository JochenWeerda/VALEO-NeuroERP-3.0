import { LazyTabs } from '@/components/ui/LazyTabs'
import type { ScreenDefinition, ScreenFieldDefinition } from './schema'
import {
  ActionBarRenderer,
  FieldRenderer,
  ScreenSummaryGrid,
  TabContentRenderer,
  TableRenderer,
  WorkflowPanelRenderer,
  getValue,
  layoutClasses,
} from './renderers'

interface UniversalMaskRendererProps {
  screen: ScreenDefinition
  data?: Record<string, unknown>
  tables?: Record<string, Record<string, unknown>[]>
  allowedPermissions?: string[]
  onTabChange?: (_tabKey: string) => void
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
}

export function UniversalMaskRenderer({
  screen,
  data = {},
  tables = {},
  allowedPermissions = [],
  onTabChange,
  onAction,
}: UniversalMaskRendererProps): JSX.Element {
  const payload = data
  const preferredLayout = screen.layout?.preferredMode ?? 'desktopDense'
  const classes = layoutClasses(preferredLayout)
  const visibleActions = (screen.actions ?? []).filter(
    (action) => !action.permission || allowedPermissions.includes(action.permission),
  )

  function renderFields(fields: ScreenFieldDefinition[] = []): JSX.Element | null {
    if (fields.length === 0) return null
    return (
      <div className={classes.fields}>
        {fields.map((field) => (
          <FieldRenderer key={field.key} field={field} value={getValue(payload, field.key)} />
        ))}
      </div>
    )
  }

  return (
    <div
      className={classes.root}
      data-screen-definition={screen.id}
      data-testid={`screen-${screen.id}`}
      data-layout-mode={preferredLayout}
      data-mobile-layout={screen.layout?.mobileMode ?? 'mobileStack'}
    >
      <ActionBarRenderer
          domain={screen.domain}
          mode={screen.mode}
          title={screen.title}
          subtitle={screen.subtitle}
          actions={visibleActions}
          headerClassName={classes.header}
          touchTargetClass={classes.touchTarget}
          onAction={onAction}
          payload={payload}
        />

      <WorkflowPanelRenderer workflow={screen.workflow} />
      <ScreenSummaryGrid items={screen.summary ?? []} />
      {renderFields(screen.fields)}

      {(screen.tables ?? []).map((table) => (
        <TableRenderer key={table.key} table={table} rows={tables[table.key] ?? []} />
      ))}

      {screen.tabs && screen.tabs.length > 0 && (
        <LazyTabs
          onValueChange={onTabChange}
          tabs={screen.tabs.map((tab) => ({
            key: tab.key,
            label: tab.label,
            lazy: tab.lazy ?? true,
            keepAlive: tab.keepAlive ?? true,
            content: () => (
              <TabContentRenderer
                fields={tab.fields}
                tables={tab.tables}
                fieldsClassName={classes.fields}
                payload={payload}
                tableRows={tables}
              />
            ),
          }))}
        />
      )}
    </div>
  )
}
