import { ArrowForwardRounded, AutoAwesomeRounded, CheckCircleRounded, TimelineRounded } from '@mui/icons-material'
import { Box, Button, Chip, Stack, Typography } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'

import { Reveal } from '@/shared/ui/motion/Reveal'

function InsightPanel() {
  const signals = [
    { label: 'Skills analyzed', value: 'Clear signal', icon: <CheckCircleRounded color="success" fontSize="small" /> },
    { label: 'Industry fit', value: 'Requirements mapped', icon: <TimelineRounded color="primary" fontSize="small" /> },
    { label: 'Next steps', value: 'Roadmap ready', icon: <AutoAwesomeRounded color="secondary" fontSize="small" /> },
  ]

  return (
    <Box
      aria-label="SkillSync AI career intelligence preview"
      sx={(theme) => ({
        backgroundColor: 'background.paper',
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: 4,
        boxShadow: theme.shadows[4],
        overflow: 'hidden',
      })}
    >
      <Stack direction="row" justifyContent="space-between" sx={(theme) => ({ alignItems: 'center', backgroundColor: theme.palette.surface.subtle, borderBottom: `1px solid ${theme.palette.divider}`, p: 2 })}>
        <Stack direction="row" spacing={1.25}>
          <Box sx={{ bgcolor: 'primary.main', borderRadius: 1, height: 10, width: 10 }} />
          <Typography fontWeight={750} variant="body2">Career intelligence</Typography>
        </Stack>
        <Chip label="Guided" size="small" variant="outlined" />
      </Stack>
      <Stack spacing={1.25} sx={{ p: { xs: 2, sm: 3 } }}>
        <Typography color="text.secondary" variant="caption">YOUR CAREER SIGNAL</Typography>
        <Typography component="p" sx={{ fontSize: { xs: '1.35rem', sm: '1.65rem' }, fontWeight: 750, letterSpacing: '-0.04em' }}>
          See what moves you forward.
        </Typography>
        <Box sx={(theme) => ({ borderTop: `1px solid ${theme.palette.divider}`, my: 0.75 })} />
        {signals.map((signal) => (
          <Stack alignItems="center" direction="row" justifyContent="space-between" key={signal.label} spacing={1} sx={{ py: 0.75 }}>
            <Stack alignItems="center" direction="row" spacing={1.25}>
              {signal.icon}
              <Typography color="text.secondary" variant="body2">{signal.label}</Typography>
            </Stack>
            <Typography fontWeight={700} variant="body2">{signal.value}</Typography>
          </Stack>
        ))}
      </Stack>
    </Box>
  )
}

export function HeroSection() {
  return (
    <Box component="section" id="home" sx={{ overflow: 'hidden', pb: { xs: 6, md: 12 }, pt: { xs: 5, md: 10 } }}>
      <Box
        sx={{
          alignItems: 'center',
          display: 'grid',
          gap: { xs: 4, sm: 5, md: 8 },
          gridTemplateColumns: { xs: '1fr', md: 'minmax(0, 1.15fr) minmax(300px, 0.85fr)' },
        }}
      >
        <Reveal>
          <Stack alignItems={{ xs: 'center', md: 'flex-start' }} spacing={3} sx={{ textAlign: { xs: 'center', md: 'left' } }}>
            <Chip color="primary" icon={<AutoAwesomeRounded />} label="Career guidance, made clearer" size="small" variant="outlined" />
            <Typography component="h1" variant="h1">
              Know Your Skills.
              <Box component="span" sx={{ color: 'primary.main', display: 'block' }}>Know Your Opportunities.</Box>
            </Typography>
            <Typography color="text.secondary" sx={{ maxWidth: 640 }} variant="body1">
              SkillSync AI turns a student resume into practical career direction—connecting your strengths to current job requirements, pinpointing skill gaps, and outlining what to learn next.
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} sx={{ pt: 1, width: { xs: '100%', sm: 'auto' } }}>
              <Button component={RouterLink} endIcon={<ArrowForwardRounded />} size="large" to="/register" variant="contained">
                Analyze My Resume
              </Button>
              <Button component="a" href="#how-it-works" size="large" variant="outlined">
                Explore How It Works
              </Button>
            </Stack>
            <Typography color="text.secondary" variant="body2">Designed to help students make informed career decisions.</Typography>
          </Stack>
        </Reveal>

        <Reveal delay={0.12} direction="left">
          <InsightPanel />
        </Reveal>
      </Box>
    </Box>
  )
}
