import { AutoAwesomeRounded, DocumentScannerRounded, InsightsRounded, MapRounded, RadarRounded, WorkOutlineRounded } from '@mui/icons-material'
import { Box } from '@mui/material'

import { FeatureCard } from '@/features/landing/components/FeatureCard'
import { SectionHeading } from '@/features/landing/components/SectionHeading'

const features = [
  { icon: DocumentScannerRounded, title: 'AI Resume Analysis', description: 'Turn your resume into a structured view of your experience and strengths.' },
  { icon: RadarRounded, title: 'Semantic Skill Matching', description: 'Connect skills in context, not just by exact keyword matches.' },
  { icon: WorkOutlineRounded, title: 'Live Job Opportunities', description: 'Discover opportunities aligned with the direction you want to pursue.' },
  { icon: InsightsRounded, title: 'Skill Gap Detection', description: 'See the capabilities that stand between you and your target roles.' },
  { icon: AutoAwesomeRounded, title: 'Career Readiness Score', description: 'Understand your preparation through a clear, actionable signal.' },
  { icon: MapRounded, title: 'Personalized Learning Roadmap', description: 'Prioritize the learning steps that can move your career forward.' },
]

export function FeatureSection() {
  return (
    <Box component="section" id="features" sx={{ py: { xs: 9, md: 14 } }}>
      <Box sx={{ maxWidth: 'lg', mx: 'auto', px: { xs: 2.5, sm: 3 } }}>
        <SectionHeading
          eyebrow="Purpose-built intelligence"
          heading="A clearer view of your career potential."
          supportingText="SkillSync AI combines the career signals students need into one straightforward experience."
        />
        <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, minmax(0, 1fr))', lg: 'repeat(3, minmax(0, 1fr))' }, mt: { xs: 5, md: 7 } }}>
          {features.map((feature, index) => <FeatureCard {...feature} index={index} key={feature.title} />)}
        </Box>
      </Box>
    </Box>
  )
}
