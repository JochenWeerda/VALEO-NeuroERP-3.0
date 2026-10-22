import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function ApiKeysPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/api-keys" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/api-keys" />
}
void madeByStudioRuntimeWireDeclaration
