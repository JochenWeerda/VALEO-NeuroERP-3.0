import { Navigate } from '@/app/routing/typed-router'

/** Legacy alias — canonical start route is start-dashboard. */
export default function Home(): JSX.Element {
  return <Navigate to="/" replace />
}
