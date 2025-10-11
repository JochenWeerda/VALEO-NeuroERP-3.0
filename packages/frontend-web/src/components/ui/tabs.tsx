import * as TabsPrimitive from '@radix-ui/react-tabs'
import { cn } from '@/lib/utils'

export const Tabs = TabsPrimitive.Root

export const TabsList = (props: TabsPrimitive.TabsListProps): JSX.Element => {
  const { className, ...rest } = props
  return (
    <TabsPrimitive.List
      className={cn(
        'inline-flex items-center justify-center rounded-md bg-muted p-1 text-muted-foreground',
        className,
      )}
      {...rest}
    />
  )
}

export const TabsTrigger = (props: TabsPrimitive.TabsTriggerProps): JSX.Element => {
  const { className, ...rest } = props
  return (
    <TabsPrimitive.Trigger
      className={cn(
        'inline-flex min-w-[120px] items-center justify-center rounded-sm px-3 py-1.5 text-sm font-medium',
        'transition-all disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-background',
        'data-[state=active]:text-foreground data-[state=active]:shadow-sm',
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
      className={cn('mt-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring', className)}
      {...rest}
    />
  )
}
