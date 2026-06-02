import { clsx } from 'clsx'
import { forwardRef, type ReactNode, type SelectHTMLAttributes } from 'react'

export interface NativeSelectOption {
  value: string
  label: string
}

export interface NativeSelectProps
  extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'onChange'> {
  /** Convenience-Callback mit dem reinen String-Wert (zusätzlich zu onChange). */
  onValueChange?: (value: string) => void
  onChange?: SelectHTMLAttributes<HTMLSelectElement>['onChange']
  options?: NativeSelectOption[]
  placeholder?: string
  ariaLabel?: string
  children?: ReactNode
}

/**
 * Natives <select>. Unterstützt sowohl controlled-Nutzung (value + onValueChange)
 * als auch uncontrolled-Nutzung via react-hook-form ({...register(...)}): durch
 * forwardRef erreicht der RHF-ref das <select>, name/onBlur/defaultValue werden
 * durchgereicht. `value` ist optional (uncontrolled).
 */
export const NativeSelect = forwardRef<HTMLSelectElement, NativeSelectProps>(
  function NativeSelect(
    {
      value,
      onValueChange,
      onChange,
      options = [],
      placeholder,
      id,
      ariaLabel,
      'aria-label': ariaLabelAttr,
      className,
      disabled = false,
      children,
      ...rest
    },
    ref,
  ) {
    return (
      <select
        ref={ref}
        id={id}
        aria-label={ariaLabel ?? ariaLabelAttr}
        value={value}
        onChange={(event) => {
          onChange?.(event)
          onValueChange?.(event.target.value)
        }}
        disabled={disabled}
        className={clsx(
          'flex h-9 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
          className,
        )}
        {...rest}
      >
        {placeholder !== undefined ? <option value="">{placeholder}</option> : null}
        {children
          ?? options.map((option) => (
            <option key={`${option.value}-${option.label}`} value={option.value}>
              {option.label}
            </option>
          ))}
      </select>
    )
  },
)
