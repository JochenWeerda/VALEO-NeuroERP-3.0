import {
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
  type ReactNode,
} from 'react'
import { cn } from '@/lib/utils'

export interface PageSection {
  key: string
  label: string
  /** Lazy sections mount once they approach the viewport or are jumped to. */
  lazy: boolean
  render: () => ReactNode
}

/** Collapse after this scroll depth, expand again only above the lower bound — avoids flicker at one threshold. */
export const HEADER_COLLAPSE_AT_PX = 96
export const HEADER_EXPAND_BELOW_PX = 48
const ANCHOR_GAP_PX = 16
const LAZY_MOUNT_MARGIN = '600px 0px'

type ScrollTarget = HTMLElement | Window

function findScrollParent(element: HTMLElement | null): ScrollTarget {
  let current = element?.parentElement ?? null
  while (current && current !== document.body && current !== document.documentElement) {
    const overflowY = window.getComputedStyle(current).overflowY
    if (overflowY === 'auto' || overflowY === 'scroll' || overflowY === 'overlay') return current
    current = current.parentElement
  }
  return window
}

// Identity check instead of `instanceof Window`: the Window constructor differs across realms (iframes, jsdom).
function isWindowTarget(target: ScrollTarget): target is Window {
  return target === window
}

// Sticky elements stick to the scroll container's content edge, so its padding
// would leave a strip above the header through which content scrolls visibly.
function scrollPaddingTop(target: ScrollTarget): number {
  if (isWindowTarget(target)) return 0
  const padding = Number.parseFloat(window.getComputedStyle(target).paddingTop)
  return Number.isFinite(padding) ? padding : 0
}

function scrollMetrics(target: ScrollTarget): { top: number; atEnd: boolean } {
  if (isWindowTarget(target)) {
    const root = document.scrollingElement ?? document.documentElement
    return { top: window.scrollY, atEnd: window.innerHeight + window.scrollY >= root.scrollHeight - 2 }
  }
  return { top: target.scrollTop, atEnd: target.clientHeight + target.scrollTop >= target.scrollHeight - 2 }
}

export function nextCondensedState(condensed: boolean, scrollTop: number): boolean {
  return condensed ? scrollTop > HEADER_EXPAND_BELOW_PX : scrollTop > HEADER_COLLAPSE_AT_PX
}

