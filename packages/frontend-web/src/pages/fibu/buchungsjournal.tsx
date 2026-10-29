import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Buchungsjournal aus der ScreenDefinition `fibu/buchungsjournal-liste`. */
export default function FibuBuchungsjournalTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="fibu/buchungsjournal-liste" testId="screen-fibu/buchungsjournal-liste" />
  )
}
