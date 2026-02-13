/**
 * Error State Component
 * Displays errors with retry option instead of silent fallback
 */

import React from 'react'

// ── Types ─────────────────────────────────────────────────────────────

export type ErrorStateProps = {
  error: {
    message?: string
    status?: number
    statusText?: string
  } | null
  onRetry?: () => void
  title?: string
  message?: string
}

// ── ErrorState Component ───────────────────────────────────────────

export function ErrorState({
  error,
  onRetry,
  title = 'Fehler beim Laden der Daten',
  message
}: ErrorStateProps) {
  const errorMessage = message || error?.message || 'Ein unbekannter Fehler ist aufgetreten.'
  const statusText = error?.statusText || (error?.status ? `${error.status} Error` : null)

  return (
    <div
      style={{
        padding: '2rem',
        textAlign: 'center',
        border: '1px solid #ef4444',
        borderRadius: '8px',
        backgroundColor: '#fef2f2',
        color: '#991b1b'
      }}
    >
      <div style={{ marginBottom: '1rem' }}>
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          style={{ margin: '0 auto', display: 'block' }}
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>

      <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.125rem', fontWeight: 600 }}>
        {title}
      </h3>

      <p style={{ margin: '0 0 1rem 0', color: '#b91c1c' }}>
        {errorMessage}
        {statusText && (
          <span style={{ display: 'block', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            ({statusText})
          </span>
        )}
      </p>

      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            padding: '0.5rem 1.5rem',
            backgroundColor: '#dc2626',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 500,
            transition: 'background-color 0.2s'
          }}
          onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#b91c1c')}
          onMouseOut={(e) => (e.currentTarget.style.backgroundColor = '#dc2626')}
        >
          Erneut versuchen
        </button>
      )}
    </div>
  )
}

// ── Loading State Component ─────────────────────────────────────────

export function LoadingState({ message = 'Daten werden geladen...' }: { message?: string }) {
  return (
    <div
      style={{
        padding: '2rem',
        textAlign: 'center',
        color: '#6b7280'
      }}
    >
      <div
        style={{
          width: '32px',
          height: '32px',
          border: '3px solid #e5e7eb',
          borderTopColor: '#3b82f6',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 1rem'
        }}
      />
      <p style={{ margin: 0 }}>{message}</p>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

// ── Empty State Component ───────────────────────────────────────────

export function EmptyState({
  title = 'Keine Daten gefunden',
  message,
  action
}: {
  title?: string
  message?: string
  action?: React.ReactNode
}) {
  return (
    <div
      style={{
        padding: '3rem',
        textAlign: 'center',
        border: '1px dashed #d1d5db',
        borderRadius: '8px',
        backgroundColor: '#f9fafb'
      }}
    >
      <div style={{ marginBottom: '1rem' }}>
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          style={{ margin: '0 auto', display: 'block', color: '#9ca3af' }}
        >
          <path d="M20 6L9 17l-5-5" />
        </svg>
      </div>
      <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem', fontWeight: 500, color: '#374151' }}>
        {title}
      </h3>
      {message && (
        <p style={{ margin: '0 0 1rem 0', color: '#6b7280', fontSize: '0.875rem' }}>
          {message}
        </p>
      )}
      {action}
    </div>
  )
}
