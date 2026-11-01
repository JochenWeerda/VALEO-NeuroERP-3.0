import { useRef, useState } from 'react'
import type { WizardProps } from '@/components/patterns/Wizard'
import { Button } from '@/components/ui/button'

/** Embedded wizard primitive: the Meridian shell supplies the page heading/actions. */
export function DomainWizard({ steps, onFinish, onCancel, getStepValidationError, onStepValidationError, labels, loading, finishDisabled }: WizardProps & { finishDisabled?: boolean }): JSX.Element {
  const [index, setIndex] = useState(0)
  const [pending, setPending] = useState(false)
  const busy = useRef(false)
  async function next(): Promise<void> {
    if (busy.current || loading || (index === steps.length - 1 && finishDisabled)) return
    busy.current = true
    setPending(true)
    try {
      const step = steps[index]
      const error = await getStepValidationError?.(step.id)
      if (error) { onStepValidationError?.(step.id, error); return }
      if (index < steps.length - 1) setIndex(index + 1)
      else await onFinish?.()
    } finally { busy.current = false; setPending(false) }
  }
  return <section className="space-y-4" aria-label="Arbeitsschritte">
    <ol className="flex flex-wrap gap-3">{steps.map((step, i) => <li key={step.id} aria-current={i === index ? 'step' : undefined} className={i === index ? 'font-semibold' : 'text-muted-foreground'}>{i + 1}. {step.title}</li>)}</ol>
    <h2 className="text-lg font-semibold">{steps[index]?.title}</h2>
    <div>{steps[index]?.content}</div>
    <div className="flex flex-wrap gap-2">
      <Button variant="outline" onClick={onCancel} disabled={pending}>{labels?.cancel ?? 'Abbrechen'}</Button>
      {index > 0 && <Button variant="outline" onClick={() => setIndex(index - 1)} disabled={pending}>Zurück</Button>}
      <Button onClick={() => { void next() }} disabled={pending || loading || (index === steps.length - 1 && finishDisabled)}>{index === steps.length - 1 ? labels?.finish ?? 'Abschliessen' : 'Weiter'}</Button>
    </div>
  </section>
}
