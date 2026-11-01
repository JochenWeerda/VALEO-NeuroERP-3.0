import { useEffect, useMemo, useState } from 'react'
import { UniversalNativeCreatePage } from '@/components/mask-builder/UniversalNativeCreatePage'
import {
  InboxPrefillBanner,
  clearInboxPrefill,
  inboxPrefillToCreationValues,
  readInboxPrefill,
  type InboxPrefillPayload,
} from '@/components/adaptive-workspace/inbox'

/**
 * Eingangsrechnung anlegen — BelegMaskeParent `beleg/purchase-invoice`.
 *
 * Die Liste `/einkauf/rechnung-eingang-erfassung` bleibt NativeListPage.
 * Prefill kommt aus `sessionStorage['valeo.inbox.prefill']`; Speichern läuft
 * über DocFlow-Create der ScreenDefinition, nicht über Inbox-approve.
 */
export default function RechnungEingangErfassungNeuPage(): JSX.Element {
  const [prefill] = useState<InboxPrefillPayload | null>(() => readInboxPrefill())
  const initialValues = useMemo(
    () => (prefill ? inboxPrefillToCreationValues(prefill) : undefined),
    [prefill],
  )

  useEffect(() => {
    if (prefill) clearInboxPrefill()
  }, [prefill])

  return (
    <div>
      {prefill ? <InboxPrefillBanner payload={prefill} /> : null}
      <UniversalNativeCreatePage
        screenId="beleg/purchase-invoice"
        testId="screen-einkauf/rechnung-eingang-erfassung-neu"
        initialValues={initialValues}
      />
    </div>
  )
}
