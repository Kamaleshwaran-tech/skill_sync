import { ArrowDownwardRounded, CheckCircleRounded, LightbulbRounded, MapRounded, RadarRounded, SchoolRounded } from '@mui/icons-material'
import { Box, Stack, Typography } from '@mui/material'

import { SectionHeading } from '@/features/landing/components/SectionHeading'
import { Reveal } from '@/shared/ui/motion/Reveal'

const intelligenceSteps = [
  { icon: LightbulbRounded, label: 'Current Skills' },
  { icon: RadarRounded, label: 'Industry Requirements' },
  { icon: SchoolRounded, label: 'Skill Gap' },
  { icon: MapRounded, label: 'Learning Roadmap' },
  { icon: CheckCircleRounded, label: 'Career Ready' },
]

export function CareerIntelligence() {
  return (
    <Box component="section" id="career-intelligence" sx={(theme) => ({ backgroundColor: theme.palette.surface.subtle, py: { xs: 9, md: 14 } })}>
      <Box sx={{ maxWidth: 'lg', mx: 'auto', px: { xs: 2.5, sm: 3 } }}>
        <Box sx={{ display: 'grid', gap: { xs: 5, lg: 8 }, gridTemplateColumns: { xs: '1fr', lg: '0.8fr 1.2fr' } }}>
          <SectionHeading
            eyebrow="Career intelligence"
            heading="Connect the dots between effort and opportunity."
            supportingText="Your career direction becomes easier to act on when every recommendation has a reason behind it."
          />
          <Reveal delay={0.1} direction="left">
            <Stack spacing={0}>
              {intelligenceSteps.map((step, index) => {
                const Icon = step.icon
                const isLastStep = index === intelligenceSteps.length - 1

                return (
                  <Box key={step.label}>
                    <Stack alignItems="center" direction="row" spacing={2.25} sx={(theme) => ({ backgroundColor: 'background.paper', border: `1px solid ${theme.palette.divider}`, borderRadius: 2.5, p: 2.25 })}>
                      <Box sx={(theme) => ({ alignItems: 'center', backgroundColor: index === intelligenceSteps.length - 1 ? 'primary.main' : theme.palette.action.selected, borderRadius: 2, color: index === intelligenceSteps.length - 1 ? 'primary.contrastText' : 'primary.main', display: 'flex', height: 38, justifyContent: 'center', width: 38 })}>
                        <Icon fontSize="small" />
                      </Box>
                      <Typography component="h3" variant="h3">{step.label}</Typography>
                    </Stack>
                    {!isLastStep ? (
                      <Box aria-hidden="true" sx={{ color: 'text.secondary', display: 'flex', height: 28, justifyContent: 'center', py: 0.25 }}>
                        <ArrowDownwardRounded fontSize="small" />
                      </Box>
                    ) : null}
                  </Box>
                )
              })}
            </Stack>
          </Reveal>
        </Box>
      </Box>
    </Box>
  )
}
