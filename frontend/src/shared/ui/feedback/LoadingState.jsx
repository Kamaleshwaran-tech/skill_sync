import { Box, CircularProgress, Stack, Typography } from '@mui/material'

export function LoadingState({ label = 'Loading…', minHeight = 240 }) {
  return (
    <Box
      aria-busy="true"
      aria-live="polite"
      sx={{ display: 'grid', minHeight, placeItems: 'center', p: 3 }}
    >
      <Stack alignItems="center" spacing={2}>
        <CircularProgress aria-label={label} />
        <Typography color="text.secondary">{label}</Typography>
      </Stack>
    </Box>
  )
}
