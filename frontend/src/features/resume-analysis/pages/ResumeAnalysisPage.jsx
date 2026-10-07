import { Box, Card, CardContent, Container, Grid, Stack, Typography } from '@mui/material'

import { EducationCard } from '@/features/resume-analysis/components/EducationCard'
import { ExperienceTimeline } from '@/features/resume-analysis/components/ExperienceTimeline'
import { ImprovementCard } from '@/features/resume-analysis/components/ImprovementCard'
import { PersonalInfoCard } from '@/features/resume-analysis/components/PersonalInfoCard'
import { ProjectCard } from '@/features/resume-analysis/components/ProjectCard'
import { ResumeScoreCard } from '@/features/resume-analysis/components/ResumeScoreCard'
import { ResumeSummary } from '@/features/resume-analysis/components/ResumeSummary'
import { SkillCategoryCard } from '@/features/resume-analysis/components/SkillCategoryCard'
import { SkillChip } from '@/features/resume-analysis/components/SkillChip'
import { StrengthCard } from '@/features/resume-analysis/components/StrengthCard'
import { emptyResumeAnalysis, resumeAnalysisService } from '@/features/resume-analysis/services/resumeAnalysisService'
import { useEffect, useState } from 'react'

function ResumeAnalysisSectionSkeleton() {
  return (
    <Card elevation={0}>
      <CardContent sx={{ p: 3 }}>
        <Stack spacing={2}>
          <Box sx={{ width: '40%', height: 28, bgcolor: 'action.hover', borderRadius: 2 }} />
          <Box sx={{ width: '100%', height: 120, bgcolor: 'action.hover', borderRadius: 2 }} />
        </Stack>
      </CardContent>
    </Card>
  )
}

function EmptyState({ title, description }) {
  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3 }}>
        <Stack spacing={1.5}>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>{title}</Typography>
          <Typography variant="body2" color="text.secondary">{description}</Typography>
        </Stack>
      </CardContent>
    </Card>
  )
}

