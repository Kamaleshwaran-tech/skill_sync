import { School } from '@mui/icons-material'
import { Box, Card, CardContent, Chip, Stack, Typography } from '@mui/material'

export function EducationCard({ education }) {
  if (!education || !education.length) {
    return (
      <Card elevation={0}>
        <CardContent>
          <Typography variant="body2" color="text.secondary">No education entries found.</Typography>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
        <Stack spacing={2.5}>
          <Typography variant="h5" sx={{ fontWeight: 800 }}>
            Education
          </Typography>

          {education.map((item) => (
            <Box key={`${item.school}-${item.degree}`} sx={{ p: 2.5, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
              <Stack spacing={1.5}>
                <Stack direction="row" spacing={1.5} alignItems="center">
                  <Box sx={{ display: 'grid', placeItems: 'center', width: 36, height: 36, borderRadius: 2, backgroundColor: 'secondary.main', color: 'common.white' }}>
                    <School fontSize="small" />
                  </Box>
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{item.school}</Typography>
                    <Typography variant="body2" color="text.secondary">{item.degree}</Typography>
                  </Box>
                </Stack>

                <Typography variant="body2" color="text.secondary">{item.period}</Typography>

                {item.achievements?.length ? (
                  <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                    {item.achievements.map((achievement) => (
                      <Chip key={achievement} label={achievement} size="small" variant="outlined" />
                    ))}
                  </Stack>
                ) : null}
              </Stack>
            </Box>
          ))}
        </Stack>
      </CardContent>
    </Card>
  )
}
