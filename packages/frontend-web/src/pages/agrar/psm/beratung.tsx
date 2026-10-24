import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** PSM Beratung aus der ScreenDefinition `agrar/psm-beratung-liste`. */
export default function AgrarPsmBeratungTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="agrar/psm-beratung-liste" testId="screen-agrar/psm-beratung-liste" />
  )
}
