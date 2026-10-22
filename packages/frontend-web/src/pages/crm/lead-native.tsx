import { NativeListPage } from '@/components/mask-builder/NativeListPage'

export default function Page(): JSX.Element {
  return (
    <NativeListPage screenId="crm/lead/:id" testId="screen-crm/lead/:id" />
  )
}
