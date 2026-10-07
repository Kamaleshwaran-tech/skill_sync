import { Box, Card, CardContent, LinearProgress, Stack, Typography } from '@mui/material'

export function SkillCategoryCard({ category }) {
  if (!category) {
    return null
  }

  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{category.name}</Typography>
            <Typography variant="body2" color="text.secondary">{category.level}%</Typography>
          </Stack>

          <LinearProgress variant="determinate" value={category.level} sx={{ height: 10, borderRadius: 999 }} />

          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
            {category.skills?.map((skill) => (
              <Box key={skill} component="span" sx={{ px: 1.25, py: 0.75, borderRadius: 999, backgroundColor: 'action.hover', fontSize: '0.75rem', fontWeight: 700 }}>
                {skill}
              </Box>
            ))}
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  )
}
