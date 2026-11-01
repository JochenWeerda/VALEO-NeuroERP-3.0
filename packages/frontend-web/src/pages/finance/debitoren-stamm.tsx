import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeCreatePage } from '@/components/mask-builder/UniversalNativeCreatePage'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/** Creation and detail use the same domain_erp.debitors aggregate. */
export default function DebitorenStammPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  if (!id || id === 'new' || id === 'neu') {
    return <UniversalNativeCreatePage screenId="finance/debitoren/new" testId="finance-debitoren-new" />
  }
  return <UniversalNativeDetailPage screenId="finance/debitoren/new" entityId={id} testId="finance-debitoren-detail" />
}
