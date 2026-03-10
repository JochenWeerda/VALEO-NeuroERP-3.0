import { clsx } from 'clsx'

export interface NativeSelectOption {
  value: string
  label: string
}

interface NativeSelectProps {
  value: string
  onValueChange: (value: string) => void
  options: NativeSelectOption[]
  placeholder?: string
  id?: string
  className?: string
  disabled?: boolean
}

export function NativeSelect({
  value,
  onValueChange,
  options,
  placeholder,
  id,
  className,
  disabled = false,
}: NativeSelectProps): JSX.Element {
  return (
    <select
      id={id}
      value={value}
      onChange={(event) => onValueChange(event.target.value)}
      disabled={disabled}
      className={clsx(
        'flex h-9 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
        className,
      )}
    >
      {placeholder !== undefined ? <option value="">{placeholder}</option> : null}
      {options.map((option) => (
        <option key={`${option.value}-${option.label}`} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  )
}
