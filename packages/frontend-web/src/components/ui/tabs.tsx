import * as React from 'react'
import * as TabsPrimitive from '@radix-ui/react-tabs'
import { cn } from '@/lib/utils'

export const Tabs = TabsPrimitive.Root

/**
 * Zwei Darstellungen, eine Semantik (Radix: ARIA-Tabs + Pfeiltasten-Navigation):
 *  - "default":  Segmented-Control für Ansichtsumschalter (Filter, Unteransichten)
 *  - "register": Belegregister/Karteireiter für Akten und Belege (Gewohnheits-
 *    Prinzip, docs/MASKEN.md) — Laschen sitzen auf einer Grundlinie, die aktive
 *    Lasche verbindet sich mit dem Blatt darunter.
 * Seiten dürfen Reiterleisten nicht mehr als rohe <button>-Reihen bauen.
 */
type TabsVariant = 'default' | 'register'

const TabsVariantContext = React.createContext<TabsVariant>('default')

export interface TabsListProps extends TabsPrimitive.TabsListProps {
  variant?: TabsVariant
}

export const TabsList = (props: TabsListProps): JSX.Element => {
  const { className, variant = 'default', ...rest } = props
  return (
    <TabsVariantContext.Provider value={variant}>
      <TabsPrimitive.List
        className={cn(
          variant === 'register'
            ? 'flex w-full items-end gap-1 overflow-x-auto border-b border-border bg-muted/60 px-3 pt-1 text-xs font-medium select-none'
            : 'inline-flex flex-wrap items-center justify-center rounded-md bg-muted p-1 text-muted-foreground',
          className,
        )}
        {...rest}
      />
    </TabsVariantContext.Provider>
  )
}

export const TabsTrigger = (props: TabsPrimitive.TabsTriggerProps): JSX.Element => {
  const { className, ...rest } = props
  const variant = React.useContext(TabsVariantContext)
  return (
    <TabsPrimitive.Trigger
      className={cn(
        'transition-all disabled:pointer-events-none disabled:opacity-50',
        'focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-inset',
        variant === 'register'
          ? cn(
              'whitespace-nowrap rounded-t-md border-x border-t border-transparent px-3 py-2 text-muted-foreground',
              'hover:bg-muted hover:text-foreground',
              'data-[state=active]:translate-y-px data-[state=active]:border-border data-[state=active]:bg-background data-[state=active]:font-semibold data-[state=active]:text-foreground',
            )
          : cn(
              'inline-flex min-w-0 sm:min-w-[120px] items-center justify-center rounded-sm px-3 py-1.5 text-sm font-medium',
              'data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm',
            ),
        className,
      )}
      {...rest}
    />
  )
}

export const TabsContent = (props: TabsPrimitive.TabsContentProps): JSX.Element => {
  const { className, ...rest } = props
  return (
    <TabsPrimitive.Content
      className={cn('mt-4 focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring', className)}
      {...rest}
    />
  )
}
