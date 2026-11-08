import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function TenantsPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/tenants" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/tenants" />
}
void madeByStudioRuntimeWireDeclaration
