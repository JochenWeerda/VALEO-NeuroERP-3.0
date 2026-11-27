import { useParams } from '@/app/routing/typed-router'
import { createStammNativeDetailPage, isStammCreationEntityId } from '@/components/mask-builder'
import { UniversalNativeCreatePage } from '@/components/mask-builder/UniversalNativeCreatePage'

/** Existing debtors: native detail. Creation: dedicated capture screen (kein ObjectPage-Legacy). */
const DebitorenDetailPage = createStammNativeDetailPage('finance/debitor', 'finance-debitoren-stamm')

export default function DebitorenStammPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  if (isStammCreationEntityId(id)) {
    return <UniversalNativeCreatePage screenId="finance/debitoren/new" testId="finance-debitoren-new" />
  }
  return <DebitorenDetailPage />
}
