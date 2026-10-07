import {
  AccountCircleOutlined,
  AssessmentOutlined,
  CloudUploadOutlined,
  DashboardOutlined,
  DarkModeOutlined,
  LightModeOutlined,
  LogoutOutlined,
  MenuRounded,
  RouteOutlined,
  TrendingUpOutlined,
  WorkOutlineRounded,
} from '@mui/icons-material'
import {
  AppBar,
  Box,
  Button,
  Chip,
  Container,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Toolbar,
  Tooltip,
  Typography,
  alpha,
} from '@mui/material'
import { useState } from 'react'
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom'

import { useThemeMode } from '@/app/theme/useThemeMode'
import { useAuth } from '@/features/auth/context/useAuth'
import { BrandLogo } from '@/shared/ui/layout/BrandLogo'

const landingNavItems = [
  { href: '#home', label: 'Home' },
  { href: '#how-it-works', label: 'How It Works' },
  { href: '#features', label: 'Features' },
  { href: '#career-intelligence', label: 'Career Intelligence' },
]

const appNavItems = [
  { to: '/dashboard', label: 'Dashboard', icon: <DashboardOutlined fontSize="small" /> },
  { to: '/resume-upload', label: 'Upload Resume', icon: <CloudUploadOutlined fontSize="small" /> },
  { to: '/resume-analysis', label: 'Resume Analysis', icon: <AssessmentOutlined fontSize="small" /> },
  { to: '/job-matching', label: 'Job Matches', icon: <WorkOutlineRounded fontSize="small" /> },
  { to: '/skill-gap-analysis', label: 'Skill Gap', icon: <TrendingUpOutlined fontSize="small" /> },
  { to: '/learning-roadmap', label: 'AI Roadmap', icon: <RouteOutlined fontSize="small" /> },
  { to: '/profile', label: 'Profile', icon: <AccountCircleOutlined fontSize="small" /> },
]

