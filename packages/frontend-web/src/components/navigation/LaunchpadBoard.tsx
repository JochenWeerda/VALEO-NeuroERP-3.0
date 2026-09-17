import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from '@/app/routing/typed-router'
import {
  Eye,
  EyeOff,
  Pencil,
  Plus,
  RotateCcw,
  Trash2,
  X,
} from 'lucide-react'
import { toast } from 'sonner'
import {
  flattenLaunchpadTiles,
  launchpadTileKind,
  launchpadTileSurface,
  matchesLaunchpadCatalogQuery,
  type LaunchpadAppTile,
  type LaunchpadPage,
  type LaunchpadSpace,
} from '@/app/navigation/launchpad-spaces'
import {
  CUSTOM_PAGE_PLACEHOLDER,
  addCustomPage,
  addTile,
  applyLaunchpadOverlay,
  catalogTileIndex,
  deletePage,
  hidePage,
  movePage,
  moveTileToPage,
  removeTile,
  renamePage,
  reorderTiles,
  resetPage,
  setTileAppearance,
  showPage,
} from '@/app/navigation/launchpad-personalization'
import { useLaunchpadPersonalization } from '@/hooks/useLaunchpadPersonalization'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const TILE_DRAG_TYPE = 'application/x-valeo-launchpad-tile'

type TileDragPayload = {
  spaceId: string
  pageId: string
  tileId: string
}

type LaunchpadBoardProps = {
  catalogSpaces: LaunchpadSpace[]
  spaceId: string
  onSpaceIdChange: (spaceId: string) => void
  pageBySpace: Record<string, string>
  onPageBySpaceChange: (pages: Record<string, string>) => void
}

