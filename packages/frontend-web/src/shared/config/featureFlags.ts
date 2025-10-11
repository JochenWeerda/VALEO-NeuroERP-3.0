import type { FeatureFlags, FeatureKey } from '@/shared/config/featureFlags.types'

const FLAG_ENV_PREFIX = 'VITE_FEATURE_'

const flagEnvMap: Record<FeatureKey, string> = {
  sse: `${FLAG_ENV_PREFIX}SSE`,
  commandPalette: `${FLAG_ENV_PREFIX}COMMAND_PALETTE`,
  agrar: `${FLAG_ENV_PREFIX}AGRAR`,
}

const remoteFlagsUrlEnv = 'VITE_FLAGS_URL'

export const defaultFlags: FeatureFlags = {
  sse: true,
  commandPalette: true,
  agrar: true,
}

const toBool = (value: unknown, fallback: boolean): boolean => {
  if (typeof value !== 'string') {
    return fallback
  }
  const normalized = value.trim().toLowerCase()
  if (normalized === 'true' || normalized === '1' || normalized === 'on' || normalized === 'enabled') {
    return true
  }
  if (normalized === 'false' || normalized === '0' || normalized === 'off' || normalized === 'disabled') {
    return false
  }
  return fallback
}

export const loadEnvFlags = (): Partial<FeatureFlags> => {
  const envFlags: Partial<FeatureFlags> = {}
  Object.entries(flagEnvMap).forEach(([key, envName]) => {
    const envValue = (import.meta.env as Record<string, string | undefined>)[envName]
    if (typeof envValue === 'string') {
      envFlags[key as FeatureKey] = toBool(envValue, defaultFlags[key as FeatureKey])
    }
  })
  return envFlags
}

export const loadRemoteFlags = async (): Promise<Partial<FeatureFlags>> => {
  const url = (import.meta.env as Record<string, string | undefined>)[remoteFlagsUrlEnv] ?? '/flags.json'
  try {
    const response = await fetch(url, { cache: 'no-store' })
    if (!response.ok) {
      return {}
    }
    const json = (await response.json()) as Partial<FeatureFlags>
    return Object.entries(json).reduce<Partial<FeatureFlags>>((acc, [key, value]) => {
      if (value == null) {
        return acc
      }
      if ((key as FeatureKey) in defaultFlags) {
        const normalizedKey = key as FeatureKey
        acc[normalizedKey] = toBool(value, defaultFlags[normalizedKey])
      }
      return acc
    }, {})
  } catch {
    return {}
  }
}
