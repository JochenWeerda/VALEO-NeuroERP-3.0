import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface PageSurfaceProps {
  children: ReactNode
  className?: string
  contentClassName?: string
  'data-page-surface'?: string
}

interface PageSectionProps {
  title?: string
  description?: string
  children: ReactNode
  className?: string
}

export function PageSurface({
  children,
  className,
  contentClassName,
  'data-page-surface': dataPageSurface = 'default',
}: PageSurfaceProps): JSX.Element {
  return (
    <div
      className={cn(
        'flex h-full flex-col bg-[radial-gradient(circle_at_top_left,hsl(var(--primary)/0.09),transparent_34%),linear-gradient(180deg,hsl(var(--background)),hsl(var(--muted)/0.45))]',
        className,
      )}
      data-page-surface={dataPageSurface}
    >
      <div className={cn('flex-1 overflow-y-auto px-4 py-5 sm:px-6 lg:px-8', contentClassName)}>{children}</div>
    </div>
  )
}

export function PageSection({
  title,
  description,
  children,
  className,
}: PageSectionProps): JSX.Element {
  const hasHeader = Boolean(title || description)
  return (
    <section
      className={cn(
        'rounded-3xl border border-border/70 bg-card/95 p-5 shadow-sm shadow-primary/5 backdrop-blur-sm sm:p-6',
        className,
      )}
    >
      {hasHeader ? (
        <header className="mb-4 space-y-1">
          {title ? <h2 className="text-base font-semibold tracking-tight text-foreground">{title}</h2> : null}
          {description ? <p className="text-sm leading-6 text-muted-foreground">{description}</p> : null}
        </header>
      ) : null}
      {children}
    </section>
  )
}
