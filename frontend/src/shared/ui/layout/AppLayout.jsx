import { Box } from '@mui/material'
import { Outlet } from 'react-router-dom'

import { Footer } from '@/shared/ui/layout/Footer'
import { Navbar } from '@/shared/ui/layout/Navbar'

export function AppLayout() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Box component="main" sx={{ flexGrow: 1 }}>
        <Outlet />
      </Box>
      <Footer />
    </Box>
  )
}
