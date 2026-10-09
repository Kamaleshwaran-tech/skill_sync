import { FindInPageRounded, LightbulbRounded, PsychologyAltRounded, SchoolRounded } from '@mui/icons-material'
import { Box, Card, CardContent, Typography } from '@mui/material'

import { SectionHeading } from '@/features/landing/components/SectionHeading'
import { Reveal } from '@/shared/ui/motion/Reveal'

const problems = [
  { icon: FindInPageRounded, text: 'Unsure which roles truly match their current skills.' },
  { icon: PsychologyAltRounded, text: 'Lack visibility into the skills companies are asking for today.' },
  { icon: SchoolRounded, text: 'Struggle to decide what to learn next and why it matters.' },
  { icon: LightbulbRounded, text: 'Have resumes that do not clearly reflect industry expectations.' },
]

export function ProblemSection() {
  return (
    <Box component="section" sx={(theme) => ({ backgroundColor: theme.palette.surface.subtle, py: { xs: 8, md: 12 } })}>
      <Box sx={{ maxWidth: 'lg', mx: 'auto', px: { xs: 2.5, sm: 3 } }}>
        <Box sx={{ display: 'grid', gap: { xs: 5, lg: 8 }, gridTemplateColumns: { xs: '1fr', lg: '0.8fr 1.2fr' } }}>
          <SectionHeading
            eyebrow="The challenge"
            heading="Career choices should not feel like guesswork."
            supportingText="Students are ready to grow, but they need a clearer connection between what they know, what the market needs, and what comes next."
          />
          <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, minmax(0, 1fr))' } }}>
            {problems.map((problem, index) => {
              const Icon = problem.icon

              return (
                <Reveal delay={index * 0.06} key={problem.text}>
                  <Card component="article" sx={{ height: '100%' }}>
                    <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
                      <Box sx={(theme) => ({ alignItems: 'center', backgroundColor: theme.palette.action.selected, borderRadius: 2, color: 'primary.main', display: 'inline-flex', height: 40, justifyContent: 'center', mb: 3, width: 40 })}>
                        <Icon fontSize="small" />
                      </Box>
                      <Typography component="p" fontWeight={680} sx={{ letterSpacing: '-0.02em' }}>
                        {problem.text}
                      </Typography>
                    </CardContent>
                  </Card>
                </Reveal>
              )
            })}
          </Box>
        </Box>
      </Box>
    </Box>
  )
}