export function LaunchpadBoard({
  catalogSpaces,
  spaceId,
  onSpaceIdChange,
  pageBySpace,
  onPageBySpaceChange,
}: LaunchpadBoardProps): JSX.Element {
  const { overlay, setOverlay } = useLaunchpadPersonalization()
  const [personalize, setPersonalize] = useState(false)
  const [finderOpen, setFinderOpen] = useState(false)
  const [addGroupOpen, setAddGroupOpen] = useState(false)
  const [settingsTile, setSettingsTile] = useState<LaunchpadAppTile | null>(null)
  const [moveTile, setMoveTile] = useState<LaunchpadAppTile | null>(null)
  const [renamePageId, setRenamePageId] = useState<string | null>(null)
  const [groupName, setGroupName] = useState('')
  const [finderQuery, setFinderQuery] = useState('')
  const [finderCategory, setFinderCategory] = useState('all')
  const navigate = useNavigate()
  const [settingsTitle, setSettingsTitle] = useState('')
  const [settingsDescription, setSettingsDescription] = useState('')
  const [moveTarget, setMoveTarget] = useState('')

  const spaces = useMemo(
    () => applyLaunchpadOverlay(catalogSpaces, overlay, { includeHidden: personalize }),
    [catalogSpaces, overlay, personalize],
  )
  const activeSpaceId = spaces.some((space) => space.id === spaceId) ? spaceId : (spaces[0]?.id ?? '')
  const activeSpace = spaces.find((space) => space.id === activeSpaceId) ?? spaces[0]
  const activePageId = activeSpace
    ? activeSpace.pages.some((page) => page.id === pageBySpace[activeSpace.id])
      ? pageBySpace[activeSpace.id]
      : (activeSpace.pages.find((page) => page.hidden !== true)?.id ?? activeSpace.pages[0]?.id ?? '')
    : ''
  const activePage = activeSpace?.pages.find((page) => page.id === activePageId)
  const catalogApps = useMemo(() => {
    const unique = new Map<string, LaunchpadAppTile & { spaceId: string; spaceLabel: string }>()
    const needle = finderQuery.trim().toLowerCase()
    for (const tile of flattenLaunchpadTiles(catalogSpaces)) {
      if (finderCategory !== 'all' && tile.spaceId !== finderCategory) {
        continue
      }
      const labeled = overlay.tileLabels[tile.id] ? { ...tile, label: overlay.tileLabels[tile.id] } : tile
      const inPlace = needle.length > 0 && (labeled.pageLabel.toLowerCase().includes(needle) || labeled.spaceLabel.toLowerCase().includes(needle))
      if (!matchesLaunchpadCatalogQuery(labeled, finderQuery) && !inPlace) {
        continue
      }
      if (!unique.has(tile.id)) {
        unique.set(tile.id, labeled)
      }
    }
    return [...unique.values()]
  }, [catalogSpaces, finderCategory, finderQuery, overlay.tileLabels])

  useEffect(() => {
    const openFinder = (): void => {
      setFinderOpen(true)
    }
    window.addEventListener('valeo:open-app-finder', openFinder)
    return () => window.removeEventListener('valeo:open-app-finder', openFinder)
  }, [])

  const selectPage = (nextSpaceId: string, nextPageId: string): void => {
    onPageBySpaceChange({ ...pageBySpace, [nextSpaceId]: nextPageId })
  }

  const handleDropOnPage = (targetPage: LaunchpadPage, event: React.DragEvent): void => {
    event.preventDefault()
    const payload = readDragPayload(event)
    if (!payload || payload.spaceId !== activeSpaceId || !activeSpace) {
      return
    }
    const sourcePage = activeSpace.pages.find((page) => page.id === payload.pageId)
    if (!sourcePage) {
      return
    }
    if (sourcePage.id === targetPage.id) {
      const fromIndex = sourcePage.tiles.findIndex((tile) => tile.id === payload.tileId)
      const dropTileId = (event.currentTarget as HTMLElement).dataset.tileId
      const toIndex = dropTileId ? targetPage.tiles.findIndex((tile) => tile.id === dropTileId) : targetPage.tiles.length - 1
      if (fromIndex >= 0 && toIndex >= 0) {
        setOverlay((current) => reorderTiles(current, activeSpaceId, sourcePage, fromIndex, toIndex))
      }
      return
    }
    setOverlay((current) => moveTileToPage(current, activeSpaceId, sourcePage, targetPage, payload.tileId))
    toast.success('Kachel verschoben')
  }

  return (
    <section className="overflow-hidden rounded-(--radius) border border-border bg-card shadow-sm">
      <Tabs
        value={activeSpaceId}
        onValueChange={(next) => {
          onSpaceIdChange(next)
        }}
      >
        <div className="flex flex-wrap items-center gap-2 border-b border-border bg-muted/40 px-3 py-2">
          <TabsList aria-label="Arbeitswelten" className="min-w-0 flex-1 flex-nowrap justify-start overflow-x-auto rounded-none bg-transparent p-0">
            {spaces.map((space) => (
              <TabsTrigger key={space.id} value={space.id} className="min-h-11 shrink-0 sm:min-w-0">
                {space.label}
              </TabsTrigger>
            ))}
          </TabsList>
          <div className="flex shrink-0 flex-wrap justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setFinderOpen(true)}
              aria-label="App-Katalog öffnen"
            >
              App-Katalog
            </Button>
            {personalize ? (
              <Button type="button" onClick={() => setPersonalize(false)}>
                Fertig
              </Button>
            ) : (
              <Button
                type="button"
                variant="outline"
                onClick={() => setPersonalize(true)}
                aria-label="Startseite anpassen"
              >
                <Pencil className="h-4 w-4" />
                Startseite anpassen
              </Button>
            )}
          </div>
        </div>
        {spaces.map((space) => {
          const pageId =
            space.pages.some((page) => page.id === pageBySpace[space.id])
              ? pageBySpace[space.id]
              : (space.pages.find((page) => page.hidden !== true)?.id ?? space.pages[0]?.id ?? '')
          const visiblePages = space.pages.filter((page) => page.hidden !== true)
          const currentPage = space.pages.find((page) => page.id === pageId) ?? visiblePages[0]
          return (
            <TabsContent key={space.id} value={space.id} className="mt-0">
              <Tabs
                value={pageId}
                onValueChange={(next) => {
                  selectPage(space.id, next)
                  setRenamePageId(null)
                }}
              >
                {personalize ? (
                  <div className="flex items-center gap-2 border-b border-border bg-background px-2 py-1">
                    <TabsList aria-label="Seiten" className="min-w-0 flex-1 flex-nowrap justify-start overflow-x-auto rounded-none bg-transparent p-0">
                      {space.pages.map((page) => (
                        <TabsTrigger
                          key={page.id}
                          value={page.id}
                          className="min-h-11 shrink-0 sm:min-w-0 data-[state=active]:shadow-sm"
                          onDragOver={(event) => event.preventDefault()}
                          onDrop={(event) => handleDropOnPage(page, event)}
                        >
                          {page.hidden === true ? `${page.label} (ausgeblendet)` : page.label}
                        </TabsTrigger>
                      ))}
                    </TabsList>
                    <Button type="button" variant="ghost" onClick={() => setAddGroupOpen(true)}>
                      <Plus className="h-4 w-4" />
                      Gruppe hinzufügen
                    </Button>
                  </div>
                ) : (
                  <div className="flex flex-wrap items-center gap-3 border-b border-border bg-background px-4 py-3">
                    {visiblePages.length > 1 ? (
                      <>
                        <span className="text-2xs tracking-wide uppercase text-muted-foreground">Prozessraum</span>
                        <Select
                          value={pageId}
                          onValueChange={(next) => {
                            selectPage(space.id, next)
                          }}
                        >
                          <SelectTrigger aria-label="Prozessraum" className="h-11 w-auto min-w-52 max-w-full bg-background">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent className="bg-background">
                            {visiblePages.map((page) => (
                              <SelectItem key={page.id} value={page.id}>
                                {page.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </>
                    ) : (
                      <h2 className="text-lg font-semibold tracking-normal text-foreground">{currentPage?.label}</h2>
                    )}
                  </div>
                )}
                {space.pages.map((page) => (
                  <TabsContent key={page.id} value={page.id} className="mt-0 p-4">
                    {personalize ? (
                      <PagePersonalizeBar
                        key={page.id}
                        page={page}
                        renaming={renamePageId === page.id}
                        onRenameStart={() => setRenamePageId(page.id)}
                        onRenameCancel={() => setRenamePageId(null)}
                        onRename={(label) => {
                          setOverlay((current) => renamePage(current, space.id, page, label))
                          setRenamePageId(null)
                        }}
                        onHide={() => {
                          setOverlay((current) => hidePage(current, space.id, page))
                          toast.success('Gruppe ausgeblendet')
                        }}
                        onShow={() => setOverlay((current) => showPage(current, space.id, page.id))}
                        onReset={() => {
                          setOverlay((current) => resetPage(current, space.id, page))
                          toast.success('Gruppe zurückgesetzt')
                        }}
                        onDelete={() => {
                          setOverlay((current) => deletePage(current, space.id, page))
                          toast.success('Gruppe gelöscht')
                        }}
                        onMoveLeft={() => {
                          const ids = space.pages.map((entry) => entry.id)
                          setOverlay((current) => movePage(current, space.id, ids, pageIndexOf(space, page.id), pageIndexOf(space, page.id) - 1))
                        }}
                        onMoveRight={() => {
                          const ids = space.pages.map((entry) => entry.id)
                          setOverlay((current) => movePage(current, space.id, ids, pageIndexOf(space, page.id), pageIndexOf(space, page.id) + 1))
                        }}
                        canMoveLeft={pageIndexOf(space, page.id) > 0}
                        canMoveRight={pageIndexOf(space, page.id) < space.pages.length - 1}
                      />
                    ) : null}
                    <div
                      className="flex min-h-36 flex-wrap gap-4 pt-2"
                      onDragOver={personalize ? (event) => event.preventDefault() : undefined}
                      onDrop={personalize ? (event) => handleDropOnPage(page, event) : undefined}
                    >
                      {page.tiles.map((tile, tileIndex) => (
                        <LaunchpadTile
                          key={tile.id}
                          tile={tile}
                          caption={personalize ? tile.description : undefined}
                          personalize={personalize}
                          onRemove={() => {
                            setOverlay((current) => removeTile(current, space.id, page, tile.id))
                            toast.success('Kachel entfernt')
                          }}
                          onSettings={() => {
                            setSettingsTile(tile)
                            setSettingsTitle(tile.label)
                            setSettingsDescription(tile.description ?? '')
                          }}
                          onMove={() => {
                            setMoveTile(tile)
                            setMoveTarget(page.id)
                          }}
                          onDragStart={(event) => {
                            event.dataTransfer.setData(
                              TILE_DRAG_TYPE,
                              JSON.stringify({ spaceId: space.id, pageId: page.id, tileId: tile.id } satisfies TileDragPayload),
                            )
                            event.dataTransfer.effectAllowed = 'move'
                          }}
                          onDrop={(event) => handleDropOnPage(page, event)}
                          onKeyReorder={(direction) => {
                            setOverlay((current) =>
                              reorderTiles(current, space.id, page, tileIndex, tileIndex + direction),
                            )
                          }}
                        />
                      ))}
                      {personalize ? (
                        <button
                          type="button"
                          onClick={() => setFinderOpen(true)}
                          className="flex h-32 w-52 shrink-0 flex-col items-center justify-center gap-2 rounded-(--radius) border border-dashed border-border text-sm text-muted-foreground hover:border-primary hover:text-foreground"
                        >
                          <Plus className="h-4 w-4" />
                          Kachel hinzufügen
                        </button>
                      ) : null}
                    </div>
                  </TabsContent>
                ))}
              </Tabs>
            </TabsContent>
          )
        })}
      </Tabs>

      <Dialog open={finderOpen} onOpenChange={setFinderOpen}>
        <DialogContent className="max-w-2xl bg-background">
          <DialogHeader>
            <DialogTitle>App-Katalog</DialogTitle>
            <DialogDescription>
            {personalize
              ? 'Verfügbare Belege und Apps. Die Auswahl landet auf der aktuellen Seite.'
              : 'Belege und Apps der Arbeitswelten öffnen. Hinzufügen nur im Anpassen-Modus.'}
          </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-2 sm:flex-row">
            <Select value={finderCategory} onValueChange={setFinderCategory}>
              <SelectTrigger aria-label="Kategorie im Katalog" className="h-11">
                <SelectValue placeholder="Arbeitswelt" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Alle Arbeitswelten</SelectItem>
                {catalogSpaces.map((space) => (
                  <SelectItem key={space.id} value={space.id}>
                    {space.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              value={finderQuery}
              onChange={(event) => setFinderQuery(event.target.value)}
              placeholder="Name oder Beschreibung..."
              aria-label="App im Katalog suchen"
            />
          </div>
          <ul className="max-h-80 space-y-1 overflow-y-auto">
            {catalogApps.map((tile) => (
                <li key={tile.id}>
                  <button
                    type="button"
                    className="flex min-h-11 w-full items-center justify-between rounded-md px-2 py-2 text-left text-sm hover:bg-muted"
                    onClick={() => {
                      if (personalize) {
                        if (!activePage || !activeSpace) {
                          return
                        }
                        if (activePage.tiles.some((entry) => entry.id === tile.id)) {
                          toast.message('Kachel ist schon auf dieser Seite')
                          return
                        }
                        const catalogTile = catalogTileIndex(catalogSpaces).get(tile.id)
                        if (!catalogTile) {
                          return
                        }
                        setOverlay((current) => addTile(current, activeSpace.id, activePage, catalogTile.id))
                        toast.success(`${tile.label} hinzugefügt`)
                        setFinderOpen(false)
                        return
                      }
                      navigate(tile.path)
                      setFinderOpen(false)
                    }}
                  >
                    <span className="flex min-w-0 flex-col">
                      <span>{tile.label}</span>
                      {tile.description ? (
                        <span className="truncate text-2xs text-muted-foreground">{tile.description}</span>
                      ) : null}
                    </span>
                    <span className="text-2xs tracking-wide uppercase text-muted-foreground">
                      {personalize ? 'Hinzufügen' : 'Öffnen'}
                    </span>
                  </button>
                </li>
              ))}
          </ul>
        </DialogContent>
      </Dialog>

      <Dialog open={addGroupOpen} onOpenChange={setAddGroupOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Gruppe hinzufügen</DialogTitle>
            <DialogDescription>Die neue Gruppe erscheint in der aktuellen Arbeitswelt.</DialogDescription>
          </DialogHeader>
          <Label htmlFor="launchpad-group-name">Gruppenname</Label>
          <Input
            id="launchpad-group-name"
            value={groupName}
            onChange={(event) => setGroupName(event.target.value)}
            placeholder={CUSTOM_PAGE_PLACEHOLDER}
          />
          <DialogFooter>
            <Button
              type="button"
              onClick={() => {
                if (!activeSpace) {
                  return
                }
                const created = addCustomPage(overlay, activeSpace.id, groupName)
                setOverlay(created.overlay)
                selectPage(activeSpace.id, created.pageId)
                setGroupName('')
                setAddGroupOpen(false)
                toast.success('Gruppe angelegt')
              }}
            >
              Anlegen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={settingsTile !== null} onOpenChange={(open) => !open && setSettingsTile(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Kachel anpassen</DialogTitle>
            <DialogDescription>Titel und Beschreibung gelten nur auf der Startseite, nicht in der Maske selbst.</DialogDescription>
          </DialogHeader>
          <Label htmlFor="launchpad-tile-title">Titel</Label>
          <Input id="launchpad-tile-title" value={settingsTitle} onChange={(event) => setSettingsTitle(event.target.value)} />
          <Label htmlFor="launchpad-tile-description">Beschreibung</Label>
          <Input
            id="launchpad-tile-description"
            value={settingsDescription}
            onChange={(event) => setSettingsDescription(event.target.value)}
          />
          <DialogFooter>
            <Button
              type="button"
              onClick={() => {
                if (!settingsTile) {
                  return
                }
                setOverlay((current) => setTileAppearance(current, settingsTile.id, settingsTitle, settingsDescription))
                setSettingsTile(null)
                toast.success('Kachel gespeichert')
              }}
            >
              Speichern
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={moveTile !== null} onOpenChange={(open) => !open && setMoveTile(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Kachel verschieben</DialogTitle>
            <DialogDescription>Ziel ist eine Gruppe in der aktuellen Arbeitswelt.</DialogDescription>
          </DialogHeader>
          <Label htmlFor="launchpad-move-target">Gruppe</Label>
          <Select value={moveTarget} onValueChange={setMoveTarget}>
            <SelectTrigger id="launchpad-move-target" aria-label="Zielgruppe">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {(activeSpace?.pages ?? []).map((page) => (
                <SelectItem key={page.id} value={page.id}>
                  {page.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <DialogFooter>
            <Button
              type="button"
              onClick={() => {
                if (!moveTile || !activeSpace || !activePage) {
                  return
                }
                const target = activeSpace.pages.find((page) => page.id === moveTarget)
                if (!target) {
                  return
                }
                setOverlay((current) => moveTileToPage(current, activeSpace.id, activePage, target, moveTile.id))
                setMoveTile(null)
                toast.success('Kachel verschoben')
              }}
            >
              Verschieben
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  )
}

function pageIndexOf(space: LaunchpadSpace, pageId: string): number {
  return space.pages.findIndex((page) => page.id === pageId)
}

function readDragPayload(event: React.DragEvent): TileDragPayload | null {
  const raw = event.dataTransfer.getData(TILE_DRAG_TYPE) || event.dataTransfer.getData('text/plain')
  if (!raw) {
    return null
  }
  try {
    const parsed: unknown = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object') {
      return null
    }
    const value = parsed as Record<string, unknown>
    if (typeof value.spaceId !== 'string' || typeof value.pageId !== 'string' || typeof value.tileId !== 'string') {
      return null
    }
    return { spaceId: value.spaceId, pageId: value.pageId, tileId: value.tileId }
  } catch {
    return null
  }
}

function PagePersonalizeBar({
  page,
  renaming,
  onRenameStart,
  onRenameCancel,
  onRename,
  onHide,
  onShow,
  onReset,
  onDelete,
  onMoveLeft,
  onMoveRight,
  canMoveLeft,
  canMoveRight,
}: {
  page: LaunchpadPage
  renaming: boolean
  onRenameStart: () => void
  onRenameCancel: () => void
  onRename: (label: string) => void
  onHide: () => void
  onShow: () => void
  onReset: () => void
  onDelete: () => void
  onMoveLeft: () => void
  onMoveRight: () => void
  canMoveLeft: boolean
  canMoveRight: boolean
}): JSX.Element {
  const [draft, setDraft] = useState(page.label)
  return (
    <div className="mb-3 flex flex-wrap items-center gap-2">
      {renaming ? (
        <Input
          value={draft}
          aria-label="Gruppenname"
          className="h-11 w-56"
          autoFocus
          onChange={(event) => setDraft(event.target.value)}
          onBlur={() => onRename(draft)}
          onKeyDown={(event) => {
            if (event.key === 'Escape') {
              event.preventDefault()
              setDraft(page.label)
              onRenameCancel()
            }
            if (event.key === 'Enter') {
              event.preventDefault()
              onRename(draft)
            }
          }}
        />
      ) : (
        <span className="text-sm font-medium text-foreground">{page.label}</span>
      )}
      <Button type="button" variant="ghost" onClick={onRenameStart}>
        Umbenennen
      </Button>
      <Button type="button" variant="ghost" onClick={onMoveLeft} disabled={!canMoveLeft}>
        Nach links
      </Button>
      <Button type="button" variant="ghost" onClick={onMoveRight} disabled={!canMoveRight}>
        Nach rechts
      </Button>
      {page.hidden === true ? (
        <Button type="button" variant="ghost" onClick={onShow}>
          <Eye className="h-4 w-4" />
          Einblenden
        </Button>
      ) : page.locked ? null : (
        <Button type="button" variant="ghost" onClick={onHide} disabled={page.locked}>
          <EyeOff className="h-4 w-4" />
          Ausblenden
        </Button>
      )}
      {page.origin === 'catalog' ? (
        <Button type="button" variant="ghost" onClick={onReset}>
          <RotateCcw className="h-4 w-4" />
          Zurücksetzen
        </Button>
      ) : (
        <Button type="button" variant="ghost" onClick={onDelete}>
          <Trash2 className="h-4 w-4" />
          Löschen
        </Button>
      )}
    </div>
  )
}

function LaunchpadTile({
  tile,
  caption,
  personalize,
  onRemove,
  onSettings,
  onMove,
  onDragStart,
  onDrop,
  onKeyReorder,
}: {
  tile: LaunchpadAppTile
  caption?: string
  personalize: boolean
  onRemove: () => void
  onSettings: () => void
  onMove: () => void
  onDragStart: (event: React.DragEvent) => void
  onDrop: (event: React.DragEvent) => void
  onKeyReorder: (direction: -1 | 1) => void
}): JSX.Element {
  const kind = tile.kind ?? launchpadTileKind(tile.id)
  const surface = launchpadTileSurface(tile.id, kind)
  const emphasized = kind === 'task' || kind === 'alert'
  const className =
    `${emphasized ? 'min-h-36 w-full max-w-56 sm:w-56' : 'min-h-32 w-full max-w-52 sm:w-52'} relative flex min-h-11 shrink-0 flex-col justify-between rounded-(--radius) border border-l-4 p-3 text-left shadow-sm transition-shadow hover:shadow-md focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring`
  const kindCaption = kind === 'alert' ? 'Ausnahme' : kind === 'task' ? 'Aufgabe' : 'App'

  const body = (
    <>
      <span className="text-2xs tracking-wide uppercase text-muted-foreground">
        {caption ?? kindCaption}
      </span>
      <span className={emphasized ? 'text-base font-semibold leading-snug text-foreground' : 'text-sm font-semibold leading-snug text-foreground'}>
        {tile.label}
      </span>
    </>
  )

  if (!personalize) {
    return (
      <Link to={tile.path} aria-label={tile.label} className={className} style={surface}>
        {body}
      </Link>
    )
  }

  return (
    <div
      className={className}
      style={surface}
      data-tile-id={tile.id}
      draggable
      onDragStart={onDragStart}
      onDragOver={(event) => event.preventDefault()}
      onDrop={onDrop}
    >
      <button
        type="button"
        className="absolute right-1 top-1 rounded-sm p-1 text-muted-foreground hover:bg-background hover:text-foreground"
        aria-label={`${tile.label} entfernen`}
        onClick={onRemove}
      >
        <X className="h-4 w-4" />
      </button>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            type="button"
            aria-label={`${tile.label} Aktionen`}
            className="flex h-full w-full flex-col justify-between pt-4 text-left"
            onKeyDown={(event) => {
              if (event.altKey && event.key === 'ArrowLeft') {
                event.preventDefault()
                onKeyReorder(-1)
              }
              if (event.altKey && event.key === 'ArrowRight') {
                event.preventDefault()
                onKeyReorder(1)
              }
            }}
          >
            {body}
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuItem onSelect={onSettings}>Kachel anpassen</DropdownMenuItem>
          <DropdownMenuItem onSelect={onMove}>Verschieben</DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onSelect={onRemove}>Entfernen</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
