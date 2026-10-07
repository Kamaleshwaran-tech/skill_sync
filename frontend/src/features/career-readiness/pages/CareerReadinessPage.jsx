import { useEffect, useState } from 'react'
import { Box, Card, CardContent, Container, Grid, Stack, Typography } from '@mui/material'

import {
  ScoreBarChart,
  ScoreRadialChart,
  ScoreTrendChart,
  SkillRadarChart,
} from '@/features/career-readiness/components/CareerReadinessCharts'
import {
  ExplanationAccordion,
  OpportunityList,
  RecommendedActionsList,
  StrengthsList,
  WeaknessesList,
} from '@/features/career-readiness/components/CareerReadinessSections'
import { careerReadinessService } from '@/features/career-readiness/services/careerReadinessService'

const emptyCareerReadiness = { overallScore: 0, dimensions: [], trend: [], scoreBreakdown: [], strengths: [], weaknesses: [], recommendedActions: [], opportunities: [], explanation: { title: 'Complete your profile', body: 'Upload and analyze a resume to generate your career readiness assessment.' } }

export function CareerReadinessPage({ data: initialData = emptyCareerReadiness }) {
  const [data, setData] = useState(initialData)

  useEffect(() => {
    let isMounted = true
    careerReadinessService.getCareerReadiness().then((res) => {
      if (isMounted && res?.overallScore !== undefined) {
        setData(res)
      }
    })
    return () => {
      isMounted = false
    }
  }, [])
  return (
    <Box sx={{ py: { xs: 2.5, sm: 3.5, md: 5 }, background: 'linear-gradient(180deg, rgba(76,87,232,0.04), rgba(76,87,232,0) 20%)', minHeight: '100vh' }}>
      <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="overline" color="text.secondary">
              Career profile
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, letterSpacing: '-0.05em' }}>
              Career readiness overview
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 700 }}>
              Track comprehensive readiness across technical competencies, industry alignment, resume quality, and practical interview readiness.
            </Typography>
          </Box>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: 'repeat(1, 1fr)',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(3, 1fr)',
                lg: 'repeat(5, 1fr)',
              },
              gap: 2,
            }}
          >
            <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
              <CardContent sx={{ p: 2.5 }}>
                <Typography variant="overline" color="text.secondary">Overall readiness</Typography>
                <Typography variant="h4" sx={{ fontWeight: 800, mt: 0.75, color: 'primary.main' }}>{data.overallScore}%</Typography>
              </CardContent>
            </Card>
            {data.dimensions.map((dimension) => (
              <Card key={dimension.name} elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
                <CardContent sx={{ p: 2.5 }}>
                  <Typography variant="overline" color="text.secondary">{dimension.name}</Typography>
                  <Typography variant="h5" sx={{ fontWeight: 800, mt: 0.75 }}>{dimension.score}%</Typography>
                </CardContent>
              </Card>
            ))}
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} lg={5}>
              <ScoreRadialChart data={data.dimensions} />
            </Grid>
            <Grid item xs={12} lg={7}>
              <ScoreTrendChart data={data.trend} />
            </Grid>
          </Grid>

          <Grid container spacing={3}>
            <Grid item xs={12} lg={7}>
              <ScoreBarChart data={data.scoreBreakdown} />
            </Grid>
            <Grid item xs={12} lg={5}>
              <SkillRadarChart data={data.dimensions} />
            </Grid>
          </Grid>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
                <CardContent sx={{ p: 3 }}>
                  <Stack spacing={2.5}>
                    <StrengthsList items={data.strengths} />
                    <WeaknessesList items={data.weaknesses} />
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
                <CardContent sx={{ p: 3 }}>
                  <Stack spacing={2.5}>
                    <RecommendedActionsList items={data.recommendedActions} />
                    <OpportunityList items={data.opportunities} />
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <ExplanationAccordion title={data.explanation.title} body={data.explanation.body} />
        </Stack>
      </Container>
    </Box>
  )
}
