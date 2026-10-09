import { FolderOpen } from '@mui/icons-material'
import { Box, Card, CardContent, Chip, Stack, Typography } from '@mui/material'

export function ProjectCard({ project }) {
  if (!project) {
    return null
  }

  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: { xs: 2.25, md: 2.75 } }}>
        <Stack spacing={2}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Box sx={{ display: 'grid', placeItems: 'center', width: 36, height: 36, borderRadius: 2, backgroundColor: 'secondary.main', color: 'common.white' }}>
              <FolderOpen fontSize="small" />
            </Box>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>{project.name}</Typography>
          </Stack>

          <Typography variant="body2" color="text.secondary">{project.description}</Typography>

          <Box>
            <Typography variant="caption" color="text.secondary">Impact</Typography>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>{project.impact}</Typography>
          </Box>

          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
            {project.stack?.map((skill) => (
              <Chip key={skill} label={skill} size="small" variant="outlined" />
            ))}
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  )
}
