import type { RenderPlan } from '../../render-plan/types'
import type { ScaleCreateState } from './scale-create-controller'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

type Props = { plan: RenderPlan; state: ScaleCreateState }
export function ScaleCreateRenderer({ plan, state }: Props): JSX.Element {
  const action = plan.actions.find(item => item.key === 'create')
  const fields = [
    { key: 'standort', value: state.standort, set: state.setStandort, type: 'text' },
    { key: 'typ', value: state.typ, set: state.setTyp, type: 'text' },
    { key: 'max_kapazitaet', value: state.maxKapazitaet, set: state.setMaxKapazitaet, type: 'number' },
  ] as const
  const unavailable = !action || action.disabled || Boolean(action.enabledWhen) || fields.some(item => !plan.fieldsByKey[item.key]?.visible || plan.fieldsByKey[item.key]?.readOnly)
  return <form onSubmit={event => { event.preventDefault(); void state.submit() }} className="space-y-4">
    {fields.map(item => {
      const field = plan.fieldsByKey[item.key]
      if (!field?.visible) return null
      return <div key={item.key} className="space-y-1">
        <Label htmlFor={`scale-${item.key}`}>{field.label}</Label>
        <Input id={`scale-${item.key}`} type={item.type} value={item.value} required={field.required}
          disabled={field.readOnly || state.pending} onChange={event => item.set(event.target.value)} />
      </div>
    })}
    {state.error && <p role="alert">{state.error}</p>}
    {action && <Button type="submit" disabled={unavailable || state.pending}>{action.label}</Button>}
  </form>
}
