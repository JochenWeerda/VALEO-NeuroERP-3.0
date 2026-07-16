import { ImportMonitor } from '@/features/feed-advice/ImportMonitor'

/** Integrationsmonitor-Route (FEED-INT-034, Maskenvertrag FEED-MASK-014). */
export default function IntegrationsmonitorPage(): JSX.Element {
  return (
    <div className="p-6">
      <ImportMonitor />
    </div>
  )
}
