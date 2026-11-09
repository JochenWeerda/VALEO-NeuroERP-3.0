import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Chargenrueckverfolgung: Studio-Liste `charge/chargen-verfolgung` (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="charge/chargen-verfolgung" testId="screen-charge/chargen-verfolgung" />
}
