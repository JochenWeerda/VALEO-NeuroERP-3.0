import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function LieferantenArtikelPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="artikel/lieferanten-artikel" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="artikel/lieferanten-artikel" />
}
void madeByStudioRuntimeWireDeclaration
