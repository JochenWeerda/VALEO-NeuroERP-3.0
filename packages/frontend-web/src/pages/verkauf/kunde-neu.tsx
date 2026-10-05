import { useEffect } from 'react'
import { useLocation, useNavigate } from '@/app/routing/typed-router'

export default function KundeNeuPage(): JSX.Element {
  const location = useLocation()
  const navigate = useNavigate()
  const target = `/verkauf/kunde/neu${location.search}`

  useEffect(() => {
    navigate(target, { replace: true })
  }, [navigate, target])

  return <div className="p-6 text-sm text-muted-foreground">Kundenmaske wird geoeffnet...</div>
}
