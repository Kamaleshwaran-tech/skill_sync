import { WorkHistory } from '@mui/icons-material'
import { Box, Card, CardContent, Chip, Stack, Typography } from '@mui/material'

export function ExperienceTimeline({ experience }) {
  if (!experience || !experience.length) {
    return (
      <Card elevation={0}>
        <CardContent>
          <Typography variant="body2" color="text.secondary">No experience entries found.</Typography>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
        <Stack spacing={2.5}>
          <Typography variant="h5" sx={{ fontWeight: 800 }}>
            Experience
          </Typography>

          {experience.map((exp) => (
            <Box key={`${exp.role}-${exp.company}`} sx={{ pl: 1.5, borderLeft: '2px solid', borderColor: 'primary.main' }}>
              <Stack spacing={1.5}>
                <Stack direction="row" spacing={1.5} alignItems="center">
                  <Box sx={{ display: 'grid', placeItems: 'center', width: 36, height: 36, borderRadius: 2, backgroundColor: 'primary.main', color: 'common.white' }}>
                    <WorkHistory fontSize="small" />
                  </Box>
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{exp.role}</Typography>
                    <Typography variant="body2" color="text.secondary">{exp.company}</Typography>
                  </Box>
                </Stack>

                <Typography variant="body2" color="text.secondary">{exp.period}</Typography>
                <Typography variant="body2">{exp.description}</Typography>

                {exp.highlights?.length ? (
                  <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                    {exp.highlights.map((highlight) => (
                      <Chip key={highlight} label={highlight} size="small" color="primary" variant="outlined" />
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
