/**
 * TouchFieldLayout — Gemeinsame Komponenten für Touch-optimierte Feldworkflows
 *
 * Gap 024: Touch-optimierte Feldworkflows (Tablet/Lager/Waage)
 * KPI: Fehlbedienungen -40% durch:
 *   - Touch-Ziele >= 44px (WCAG 2.1 / iOS HIG / Android Material)
 *   - Vereinfachte Formulare ohne Maus-abhängige Interaktionen
 *   - Große, fingerfreundliche Aktionsflächen
 *   - Klartext-Bestätigung vor kritischen Aktionen
 *
 * Verwendung:
 *   <TouchCard selected={val === 'weizen'} onSelect={() => setVal('weizen')}>Weizen</TouchCard>
 *   <TouchNumericInput label="Brutto (kg)" value={kg} onChange={setKg} />
 *   <TouchToggle value={ja} onChange={setJa} labelYes="Ja" labelNo="Nein" />
 *   <TouchSubmitButton onClick={onSubmit} loading={loading}>Einlagern</TouchSubmitButton>
 */

import React from 'react'
import { cn } from '@/lib/utils'
import { Check } from 'lucide-react'

// ---------------------------------------------------------------------------
// useTouchDevice — erkennt Touch-Gerät (Tablet/Smartphone)
// ---------------------------------------------------------------------------

export function useTouchDevice(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(pointer: coarse)').matches
}

// ---------------------------------------------------------------------------
// TouchCard — Große Auswahl-Karte (min 64px Höhe, volle Breite)
// ---------------------------------------------------------------------------

interface TouchCardProps {
  selected?: boolean
  onSelect?: () => void
  children: React.ReactNode
  className?: string
  disabled?: boolean
  icon?: React.ReactNode
  description?: string
}

export function TouchCard({
  selected,
  onSelect,
  children,
  className,
  disabled,
  icon,
  description,
}: TouchCardProps): JSX.Element {
  return (
    <button
      type="button"
      onClick={onSelect}
      disabled={disabled}
      className={cn(
        // Mindest-Touch-Target: 64px Höhe für sichere Bedienung mit Finger
        'relative flex w-full items-center gap-3 rounded-xl border-2 px-4 py-4 text-left transition-all',
        'min-h-[64px] select-none',
        // Visuelle Zustände
        selected
          ? 'border-blue-500 bg-blue-50 text-blue-900 shadow-sm'
          : 'border-slate-200 bg-white text-slate-800 hover:border-slate-300 active:bg-slate-50',
        disabled && 'cursor-not-allowed opacity-50',
        className,
      )}
      aria-pressed={selected}
    >
      {icon && (
        <span className="flex-shrink-0 text-slate-500">{icon}</span>
      )}
      <span className="flex-1">
        <span className="block text-base font-semibold leading-tight">{children}</span>
        {description && (
          <span className="mt-0.5 block text-sm text-slate-500">{description}</span>
        )}
      </span>
      {selected && (
        <Check className="h-5 w-5 flex-shrink-0 text-blue-500" aria-hidden />
      )}
    </button>
  )
}

// ---------------------------------------------------------------------------
// TouchCardGroup — Gruppe von Auswahl-Karten mit Beschriftung
// ---------------------------------------------------------------------------

interface TouchCardGroupProps {
  label: string
  children: React.ReactNode
  required?: boolean
}

