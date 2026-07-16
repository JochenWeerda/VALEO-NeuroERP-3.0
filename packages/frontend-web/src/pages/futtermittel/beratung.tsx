import { useLocation } from '@/app/routing/typed-router'
import { ConsultingCases } from '@/features/feed-advice/ConsultingCases'

/** Beratungs-Worklist + Falldetail (FEED-CONS-031); optional ?case_id=… */
export default function BeratungPage(): JSX.Element {
  const location = useLocation()
  const caseId = new URLSearchParams(location.search).get('case_id') ?? undefined

  return (
    <div className="p-6">
      <ConsultingCases initialCaseId={caseId} />
    </div>
  )
}
