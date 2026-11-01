from pathlib import Path

Path("packages/frontend-web/src/pages/analytics.tsx").write_text(
    """import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

export default function AnalyticsPage(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId="copilot/analytics"
      testId="screen-copilot-analytics"
    />
  )
}
""",
    encoding="utf-8",
)
