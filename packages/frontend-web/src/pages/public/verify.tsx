import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertCircle, CheckCircle2, Loader2, XCircle } from 'lucide-react'

type VerificationResult = {
  valid: boolean
  domain: string
  number: string
  status: string
  date: string
  hash: string
  message: string
}

export default function VerifyPage(): JSX.Element {
  const { domain, number, hash } = useParams<{ domain?: string; number?: string; hash?: string }>()
  const [result, setResult] = useState<VerificationResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const buildVerifyUrl = (docDomain: string, docNumber: string, docHash?: string): string => {
    if (typeof docHash === 'string' && docHash.length > 0) {
      return `/verify/${docDomain}/${docNumber}/${docHash}`
    }
    return `/verify/${docDomain}/${docNumber}`
  }

  const isVerificationResult = (payload: unknown): payload is VerificationResult => {
    if (payload == null || typeof payload !== 'object') {
      return false
    }

    const candidate = payload as Partial<VerificationResult>
    return (
      typeof candidate.valid === 'boolean' ||
      typeof candidate.status === 'string' ||
      typeof candidate.number === 'string'
    )
  }

  useEffect(() => {
    async function verify(): Promise<void> {
      try {
        setLoading(true)
        setError(null)

        const url = buildVerifyUrl(domain || '', number || '', hash || '')

        const response = await fetch(url)
        const data: unknown = await response.json()

        if (!response.ok) {
          const detail = typeof (data as { detail?: string }).detail === 'string' ? (data as { detail: string }).detail : null
          throw new Error(detail ?? 'Verification failed')
        }

        if (isVerificationResult(data)) {
          setResult(data)
        } else {
          throw new Error('Ungültige Antwort vom Server')
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    if (typeof domain === 'string' && typeof number === 'string') {
      void verify()
    }
  }, [domain, number, hash])

  const getStatusBadge = (status: string): JSX.Element => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      posted: 'default',
      approved: 'secondary',
      pending: 'outline',
      rejected: 'destructive',
      unknown: 'destructive',
    }
    const variant = variants[status] ?? 'outline'
    return <Badge variant={variant}>{status.toUpperCase()}</Badge>
}

  const getDomainLabel = (domainValue: string): string => {
    const labels: Record<string, string> = {
      sales: 'Sales Order',
      purchase: 'Purchase Order',
      invoice: 'Invoice',
      delivery: 'Delivery Note',
    }
    return labels[domainValue] ?? domainValue
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center gap-4">
              <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
              <p className="text-gray-600">Verifying document...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error !== null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md border-red-200">
          <CardHeader>
            <div className="flex items-center gap-3">
              <XCircle className="h-8 w-8 text-red-600" />
              <div>
                <CardTitle className="text-red-900">Verification Failed</CardTitle>
                <CardDescription className="text-red-600">{error}</CardDescription>
              </div>
            </div>
          </CardHeader>
        </Card>
      </div>
    )
  }

  if (result == null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>No Document Specified</CardTitle>
            <CardDescription>Please scan a valid QR code</CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  const isValid = result.valid === true && result.status !== 'unknown'

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className={`w-full max-w-md ${isValid ? 'border-green-200' : 'border-yellow-200'}`}>
        <CardHeader>
          <div className="flex items-center gap-3">
            {isValid ? (
              <CheckCircle2 className="h-10 w-10 text-green-600" />
            ) : (
              <AlertCircle className="h-10 w-10 text-yellow-600" />
            )}
            <div>
              <CardTitle className={isValid ? 'text-green-900' : 'text-yellow-900'}>
                {isValid ? 'Document Valid' : 'Document Not Verified'}
              </CardTitle>
              <CardDescription className={isValid ? 'text-green-600' : 'text-yellow-600'}>
                {result.message}
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-500">Document Type</p>
              <p className="text-base font-semibold">{getDomainLabel(result.domain)}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Document Number</p>
              <p className="text-base font-semibold">{result.number}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Status</p>
              <div className="mt-1">{getStatusBadge(result.status)}</div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Date</p>
              <p className="text-base font-semibold">{result.date}</p>
            </div>
          </div>

          {typeof hash === 'string' && hash.length > 0 && (
            <div className="pt-4 border-t">
              <p className="text-sm font-medium text-gray-500 mb-2">Verification Hash</p>
              <code className="text-xs bg-gray-100 p-2 rounded block break-all font-mono">
                {result.hash}
              </code>
            </div>
          )}

          <div className="pt-4 border-t">
            <p className="text-xs text-gray-500 text-center">
              This document was verified against VALEO-NeuroERP records.
              <br />
              For questions, contact: support@valeo-erp.com
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

