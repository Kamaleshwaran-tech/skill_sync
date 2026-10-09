import { Box, Chip, Stack, Typography } from '@mui/material'

export function JobMatchScore({ score, large = false }) {
  const normalizedScore = Number(score ?? 0)

  return (
    <Stack direction="row" spacing={1} alignItems="center">
      <Box
        sx={{
          minWidth: large ? 74 : 62,
          px: large ? 1.5 : 1,
          py: large ? 0.75 : 0.5,
          borderRadius: 1.5,
          backgroundColor:
            normalizedScore >= 90 ? 'success.main' : normalizedScore >= 80 ? 'primary.main' : 'warning.main',
          color: 'common.white',
          textAlign: 'center',
        }}
      >
        <Typography variant={large ? 'subtitle2' : 'caption'} sx={{ fontWeight: 800 }}>
          {normalizedScore}%
        </Typography>
      </Box>
      <Chip label="Match" variant="outlined" size={large ? 'medium' : 'small'} />
    </Stack>
  )
}
