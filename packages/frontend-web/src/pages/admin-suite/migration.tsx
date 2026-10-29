import { createLegacyMaskPage } from '@/components/mask-builder'

export default createLegacyMaskPage(() => import('./migration-legacy'))
