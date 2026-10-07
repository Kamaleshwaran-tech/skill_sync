import { CheckCircle, Flag, TrendingUp } from '@mui/icons-material'
import {
  Box,
  Card,
  CardContent,
  Chip,
  Container,
  Grid,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material'
import { useEffect, useState } from 'react'

import { RoadmapItemCard } from '@/features/learning-roadmap/components/RoadmapItemCard'
import { learningRoadmapService } from '@/features/learning-roadmap/services/learningRoadmapService'

const emptyRoadmap = { currentSkillLevel: 'Not assessed', targetRole: 'Add a target role', estimatedDuration: 'Not available', requiredSkills: [], missingSkills: [], roadmapItems: [] }

const mapStatus = {
  completed: 'completed',
  in_progress: 'in progress',
  not_started: 'not started',
}

export function LearningRoadmapPage({ data = emptyRoadmap }) {
  const [roadmap, setRoadmap] = useState(data)
  const [roadmapItems, setRoadmapItems] = useState(data.roadmapItems || [])
  const [expandedIds, setExpandedIds] = useState(() => new Set([data.roadmapItems?.[0]?.id || '']))

  useEffect(() => {
    let isMounted = true
    learningRoadmapService.getRoadmap().then((res) => {
      if (isMounted && res?.roadmapItems && res.roadmapItems.length > 0) {
        setRoadmap(res)
        setRoadmapItems(res.roadmapItems)
      }
    })
    return () => {
      isMounted = false
    }
  }, [])

  const completedCount = roadmapItems.filter((item) => item.completionStatus === 'completed').length
  const progressValue = Math.round((completedCount / roadmapItems.length) * 100) || 0

  const toggleStatus = (id, nextStatus) => {
    setRoadmapItems((currentItems) =>
      currentItems.map((item) => {
        if (item.id !== id) {
          return item
        }

        return { ...item, completionStatus: nextStatus, started: nextStatus !== 'not_started' }
      }),
    )
  }

  const toggleExpanded = (id) => {
    setExpandedIds((currentSet) => {
      const nextSet = new Set(currentSet)

      if (nextSet.has(id)) {
        nextSet.delete(id)
      } else {
        nextSet.add(id)
      }

      return nextSet
    })
  }

  return (
    <Box sx={{ py: { xs: 2.5, sm: 3.5, md: 5 }, background: 'linear-gradient(180deg, rgba(76,87,232,0.04), rgba(76,87,232,0) 20%)', minHeight: '100vh' }}>
      <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="overline" color="text.secondary">
              Career roadmap
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, letterSpacing: '-0.05em' }}>
              Personalized learning roadmap
            </Typography>
            <Typography variant="body1" color="text.secondary">
              A personalized roadmap generated from your analyzed skills, job gaps, and career readiness.
            </Typography>
          </Box>

          <Grid container spacing={2.5}>
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
                <CardContent sx={{ p: 2.5 }}>
                  <Typography variant="overline" color="text.secondary">Current skill level</Typography>
                  <Typography variant="h5" sx={{ fontWeight: 800 }}>{roadmap.currentSkillLevel}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
                <CardContent sx={{ p: 2.5 }}>
                  <Typography variant="overline" color="text.secondary">Target role</Typography>
                  <Typography variant="h5" sx={{ fontWeight: 800 }}>{roadmap.targetRole}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
                <CardContent sx={{ p: 2.5 }}>
                  <Typography variant="overline" color="text.secondary">Estimated duration</Typography>
                  <Typography variant="h5" sx={{ fontWeight: 800 }}>{roadmap.estimatedDuration}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
                <CardContent sx={{ p: 2.5 }}>
                  <Typography variant="overline" color="text.secondary">Progress</Typography>
                  <Typography variant="h5" sx={{ fontWeight: 800 }}>{progressValue}%</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
            <CardContent sx={{ p: 2.5 }}>
              <Stack spacing={2}>
                <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={2}>
                  <Typography variant="h6" sx={{ fontWeight: 800 }}>Roadmap progress</Typography>
                  <Chip label={`${completedCount}/${roadmapItems.length} completed`} color="primary" variant="outlined" />
                </Stack>
                <LinearProgress variant="determinate" value={progressValue} sx={{ height: 10, borderRadius: 999 }} />
              </Stack>
            </CardContent>
          </Card>

          <Grid container spacing={3}>
            <Grid item xs={12} lg={4}>
              <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
                <CardContent sx={{ p: 2.5 }}>
                  <Stack spacing={2.5}>
                    <Box>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Flag color="primary" />
                        <Typography variant="h6" sx={{ fontWeight: 800 }}>Required skills</Typography>
                      </Stack>
                      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1.5 }}>
                        {roadmap.requiredSkills.map((skill) => (
                          <Chip key={skill} label={skill} variant="outlined" size="small" />
                        ))}
                      </Stack>
                    </Box>

                    <Box>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <TrendingUp color="warning" />
                        <Typography variant="h6" sx={{ fontWeight: 800 }}>Missing skills</Typography>
                      </Stack>
                      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1.5 }}>
                        {roadmap.missingSkills.map((skill) => (
                          <Chip key={skill} label={skill} color="warning" variant="outlined" size="small" />
                        ))}
                      </Stack>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} lg={8}>
              <Stack spacing={2}>
                {roadmapItems.map((item) => (
                  <RoadmapItemCard
                    key={item.id}
                    item={item}
                    expanded={expandedIds.has(item.id)}
                    onToggleExpanded={() => toggleExpanded(item.id)}
                    onToggleStatus={toggleStatus}
                  />
                ))}
              </Stack>
            </Grid>
          </Grid>

          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
            <CardContent sx={{ p: 2.5 }}>
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
                <CheckCircle color="success" />
                <Typography variant="h6" sx={{ fontWeight: 800 }}>Learning status summary</Typography>
              </Stack>

              <Grid container spacing={2}>
                {roadmapItems.map((item) => (
                  <Grid item xs={12} sm={6} md={3} key={item.id}>
                    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                      <CardContent sx={{ p: 2 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>{item.skill}</Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.75 }}>
                          {mapStatus[item.completionStatus]}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Stack>
      </Container>
    </Box>
  )
}
