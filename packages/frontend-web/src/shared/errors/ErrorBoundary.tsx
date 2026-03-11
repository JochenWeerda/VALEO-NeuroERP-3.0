import { Component, type ErrorInfo, type ReactNode } from 'react'
import { ErrorState } from '@/components/ErrorState'

interface ErrorBoundaryProps {
  fallback?: ReactNode
  children: ReactNode
  /** Optional name for better error identification */
  name?: string
}

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    if (import.meta.env.DEV) {
      console.error(`ErrorBoundary${this.props.name ? ` [${this.props.name}]` : ''} caught error:`, error, info)
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined })
  }

  handleReload = () => {
    window.location.reload()
  }

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="flex h-96 items-center justify-center p-8">
          <div className="w-full max-w-2xl">
            <ErrorState
              error={this.state.error ?? null}
              title="Fehler beim Laden der Seite"
              message="Es ist ein unerwarteter Fehler aufgetreten."
              recoveryHint="Versuchen Sie es erneut. Wenn der Fehler bestehen bleibt, laden Sie die Seite neu."
              onRetry={this.handleReset}
              onReload={this.handleReload}
              onHome={() => {
                window.location.href = '/'
              }}
            />
            {import.meta.env.DEV && this.state.error ? (
              <pre className="mt-4 max-h-32 overflow-auto rounded-md bg-muted p-3 text-left text-xs text-red-700">
                {this.state.error.message}
              </pre>
            ) : null}
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
