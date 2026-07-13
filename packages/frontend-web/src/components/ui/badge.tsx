import * as React from 'react'
import { type VariantProps, cva } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-hidden focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-primary text-primary-foreground hover:bg-primary/80',
        secondary:
          'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
        destructive:
          'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80',
        outline: 'text-foreground',
        success:
          'border-[hsl(var(--color-semantic-success-500-hsl)/0.25)] bg-[hsl(var(--color-semantic-success-50-hsl))] text-[hsl(var(--color-semantic-success-700-hsl))] dark:border-[hsl(var(--color-semantic-success-500-hsl)/0.35)] dark:bg-[hsl(var(--color-semantic-success-500-hsl)/0.15)] dark:text-[hsl(var(--color-semantic-success-50-hsl))]',
        warning:
          'border-[hsl(var(--color-semantic-warning-500-hsl)/0.25)] bg-[hsl(var(--color-semantic-warning-50-hsl))] text-[hsl(var(--color-semantic-warning-700-hsl))] dark:border-[hsl(var(--color-semantic-warning-500-hsl)/0.35)] dark:bg-[hsl(var(--color-semantic-warning-500-hsl)/0.15)] dark:text-[hsl(var(--color-semantic-warning-50-hsl))]',
        info:
          'border-[hsl(var(--color-semantic-info-500-hsl)/0.25)] bg-[hsl(var(--color-semantic-info-50-hsl))] text-[hsl(var(--color-semantic-info-700-hsl))] dark:border-[hsl(var(--color-semantic-info-500-hsl)/0.35)] dark:bg-[hsl(var(--color-semantic-info-500-hsl)/0.15)] dark:text-[hsl(var(--color-semantic-info-50-hsl))]',
        muted:
          'border-transparent bg-muted text-muted-foreground',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps): JSX.Element {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}
