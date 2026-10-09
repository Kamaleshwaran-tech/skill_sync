import { Error, Replay } from '@mui/icons-material'
import { Box, Button, Stack, Typography } from '@mui/material'

export function UploadErrorState({ title, message, onRetry, onRemove }) {
  return (
    <Box sx={(theme) => ({
      p: 3,
      borderRadius: 3,
      border: '1px solid',
      borderColor: theme.palette.error.main,
      backgroundColor: theme.palette.mode === 'dark'
        ? 'rgba(255, 107, 107, 0.10)'
        : 'rgba(220, 53, 69, 0.07)',
    })}>
      <Stack spacing={2} alignItems="center" textAlign="center">
        <Box sx={{ width: 64, height: 64, borderRadius: '50%', display: 'grid', placeItems: 'center', bgcolor: 'error.main', color: 'common.white' }}>
          <Error sx={{ fontSize: 32 }} />
        </Box>

        <Box>
          <Typography variant="h6" sx={{ fontWeight: 800 }}>
            {title || 'Upload failed'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {message}
          </Typography>
        </Box>

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          <Button variant="contained" startIcon={<Replay />} onClick={onRetry}>
            Try again
          </Button>
          <Button variant="outlined" onClick={onRemove}>
            Remove file
          </Button>
        </Stack>
      </Stack>
    </Box>
  )
}
