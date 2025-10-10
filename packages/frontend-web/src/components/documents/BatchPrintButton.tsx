import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Loader2, Download } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface BatchPrintButtonProps {
  selectedIds: string[]
  domain: 'sales' | 'purchase' | 'invoice' | 'delivery'
  onComplete?: () => void
}

export function BatchPrintButton({ selectedIds, domain, onComplete }: BatchPrintButtonProps) {
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleBatchPrint = async () => {
    if (selectedIds.length === 0) {
      toast({
        title: 'No documents selected',
        description: 'Please select at least one document to print',
        variant: 'destructive',
      })
      return
    }

    try {
      setLoading(true)

      const response = await fetch(`/api/print/batch/${domain}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ids: selectedIds,
        }),
      })

      if (!response.ok) {
        throw new Error('Batch print failed')
      }

      // Download ZIP file
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${domain}_batch_${new Date().toISOString().split('T')[0]}.zip`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast({
        title: 'Batch print completed',
        description: `${selectedIds.length} documents printed successfully`,
      })

      onComplete?.()
    } catch (error) {
      toast({
        title: 'Batch print failed',
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Button
      onClick={handleBatchPrint}
      disabled={loading || selectedIds.length === 0}
      variant="outline"
    >
      {loading ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Printing...
        </>
      ) : (
        <>
          <Download className="mr-2 h-4 w-4" />
          Print Selected ({selectedIds.length})
        </>
      )}
    </Button>
  )
}

