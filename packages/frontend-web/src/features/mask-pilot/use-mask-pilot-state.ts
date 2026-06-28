import { useCallback, useMemo, useState } from 'react'

/** Separates mask UI state so tab/table updates do not reset summary or entity state. */
export function useMaskPilotState(initialTab?: string) {
  const [activeTabKey, setActiveTabKey] = useState<string | undefined>(initialTab)
  const [tablePage, setTablePage] = useState(1)

  const onTabChange = useCallback((tabKey: string) => {
    setActiveTabKey(tabKey)
    setTablePage(1)
  }, [])

  const tabState = useMemo(
    () => ({
      activeTabKey,
      tablePage,
      setTablePage,
      onTabChange,
    }),
    [activeTabKey, onTabChange, tablePage],
  )

  return tabState
}
