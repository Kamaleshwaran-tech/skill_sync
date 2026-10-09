import { QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

import { ThemeModeProvider } from '@/app/theme/ThemeModeProvider'
import { AuthProvider } from '@/features/auth/context/AuthProvider'
import { createQueryClient } from '@/shared/query/queryClient'

export function AppProviders({ children }) {
  const [queryClient] = useState(createQueryClient)

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeModeProvider>
        <AuthProvider>{children}</AuthProvider>
      </ThemeModeProvider>
    </QueryClientProvider>
  )
}
