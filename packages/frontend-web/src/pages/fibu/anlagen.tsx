import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Anlagen aus der ScreenDefinition `fibu/anlagen-liste`. */
export default function FibuAnlagenTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="fibu/anlagen-liste" testId="screen-fibu/anlagen-liste" />
  )
}
