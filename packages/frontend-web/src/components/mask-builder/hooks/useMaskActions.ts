import { useCallback, useRef, useState } from 'react'
import { useToast } from '@/hooks/use-toast'
import { getAxiosErrorMessage } from '@/lib/api-client'

interface ActionHandler {
  (_action: string, _data: Record<string, unknown>): Promise<void> | void
}

export function useMaskActions(onAction?: ActionHandler) {
  const { toast } = useToast()
  const loadingRef = useRef<string | null>(null)
  const [loadingActionKey, setLoadingActionKey] = useState<string | null>(null)

  const handleAction = useCallback(async (actionKey: string, data?: Record<string, unknown>) => {
    if (loadingRef.current !== null) return
    loadingRef.current = actionKey
    setLoadingActionKey(actionKey)
    try {
      if (onAction) {
        await onAction(actionKey, data ?? {})
      }

      // Show success toast for common actions that don't manage their own feedback
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
      const errorMessage = getAxiosErrorMessage(error)

      toast({
        title: "Fehler",
        description: errorMessage,
        variant: "destructive",
      })

      throw error
    } finally {
      loadingRef.current = null
      setLoadingActionKey(null)
    }
  }, [onAction, toast])

  const confirmAction = useCallback((actionKey: string, message: string, data?: Record<string, unknown>) => {
    if (window.confirm(message)) {
      return handleAction(actionKey, data)
    }
  }, [handleAction])

  const handleBulkAction = useCallback(async (actionKey: string, items: Record<string, unknown>[], data?: Record<string, unknown>) => {
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
      if (loadingRef.current !== null) return
      loadingRef.current = actionKey
      setLoadingActionKey(actionKey)
      try {
        if (onAction) {
          await onAction(actionKey, { items, ...data })
        }
        toast({
          title: "Massenaktion ausgeführt",
          description: `Die Aktion wurde auf ${items.length} Element(e) angewendet.`,
        })
      } catch (error) {
        const errorMessage = getAxiosErrorMessage(error)

        toast({
          title: "Fehler bei Massenaktion",
          description: errorMessage,
          variant: "destructive",
        })
      } finally {
        loadingRef.current = null
        setLoadingActionKey(null)
      }
    }
  }, [onAction, toast])

  return {
    handleAction,
    confirmAction,
    handleBulkAction,
    loadingActionKey,
  }
}
