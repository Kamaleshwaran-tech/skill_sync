import { CheckCircle } from '@mui/icons-material'
import { Box, Card, CardContent, Stack, Typography } from '@mui/material'

export function StrengthCard({ strength }) {
  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack direction="row" spacing={1.5} alignItems="flex-start">
          <Box sx={{ width: 28, height: 28, borderRadius: '50%', display: 'grid', placeItems: 'center', backgroundColor: 'success.main', color: 'common.white' }}>
            <CheckCircle fontSize="small" />
          </Box>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>{strength}</Typography>
        </Stack>
      </CardContent>
    </Card>
  )
}
