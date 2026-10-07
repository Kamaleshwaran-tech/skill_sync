import { Cancel, CloudUpload } from '@mui/icons-material'
import { Box, Button, LinearProgress, Stack, Typography } from '@mui/material'

export function UploadProgress({ progress, onCancel }) {
  return (
    <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 3, bgcolor: 'background.paper' }}>
      <Stack spacing={2}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Stack direction="row" spacing={1} alignItems="center">
            <CloudUpload color="primary" />
            <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
              Uploading resume
            </Typography>
          </Stack>
          <Typography variant="body2" color="text.secondary">
            {progress}%
          </Typography>
        </Stack>

        <LinearProgress variant="determinate" value={progress} sx={{ height: 10, borderRadius: 999 }} />

        <Button
          variant="outlined"
          color="error"
          startIcon={<Cancel />}
          onClick={onCancel}
          sx={{ alignSelf: 'flex-start' }}
        >
          Cancel upload
        </Button>
      </Stack>
    </Box>
  )
}
