import { useState, useEffect } from 'react'
import { useToast } from '@/hooks/use-toast'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'

interface UseMaskDataOptions<TData> {
  apiUrl: string
  id?: string
  autoLoad?: boolean
  transformResponse?: (_data: unknown) => TData
}

function resolveData<T>(rawData: unknown, transformResponse?: (_data: unknown) => T): T {
  return (typeof transformResponse === 'function' ? transformResponse(rawData) : rawData) as T
}

export function useMaskData<T extends object = Record<string, unknown>>({
  apiUrl,
  id,
  autoLoad = true,
  transformResponse,
}: UseMaskDataOptions<T>) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  const loadData = async () => {
    if (!id) return

    setLoading(true)
    setError(null)

    try {
      const response = await apiClient.get<T>(`${apiUrl}/${id}`)
      const nextData = resolveData<T>(response.data, transformResponse)
      setData(nextData)
    } catch (err) {
      const errorMessage = getAxiosErrorMessage(err)
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
      const response = id
        ? await apiClient.put<T>(`${apiUrl}/${id}`, formData)
        : await apiClient.post<T>(apiUrl, formData)

      const nextData = resolveData<T>(response.data, transformResponse)
      setData(nextData)

      toast({
        title: "Erfolgreich gespeichert",
        description: "Die Daten wurden erfolgreich gespeichert.",
      })

      return response.data
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
      await apiClient.delete(`${apiUrl}/${id}`)

      setData(null)

      toast({
        title: "Erfolgreich gelöscht",
        description: "Das Element wurde erfolgreich gelöscht.",
      })
    } catch (err) {
      const errorMessage = getAxiosErrorMessage(err)
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
    isLoading: loading,
    error,
    loadData,
    saveData,
    updateData: saveData,
    deleteData,
    setData,
  }
}
