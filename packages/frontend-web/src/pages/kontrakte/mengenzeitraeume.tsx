import { NativeListPage } from '@/components/mask-builder'

/**
 * Native Workspace: ScreenDefinition kontrakte/mengenzeitraeume
 * Mengenzeiträume anlegen/generieren/löschen + Zu-/Abschläge — volle Legacy-Parität.
 */
export default function KontraktMengenzeitraeumePage(): JSX.Element {
  return (
    <NativeListPage screenId="kontrakte/mengenzeitraeume" testId="screen-kontrakte/mengenzeitraeume" />
  )
}
