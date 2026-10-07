import { Box, Chip, Stack, Typography } from '@mui/material'

export function MatchedSkills({ skills }) {
  if (!skills || !skills.length) {
    return null
  }

  return (
    <Box>
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.75 }}>
        Matched skills
      </Typography>
      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
        {skills.map((skill) => (
          <Chip key={skill} label={skill} size="small" color="success" variant="outlined" />
        ))}
      </Stack>
    </Box>
  )
}
