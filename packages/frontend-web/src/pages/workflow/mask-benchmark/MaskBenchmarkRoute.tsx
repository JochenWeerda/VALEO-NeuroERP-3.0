import { NativeListPage } from '@/components/mask-builder/NativeListPage'

export default function Page(): JSX.Element {
  return (
    <NativeListPage screenId="dev/mask-benchmark/:domain/:variant/:id" testId="screen-dev/mask-benchmark/:domain/:variant/:id" />
  )
}
