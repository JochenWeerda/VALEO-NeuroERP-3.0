import { AgentenIntegrationWorkspace } from '@/pages/admin/agenten-integration'

export default function AdminControlCenterPage(): JSX.Element {
  return (
    <AgentenIntegrationWorkspace
      section="overview"
      title="Admin Kontroll- und Ueberwachungszentrum"
      subtitle="Zentraler Leitstand fuer Agenten, Superglue, API-Zugaenge und operativen Integrationszustand."
    />
  )
}
