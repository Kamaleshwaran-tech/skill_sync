const fontFamily = 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'

const sharedShadows = [
  'none',
  '0 1px 2px rgba(15, 23, 42, 0.04)',
  '0 2px 8px rgba(15, 23, 42, 0.06)',
  '0 8px 20px rgba(15, 23, 42, 0.08)',
  '0 16px 32px rgba(15, 23, 42, 0.10)',
]

function createShadows(mode) {
  const shadowColor = mode === 'dark' ? 'rgba(0, 0, 0, 0.28)' : 'rgba(15, 23, 42, 0.10)'
  const shadows = [...sharedShadows]

  while (shadows.length < 25) {
    const index = shadows.length
    shadows.push(`0 ${Math.min(index * 2, 32)}px ${Math.min(index * 3, 48)}px ${shadowColor}`)
  }

  return shadows
}

export function getDesignTokens(mode) {
  const isDark = mode === 'dark'
  const colors = isDark
    ? {
        background: '#0d0f14',
        surface: '#141820',
        surfaceSubtle: '#1a1f29',
        primary: '#8b95ff',
        primaryContrast: '#11131a',
        secondary: '#6dd3e8',
        text: '#f4f6fb',
        textSecondary: '#a8b0c0',
        divider: '#2a303d',
        success: '#56c58a',
      }
    : {
        background: '#fbfbfc',
        surface: '#ffffff',
        surfaceSubtle: '#f4f6f9',
        primary: '#4c57e8',
        primaryContrast: '#ffffff',
        secondary: '#087e98',
        text: '#171a22',
        textSecondary: '#667085',
        divider: '#e6e9ef',
        success: '#17834d',
      }

  return {
    palette: {
      mode,
      primary: {
        main: colors.primary,
        contrastText: colors.primaryContrast,
      },
      secondary: {
        main: colors.secondary,
      },
      success: {
        main: colors.success,
      },
      background: {
        default: colors.background,
        paper: colors.surface,
      },
      text: {
        primary: colors.text,
        secondary: colors.textSecondary,
      },
      divider: colors.divider,
      action: {
        hover: isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(23, 26, 34, 0.04)',
        selected: isDark ? 'rgba(139, 149, 255, 0.14)' : 'rgba(76, 87, 232, 0.08)',
      },
      surface: {
        subtle: colors.surfaceSubtle,
      },
    },
    breakpoints: {
      values: {
        xs: 0,
        sm: 600,
        md: 900,
        lg: 1200,
        xl: 1536,
      },
    },
    spacing: 8,
    shape: {
      borderRadius: 12,
    },
    shadows: createShadows(mode),
    typography: {
      fontFamily,
      h1: {
        fontSize: '3.25rem',
        fontWeight: 800,
        letterSpacing: '-0.05em',
        lineHeight: 1.08,
      },
      h2: {
        fontSize: '2.5rem',
        fontWeight: 750,
        letterSpacing: '-0.04em',
        lineHeight: 1.12,
      },
      h3: {
        fontSize: '2rem',
        fontWeight: 750,
        letterSpacing: '-0.03em',
        lineHeight: 1.22,
      },
      h4: {
        fontSize: '1.5rem',
        fontWeight: 700,
        letterSpacing: '-0.02em',
        lineHeight: 1.3,
      },
      h5: {
        fontSize: '1.25rem',
        fontWeight: 700,
        letterSpacing: '-0.015em',
        lineHeight: 1.35,
      },
      h6: {
        fontSize: '1.125rem',
        fontWeight: 700,
        lineHeight: 1.4,
      },
      body1: {
        fontSize: '1rem',
        lineHeight: 1.6,
      },
      body2: {
        fontSize: '0.875rem',
        lineHeight: 1.55,
      },
      button: {
        fontWeight: 700,
        letterSpacing: '-0.01em',
        textTransform: 'none',
      },
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundColor: colors.background,
          },
          '::selection': {
            backgroundColor: isDark ? 'rgba(139, 149, 255, 0.35)' : 'rgba(76, 87, 232, 0.18)',
          },
          '*:focus-visible': {
            outline: `3px solid ${colors.primary}`,
            outlineOffset: '3px',
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: isDark ? 'rgba(13, 15, 20, 0.84)' : 'rgba(251, 251, 252, 0.86)',
            backdropFilter: 'blur(14px)',
          },
        },
      },
      MuiButton: {
        defaultProps: {
          disableElevation: true,
        },
        styleOverrides: {
          root: {
            borderRadius: 10,
            minHeight: 42,
            padding: '10px 18px',
          },
          contained: {
            boxShadow: 'none',
            '&:hover': {
              boxShadow: 'none',
            },
          },
          outlined: {
            borderWidth: 1,
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            border: `1px solid ${colors.divider}`,
            borderRadius: 12,
            boxShadow: 'none',
            backgroundImage: 'none',
            overflow: 'hidden',
          },
        },
      },
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            borderRadius: 10,
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: colors.divider,
            },
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            fontWeight: 700,
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
          },
        },
      },
    },
  }
}
