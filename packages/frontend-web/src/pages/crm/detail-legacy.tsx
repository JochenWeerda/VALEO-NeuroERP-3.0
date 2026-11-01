import { Button } from '@/components/ui/button'
import { useNavigate } from '@/app/routing/typed-router'

/** Retired shared fallback: contact/farm creation must never create a CRM activity. */
export default function UnavailableCRMCreation(): JSX.Element {
  const navigate = useNavigate()
  return <div className="space-y-3 p-4 text-foreground">
    <p role="alert">Für diesen Bereich ist noch keine geprüfte Neuanlage verfügbar.</p>
    <Button variant="outline" onClick={() => navigate(-1)}>Zurück zur Übersicht</Button>
  </div>
}
