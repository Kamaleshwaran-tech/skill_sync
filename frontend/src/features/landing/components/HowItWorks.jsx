import { ArrowDownwardRounded, ArrowForwardRounded, AutoAwesomeRounded, CloudUploadRounded, MapRounded, WorkOutlineRounded } from '@mui/icons-material'
import { Box, Stack, Typography } from '@mui/material'

import { SectionHeading } from '@/features/landing/components/SectionHeading'
import { Reveal } from '@/shared/ui/motion/Reveal'

const steps = [
  { icon: CloudUploadRounded, label: 'Upload Resume', number: '01' },
  { icon: AutoAwesomeRounded, label: 'AI Skill Analysis', number: '02' },
  { icon: WorkOutlineRounded, label: 'Live Job Matching', number: '03' },
  { icon: MapRounded, label: 'Personalized Roadmap', number: '04' },
]

export function HowItWorks() {
  return (
    <Box component="section" id="how-it-works" sx={{ py: { xs: 9, md: 14 } }}>
      <Box sx={{ maxWidth: 'lg', mx: 'auto', px: { xs: 2.5, sm: 3 } }}>
        <SectionHeading
          align="center"
          eyebrow="How it works"
          heading="From resume to a more confident next step."
          supportingText="A focused path that translates your experience into practical career insight."
        />
        <Box sx={{ alignItems: 'stretch', display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: { xs: 1.5, md: 0 }, mt: { xs: 5, md: 7 } }}>
          {steps.map((step, index) => {
            const Icon = step.icon
            const isLastStep = index === steps.length - 1

            return (
              <Box alignItems="center" display="flex" flex={{ md: 1 }} flexDirection={{ xs: 'column', md: 'row' }} key={step.number}>
                <Reveal delay={index * 0.07}>
                  <Stack alignItems="center" spacing={2} sx={(theme) => ({ backgroundColor: 'background.paper', border: `1px solid ${theme.palette.divider}`, borderRadius: 3, minHeight: { xs: 138, md: 172 }, p: 3, textAlign: 'center', width: '100%' })}>
                    <Box sx={(theme) => ({ alignItems: 'center', backgroundColor: theme.palette.action.selected, borderRadius: 2, color: 'primary.main', display: 'flex', height: 40, justifyContent: 'center', width: 40 })}>
                      <Icon fontSize="small" />
                    </Box>
                    <Stack spacing={0.25}>
                      <Typography color="text.secondary" variant="caption">{step.number}</Typography>
                      <Typography component="h3" variant="h3">{step.label}</Typography>
                    </Stack>
                  </Stack>
                </Reveal>
                {!isLastStep ? (
                  <Box aria-hidden="true" sx={{ color: 'text.secondary', display: 'flex', justifyContent: 'center', p: { xs: 0.5, md: 1 } }}>
                    <ArrowForwardRounded sx={{ display: { xs: 'none', md: 'block' } }} />
                    <ArrowDownwardRounded sx={{ display: { md: 'none' } }} />
                  </Box>
                ) : null}
              </Box>
            )
          })}
        </Box>
      </Box>
    </Box>
  )
}
