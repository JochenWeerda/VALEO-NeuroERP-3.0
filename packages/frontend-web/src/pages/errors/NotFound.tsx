import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

/** 404 als Studio-Einstieg (errors/NotFound): Ueberschrift und Wege zurueck kommen aus der ScreenDefinition. */
export default function Page(): JSX.Element {
  return <UniversalNativeCockpitPage screenId="errors/NotFound" testId="screen-errors-NotFound" />
}
