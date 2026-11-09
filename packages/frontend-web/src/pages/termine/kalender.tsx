import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

/** Termine: derselbe Planungskalender (eigene und autorisierte Teamtermine) - keine zweite Kalendermaske. */
export default function Page(): JSX.Element {
  return <UniversalNativeCockpitPage screenId="planung/kalender" testId="screen-termine-kalender" />
}
