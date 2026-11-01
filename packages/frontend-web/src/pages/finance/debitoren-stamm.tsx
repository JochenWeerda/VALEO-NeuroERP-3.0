import { useParams } from '@/app/routing/typed-router'
import { createStammNativeDetailPage, isStammCreationEntityId } from '@/components/mask-builder'
import { UniversalNativeCreatePage } from '@/components/mask-builder/UniversalNativeCreatePage'

/** Existing debtors keep the three-register detail; only creation uses the native domain_erp.debitors form. */
const DebitorenDetailPage = createStammNativeDetailPage(
  'finance/debitor',
  'finance-debitoren-stamm',
  () => import('./debitoren-stamm-legacy'),
)

export default function DebitorenStammPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  if (isStammCreationEntityId(id)) {
    return <UniversalNativeCreatePage screenId="finance/debitoren/new" testId="finance-debitoren-new" />
  }
  return <DebitorenDetailPage />
}
