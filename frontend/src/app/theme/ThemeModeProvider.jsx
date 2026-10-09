import { CssBaseline, ThemeProvider, createTheme } from '@mui/material'
import { useEffect, useMemo, useState } from 'react'

import { ThemeModeContext } from '@/app/theme/ThemeModeContext'
import { getDesignTokens } from '@/app/theme/theme'

const COLOR_MODE_STORAGE_KEY = 'skillsync-color-mode'

function getInitialMode() {
  const savedMode = window.localStorage.getItem(COLOR_MODE_STORAGE_KEY)

  if (savedMode === 'light' || savedMode === 'dark') {
    return savedMode
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light'
}

export function ThemeModeProvider({ children }) {
  const [mode, setMode] = useState(getInitialMode)
  const theme = useMemo(() => createTheme(getDesignTokens(mode)), [mode])

  useEffect(() => {
    window.localStorage.setItem(COLOR_MODE_STORAGE_KEY, mode)
  }, [mode])

  const value = useMemo(
    () => ({
      mode,
      toggleMode: () =>
        setMode((currentMode) =>
          currentMode === 'light' ? 'dark' : 'light',
        ),
    }),
    [mode],
  )

  return (
    <ThemeModeContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeModeContext.Provider>
  )
}
