import { Delete, Description, Edit } from '@mui/icons-material'
import { Box, Button, Card, CardContent, Chip, IconButton, Stack, Typography } from '@mui/material'

export function FilePreview({ file, onReplace, onRemove }) {
  if (!file) {
    return null
  }

  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', bgcolor: 'background.paper' }}>
      <CardContent>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Box sx={{ width: 44, height: 44, borderRadius: 2, display: 'grid', placeItems: 'center', bgcolor: 'primary.main', color: 'common.white' }}>
              <Description fontSize="small" />
            </Box>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                {file.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {file.size ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : 'File size not available'}
              </Typography>
            </Box>
          </Stack>

          <Stack direction="row" spacing={1} alignItems="center">
            <Chip label="Ready" color="success" size="small" />
            <Button variant="outlined" size="small" startIcon={<Edit />} onClick={onReplace}>
              Replace
            </Button>
            <IconButton aria-label="remove file" color="error" onClick={onRemove}>
              <Delete />
            </IconButton>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  )
}
