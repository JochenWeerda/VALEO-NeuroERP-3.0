import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Etikettendruck: Studio-Liste `etiketten/drucken` (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="etiketten/drucken" testId="screen-etiketten/drucken" />
}
