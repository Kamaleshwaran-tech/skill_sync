import { useEffect, useState } from 'react'
import { Box, Card, CardContent, Container, Grid, Stack, Typography } from '@mui/material'

import {
  CurrentVsRequiredChart,
  MissingSkillCard,
  SkillDemandChart,
  SkillPillList,
  SkillPriorityChart,
  SummaryStatCard,
} from '@/features/skill-gap-analysis/components/SkillGapVisualization'
import { skillGapService } from '@/features/skill-gap-analysis/services/skillGapService'

const emptySkillGap = {
  currentSkills: [],
  requiredSkills: [],
  matchedSkills: [],
  missingSkills: [],
  proficiencyComparison: [],
  skillPriority: [],
  industryDemand: [],
  summary: {},
}

export function SkillGapAnalysisPage({ data: initialData = emptySkillGap }) {
  const [data, setData] = useState(initialData)

  useEffect(() => {
    let isMounted = true
    skillGapService.getSkillGaps().then((res) => {
      if (isMounted && res?.summary) {
        setData(res)
      }
    })
    return () => {
      isMounted = false
    }
  }, [])

  const currentSkills = data.currentSkills || []
  const requiredSkills = data.requiredSkills || []
  const matchedSkills = data.matchedSkills || []
  const missingSkills = data.missingSkills || []
  const proficiencyComparison = data.proficiencyComparison || []
  const skillPriority = data.skillPriority || []
  const industryDemand = data.industryDemand || []

  return (
    <Box sx={{ py: { xs: 3, md: 6 }, background: 'linear-gradient(180deg, rgba(76,87,232,0.04), rgba(76,87,232,0) 20%)' }}>
      <Container maxWidth="xl">
        <Stack spacing={3}>
          <Box>
            <Typography variant="overline" color="text.secondary">
              Skill strategy
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, letterSpacing: '-0.05em' }}>
              Skill gap analysis
            </Typography>
            <Typography variant="body1" color="text.secondary">
              A dynamic view of the skills you already have, the gaps you still need to close, and the areas worth prioritizing next based on real job market demand.
            </Typography>
          </Box>

          <Grid container spacing={2.5}>
            <Grid item xs={12} sm={6} md={3}>
              <SummaryStatCard label="Current skills" value={currentSkills.length} tone="primary" />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <SummaryStatCard label="Required skills" value={requiredSkills.length} tone="info" />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <SummaryStatCard label="Matched skills" value={matchedSkills.length} tone="success" />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <SummaryStatCard label="Missing skills" value={missingSkills.length} tone="warning" />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <SummaryStatCard label="Skill priority" value={data.summary?.skillPriority || 'High'} tone="error" />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <SummaryStatCard label="Industry demand" value={data.summary?.industryDemand || 'Strong'} tone="secondary" />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <SummaryStatCard label="Overall gap" value={`${data.summary?.overallGap || 0}%`} tone="warning" />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <SummaryStatCard label="Learning difficulty" value={data.summary?.learningDifficulty || 'Moderate'} tone="primary" />
            </Grid>
          </Grid>

          <Grid container spacing={3}>
            <Grid item xs={12} lg={7}>
              <CurrentVsRequiredChart data={proficiencyComparison} />
            </Grid>
            <Grid item xs={12} lg={5}>
              <SkillPriorityChart data={skillPriority} />
            </Grid>
          </Grid>

          <Grid container spacing={3}>
            <Grid item xs={12} lg={8}>
              <SkillDemandChart data={industryDemand} />
            </Grid>
            <Grid item xs={12} lg={4}>
              <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
                <CardContent sx={{ p: 2.5 }}>
                  <Typography variant="h6" sx={{ fontWeight: 800, mb: 2 }}>
                    Skill overview
                  </Typography>
                  <Stack spacing={2.5}>
                    <SkillPillList title="Current skills" items={currentSkills} color="primary" />
                    <SkillPillList title="Required skills" items={requiredSkills} color="info" />
                    <SkillPillList title="Matched skills" items={matchedSkills} color="success" />
                    <SkillPillList title="Missing skills" items={missingSkills.map((skill) => skill.name)} color="warning" />
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Box>
            <Typography variant="h5" sx={{ fontWeight: 800, mb: 2 }}>
              Missing skills to prioritize
            </Typography>
            {missingSkills.length ? (
              <Grid container spacing={2}>
                {missingSkills.map((skill) => (
                  <Grid key={skill.name} item xs={12} md={6}>
                    <MissingSkillCard skill={skill} />
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="body1" color="text.secondary">
                    No missing skills to display in the current analysis snapshot.
                  </Typography>
                </CardContent>
              </Card>
            )}
          </Box>
        </Stack>
      </Container>
    </Box>
  )
}
