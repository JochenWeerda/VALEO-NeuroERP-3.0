import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `wartung/anlagen-liste`; Spalten und Aktionen stehen in der Definition. */
export default function WartungAnlagenListePage(): JSX.Element {
  return <NativeListPage screenId="wartung/anlagen-liste" testId="screen-wartung/anlagen-liste" />
}
