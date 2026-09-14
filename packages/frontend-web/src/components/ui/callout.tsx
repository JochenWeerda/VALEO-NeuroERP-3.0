import * as React from 'react'
import { type VariantProps } from 'class-variance-authority'

import { alertVariants } from '@/components/ui/alert'
import { cn } from '@/lib/utils'

/**
 * Ruhiger Hinweiskasten in den Statusfarben des Designsystems.
 *
 * Teilt die Varianten mit `Alert`, rendert aber bewusst **ohne** `role="alert"`:
 * Callouts stehen dauerhaft in der Maske, eine assertive Ansage bei jedem Render
 * waere eine Verschlechterung fuer Screenreader. Fuer echte, erscheinende
 * Meldungen bleibt `Alert` zustaendig.
 */
const Callout = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & VariantProps<typeof alertVariants>
>(({ className, variant, ...props }, ref) => (
  <div ref={ref} className={cn(alertVariants({ variant }), className)} {...props} />
))
Callout.displayName = 'Callout'

const CalloutTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h5
    ref={ref}
    className={cn('mb-1 font-medium leading-none tracking-tight', className)}
    {...props}
  />
))
CalloutTitle.displayName = 'CalloutTitle'

const CalloutDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('text-sm [&_p]:leading-relaxed', className)} {...props} />
))
CalloutDescription.displayName = 'CalloutDescription'

export { Callout, CalloutTitle, CalloutDescription }
export type CalloutVariant = NonNullable<VariantProps<typeof alertVariants>['variant']>
