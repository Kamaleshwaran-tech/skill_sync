import { Button, Paper, Stack, Typography } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <Paper
      component="section"
      elevation={0}
      sx={{
        mx: 'auto',
        maxWidth: 560,
        px: { xs: 3, sm: 5 },
        py: { xs: 5, sm: 7 },
        textAlign: 'center',
      }}
    >
      <Stack alignItems="center" spacing={2}>
        <Typography component="h1" variant="h4">
          Page not found
        </Typography>
        <Typography color="text.secondary">
          The page you requested is not available.
        </Typography>
        <Button component={RouterLink} to="/" variant="contained">
          Return home
        </Button>
      </Stack>
    </Paper>
  )
}
