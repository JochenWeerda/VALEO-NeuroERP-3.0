import { NativeListPage } from '@/components/mask-builder/NativeListPage'

const SCREEN_ID = 'compliance/pcn-ufi'

export default function PcnUfiPage(): JSX.Element {
  return <NativeListPage screenId={SCREEN_ID} testId="compliance-pcn-ufi" />
}
