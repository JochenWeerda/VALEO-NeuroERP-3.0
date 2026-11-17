import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from '@/app/routing/test-router'
import { beforeEach, describe, expect, it } from 'vitest'
import { LAUNCHPAD_OVERLAY_STORAGE_KEY } from '@/app/navigation/launchpad-personalization'
import type { LaunchpadSpace } from '@/app/navigation/launchpad-spaces'
import { LaunchpadBoard } from '@/components/navigation/LaunchpadBoard'

const catalog: LaunchpadSpace[] = [
  {
    id: 'handel',
    label: 'Handel & CRM',
    pages: [
      {
        id: 'kunden',
        label: 'Meine Kunden',
        origin: 'catalog',
        locked: true,
        tiles: [
          { id: 'kunden', label: 'Kunden', path: '/verkauf/kunden-liste', kind: 'app' },
          { id: 'kim-cockpit', label: 'KIM – Kunde im Mittelpunkt', path: '/crm', kind: 'task' },
          {
            id: 'meine-aufgaben',
            label: 'Meine Aufgaben',
            path: '/crm/aktivitaeten',
            description: 'Wiedervorlagen und offene Aktivitäten',
            kind: 'task',
          },
        ],
      },
    ],
  },
  {
    id: 'ernte',
    label: 'Ernte & Warenannahme',
    pages: [
      {
        id: 'waage',
        label: 'Annahme & Waage',
        origin: 'catalog',
        locked: true,
        tiles: [
          {
            id: 'warteschlange',
            label: 'Annahme',
            path: '/annahme/warteschlange',
            description: 'Waage und Hofliste',
          },
        ],
      },
    ],
  },
  {
    id: 'steuerung',
    label: 'Steuerung & Compliance',
    pages: [
      {
        id: 'leitstand',
        label: 'Leitstand',
        origin: 'catalog',
        locked: true,
        tiles: [{ id: 'leitstand', label: 'Leitstand', path: '/workflow/leitstand', kind: 'alert' }],
      },
    ],
  },
]

function renderBoard(spaceId = 'handel'): void {
  render(
    <MemoryRouter>
      <LaunchpadBoard
        catalogSpaces={catalog}
        spaceId={spaceId}
        onSpaceIdChange={() => undefined}
        pageBySpace={{}}
        onPageBySpaceChange={() => undefined}
      />
    </MemoryRouter>,
  )
}

