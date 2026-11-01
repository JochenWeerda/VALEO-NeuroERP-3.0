import type { RenderPlan } from '../../render-plan/types'
import { useDomainDispatch } from '../intake/domain-runtime'
import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'

export function useScaleCreateController(enabled: boolean, plan: RenderPlan) {
  const navigate = useNavigate()
  const [standort, setStandort] = useState('')
  const [typ, setTyp] = useState('')
  const [maxKapazitaet, setMaxKapazitaet] = useState('')
  const [pending, setPending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  async function submit(): Promise<void> {
    const capacity = Number(maxKapazitaet)
    if (!enabled || pending || !standort.trim() || !typ.trim() || !maxKapazitaet.trim() || !Number.isFinite(capacity) || capacity <= 0) return
    setPending(true)
    setError(null)
    try {
      await apiClient.post('/api/v1/waage/waagen', { standort: standort.trim(), typ: typ.trim(), max_kapazitaet: capacity })
      navigate('/waage/liste')
    } catch (cause) {
      setError(getAxiosErrorMessage(cause))
    } finally {
      setPending(false)
    }
  }
  useDomainDispatch(plan, { create: submit })
  return { standort, setStandort, typ, setTyp, maxKapazitaet, setMaxKapazitaet, pending, error, submit }
}
export type ScaleCreateState = ReturnType<typeof useScaleCreateController>
