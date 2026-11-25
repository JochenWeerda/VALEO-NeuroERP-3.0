import { NativeListPage } from '@/components/mask-builder'

/**
 * Native Liste: ScreenDefinition agrar/sammelabrechnung
 * (POST anlegen, berechnen/buchen/löschen) — Feld-/Aktionsparität zur Legacy-Wizard-Maske.
 */
export default function SammelabrechnungPage(): JSX.Element {
  return <NativeListPage screenId="agrar/sammelabrechnung" testId="screen-agrar/sammelabrechnung" />
}
