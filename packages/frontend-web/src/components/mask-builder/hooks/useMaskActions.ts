import { useCallback } from 'react'
import { useToast } from '@/hooks/use-toast'

interface ActionHandler {
  (_action: string, _data?: any): Promise<void> | void
}

export function useMaskActions(onAction?: ActionHandler) {
  const { toast } = useToast()

  const handleAction = useCallback(async (actionKey: string, data?: any) => {
    try {
      if (onAction) {
        await onAction(actionKey, data)
      }

      // Show success toast for common actions
      switch (actionKey) {
        case 'save':
          toast({
            title: "Gespeichert",
            description: "Die Änderungen wurden erfolgreich gespeichert.",
          })
          break
        case 'delete':
          toast({
            title: "Gelöscht",
            description: "Das Element wurde erfolgreich gelöscht.",
          })
          break
        case 'create':
          toast({
            title: "Erstellt",
            description: "Das neue Element wurde erfolgreich erstellt.",
          })
          break
        case 'update':
          toast({
            title: "Aktualisiert",
            description: "Das Element wurde erfolgreich aktualisiert.",
          })
          break
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unbekannter Fehler'

      toast({
        title: "Fehler",
        description: errorMessage,
        variant: "destructive",
      })

      throw error
    }
  }, [onAction, toast])

  const confirmAction = useCallback((actionKey: string, message: string, data?: any) => {
    if (window.confirm(message)) {
      return handleAction(actionKey, data)
    }
  }, [handleAction])

  const handleBulkAction = useCallback(async (actionKey: string, items: any[], data?: any) => {
    if (items.length === 0) {
      toast({
        title: "Keine Elemente ausgewählt",
        description: "Bitte wählen Sie mindestens ein Element aus.",
        variant: "destructive",
      })
      return
    }

    const message = `Möchten Sie die Aktion "${actionKey}" wirklich auf ${items.length} Element(e) anwenden?`

    if (window.confirm(message)) {
      try {
        // Handle bulk actions
        console.log('Bulk action:', actionKey, items, data)

        toast({
          title: "Massenaktion ausgeführt",
          description: `Die Aktion wurde auf ${items.length} Element(e) angewendet.`,
        })
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unbekannter Fehler'

        toast({
          title: "Fehler bei Massenaktion",
          description: errorMessage,
          variant: "destructive",
        })
      }
    }
  }, [toast])

  return {
    handleAction,
    confirmAction,
    handleBulkAction,
  }
}