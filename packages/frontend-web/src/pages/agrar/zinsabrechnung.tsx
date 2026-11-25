import { NativeListPage } from '@/components/mask-builder'

/**
 * Native Liste + Anlegen: ScreenDefinition agrar/zinsabrechnung
 * (POST /api/v1/zinsabrechnung, buchen/stornieren/drucken) — Feld-/Aktionsparitaet zur Legacy-Maske.
 */
export default function ZinsabrechnungPage(): JSX.Element {
  return <NativeListPage screenId="agrar/zinsabrechnung" testId="screen-agrar/zinsabrechnung" />
}
