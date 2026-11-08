import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Saatgut-Bestellungen aus der ScreenDefinition `agrar/saatgut-bestellungen-liste`. */
export default function AgrarSaatgutBestellungenTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="agrar/saatgut-bestellungen-liste" testId="screen-agrar/saatgut-bestellungen-liste" />
  )
}
