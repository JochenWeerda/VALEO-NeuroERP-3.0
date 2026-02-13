import * as React from 'react'

import { cn } from '@/lib/utils'

// Lightweight fallback ScrollArea that does not require additional dependencies.
// If you later want Radix ScrollArea behavior, swap the internals and keep this API.
export const ScrollArea = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('overflow-auto', className)} {...props} />
  )
)
ScrollArea.displayName = 'ScrollArea'

