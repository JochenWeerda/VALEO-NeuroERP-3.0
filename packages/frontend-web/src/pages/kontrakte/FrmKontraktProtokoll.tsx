import { useParams, useSearchParams } from '@/app/routing/typed-router'
import { NativeAuditListPage } from '@/components/mask-builder/NativeAuditListPage'

export default function FrmKontraktProtokoll({ contractId }: { contractId?: string }): JSX.Element {
  const params = useParams()
  const [query] = useSearchParams()
  const rawQuery: URLSearchParams = query
  const id = contractId ?? params.id ?? rawQuery.get('contractId') ?? rawQuery.get('contract_id') ?? undefined
  return <NativeAuditListPage screenId="kontrakte/FrmKontraktProtokoll" entityId={id} />
}
