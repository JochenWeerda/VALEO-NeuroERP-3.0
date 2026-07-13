import * as React from 'react'

import { cn } from '@/lib/utils'

export type SwitchProps = Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange'> & {
  onCheckedChange?: (checked: boolean) => void
}

export const Switch = React.forwardRef<HTMLInputElement, SwitchProps>(
  ({ className, checked, defaultChecked, disabled, onCheckedChange, ...props }, ref) => {
    const isControlled = typeof checked === 'boolean'
    const [uncontrolled, setUncontrolled] = React.useState<boolean>(Boolean(defaultChecked))
    const value = isControlled ? (checked as boolean) : uncontrolled

    return (
      <label
        className={cn(
          'inline-flex cursor-pointer items-center',
          disabled && 'cursor-not-allowed opacity-50',
          className
        )}
      >
        <input
          ref={ref}
          type="checkbox"
          className="peer sr-only"
          checked={isControlled ? checked : undefined}
          defaultChecked={isControlled ? undefined : defaultChecked}
          disabled={disabled}
          onChange={(e) => {
            const next = e.currentTarget.checked
            if (!isControlled) setUncontrolled(next)
            onCheckedChange?.(next)
          }}
          {...props}
        />
        <span
          aria-hidden="true"
          className={cn(
            'relative inline-flex h-5 w-9 flex-none items-center rounded-full border border-slate-300 bg-slate-100 transition-colors',
            'peer-focus-visible:outline-hidden peer-focus-visible:ring-2 peer-focus-visible:ring-slate-950 peer-focus-visible:ring-offset-2',
            'peer-checked:bg-slate-900 peer-checked:border-slate-900'
          )}
        >
          <span
            className={cn(
              'pointer-events-none inline-block h-4 w-4 translate-x-0.5 rounded-full bg-white shadow transition-transform',
              value && 'translate-x-4'
            )}
          />
        </span>
      </label>
    )
  }
)
Switch.displayName = 'Switch'

