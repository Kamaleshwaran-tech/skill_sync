import { useEffect, useState } from 'react'
import { Box, Stack } from '@mui/material'
import Grid from '@mui/material/Grid'

import {
  CareerMatchCard,
  CareerReadinessCard,
  CertificationCard,
  DashboardEmptyState,
  DashboardHeader,
  DashboardLayout,
  JobRecommendationCard,
  LearningProgressCard,
  ProjectRecommendationCard,
  RecentActivity,
  SkillDemandChart,
  SkillOverview,
} from '@/features/student-dashboard/components/DashboardLayout'
import { dashboardService } from '@/features/student-dashboard/services/dashboardService'
import { useAuth } from '@/features/auth/context/useAuth'

const emptyDashboard = {
  profile: { name: 'Student', role: 'Candidate', lastUpdated: 'Updated today', focus: 'Upload a resume to get started' },
  readiness: { overall: 0, metrics: [
    { label: 'Technical Skills', value: 0, trend: '' }, { label: 'Industry Match', value: 0, trend: '' },
    { label: 'Resume Quality', value: 0, trend: '' }, { label: 'Project Strength', value: 0, trend: '' },
  ] },
  careerMatches: [], skillOverview: { current: [], strong: [], developing: [], missing: [] },
  recommendedJobs: [], skillDemand: [], learningProgress: { roadmap: 'No roadmap yet', completedSkills: 0, totalSkills: 0, skillsInProgress: 0, nextRecommendedSkill: 'Upload a resume to get started' },
  recommendedProjects: [], certifications: [], recentActivity: [],
}

export function StudentDashboardPage() {
  const { user } = useAuth()
  const sessionName = user?.full_name || user?.email?.split('@')[0] || 'Student'
  const sessionProfile = {
    ...emptyDashboard.profile,
    name: sessionName,
    role: user?.role ? user.role.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase()) : emptyDashboard.profile.role,
  }
  const [data, setData] = useState({ ...emptyDashboard, profile: sessionProfile })

  useEffect(() => {
    let isMounted = true
    dashboardService.getDashboardData().then((res) => {
      if (isMounted && res) {
        setData((prev) => ({ ...prev, ...res, profile: { ...prev.profile, ...res.profile } }))
      }
    }).catch(() => {})
    return () => {
      isMounted = false
    }
  }, [])

  const {
    profile = emptyDashboard.profile,
    readiness = emptyDashboard.readiness,
    careerMatches = emptyDashboard.careerMatches,
    skillOverview = emptyDashboard.skillOverview,
    recommendedJobs = emptyDashboard.recommendedJobs,
    skillDemand = emptyDashboard.skillDemand,
    learningProgress = emptyDashboard.learningProgress,
    recommendedProjects = emptyDashboard.recommendedProjects,
    certifications = emptyDashboard.certifications,
    recentActivity = emptyDashboard.recentActivity,
  } = data

  return (
    <DashboardLayout title="Dashboard Overview" subtitle="Your career readiness snapshot and recommended next steps.">
      <DashboardHeader
        name={profile.name}
        role={profile.role}
        lastUpdated={profile.lastUpdated}
        focus={profile.focus}
      />

      <Box>
        <CareerReadinessCard readiness={readiness} />
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={7}>
          <Stack spacing={3}>
            <Box>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box component="h3" sx={{ m: 0, fontSize: '1.5rem', fontWeight: 800 }}>
                    Top Career Matches
                  </Box>
                </Box>
                {careerMatches.length ? (
                  <Grid container spacing={2}>
                    {careerMatches.map((match) => (
                      <Grid key={match.role} item xs={12} sm={6}>
                        <CareerMatchCard {...match} />
                      </Grid>
                    ))}
                  </Grid>
                ) : (
                  <DashboardEmptyState
                    title="No career matches yet"
                    description="Complete more learning milestones to unlock stronger role recommendations."
                  />
                )}
              </Stack>
            </Box>
          </Stack>
        </Grid>

        <Grid item xs={12} lg={5}>
          <SkillOverview skillOverview={skillOverview} />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid
          item
          xs={12}
          lg={7}
          sx={{
            minWidth: 0,
            flex: { xs: '1 1 100%', lg: '0 0 58.333333%' },
            width: { xs: '100%', lg: '58.333333%' },
            maxWidth: { xs: '100%', lg: '58.333333%' },
          }}
        >
          <Stack spacing={2}>
            <Box component="h3" sx={{ m: 0, fontSize: '1.5rem', fontWeight: 800 }}>
              Recommended Jobs
            </Box>
            {recommendedJobs.length ? (
              <Grid container spacing={2}>
                {recommendedJobs.map((job) => (
                  <Grid key={job.title} item xs={12}>
                    <JobRecommendationCard job={job} />
                  </Grid>
                ))}
              </Grid>
            ) : (
              <DashboardEmptyState
                title="No job recommendations available"
                description="Your recommended job feed will appear here once you finish more profile steps."
              />
            )}
          </Stack>
        </Grid>

        <Grid
          item
          xs={12}
          lg={5}
          sx={{
            minWidth: 0,
            flex: { xs: '1 1 100%', lg: '0 0 41.666667%' },
            width: { xs: '100%', lg: '41.666667%' },
            maxWidth: { xs: '100%', lg: '41.666667%' },
          }}
        >
          <SkillDemandChart data={skillDemand} />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={7}>
          <LearningProgressCard learningProgress={learningProgress} />
        </Grid>

        <Grid item xs={12} lg={5}>
          <Stack spacing={3}>
            <Box>
              <Box component="h3" sx={{ m: 0, mb: 2, fontSize: '1.5rem', fontWeight: 800 }}>
                Recommended Projects
              </Box>
              {recommendedProjects.length ? (
                <Stack spacing={2}>
                  {recommendedProjects.map((project) => (
                    <ProjectRecommendationCard key={project.title} project={project} />
                  ))}
                </Stack>
              ) : (
                <DashboardEmptyState
                  title="No project suggestions"
                  description="We will suggest project ideas after your next skill assessment."
                />
              )}
            </Box>
          </Stack>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={7}>
          <Stack spacing={2}>
            <Box component="h3" sx={{ m: 0, fontSize: '1.5rem', fontWeight: 800 }}>
              Recommended Certifications
            </Box>
            {certifications.length ? (
              <Grid container spacing={2}>
                {certifications.map((certification) => (
                  <Grid key={certification.title} item xs={12} md={6}>
                    <CertificationCard certification={certification} />
                  </Grid>
                ))}
              </Grid>
            ) : (
              <DashboardEmptyState
                title="No certifications queued"
                description="Industry-aligned certifications will appear here as your roadmap progresses."
              />
            )}
          </Stack>
        </Grid>

        <Grid item xs={12} lg={5}>
          <RecentActivity activityItems={recentActivity} />
        </Grid>
      </Grid>
    </DashboardLayout>
  )
}
