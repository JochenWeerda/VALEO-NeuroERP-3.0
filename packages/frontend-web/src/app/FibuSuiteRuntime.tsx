import { useMemo } from 'react'
import { useLocation } from '@/app/routing/typed-router'
import { FIBU_SUITE_ITEMS } from '@/app/navigation/fibu-suite'
import { createRouteElementByModule } from '@/app/page-module-loader'
import FibuSuiteDashboard from '@/layouts/FibuSuiteDashboard'
import FibuSuiteLayout from '@/layouts/FibuSuiteLayout'

function getSuitePath(child: { path?: string; module?: string }): string | null {
  if (!child.path) return null
  const p = child.path.startsWith('/') ? child.path.slice(1) : child.path
  if (p.startsWith('fibu/')) return p.replace('fibu/', '')
  if (p.startsWith('finance/')) return `finance/${p.replace('finance/', '')}`
  if (p.startsWith('export/')) return p.replace('export/', '')
  if (p.startsWith('pos/')) return p
  return p
}

export default function FibuSuiteRuntime(): JSX.Element {
  const location = useLocation()

  const activeElement = useMemo(() => {
    const raw = location.pathname.replace(/^\/fibu-suite\/?/, '')
    const normalized = raw.replace(/\/+$/, '')

    if (!normalized) {
      return <FibuSuiteDashboard />
    }

    const match = FIBU_SUITE_ITEMS.find((item) => getSuitePath(item) === normalized)
    if (!match?.module) {
      return createRouteElementByModule('@/pages/errors/NotFound')
    }

    return createRouteElementByModule(match.module)
  }, [location.pathname])

  return <FibuSuiteLayout>{activeElement}</FibuSuiteLayout>
}
