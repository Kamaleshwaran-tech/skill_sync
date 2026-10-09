import { Box, Typography } from '@mui/material'

export function BrandLogo() {
  return (
    <Box alignItems="center" display="inline-flex" gap={1.25}>
      <Box
        aria-hidden="true"
        sx={{
          alignItems: 'center',
          backgroundColor: 'primary.main',
          borderRadius: '9px',
          color: 'primary.contrastText',
          display: 'inline-flex',
          height: 30,
          justifyContent: 'center',
          width: 30,
        }}
      >
        <svg fill="none" height="18" viewBox="0 0 24 24" width="18">
          <path
            d="M6.5 7.5 12 4l5.5 3.5v6L12 17l-5.5-3.5v-6Z"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.8"
          />
          <path d="m9.5 11 1.7 1.7 3.5-3.7" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" />
        </svg>
      </Box>
      <Typography color="text.primary" component="span" sx={{ fontSize: '1.1rem', fontWeight: 760, letterSpacing: '-0.035em' }}>
        SkillSync AI
      </Typography>
    </Box>
  )
}