function prefersReducedMotion(): boolean {
  return typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

function sectionIndexFromShortcut(event: ReactKeyboardEvent<HTMLElement>): number | undefined {
  if (!event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return undefined
  const digit = /^Digit([1-9])$/.exec(event.code)?.[1] ?? (/^[1-9]$/.test(event.key) ? event.key : undefined)
  return digit ? Number(digit) - 1 : undefined
}

/**
 * Durchgehende Belegseite (Meridian `sectionNavigation=anchors`): alle Abschnitte
 * stehen untereinander, die Register werden zu Sprungmarken mit Scroll-Spy.
 * Kopf und Sprungleiste bilden gemeinsam einen sticky Bereich, damit die
 * Sprungziele genau unter ihm landen.
 */
export function SectionPageRenderer({
  header,
  sections,
  requestedSectionKey,
  onRequestHandled,
  children,
}: {
  header: (_condensed: boolean) => ReactNode
  sections: PageSection[]
  /** Section that must become visible, e.g. to reveal a field from the message panel. */
  requestedSectionKey?: string
  onRequestHandled?: () => void
  /** Content between the sticky area and the first section (messages, workflow, summary). */
  children?: ReactNode
}): JSX.Element {
  const idPrefix = useId().replace(/:/g, '')
  const rootRef = useRef<HTMLDivElement>(null)
  const stickyRef = useRef<HTMLDivElement>(null)
  const sectionRefs = useRef(new Map<string, HTMLElement>())
  const scrollTargetRef = useRef<ScrollTarget | null>(null)
  const [condensed, setCondensed] = useState(false)
  const [stickyHeight, setStickyHeight] = useState(0)
  const [stickyInset, setStickyInset] = useState(0)
  const [activeKey, setActiveKey] = useState(sections[0]?.key)
  const [mounted, setMounted] = useState<Set<string>>(
    () => new Set(sections.filter((section, index) => index === 0 || !section.lazy).map((section) => section.key)),
  )

  const sectionKeys = sections.map((section) => section.key).join('|')

  const mountSection = useCallback((key: string) => {
    setMounted((current) => (current.has(key) ? current : new Set(current).add(key)))
  }, [])

  useLayoutEffect(() => {
    const element = stickyRef.current
    if (!element) return
    const measure = (): void => setStickyHeight(element.getBoundingClientRect().height)
    measure()
    if (typeof ResizeObserver === 'undefined') return
    const observer = new ResizeObserver(measure)
    observer.observe(element)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    const target = findScrollParent(rootRef.current)
    scrollTargetRef.current = target
    const measureInset = (): void => setStickyInset(scrollPaddingTop(target))
    measureInset()
    window.addEventListener('resize', measureInset)
    let frame = 0
    const update = (): void => {
      frame = 0
      const { top, atEnd } = scrollMetrics(target)
      setCondensed((current) => nextCondensedState(current, top))
      const keys = sectionKeys ? sectionKeys.split('|') : []
      if (keys.length === 0) return
      if (top <= 0) {
        setActiveKey(keys[0])
        return
      }
      if (atEnd) {
        setActiveKey(keys[keys.length - 1])
        return
      }
      const line = (stickyRef.current?.getBoundingClientRect().bottom ?? 0) + ANCHOR_GAP_PX
      let next = keys[0]
      for (const key of keys) {
        const element = sectionRefs.current.get(key)
        if (element && element.getBoundingClientRect().top <= line) next = key
      }
      setActiveKey(next)
    }
    const onScroll = (): void => {
      if (!frame) frame = window.requestAnimationFrame(update)
    }
    target.addEventListener('scroll', onScroll, { passive: true })
    update()
    return () => {
      target.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', measureInset)
      if (frame) window.cancelAnimationFrame(frame)
    }
  }, [sectionKeys])

  useEffect(() => {
    if (typeof IntersectionObserver === 'undefined') {
      setMounted(new Set(sectionKeys ? sectionKeys.split('|') : []))
      return
    }
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        const key = (entry.target as HTMLElement).dataset.sectionKey
        if (entry.isIntersecting && key) mountSection(key)
      }
    }, { rootMargin: LAZY_MOUNT_MARGIN })
    for (const element of sectionRefs.current.values()) observer.observe(element)
    return () => observer.disconnect()
  }, [mountSection, sectionKeys])

  const jumpTo = useCallback((key: string, moveFocus: boolean) => {
    const element = sectionRefs.current.get(key)
    if (!element) return
    mountSection(key)
    setActiveKey(key)
    element.scrollIntoView?.({ block: 'start', behavior: prefersReducedMotion() ? 'auto' : 'smooth' })
    if (moveFocus) element.querySelector<HTMLElement>('[data-section-heading]')?.focus({ preventScroll: true })
  }, [mountSection])

  useEffect(() => {
    if (!requestedSectionKey) return
    jumpTo(requestedSectionKey, false)
    onRequestHandled?.()
  }, [jumpTo, onRequestHandled, requestedSectionKey])

  function handleKeyDown(event: ReactKeyboardEvent<HTMLDivElement>): void {
    if (event.defaultPrevented) return
    const index = sectionIndexFromShortcut(event)
    const section = index === undefined ? undefined : sections[index]
    if (!section) return
    event.preventDefault()
    jumpTo(section.key, true)
  }

  return (
    <div ref={rootRef} onKeyDown={handleKeyDown} data-testid="section-page" data-header-condensed={condensed ? 'true' : 'false'}>
      <div
        ref={stickyRef}
        className="sticky top-0 z-30 space-y-2 bg-background pb-2"
        style={stickyInset ? { top: -stickyInset, marginTop: -stickyInset, paddingTop: stickyInset } : undefined}
        data-testid="section-page-sticky"
      >
        {header(condensed)}
        {sections.length > 1 ? (
          <nav aria-label="Abschnitte" data-testid="section-anchor-nav" className="border-b border-border">
            <ul className="flex flex-wrap gap-1">
              {sections.map((section, index) => {
                const active = section.key === activeKey
                return (
                  <li key={section.key}>
                    <a
                      href={`#${idPrefix}-${section.key}`}
                      aria-current={active ? 'location' : undefined}
                      aria-keyshortcuts={index < 9 ? `Alt+${index + 1}` : undefined}
                      title={index < 9 ? `${section.label} (Alt+${index + 1})` : undefined}
                      data-testid={`section-anchor-${section.key}`}
                      onClick={(event) => {
                        event.preventDefault()
                        jumpTo(section.key, true)
                      }}
                      className={cn(
                        'inline-flex min-h-11 items-center border-b-2 px-3 text-sm transition-colors',
                        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                        active
                          ? 'border-primary font-medium text-foreground'
                          : 'border-transparent text-muted-foreground hover:text-foreground',
                      )}
                    >
                      {section.label}
                    </a>
                  </li>
                )
              })}
            </ul>
          </nav>
        ) : null}
      </div>

      {children ? <div className="space-y-4 pt-2">{children}</div> : null}

      <div className="space-y-8 pt-4">
        {sections.map((section) => {
          const headingId = `${idPrefix}-${section.key}-heading`
          return (
            <section
              key={section.key}
              id={`${idPrefix}-${section.key}`}
              ref={(element) => {
                if (element) sectionRefs.current.set(section.key, element)
                else sectionRefs.current.delete(section.key)
              }}
              data-section-key={section.key}
              data-testid={`page-section-${section.key}`}
              aria-labelledby={headingId}
              style={{ scrollMarginTop: stickyHeight + ANCHOR_GAP_PX }}
              className="space-y-3"
            >
              <h2 id={headingId} tabIndex={-1} data-section-heading className="text-base font-semibold text-foreground focus:outline-none">
                {section.label}
              </h2>
              {mounted.has(section.key)
                ? section.render()
                : <div className="min-h-32 rounded-md border border-dashed border-border" aria-busy="true" />}
            </section>
          )
        })}
      </div>
    </div>
  )
}
