import { type ReactNode, useMemo, useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export interface LazyTabItem {
  key: string
  label: string
  lazy?: boolean
  keepAlive?: boolean
  content: ReactNode | (() => ReactNode)
}

interface LazyTabsProps {
  tabs: LazyTabItem[]
  defaultValue?: string
  onValueChange?: (_value: string) => void
  className?: string
  /** "register" = Belegregister-Optik (Akten/Belege); "default" = Segmented-Control. */
  variant?: 'default' | 'register'
}

export function LazyTabs({ tabs, defaultValue, onValueChange, className, variant = 'default' }: LazyTabsProps): JSX.Element {
  const firstKey = tabs[0]?.key ?? ''
  const [activeTab, setActiveTab] = useState(defaultValue ?? firstKey)
  const [visited, setVisited] = useState<Set<string>>(() => new Set(activeTab ? [activeTab] : []))

  const columnsClass = useMemo(() => {
    const count = Math.min(Math.max(tabs.length, 1), 6)
    return `repeat(${count}, minmax(0, 1fr))`
  }, [tabs.length])

  function handleChange(next: string): void {
    setActiveTab(next)
    setVisited((prev) => {
      if (prev.has(next)) return prev
      const copy = new Set(prev)
      copy.add(next)
      return copy
    })
    onValueChange?.(next)
  }

  return (
    <Tabs value={activeTab} onValueChange={handleChange} className={className}>
      <TabsList
        variant={variant}
        className={variant === 'register' ? undefined : 'grid w-full'}
        style={variant === 'register' ? undefined : { gridTemplateColumns: columnsClass }}
      >
        {tabs.map((tab) => (
          <TabsTrigger key={tab.key} value={tab.key}>
            {tab.label}
          </TabsTrigger>
        ))}
      </TabsList>
      {tabs.map((tab) => {
        const shouldRender = tab.lazy === false || tab.key === activeTab || (tab.keepAlive === true && visited.has(tab.key))
        return (
          <TabsContent key={tab.key} value={tab.key} className="mt-4">
            {shouldRender ? (typeof tab.content === 'function' ? tab.content() : tab.content) : null}
          </TabsContent>
        )
      })}
    </Tabs>
  )
}
