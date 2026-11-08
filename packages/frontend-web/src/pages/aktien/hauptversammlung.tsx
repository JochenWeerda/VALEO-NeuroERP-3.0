import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function HauptversammlungPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="aktien/hauptversammlung" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="aktien/hauptversammlung" />
}
void madeByStudioRuntimeWireDeclaration
