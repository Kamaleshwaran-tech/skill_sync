import { Box, Container } from '@mui/material'

import { CTASection } from '@/features/landing/components/CTASection'
import { CareerIntelligence } from '@/features/landing/components/CareerIntelligence'
import { FeatureSection } from '@/features/landing/components/FeatureSection'
import { HeroSection } from '@/features/landing/components/HeroSection'
import { HowItWorks } from '@/features/landing/components/HowItWorks'
import { ProblemSection } from '@/features/landing/components/ProblemSection'

export function LandingPage() {
  return (
    <Box>
      <Container maxWidth="lg">
        <HeroSection />
      </Container>
      <ProblemSection />
      <HowItWorks />
      <FeatureSection />
      <CareerIntelligence />
      <Container maxWidth="lg" sx={{ px: { xs: 2.5, sm: 3 } }}>
        <CTASection />
      </Container>
    </Box>
  )
}
