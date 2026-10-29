import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Wartung aus der ScreenDefinition `wartung/anlagen-liste`; Aktionen und Spalten stehen in der Definition. */
export default function WartungAnlagenListePage(): JSX.Element {
  return <NativeListPage screenId="wartung/anlagen-liste" testId="screen-wartung/anlagen-liste" />
}
