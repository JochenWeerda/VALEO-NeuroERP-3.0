/**
 * Generischer Hook für Listen-Aktionen (Export, Drucken, Löschen)
 */

import { useCallback } from 'react'
import { exportToCSV, printTable } from '@/lib/export-utils'
import { useToast } from '@/hooks/use-toast'

export interface UseListActionsOptions<T> {
  data: T[]
  entityName: string
  columns?: { key: keyof T; label: string }[]
  onDelete?: (id: string) => Promise<void>
}

export function useListActions<T extends Record<string, any>>({
  data,
  entityName,
  columns,
  onDelete,
}: UseListActionsOptions<T>) {
  const { toast } = useToast()

  const handleExport = useCallback(() => {
    const pageName = window.location.pathname.split('/').pop() || entityName
    console.info(`FB:LEVEL=2 PAGE=${pageName} ACTION=export`)
    
    if (data.length === 0) {
      toast({
        title: 'Keine Daten',
        description: 'Es gibt keine Daten zum Exportieren.',
        variant: 'destructive',
      })
      return
    }

    const filename = `${entityName}-export-${new Date().toISOString().split('T')[0]}.csv`
    exportToCSV(data, filename, columns)
    
    toast({
      title: 'Export erfolgreich',
      description: `${data.length} Einträge wurden exportiert.`,
    })
  }, [data, entityName, columns, toast])

  const handlePrint = useCallback(() => {
    const pageName = window.location.pathname.split('/').pop() || entityName
    console.info(`FB:LEVEL=2 PAGE=${pageName} ACTION=print`)
    
    if (data.length === 0) {
      toast({
        title: 'Keine Daten',
        description: 'Es gibt keine Daten zum Drucken.',
        variant: 'destructive',
      })
      return
    }

    printTable(data, `${entityName}-Übersicht`, columns)
  }, [data, entityName, columns, toast])

  const handleDelete = useCallback(async (_id: string) => {
    const pageName = window.location.pathname.split('/').pop() || entityName
    console.info(`FB:LEVEL=2 PAGE=${pageName} ACTION=delete`)
    
    if (!onDelete) {
      toast({
        title: 'Funktion nicht verfügbar',
        description: 'Löschen ist für diese Liste nicht implementiert.',
        variant: 'destructive',
      })
      return
    }

    const confirmed = window.confirm('Möchten Sie diesen Eintrag wirklich löschen?')
    if (!confirmed) return

    try {
      await onDelete(_id)
      toast({
        title: 'Eintrag gelöscht',
        description: 'Der Eintrag wurde erfolgreich gelöscht.',
      })
    } catch (error) {
      toast({
        title: 'Fehler beim Löschen',
        description: error instanceof Error ? error.message : 'Ein unbekannter Fehler ist aufgetreten.',
        variant: 'destructive',
      })
    }
  }, [onDelete, toast, entityName])

  return {
    handleExport,
    handlePrint,
    handleDelete,
  }
}

