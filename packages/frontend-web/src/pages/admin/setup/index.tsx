import DmsIntegrationCard from './dms-integration'

export default function AdminSetupPage() {
  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Ersteinrichtung</h1>
        <p className="text-muted-foreground">
          Konfigurieren Sie die wichtigsten Integrationen für VALEO NeuroERP
        </p>
      </div>

      <div className="grid gap-6">
        {/* Mayan-DMS-Integration */}
        <DmsIntegrationCard />

        {/* Weitere Setup-Cards können hier hinzugefügt werden */}
        {/* z.B. OIDC-Setup, SMTP-Setup, etc. */}
      </div>
    </div>
  )
}

