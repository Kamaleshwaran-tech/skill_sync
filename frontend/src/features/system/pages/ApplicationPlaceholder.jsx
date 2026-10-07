import { Paper, Stack, Typography } from '@mui/material'

export function ApplicationPlaceholder() {
  return (
    <Paper
      component="section"
      elevation={0}
      sx={{
        mx: 'auto',
        maxWidth: 640,
        px: { xs: 3, sm: 5 },
        py: { xs: 5, sm: 7 },
        textAlign: 'center',
      }}
    >
      <Stack spacing={2}>
        <Typography component="h1" variant="h4">
          SkillSync AI
        </Typography>
        <Typography color="text.secondary">
          The frontend foundation is ready. Feature experiences will be added in
          subsequent approved phases.
        </Typography>
      </Stack>
    </Paper>
  )
}
