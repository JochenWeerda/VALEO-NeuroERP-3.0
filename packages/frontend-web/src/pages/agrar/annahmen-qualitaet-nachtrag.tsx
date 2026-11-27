import { NativeListPage } from '@/components/mask-builder'

/**
 * Native Worklist: ScreenDefinition agrar/annahmen-qualitaet-nachtrag
 * Zeilen-Nachtrag + Batch — dieselben Endpunkte wie die Legacy-Maske (Human/CI/MCP).
 */
export default function AnnahmenQualitaetNachtragPage(): JSX.Element {
  return (
    <NativeListPage
      screenId="agrar/annahmen-qualitaet-nachtrag"
      testId="screen-agrar/annahmen-qualitaet-nachtrag"
    />
  )
}
