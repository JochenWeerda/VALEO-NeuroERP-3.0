import { useCallback, useEffect, useState } from 'react'

const DEFAULT_TENANT_ID =
  import.meta.env.VITE_TENANT_ID || '00000000-0000-0000-0000-000000000001'

function getTenantIdFromStorage(): string {
  if (typeof window === 'undefined') return DEFAULT_TENANT_ID
  return (
    window.localStorage.getItem('tenant_id') ||
    window.sessionStorage.getItem('tenant_id') ||
    DEFAULT_TENANT_ID
  )
}

export function useTenant(): {
  tenantId: string
  setTenantId: (id: string) => void
} {
  const [tenantId, setTenantIdState] = useState<string>(getTenantIdFromStorage)

  useEffect(() => {
    setTenantIdState(getTenantIdFromStorage())
  }, [])

  const setTenantId = useCallback((id: string) => {
    const value = id || DEFAULT_TENANT_ID
    window.localStorage.setItem('tenant_id', value)
    setTenantIdState(value)
  }, [])

  return { tenantId, setTenantId }
}
