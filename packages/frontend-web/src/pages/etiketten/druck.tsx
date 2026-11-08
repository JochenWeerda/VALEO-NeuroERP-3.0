import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Etikettendruck aus der ScreenDefinition `etiketten/druck-liste`. */
export default function EtikettenDruckTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="etiketten/druck-liste" testId="screen-etiketten/druck-liste" />
  )
}
