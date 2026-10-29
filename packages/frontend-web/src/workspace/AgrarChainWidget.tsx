import { useEffect, useState } from 'react'
import { Link, type RouteTarget } from '@/app/routing/typed-router'
import {
  agrarChainErrorMessage,
  agrarChainLinkForHint,
  loadAgrarChainHints,
  loadVisibleAgrarChain,
  type AgrarChainQuery,
  type AgrarChainViewState,
} from './agrar-chain'

type AgrarChainWidgetProps = {
  queries?: AgrarChainQuery[]
  /** Schon geladene Sicht. Dann kein zweiter GET. */
  view?: AgrarChainViewState
}

export function useAgrarChainView(queries?: AgrarChainQuery[], enabled = true): AgrarChainViewState {
  const [state, setState] = useState<AgrarChainViewState>({ status: 'pending' })
  const queryKey = queries === undefined ? null : JSON.stringify(queries)

  useEffect(() => {
    if (!enabled) {
      return
    }
    let cancelled = false
    void (async () => {
      try {
        const next =
          queryKey === null
            ? await loadVisibleAgrarChain()
            : await loadAgrarChainHints(JSON.parse(queryKey) as AgrarChainQuery[])
        if (!cancelled) {
          setState(next)
        }
      } catch (error) {
        if (!cancelled) {
          setState({ status: 'error', message: agrarChainErrorMessage(error) })
        }
      }
    })()
    return () => {
      cancelled = true
    }
  }, [enabled, queryKey])

  return state
}

export function AgrarChainWidget({ queries, view }: AgrarChainWidgetProps): JSX.Element | null {
  const loaded = useAgrarChainView(queries, view === undefined)
  const state = view ?? loaded

  if (state.status === 'hidden') {
    return null
  }

  return (
    <section
      aria-label="Agrar-Kette"
      aria-busy={state.status === 'pending'}
      data-testid="workspace-agrar-chain"
      data-chain-status={state.status}
    >
      <h2 className="text-lg font-semibold text-foreground">Agrar-Kette</h2>
      {state.status === 'pending' ? (
        <p className="mt-2 text-sm text-muted-foreground">Kette wird geladen</p>
      ) : null}
      {state.status === 'error' ? (
        <p className="mt-2 text-sm text-status-error" role="alert">
          {state.message}
        </p>
      ) : null}
      {state.status === 'empty' ? (
        <p className="mt-2 text-sm text-muted-foreground">keine Kette</p>
      ) : null}
      {state.status === 'ready' ? (
        <>
          {state.warning ? (
            <p className="mt-2 text-sm text-status-error" role="alert">
              {state.warning}
            </p>
          ) : null}
          <ul className="mt-2 flex flex-col gap-2">
            {state.hints.map((hint) => {
              const link = agrarChainLinkForHint(hint)
              const label = `${hint.contract_ref}: ${link.label}`
              return (
                <li
                  key={`${hint.source_model}:${hint.contract_ref}:${hint.next_step}`}
                  className="rounded-(--radius) border border-border bg-card px-3 py-2"
                  data-contract-ref={hint.contract_ref}
                  data-next-step={hint.next_step}
                  data-source-model={hint.source_model}
                >
                  {link.clickable && link.route ? (
                    <Link
                      to={link.route as RouteTarget}
                      className="text-sm font-medium text-foreground underline-offset-4 hover:underline"
                    >
                      {label}
                    </Link>
                  ) : (
                    <p className="text-sm font-medium text-foreground">{label}</p>
                  )}
                  {hint.reason ? (
                    <p className="truncate text-xs text-muted-foreground">{hint.reason}</p>
                  ) : null}
                </li>
              )
            })}
          </ul>
        </>
      ) : null}
    </section>
  )
}
