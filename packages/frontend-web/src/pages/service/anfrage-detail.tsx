import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Native Detail + Create fuer Serviceanfragen.
 * Kanonische ScreenDefinition: `service/anfrage` (Stamm-Registry);
 * Batch-15-ID `service/anfrage-detail` bleibt Alias fuer Gate E.
 */
export default createStammNativeDetailPage(
  'service/anfrage',
  'service-anfrage-stamm',
)
