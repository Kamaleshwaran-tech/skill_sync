import { Email, Language, LocationOn, Phone, Public } from '@mui/icons-material'
import { Box, Card, CardContent, Grid, Stack, Typography } from '@mui/material'

const infoItems = [
  { key: 'email', label: 'Email', icon: Email },
  { key: 'phone', label: 'Phone', icon: Phone },
  { key: 'location', label: 'Location', icon: LocationOn },
  { key: 'linkedin', label: 'LinkedIn', icon: Public },
  { key: 'portfolio', label: 'Portfolio', icon: Language },
]

export function PersonalInfoCard({ personalInfo }) {
  if (!personalInfo) {
    return null
  }

  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
        <Stack spacing={2.5}>
          <Typography variant="h5" sx={{ fontWeight: 800 }}>
            Extracted personal information
          </Typography>

          <Grid container spacing={2}>
            {infoItems.map(({ key, label, icon: Icon }) => (
              <Grid item xs={12} sm={6} key={key}>
                <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <Box sx={{ display: 'grid', placeItems: 'center', width: 30, height: 30, borderRadius: '50%', backgroundColor: 'primary.main', color: 'common.white' }}>
                      <Icon fontSize="small" />
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary">{label}</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>{personalInfo[key]}</Typography>
                    </Box>
                  </Stack>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Stack>
      </CardContent>
    </Card>
  )
}
