import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Schlaege aus der ScreenDefinition `agrar/schlaege-liste`. */
export default function AgrarSchlaegeIndexTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="agrar/schlaege-liste" testId="screen-agrar/schlaege-liste" />
  )
}
