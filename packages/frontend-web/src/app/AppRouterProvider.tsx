import { RouterProvider } from '@tanstack/react-router'
import { router } from '@/app/routing/router'

export default function AppRouterProvider(): JSX.Element {
  return <RouterProvider router={router} />
}
