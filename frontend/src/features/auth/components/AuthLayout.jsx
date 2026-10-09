import { DarkModeOutlined, LightModeOutlined } from '@mui/icons-material'
import { Box, Container, IconButton, Link, Stack, Tooltip } from '@mui/material'
import { Link as RouterLink, Outlet } from 'react-router-dom'

import { useThemeMode } from '@/app/theme/useThemeMode'
import { BrandLogo } from '@/shared/ui/layout/BrandLogo'

export function AuthLayout() {
  const { mode, toggleMode } = useThemeMode()
  const nextMode = mode === 'light' ? 'dark' : 'light'

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Container component="header" maxWidth="lg" sx={{ py: { xs: 2, md: 3 } }}>
        <Stack alignItems="center" direction="row" justifyContent="space-between">
          <Link aria-label="Return to SkillSync AI home" color="inherit" component={RouterLink} to="/" underline="none">
            <BrandLogo />
          </Link>
          <Tooltip title={`Switch to ${nextMode} mode`}>
            <IconButton aria-label={`Switch to ${nextMode} mode`} color="inherit" onClick={toggleMode}>
              {mode === 'light' ? <DarkModeOutlined /> : <LightModeOutlined />}
            </IconButton>
          </Tooltip>
        </Stack>
      </Container>
      <Box component="main" sx={{ alignItems: 'center', display: 'flex', flexGrow: 1, py: { xs: 4, md: 7 } }}>
        <Container maxWidth="sm" sx={{ px: { xs: 2, sm: 3 } }}>
          <Outlet />
        </Container>
      </Box>
    </Box>
  )
}
