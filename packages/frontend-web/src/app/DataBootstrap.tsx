import { type ReactNode } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { FeatureFlagProvider } from '@/app/providers/FeatureFlagProvider'
import { createQueryClient } from '@/lib/query'

const queryClient = createQueryClient()

export default function DataBootstrap({ children }: { children: ReactNode }): JSX.Element {
  return (
    <QueryClientProvider client={queryClient}>
      <FeatureFlagProvider>{children}</FeatureFlagProvider>
    </QueryClientProvider>
  )
}
