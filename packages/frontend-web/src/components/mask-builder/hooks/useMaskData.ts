import { useState, useEffect } from 'react'
import { useToast } from '@/hooks/use-toast'

interface UseMaskDataOptions {
  apiUrl: string
  id?: string
  autoLoad?: boolean
}

export function useMaskData<T = any>({ apiUrl, id, autoLoad = true }: UseMaskDataOptions) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  const loadData = async () => {
    if (!id) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${apiUrl}/${id}`)
      if (!response.ok) throw new Error('Failed to load data')

      const result = await response.json()
      setData(result)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      toast({
        title: "Fehler beim Laden",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const saveData = async (formData: Partial<T>) => {
    setLoading(true)
    setError(null)

    try {
      const method = id ? 'PUT' : 'POST'
      const url = id ? `${apiUrl}/${id}` : apiUrl

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) throw new Error('Failed to save data')

      const result = await response.json()
      setData(result)

      toast({
        title: "Erfolgreich gespeichert",
        description: "Die Daten wurden erfolgreich gespeichert.",
      })

      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      toast({
        title: "Fehler beim Speichern",
        description: errorMessage,
        variant: "destructive",
      })
      throw err
    } finally {
      setLoading(false)
    }
  }

  const deleteData = async () => {
    if (!id) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${apiUrl}/${id}`, {
        method: 'DELETE',
      })

      if (!response.ok) throw new Error('Failed to delete data')

      setData(null)

      toast({
        title: "Erfolgreich gelöscht",
        description: "Das Element wurde erfolgreich gelöscht.",
      })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      toast({
        title: "Fehler beim Löschen",
        description: errorMessage,
        variant: "destructive",
      })
      throw err
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (autoLoad && id) {
      loadData()
    }
  }, [id, autoLoad])

  return {
    data,
    loading,
    error,
    loadData,
    saveData,
    deleteData,
    setData,
  }
}