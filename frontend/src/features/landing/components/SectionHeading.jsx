import { Stack, Typography } from '@mui/material'

import { Reveal } from '@/shared/ui/motion/Reveal'

export function SectionHeading({ align = 'left', eyebrow, heading, supportingText }) {
  const textAlign = align === 'center' ? 'center' : 'left'

  return (
    <Reveal>
      <Stack alignItems={align === 'center' ? 'center' : 'flex-start'} spacing={2} sx={{ maxWidth: 700, textAlign }}>
        <Typography color="primary" sx={{ fontSize: '0.78rem', fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase' }} variant="overline">
          {eyebrow}
        </Typography>
        <Typography component="h2" variant="h2">
          {heading}
        </Typography>
        <Typography color="text.secondary" variant="body1">
          {supportingText}
        </Typography>
      </Stack>
    </Reveal>
  )
}
