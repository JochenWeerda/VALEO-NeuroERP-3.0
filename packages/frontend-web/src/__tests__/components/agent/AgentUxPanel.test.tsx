import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AgentUxPanel } from '@/components/agent/AgentUxPanel'

describe('AgentUxPanel', () => {
  it('zeigt Confidence, Quellen und Aktion', () => {
    render(
      <AgentUxPanel
        summary="Agentenfaehigkeit und Wissenssicherheit fuer den Prozesskern."
        confidence={87}
        sources={[
          {
            label: 'Agent Manifest',
            href: '/api/v1/admin/agent-manifest',
            description: 'Einstiegspunkt fuer externe Agenten.',
          },
          {
            label: 'Command Catalog',
            href: '/api/v1/commands/catalog',
            description: 'Maschinenlesbare Command-Sicht.',
          },
        ]}
        action={{
          label: 'Monitoring oeffnen',
          href: '#idempotency-monitoring',
          description: 'Wechselt zur Idempotenz-Sicht.',
        }}
      />,
    )

    expect(screen.getByText('Agent UX Panel')).toBeInTheDocument()
    expect(screen.getByText('87%')).toBeInTheDocument()
    expect(screen.getByText('Agent Manifest')).toBeInTheDocument()
    expect(screen.getByText('Command Catalog')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Monitoring oeffnen/i })).toBeInTheDocument()
  })
})
