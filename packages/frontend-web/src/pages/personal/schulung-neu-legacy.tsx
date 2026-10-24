import { useEffect } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Skeleton } from '@/components/ui/skeleton'

/** Alte Erfassungsroute: die Zuweisung liegt jetzt in der Schulungen-Arbeitsliste. */
export default function SchulungNeuRedirectPage(): JSX.Element {
  const navigate = useNavigate()

  useEffect(() => {
    navigate('/personal/schulungen')
  }, [navigate])

  return (
    <div className="space-y-6 p-3 md:p-6">
      <Skeleton className="min-h-touch h-10 w-48" />
      <Skeleton className="h-40" />
    </div>
  )
}
