import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function UsersPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/users" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/users" />
}
void madeByStudioRuntimeWireDeclaration
