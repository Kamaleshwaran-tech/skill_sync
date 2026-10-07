import { ArrowForwardRounded } from '@mui/icons-material'
import { Box, Button, Stack, Typography } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'

import { Reveal } from '@/shared/ui/motion/Reveal'

export function CTASection() {
  return (
    <Box component="section" id="get-started" sx={{ py: { xs: 9, md: 14 } }}>
      <Box sx={{ backgroundColor: 'primary.main', borderRadius: { xs: 3, md: 4 }, color: 'primary.contrastText', maxWidth: 'lg', mx: 'auto', overflow: 'hidden', px: { xs: 3, sm: 6, md: 9 }, py: { xs: 6, md: 9 }, textAlign: 'center' }}>
        <Reveal>
          <Stack alignItems="center" spacing={2.5}>
            <Typography component="h2" sx={{ color: 'inherit', fontSize: 'clamp(2rem, 4.5vw, 3.7rem)', fontWeight: 750, letterSpacing: '-0.055em', lineHeight: 1.02 }}>
              Ready to discover your career path?
            </Typography>
            <Typography sx={{ color: 'inherit', maxWidth: 580, opacity: 0.84 }} variant="body1">
              Start with a better understanding of your skills and the opportunities ahead.
            </Typography>
            <Button component={RouterLink} endIcon={<ArrowForwardRounded />} sx={(theme) => ({ '&:hover': { backgroundColor: theme.palette.background.paper }, backgroundColor: theme.palette.background.paper, color: theme.palette.text.primary, mt: 1 })} to="/register">
              Get Started
            </Button>
          </Stack>
        </Reveal>
      </Box>
    </Box>
  )
}
