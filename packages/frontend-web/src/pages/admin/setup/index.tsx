import DmsIntegrationCard from './dms-integration'

export default function AdminSetupPage(): JSX.Element {
  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Ersteinrichtung</h1>
        <p className="text-muted-foreground">
          Konfigurieren Sie die wichtigsten Integrationen fuer VALEO NeuroERP.
        </p>
      </div>

      <div className="grid gap-6">
        <DmsIntegrationCard />
      </div>
    </div>
  )
}
