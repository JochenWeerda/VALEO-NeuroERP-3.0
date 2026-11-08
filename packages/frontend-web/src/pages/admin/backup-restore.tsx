import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function BackupRestorePage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/backup-restore" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/backup-restore" />
}
void madeByStudioRuntimeWireDeclaration
