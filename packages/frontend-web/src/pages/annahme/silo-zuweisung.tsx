import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function SiloZuweisungPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="annahme/silo-zuweisung" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="annahme/silo-zuweisung" />
}
void madeByStudioRuntimeWireDeclaration
