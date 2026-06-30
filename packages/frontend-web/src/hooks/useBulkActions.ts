/**
 * Bulk Actions Hook
 * Für Bulk-Delete, Bulk-Update, Bulk-Export Operationen
 */

import { useState, useCallback } from 'react'
import { useToast } from '@/hooks/use-toast'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { bulkDeleteDocuments, type DocumentType } from '@/lib/document-api'
import { stringValue } from '@/lib/record-utils'

export interface UseBulkActionsOptions {
  docType: DocumentType
  onSuccess?: () => void
}

export function useBulkActions({ docType, onSuccess }: UseBulkActionsOptions) {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [selectedItems, setSelectedItems] = useState<string[]>([])

  const handleSelect = useCallback((itemId: string, selected: boolean) => {
    setSelectedItems(prev => 
      selected 
        ? [...prev, itemId]
        : prev.filter(id => id !== itemId)
    )
  }, [])

  const handleSelectAll = useCallback((itemIds: string[], selected: boolean) => {
    setSelectedItems(selected ? itemIds : [])
  }, [])

  const handleBulkDelete = useCallback(async () => {
    if (selectedItems.length === 0) {
      toast({
        title: 'Keine Auswahl',
        description: 'Bitte wählen Sie mindestens ein Element aus.',
        variant: 'destructive',
      })
      return
    }

    const confirmed = window.confirm(
      `Möchten Sie wirklich ${selectedItems.length} Element(e) löschen?`
    )
    if (!confirmed) return

    setLoading(true)
    try {
      const result = await bulkDeleteDocuments(docType, selectedItems)
      
      if (result.ok) {
        toast({
          title: 'Löschung erfolgreich',
          description: `${result.deleted?.length || 0} Element(e) wurden gelöscht.`,
        })
        setSelectedItems([])
        onSuccess?.()
      } else {
        toast({
          title: 'Fehler beim Löschen',
          description: result.error || 'Ein unbekannter Fehler ist aufgetreten.',
          variant: 'destructive',
        })
      }
    } catch (error) {
      toast({
        title: 'Fehler beim Löschen',
        description: getAxiosErrorMessage(error),
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }, [selectedItems, docType, toast, onSuccess])

  const handleBulkExport = useCallback((data: Record<string, unknown>[]) => {
    if (selectedItems.length === 0) {
      toast({
        title: 'Keine Auswahl',
        description: 'Bitte wählen Sie mindestens ein Element aus.',
        variant: 'destructive',
      })
      return
    }

    const filteredData = data.filter(item => selectedItems.includes(stringValue(item.id, stringValue(item.number))))
    
    // Export-Logik (kann erweitert werden)
    const csv = filteredData.map(item => 
      Object.values(item).join(';')
    ).join('\n')
    
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `${docType}-bulk-export-${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    toast({
      title: 'Export erfolgreich',
      description: `${selectedItems.length} Element(e) wurden exportiert.`,
    })
  }, [selectedItems, docType, toast])

  return {
    selectedItems,
    loading,
    handleSelect,
    handleSelectAll,
    handleBulkDelete,
    handleBulkExport,
    clearSelection: () => setSelectedItems([]),
  }
}

