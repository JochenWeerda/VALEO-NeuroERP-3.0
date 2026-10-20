import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Wechselkurse aus der ScreenDefinition `finance/wechselkurse`; Erfassen und Deaktivieren stehen in der Definition. */
export default function WechselkursePage(): JSX.Element {
  return <NativeListPage screenId="finance/wechselkurse" testId="screen-finance/wechselkurse" />
}
