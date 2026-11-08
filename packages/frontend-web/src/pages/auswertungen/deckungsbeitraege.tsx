import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function DeckungsbeitraegePage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="auswertungen/deckungsbeitraege" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="auswertungen/deckungsbeitraege" />
}
void madeByStudioRuntimeWireDeclaration
