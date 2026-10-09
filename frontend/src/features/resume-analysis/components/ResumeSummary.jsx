import { CheckCircle, AutoAwesome, FilePresent, TrendingUp } from '@mui/icons-material'
import { Box, Card, CardContent, Chip, Grid, Stack, Typography } from '@mui/material'

export function ResumeSummary({ overview }) {
  if (!overview) {
    return null
  }

  const summaryMetrics = [
    { label: 'Quality score', value: `${overview.qualityScore}/100`, icon: TrendingUp },
    { label: 'Role match', value: `${overview.matchScore}%`, icon: CheckCircle },
    { label: 'Resume file', value: overview.fileName, icon: FilePresent },
  ]

  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
        <Stack spacing={2.5}>
          <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" spacing={2} alignItems={{ xs: 'flex-start', sm: 'center' }}>
            <Box>
              <Typography variant="overline" color="text.secondary">
                Resume overview
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 800 }}>
                {overview.fileName}
              </Typography>
            </Box>
            <Chip icon={<AutoAwesome />} label={overview.status} color="primary" />
          </Stack>

          <Grid container spacing={2}>
            {summaryMetrics.map(({ label, value, icon: Icon }) => (
              <Grid item xs={12} sm={4} key={label}>
                <Box sx={{ p: 2, borderRadius: 2, border: '1px solid', borderColor: 'divider', backgroundColor: 'background.paper' }}>
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <Box sx={{ display: 'grid', placeItems: 'center', width: 34, height: 34, borderRadius: 2, backgroundColor: 'primary.main', color: 'common.white' }}>
                      <Icon fontSize="small" />
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">{label}</Typography>
                      <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{value}</Typography>
                    </Box>
                  </Stack>
                </Box>
              </Grid>
            ))}
          </Grid>

          <Typography variant="body1" color="text.secondary">
            {overview.summary}
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  )
}
