import { LockOutlined } from '@mui/icons-material'
import { Box, Stack, Typography } from '@mui/material'

export function ProtectedRoutePlaceholder() {
  return (
    <Box sx={{ p: 4 }}>
      <Stack spacing={1.5}>
        <LockOutlined color="primary" />
        <Typography component="h1" variant="h4">Protected application area</Typography>
        <Typography color="text.secondary">A future authenticated experience will be added here.</Typography>
      </Stack>
    </Box>
  )
}