export function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const { mode, toggleMode } = useThemeMode()
  const { clearSession, isAuthenticated } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const nextMode = mode === 'light' ? 'dark' : 'light'

  const isLanding = location.pathname === '/'

  const closeMenu = () => setIsMenuOpen(false)
  const handleLogout = async () => {
    closeMenu()
    await clearSession()
    navigate('/', { replace: true })
  }

  return (
    <AppBar
      component="header"
      elevation={0}
      position="sticky"
      sx={(theme) => ({
        borderBottom: `1px solid ${theme.palette.divider}`,
        zIndex: theme.zIndex.drawer + 1,
      })}
    >
      <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
        <Toolbar disableGutters sx={{ minHeight: { xs: 58, sm: 64, md: 70 } }}>
          <Box component={RouterLink} to="/" sx={{ textDecoration: 'none', color: 'inherit', display: 'flex', alignItems: 'center', mr: { xs: 1, lg: 2 }, flexShrink: 0 }}>
            <BrandLogo />
          </Box>

          {isLanding ? (
            <Stack
              component="nav"
              direction="row"
              spacing={0.5}
              sx={{ display: { xs: 'none', md: 'flex' }, ml: 'auto', mr: 2 }}
            >
              {landingNavItems.map((item) => (
                <Button
                  component="a"
                  href={item.href}
                  key={item.label}
                  size="small"
                  sx={{ color: 'text.secondary', px: 1.25, fontWeight: 600 }}
                >
                  {item.label}
                </Button>
              ))}
            </Stack>
          ) : (
            <Stack
              component="nav"
              direction="row"
              spacing={0.5}
              sx={{
                display: { xs: 'none', lg: 'flex' },
                ml: 'auto',
                mr: 2,
                minWidth: 0,
                flex: 1,
                overflowX: 'auto',
                scrollbarWidth: 'none',
                py: 0.5,
                '&::-webkit-scrollbar': { display: 'none' },
              }}
            >
              {appNavItems.map((item) => {
                const isActive = location.pathname === item.to
                return (
                  <Button
                    component={RouterLink}
                    to={item.to}
                    key={item.to}
                    size="small"
                    startIcon={item.icon}
                    sx={(theme) => ({
                      px: { lg: 1, xl: 1.5 },
                      py: 0.75,
                      fontSize: '0.875rem',
                      whiteSpace: 'nowrap',
                      fontWeight: isActive ? 750 : 600,
                      color: isActive ? theme.palette.primary.main : 'text.secondary',
                      backgroundColor: isActive
                        ? alpha(theme.palette.primary.main, mode === 'dark' ? 0.16 : 0.08)
                        : 'transparent',
                      borderRadius: 2,
                      '&:hover': {
                        backgroundColor: alpha(theme.palette.primary.main, mode === 'dark' ? 0.22 : 0.12),
                      },
                    })}
                  >
                    {item.label}
                  </Button>
                )
              })}
            </Stack>
          )}

          <Stack alignItems="center" direction="row" spacing={1} sx={{ ml: { xs: 'auto', lg: 0 } }}>
            <Tooltip title={`Switch to ${nextMode} mode`}>
              <IconButton
                aria-label={`Switch to ${nextMode} mode`}
                color="inherit"
                onClick={toggleMode}
                size="small"
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 2,
                  p: 0.8,
                }}
              >
                {mode === 'light' ? <DarkModeOutlined fontSize="small" /> : <LightModeOutlined fontSize="small" />}
              </IconButton>
            </Tooltip>

            {isLanding ? (
              <>
                <Button
                  component={RouterLink}
                  size="small"
                  sx={{ color: 'text.primary', display: { xs: 'none', sm: 'inline-flex' }, fontWeight: 700 }}
                  to="/login"
                >
                  Login
                </Button>
                <Button
                  component={RouterLink}
                  size="small"
                  sx={{ display: { xs: 'none', sm: 'inline-flex' }, fontWeight: 700 }}
                  to="/register"
                  variant="contained"
                >
                  Get Started
                </Button>
              </>
            ) : (
              <Button
                startIcon={<LogoutOutlined />}
                onClick={handleLogout}
                size="small"
                variant="text"
                sx={{ display: { xs: 'none', sm: 'inline-flex' }, fontWeight: 700 }}
              >
                Logout
              </Button>
            )}

            <IconButton
              aria-label="Open navigation menu"
              color="inherit"
              onClick={() => setIsMenuOpen(true)}
              sx={{
                display: { lg: 'none' },
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
                p: 0.8,
              }}
            >
              <MenuRounded />
            </IconButton>
          </Stack>
        </Toolbar>
      </Container>

      <Drawer
        anchor="right"
        onClose={closeMenu}
        open={isMenuOpen}
        PaperProps={{
          sx: {
            p: 2,
            width: { xs: '82vw', sm: 340 },
            maxWidth: '100%',
            boxSizing: 'border-box',
          },
        }}
      >
        <Stack spacing={2} sx={{ mt: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pb: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 800 }}>
              Navigation Menu
            </Typography>
            <Chip label="SkillSync AI" size="small" color="primary" variant="outlined" />
          </Box>

          <Divider />

          {isLanding ? (
            <Stack component="nav" spacing={0.5}>
              <Typography variant="overline" color="text.secondary" sx={{ px: 1 }}>
                Explore Platform
              </Typography>
              {landingNavItems.map((item) => (
                <Button
                  component="a"
                  href={item.href}
                  key={item.label}
                  onClick={closeMenu}
                  sx={{ justifyContent: 'flex-start', px: 2, py: 1, borderRadius: 2 }}
                >
                  {item.label}
                </Button>
              ))}

              <Divider sx={{ my: 1.5 }} />

              <Typography variant="overline" color="text.secondary" sx={{ px: 1 }}>
                Get Started
              </Typography>
              <Button component={RouterLink} onClick={closeMenu} sx={{ justifyContent: 'flex-start', px: 2, py: 1 }} to="/login">
                Login
              </Button>
              <Button component={RouterLink} onClick={closeMenu} to="/register" variant="contained" sx={{ mt: 1 }}>
                Register Free
              </Button>
            </Stack>
          ) : (
            <List disablePadding>
              <Typography variant="overline" color="text.secondary" sx={{ px: 1, mb: 1, display: 'block' }}>
                Career Platform
              </Typography>
              {appNavItems.map((item) => {
                const isActive = location.pathname === item.to
                return (
                  <ListItem disablePadding key={item.to} sx={{ mb: 0.5 }}>
                    <ListItemButton
                      component={RouterLink}
                      to={item.to}
                      onClick={closeMenu}
                      selected={isActive}
                      sx={{
                        borderRadius: 2,
                        py: 1,
                        '&.Mui-selected': {
                          backgroundColor: (theme) => alpha(theme.palette.primary.main, 0.12),
                        },
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 36, color: isActive ? 'primary.main' : 'text.secondary' }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.label}
                        primaryTypographyProps={{
                          fontWeight: isActive ? 750 : 600,
                          fontSize: '0.925rem',
                          color: isActive ? 'primary.main' : 'text.primary',
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
                )
              })}

              <Divider sx={{ my: 2 }} />

              <Box sx={{ px: 1 }}>
                {isAuthenticated ? (
                  <Button
                    color="error"
                    fullWidth
                    onClick={handleLogout}
                    startIcon={<LogoutOutlined />}
                    variant="outlined"
                  >
                    Logout
                  </Button>
                ) : null}
                <Button component={RouterLink} to="/" onClick={closeMenu} fullWidth variant="outlined" size="small">
                  Back to Home
                </Button>
              </Box>
            </List>
          )}
        </Stack>
      </Drawer>
    </AppBar>
  )
}
