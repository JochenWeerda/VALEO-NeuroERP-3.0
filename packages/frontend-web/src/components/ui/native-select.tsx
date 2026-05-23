import { clsx } from 'clsx'
import type { ChangeEventHandler, ReactNode } from 'react'

export interface NativeSelectOption {
  value: string
  label: string
}

interface NativeSelectProps {
  value: string
  onValueChange?: (value: string) => void
  onChange?: ChangeEventHandler<HTMLSelectElement>
  options?: NativeSelectOption[]
  placeholder?: string
  id?: string
  ariaLabel?: string
  className?: string
  disabled?: boolean
  children?: ReactNode
}

export function NativeSelect({
  value,
  onValueChange,
  onChange,
  options = [],
  placeholder,
  id,
  ariaLabel,
  className,
  disabled = false,
  children,
}: NativeSelectProps): JSX.Element {
  return (
    <select
      id={id}
      aria-label={ariaLabel}
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
}
