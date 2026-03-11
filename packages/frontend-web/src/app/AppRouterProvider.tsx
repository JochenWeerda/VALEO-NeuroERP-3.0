import { RouterProvider } from 'react-router-dom'
import { router } from '@/app/routes'

export default function AppRouterProvider(): JSX.Element {
  return (
    <RouterProvider
      router={router}
      future={{ v7_startTransition: true }}
    />
  )
}
