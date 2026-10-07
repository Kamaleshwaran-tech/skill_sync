import { Autorenew } from '@mui/icons-material'
import { Alert, Box, CircularProgress, Stack, Typography } from '@mui/material'

export function ResumeProcessingState() {
  return (
    <Box sx={{ p: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider', bgcolor: 'background.paper' }}>
      <Stack spacing={2} alignItems="center" textAlign="center">
        <CircularProgress size={42} />
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 800 }}>
            Processing resume
          </Typography>
          <Typography variant="body2" color="text.secondary">
            We are extracting skills, experience, and job-fit insights.
          </Typography>
        </Box>
        <Alert severity="info" sx={{ width: '100%' }} icon={<Autorenew fontSize="inherit" />}>
          This is a presentation-only UI state while the resume is being reviewed.
        </Alert>
      </Stack>
    </Box>
  )
}