export function ResumeAnalysisPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { resumeAnalysisService.getResumeAnalysis().then(setData).catch((err) => setError(err?.response?.data?.detail || 'Unable to load resume analysis.')) }, [])
  const {
    overview,
    personalInfo,
    education,
    experience,
    projects,
    certifications,
    technicalSkills,
    softSkills,
    skillCategories,
    strengths,
    improvements,
    aiSummary,
  } = data || emptyResumeAnalysis
  const isLoading = !data && !error

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(180deg, rgba(76,87,232,0.04), rgba(76,87,232,0) 20%)', py: { xs: 2.5, sm: 3.5, md: 5 } }}>
      <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="overline" color="text.secondary">AI resume analysis</Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, letterSpacing: '-0.05em' }}>
              Resume analysis overview
            </Typography>
          </Box>

          {isLoading ? (
            <Grid container spacing={3}>
              {[1, 2, 3].map((item) => (
                <Grid item xs={12} key={item}>
                  <ResumeAnalysisSectionSkeleton />
                </Grid>
              ))}
            </Grid>
          ) : error ? <EmptyState title="Analysis unavailable" description={error} /> : (
            <>
              <ResumeSummary overview={overview} />

              <Grid container spacing={3}>
                <Grid item xs={12} lg={6}>
                  <PersonalInfoCard personalInfo={personalInfo} />
                </Grid>
                <Grid item xs={12} lg={6}>
                  <ResumeScoreCard score={overview.qualityScore} />
                </Grid>
              </Grid>

              <Grid container spacing={3}>
                <Grid item xs={12} lg={6}>
                  <EducationCard education={education} />
                </Grid>
                <Grid item xs={12} lg={6}>
                  <ExperienceTimeline experience={experience} />
                </Grid>
              </Grid>

              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Card elevation={0}>
                    <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
                      <Stack spacing={2.5}>
                        <Typography variant="h5" sx={{ fontWeight: 800 }}>Projects</Typography>
                        {projects && projects.length ? (
                          <Grid container spacing={2}>
                            {projects.map((project) => (
                              <Grid item xs={12} md={6} key={project.name}>
                                <ProjectCard project={project} />
                              </Grid>
                            ))}
                          </Grid>
                        ) : (
                          <EmptyState title="No projects found" description="Project data will appear when a resume includes portfolio work." />
                        )}
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card elevation={0}>
                    <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
                      <Stack spacing={2.5}>
                        <Typography variant="h5" sx={{ fontWeight: 800 }}>Certifications</Typography>
                        {certifications && certifications.length ? (
                          <Stack spacing={2}>
                            {certifications.map((cert) => (
                              <Box key={`${cert.name}-${cert.issuer}`} sx={{ p: 2.25, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                                <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{cert.name}</Typography>
                                <Typography variant="body2" color="text.secondary">{cert.issuer}</Typography>
                                <Typography variant="caption" color="text.secondary">{cert.year}</Typography>
                              </Box>
                            ))}
                          </Stack>
                        ) : (
                          <EmptyState title="No certifications" description="There are no certifications listed in this resume." />
                        )}
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card elevation={0}>
                    <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
                      <Stack spacing={2.5}>
                        <Typography variant="h5" sx={{ fontWeight: 800 }}>Technical skills</Typography>
                        {technicalSkills && technicalSkills.length ? (
                          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                            {technicalSkills.map((skill) => (
                              <SkillChip key={skill} label={skill} color="primary" />
                            ))}
                          </Stack>
                        ) : (
                          <EmptyState title="No technical skills" description="No technical skills were detected from this resume." />
                        )}
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card elevation={0}>
                    <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
                      <Stack spacing={2.5}>
                        <Typography variant="h5" sx={{ fontWeight: 800 }}>Soft skills</Typography>
                        {softSkills && softSkills.length ? (
                          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                            {softSkills.map((skill) => (
                              <SkillChip key={skill} label={skill} color="secondary" variant="outlined" />
                            ))}
                          </Stack>
                        ) : (
                          <EmptyState title="No soft skills" description="This resume does not contain clear soft skill signals." />
                        )}
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card elevation={0}>
                    <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
                      <Stack spacing={2.5}>
                        <Typography variant="h5" sx={{ fontWeight: 800 }}>Skill categories</Typography>
                        {skillCategories && skillCategories.length ? (
                          <Grid container spacing={2}>
                            {skillCategories.map((category) => (
                              <Grid item xs={12} key={category.name}>
                                <SkillCategoryCard category={category} />
                              </Grid>
                            ))}
                          </Grid>
                        ) : (
                          <EmptyState title="No skill categories" description="Category insights will appear when the resume includes detailed skills." />
                        )}
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card elevation={0}>
                    <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
                      <Stack spacing={2.5}>
                        <Typography variant="h5" sx={{ fontWeight: 800 }}>Strengths</Typography>
                        {strengths && strengths.length ? (
                          <Grid container spacing={2}>
                            {strengths.map((strength) => (
                              <Grid item xs={12} key={strength}>
                                <StrengthCard strength={strength} />
                              </Grid>
                            ))}
                          </Grid>
                        ) : (
                          <EmptyState title="No strengths" description="Strength signals will populate once analysis is complete." />
                        )}
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card elevation={0}>
                    <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
                      <Stack spacing={2.5}>
                        <Typography variant="h5" sx={{ fontWeight: 800 }}>Areas for improvement</Typography>
                        {improvements && improvements.length ? (
                          <Grid container spacing={2}>
                            {improvements.map((improvement) => (
                              <Grid item xs={12} key={improvement}>
                                <ImprovementCard improvement={improvement} />
                              </Grid>
                            ))}
                          </Grid>
                        ) : (
                          <EmptyState title="No improvement suggestions" description="No content gaps were identified for this resume." />
                        )}
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <Card elevation={0}>
                <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
                  <Stack spacing={2}>
                    <Typography variant="h5" sx={{ fontWeight: 800 }}>AI analysis summary</Typography>
                    <Typography variant="body1" color="text.secondary">{aiSummary}</Typography>
                  </Stack>
                </CardContent>
              </Card>
            </>
          )}
        </Stack>
      </Container>
    </Box>
  )
}
