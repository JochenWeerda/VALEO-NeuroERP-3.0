import { type PropsWithChildren, createContext, useContext, useEffect, useState } from 'react'
import { defaultFlags, loadEnvFlags, loadRemoteFlags } from '@/shared/config/featureFlags'
import type { FeatureFlags, FeatureKey } from '@/shared/config/featureFlags.types'

const FeatureFlagContext = createContext<FeatureFlags>(defaultFlags)

// Initialisiere Flags außerhalb der Komponente, um Hook-Probleme zu vermeiden
let initialFlags: FeatureFlags
try {
  initialFlags = { ...defaultFlags, ...loadEnvFlags() }
} catch (error) {
  console.warn('Failed to load env flags:', error)
  initialFlags = defaultFlags
}

export function FeatureFlagProvider({ children }: PropsWithChildren): JSX.Element {
  const [flags, setFlags] = useState<FeatureFlags>(initialFlags)

  useEffect(() => {
    let cancelled = false
    void loadRemoteFlags().then((remote) => {
      if (cancelled || remote == null) {
        return
      }
      setFlags((prev) => ({ ...prev, ...remote }))
    })
    return () => {
      cancelled = true
    }
  }, [])

  return <FeatureFlagContext.Provider value={flags}>{children}</FeatureFlagContext.Provider>
}

export function useFeatureFlag(key: FeatureKey): boolean {
  const flags = useContext(FeatureFlagContext)
  if (flags == null) {
    return defaultFlags[key]
  }
  return flags[key] ?? defaultFlags[key]
}

export function useFeatureFlags(): FeatureFlags {
  return useContext(FeatureFlagContext)
}