export function TouchCardGroup({ label, children, required }: TouchCardGroupProps): JSX.Element {
  return (
    <div className="space-y-2">
      <p className="text-base font-medium text-slate-700">
        {label}
        {required && <span className="ml-1 text-red-500">*</span>}
      </p>
      <div className="space-y-2">{children}</div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// TouchNumericInput — Nummerische Eingabe mit großem Display
// ---------------------------------------------------------------------------

interface TouchNumericInputProps {
  label: string
  value: number | string
  onChange: (val: string) => void
  unit?: string
  placeholder?: string
  min?: number
  max?: number
  step?: number
  required?: boolean
  className?: string
}

export function TouchNumericInput({
  label,
  value,
  onChange,
  unit,
  placeholder,
  min,
  max,
  step,
  required,
  className,
}: TouchNumericInputProps): JSX.Element {
  return (
    <div className={cn('space-y-1', className)}>
      <label className="block text-base font-medium text-slate-700">
        {label}
        {required && <span className="ml-1 text-red-500">*</span>}
      </label>
      <div className="relative flex items-center">
        <input
          type="number"
          // inputMode="decimal" löst auf iOS/Android den Ziffernblock aus
          inputMode="decimal"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder ?? '0'}
          min={min}
          max={max}
          step={step ?? 'any'}
          className={cn(
            // Touch-Mindestgröße: min-h-[54px], große Schrift für einfaches Ablesen
            'flex w-full rounded-lg border-2 border-slate-200 bg-white px-4 py-3',
            'min-h-[54px] text-2xl font-bold tabular-nums text-slate-900',
            'placeholder:text-base placeholder:font-normal placeholder:text-slate-400',
            'focus:border-blue-500 focus:outline-none focus:ring-0',
            unit && 'pr-16',
          )}
        />
        {unit && (
          <span className="pointer-events-none absolute right-4 text-lg font-medium text-slate-400">
            {unit}
          </span>
        )}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// TouchToggle — Ja/Nein Umschalter (2 große Buttons nebeneinander)
// ---------------------------------------------------------------------------

interface TouchToggleProps {
  value: boolean | null
  onChange: (val: boolean) => void
  label?: string
  labelYes?: string
  labelNo?: string
  required?: boolean
}

export function TouchToggle({
  value,
  onChange,
  label,
  labelYes = 'Ja',
  labelNo = 'Nein',
  required,
}: TouchToggleProps): JSX.Element {
  return (
    <div className="space-y-2">
      {label && (
        <p className="text-base font-medium text-slate-700">
          {label}
          {required && <span className="ml-1 text-red-500">*</span>}
        </p>
      )}
      <div className="grid grid-cols-2 gap-3">
        <button
          type="button"
          onClick={() => onChange(false)}
          className={cn(
            'min-h-[52px] rounded-xl border-2 text-base font-semibold transition-all',
            value === false
              ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
              : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300',
          )}
        >
          {labelNo}
        </button>
        <button
          type="button"
          onClick={() => onChange(true)}
          className={cn(
            'min-h-[52px] rounded-xl border-2 text-base font-semibold transition-all',
            value === true
              ? 'border-red-500 bg-red-50 text-red-700'
              : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300',
          )}
        >
          {labelYes}
        </button>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// TouchSubmitButton — Großer, gut erreichbarer Bestätigungsbutton
// ---------------------------------------------------------------------------

interface TouchSubmitButtonProps {
  onClick?: () => void
  loading?: boolean
  disabled?: boolean
  children: React.ReactNode
  variant?: 'primary' | 'danger' | 'success'
  className?: string
  type?: 'button' | 'submit'
}

export function TouchSubmitButton({
  onClick,
  loading,
  disabled,
  children,
  variant = 'primary',
  className,
  type = 'button',
}: TouchSubmitButtonProps): JSX.Element {
  const colors = {
    primary: 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white',
    danger: 'bg-red-600 hover:bg-red-700 active:bg-red-800 text-white',
    success: 'bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white',
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={cn(
        // Touch-Ziel: 56px Mindesthöhe, volle Breite, großer Text
        'flex min-h-[56px] w-full items-center justify-center rounded-xl',
        'text-lg font-semibold shadow-sm transition-all',
        'disabled:cursor-not-allowed disabled:opacity-50',
        colors[variant],
        className,
      )}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
          Wird gespeichert…
        </span>
      ) : (
        children
      )}
    </button>
  )
}

// ---------------------------------------------------------------------------
// TouchTextInput — Text-Eingabe mit großem Touch-Target
// ---------------------------------------------------------------------------

interface TouchTextInputProps {
  label: string
  value: string
  onChange: (val: string) => void
  placeholder?: string
  required?: boolean
  autoCapitalize?: string
  autoComplete?: string
  className?: string
  hint?: string
}

export function TouchTextInput({
  label,
  value,
  onChange,
  placeholder,
  required,
  autoCapitalize,
  autoComplete,
  className,
  hint,
}: TouchTextInputProps): JSX.Element {
  return (
    <div className={cn('space-y-1', className)}>
      <label className="block text-base font-medium text-slate-700">
        {label}
        {required && <span className="ml-1 text-red-500">*</span>}
      </label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        autoCapitalize={autoCapitalize ?? 'on'}
        autoComplete={autoComplete}
        className={cn(
          'flex w-full rounded-lg border-2 border-slate-200 bg-white px-4 py-3',
          'min-h-[54px] text-lg text-slate-900',
          'placeholder:text-base placeholder:text-slate-400',
          'focus:border-blue-500 focus:outline-none focus:ring-0',
        )}
      />
      {hint && <p className="text-sm text-slate-500">{hint}</p>}
    </div>
  )
}

// ---------------------------------------------------------------------------
// TouchSection — Abschnitt mit Überschrift für Wizard-Schritte
// ---------------------------------------------------------------------------

interface TouchSectionProps {
  title?: string
  children: React.ReactNode
  className?: string
}

export function TouchSection({ title, children, className }: TouchSectionProps): JSX.Element {
  return (
    <div className={cn('space-y-4', className)}>
      {title && (
        <h3 className="text-lg font-semibold text-slate-800">{title}</h3>
      )}
      {children}
    </div>
  )
}

// ---------------------------------------------------------------------------
// TouchConfirmCard — Zusammenfassungs-Karte vor finalem Absenden
// ---------------------------------------------------------------------------

interface TouchConfirmField {
  label: string
  value: string | number
  highlight?: boolean
}

interface TouchConfirmCardProps {
  fields: TouchConfirmField[]
  title?: string
}

export function TouchConfirmCard({ fields, title }: TouchConfirmCardProps): JSX.Element {
  return (
    <div className="rounded-xl border-2 border-slate-200 bg-slate-50 p-4">
      {title && (
        <p className="mb-3 text-base font-semibold text-slate-700">{title}</p>
      )}
      <dl className="space-y-2">
        {fields.map((f) => (
          <div key={f.label} className="flex items-baseline justify-between gap-2">
            <dt className="text-sm text-slate-500">{f.label}</dt>
            <dd
              className={cn(
                'text-right text-base font-medium',
                f.highlight ? 'text-blue-700' : 'text-slate-900',
              )}
            >
              {f.value}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  )
}
