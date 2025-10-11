import { Component, type ErrorInfo, type ReactNode } from 'react'

interface ErrorBoundaryProps {
  fallback?: ReactNode
  children: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught error:', error, info)
    }
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div className="flex h-full flex-col items-center justify-center gap-4 p-6 text-sm text-muted-foreground">
          <p>Etwas ist schiefgelaufen.</p>
          <button
            type="button"
            onClick={() => this.setState({ hasError: false })}
            className="rounded border px-3 py-1 text-xs"
          >
            Erneut versuchen
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
