import { Navigate } from '@/app/routing/typed-router'

/** Alias der Startseite — kanonische Route ist `start-dashboard` unter `/`. */
export default function Home(): JSX.Element {
  return <Navigate to="/" replace />
}
