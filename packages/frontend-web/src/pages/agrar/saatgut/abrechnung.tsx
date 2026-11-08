import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function AbrechnungPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="agrar/saatgut/abrechnung" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="agrar/saatgut/abrechnung" />
}
void madeByStudioRuntimeWireDeclaration