describe('LaunchpadBoard', () => {
  beforeEach(() => {
    window.localStorage.clear()
    window.sessionStorage.removeItem(LAUNCHPAD_OVERLAY_STORAGE_KEY)
  })

  it('zeigt gruppierte Starter, filtert Stichworte und Gruppen und entfernt doppelte Routen', async () => {
    const user = userEvent.setup()
    const duplicateCatalog: LaunchpadSpace[] = [
      { ...catalog[0], pages: [{ ...catalog[0].pages[0], tiles: [
        { ...catalog[0].pages[0].tiles[0], keywords: ['Adressbuch'] },
        { id: 'duplicate', label: 'Doppelt', path: '/verkauf/kunden-liste' },
      ] }] },
      catalog[1],
    ]
    render(<MemoryRouter><LaunchpadBoard catalogSpaces={duplicateCatalog} spaceId="handel"
      onSpaceIdChange={() => undefined} pageBySpace={{}} onPageBySpaceChange={() => undefined}
      presentation="launcher" /></MemoryRouter>)

    expect(screen.getByRole('heading', { name: 'Meine Kunden' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Annahme & Waage' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Kunden' })).toHaveAttribute('href', '/verkauf/kunden-liste')
    expect(screen.queryByRole('link', { name: 'Doppelt' })).not.toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent('2 Einstiege')
    const search = screen.getByLabelText('Apps und Masken suchen')
    await user.type(search, 'Adressbuch')
    expect(screen.getByRole('link', { name: 'Kunden' })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Annahme' })).not.toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent('1 Einstieg')
    await user.clear(search)
    await user.type(search, 'Doppelt')
    expect(screen.getByRole('link', { name: 'Doppelt' })).toHaveAttribute('href', '/verkauf/kunden-liste')
    await user.clear(search)
    await user.type(search, 'Ernte')
    expect(screen.getByRole('link', { name: 'Annahme' })).toBeInTheDocument()
    await user.clear(search)
    await user.type(search, 'unbekannt')
    expect(screen.getByText('Keine passenden Apps oder Masken gefunden.')).toBeInTheDocument()
    await user.clear(search)
    await user.click(screen.getByRole('button', { name: 'Startseite anpassen' }))
    expect(screen.getByRole('tab', { name: 'Handel & CRM' })).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Fertig' }))
    expect(screen.getByTestId('launchpad-overview')).toBeInTheDocument()
  })

  it('zeigt Meine Kunden mit drei Einstiegen und Task-Kacheln', () => {
    renderBoard()
    expect(screen.getByRole('link', { name: 'Kunden' })).toHaveAttribute('href', '/verkauf/kunden-liste')
    expect(screen.getByRole('link', { name: 'KIM – Kunde im Mittelpunkt' })).toHaveAttribute('href', '/crm')
    expect(screen.getByRole('link', { name: 'Meine Aufgaben' })).toHaveAttribute('href', '/crm/aktivitaeten')
    expect(screen.getAllByText('Aufgabe')).toHaveLength(2)
    expect(screen.queryByRole('link', { name: /Kunden-Cockpit/i })).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Meine Kunden', level: 2 })).toBeInTheDocument()
    expect(screen.queryByRole('tab', { name: 'Meine Kunden' })).not.toBeInTheDocument()
  })

  it('öffnet den App-Finder ohne Anpassen und sucht in der Beschreibung', async () => {
    const user = userEvent.setup()
    renderBoard()

    await user.click(screen.getByRole('button', { name: 'App-Katalog öffnen' }))
    expect(await screen.findByRole('dialog', { name: 'App-Katalog' })).toBeInTheDocument()
    expect(screen.getByLabelText('Kategorie im Katalog')).toBeInTheDocument()
    expect(screen.queryByText('Hinzufügen')).not.toBeInTheDocument()

    await user.type(screen.getByLabelText('App im Katalog suchen'), 'waage')
    expect(screen.getByRole('button', { name: /Annahme/ })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Meine Aufgaben/ })).not.toBeInTheDocument()
    expect(screen.getByText('Öffnen')).toBeInTheDocument()
  })

  it('hebt den Leitstand als Ausnahme-Kachel hervor', () => {
    renderBoard('steuerung')
    expect(screen.getByRole('link', { name: 'Leitstand' })).toHaveAttribute('href', '/workflow/leitstand')
    expect(screen.getByText('Ausnahme')).toBeInTheDocument()
  })

  it('hält Katalog und Bereichsreiter auf 44 Pixel', () => {
    renderBoard()
    expect(screen.getByRole('button', { name: 'App-Katalog öffnen' })).toHaveClass('h-11')
    expect(screen.getByRole('tab', { name: 'Handel & CRM' })).toHaveClass('min-h-11')
  })

  it('zeigt den Prozessraum als Auswahl statt als Unterreiter', () => {
    const twoPages: LaunchpadSpace[] = [
      {
        ...catalog[0],
        pages: [
          catalog[0].pages[0],
          {
            id: 'crm',
            label: 'CRM & Außendienst',
            origin: 'catalog',
            locked: false,
            tiles: [{ id: 'aktivitaeten', label: 'Aktivitäten', path: '/crm/aktivitaeten', kind: 'task' }],
          },
        ],
      },
    ]

    render(
      <MemoryRouter>
        <LaunchpadBoard
          catalogSpaces={twoPages}
          spaceId="handel"
          onSpaceIdChange={() => undefined}
          pageBySpace={{}}
          onPageBySpaceChange={() => undefined}
        />
      </MemoryRouter>,
    )

    expect(screen.getByRole('combobox', { name: 'Prozessraum' })).toHaveClass('h-11')
    expect(screen.getByRole('combobox', { name: 'Prozessraum' })).toHaveTextContent('Meine Kunden')
    expect(screen.queryByRole('tab', { name: 'Meine Kunden' })).not.toBeInTheDocument()
    expect(screen.queryByRole('tab', { name: 'CRM & Außendienst' })).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Kunden' })).toBeInTheDocument()
  })
})
