import { CheckCircle } from '@mui/icons-material'
import { Box, Button, Stack, Typography } from '@mui/material'

export function UploadSuccessState({ fileName, onReview, onViewDashboard, onUploadAnother }) {
  return (
    <Box sx={(theme) => ({
      p: 3,
      borderRadius: 3,
      border: '1px solid',
      borderColor: theme.palette.success.main,
      backgroundColor: theme.palette.mode === 'dark'
        ? 'rgba(86, 197, 138, 0.10)'
        : 'rgba(23, 131, 77, 0.08)',
    })}>
      <Stack spacing={2.5} alignItems="center" textAlign="center">
        <Box sx={{ width: 64, height: 64, borderRadius: '50%', display: 'grid', placeItems: 'center', bgcolor: 'success.main', color: 'common.white' }}>
          <CheckCircle sx={{ fontSize: 32 }} />
        </Box>

        <Box>
          <Typography variant="h6" sx={{ fontWeight: 800 }}>
            Resume uploaded successfully
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {fileName} is saved. Head to your dashboard to set a target role and generate your skill gap and AI roadmap.
          </Typography>
        </Box>

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          <Button variant="contained" onClick={onViewDashboard}>
            Go to Dashboard
          </Button>
          <Button variant="outlined" onClick={onReview}>
            View Resume Analysis
          </Button>
          <Button variant="text" color="inherit" onClick={onUploadAnother}>
            Upload another
          </Button>
        </Stack>
      </Stack>
    </Box>
  )
}
