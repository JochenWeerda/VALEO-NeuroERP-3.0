import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function SystemEinstellungenPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/system-einstellungen" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/system-einstellungen" />
}
void madeByStudioRuntimeWireDeclaration
