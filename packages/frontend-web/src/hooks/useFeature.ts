import { useFeatureFlag, useFeatureFlags } from '@/app/providers/FeatureFlagProvider'
import type { FeatureKey } from '@/shared/config/featureFlags.types'

export const useFeature = (key: FeatureKey): boolean => {
  return useFeatureFlag(key)
}

export const useAllFeatures = useFeatureFlags
