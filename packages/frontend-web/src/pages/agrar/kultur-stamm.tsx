import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Kulturen aus der ScreenDefinition `agrar/kultur-stamm-liste`. */
export default function AgrarKulturStammTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="agrar/kultur-stamm-liste" testId="screen-agrar/kultur-stamm-liste" />
  )
}
