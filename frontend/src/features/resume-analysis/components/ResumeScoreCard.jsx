import { Box, Card, CardContent, CircularProgress, Stack, Typography } from '@mui/material'

export function ResumeScoreCard({ score }) {
  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
        <Stack spacing={2.5} alignItems="center" textAlign="center">
          <Box sx={{ position: 'relative', display: 'inline-flex' }}>
            <CircularProgress variant="determinate" value={score} size={132} thickness={6} />
            <Box sx={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 800 }}>{score}</Typography>
            </Box>
          </Box>

          <Box>
            <Typography variant="h6" sx={{ fontWeight: 800 }}>Resume quality score</Typography>
            <Typography variant="body2" color="text.secondary">Overall fit and clarity assessment</Typography>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  )
}
