import { useEffect, useMemo, useState } from 'react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import {
  AccountCircle,
  AutoStories,
  CloudUpload,
  PsychologyAlt,
  School,
  WorkOutlineRounded,
} from '@mui/icons-material'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Divider,
  Grid,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Stack,
  TextField,
  Typography,
} from '@mui/material'

import { dashboardService } from '@/features/student-dashboard/services/dashboardService'
import { useAuth } from '@/features/auth/context/useAuth'

const priorityColor = {
  HIGH: 'error',
  MEDIUM: 'warning',
  LOW: 'info',
}

function ResumeSummaryCard({ profile, hasResume, parsedSkills = [], personalInfo = {}, resumeScore }) {
  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
      <CardContent sx={{ p: 3 }}>
        <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 2 }}>
          <AccountCircle color="primary" />
          <Typography variant="h6" sx={{ fontWeight: 800 }}>Your profile</Typography>
        </Stack>
        {hasResume ? (
          <Stack spacing={1.5}>
            <Typography variant="h5" sx={{ fontWeight: 800 }}>{personalInfo.name || profile.name}</Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {personalInfo.location && <Chip size="small" variant="outlined" label={personalInfo.location} />}
              {personalInfo.phone && <Chip size="small" variant="outlined" label={personalInfo.phone} />}
              {typeof personalInfo.experienceCount === 'number' && (
                <Chip size="small" color="primary" variant="outlined" label={`${personalInfo.experienceCount} experience entries`} />
              )}
              {typeof personalInfo.projectCount === 'number' && (
                <Chip size="small" color="secondary" variant="outlined" label={`${personalInfo.projectCount} projects`} />
              )}
              {typeof personalInfo.educationCount === 'number' && (
                <Chip size="small" variant="outlined" label={`${personalInfo.educationCount} education entries`} />
              )}
            </Stack>
            {personalInfo.summary && (
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                {String(personalInfo.summary).slice(0, 280)}{String(personalInfo.summary).length > 280 ? '…' : ''}
              </Typography>
            )}
            {resumeScore !== null && resumeScore !== undefined && (
              <Box>
                <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.5 }}>
                  <Typography variant="caption" color="text.secondary">Resume parse quality</Typography>
                  <Typography variant="caption" fontWeight={700}>{resumeScore}%</Typography>
                </Stack>
                <LinearProgress
                  variant="determinate"
                  value={Math.max(0, Math.min(100, resumeScore))}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            )}
            {parsedSkills.length > 0 && (
              <Box>
                <Typography variant="overline" color="text.secondary">Skills detected ({parsedSkills.length})</Typography>
                <Stack direction="row" spacing={0.75} flexWrap="wrap" useFlexGap sx={{ mt: 0.5 }}>
                  {parsedSkills.slice(0, 20).map((skill) => (
                    <Chip key={skill} size="small" label={skill} />
                  ))}
                </Stack>
              </Box>
            )}
          </Stack>
        ) : (
          <Stack spacing={2} alignItems="flex-start">
            <Typography variant="body2" color="text.secondary">
              Upload your resume so we can extract your skills, experience and projects.
            </Typography>
            <Button component={RouterLink} to="/resume-upload" variant="contained" startIcon={<CloudUpload />}>
              Upload resume
            </Button>
          </Stack>
        )}
      </CardContent>
    </Card>
  )
}

function TargetRoleCard({ targetRole, onSave, saving }) {
  const [value, setValue] = useState(targetRole || '')
  const [error, setError] = useState('')

  useEffect(() => { setValue(targetRole || '') }, [targetRole])

  const handleSubmit = async (event) => {
    event.preventDefault()
    const role = value.trim()
    if (role.length < 2) { setError('Please enter a target role.'); return }
    setError('')
    try { await onSave(role) } catch (err) { setError(err?.response?.data?.detail || 'Unable to save target role.') }
  }

  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
      <CardContent sx={{ p: 3 }}>
        <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 2 }}>
          <WorkOutlineRounded color="primary" />
          <Typography variant="h6" sx={{ fontWeight: 800 }}>Target role</Typography>
        </Stack>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Tell us the role you are preparing for. We will analyze gaps between your resume and this role and build a personalized AI roadmap.
        </Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate>
          <TextField
            autoComplete="off"
            error={Boolean(error)}
            fullWidth
            helperText={error}
            label="e.g. Full Stack Developer, Data Scientist, Cloud Engineer"
            onChange={(e) => setValue(e.target.value)}
            placeholder="Enter your target role"
            value={value}
          />
          <Button
            disabled={saving || !value.trim()}
            fullWidth
            size="large"
            startIcon={saving ? <CircularProgress color="inherit" size={18} /> : <PsychologyAlt />}
            sx={{ mt: 2 }}
            type="submit"
            variant="contained"
          >
            {saving ? 'Saving…' : 'Save target role'}
          </Button>
        </Box>
      </CardContent>
    </Card>
  )
}

function SkillGapCard({ skillGap = [], matchedSkills = [], loading, onAnalyze, canAnalyze, analysisError }) {
  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
      <CardContent sx={{ p: 3 }}>
        <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 2 }}>
          <AutoStories color="primary" />
          <Typography variant="h6" sx={{ fontWeight: 800 }}>Skill gap analysis</Typography>
        </Stack>

        {analysisError && <Alert severity="error" sx={{ mb: 2 }}>{analysisError}</Alert>}

        {!canAnalyze ? (
          <Alert severity="info">Upload a resume and set a target role to generate your personalized skill gap analysis.</Alert>
        ) : loading ? (
          <Stack alignItems="center" spacing={2} sx={{ py: 4 }}>
            <CircularProgress />
            <Typography variant="body2" color="text.secondary">Analyzing your resume against target role…</Typography>
          </Stack>
        ) : skillGap.length === 0 && matchedSkills.length === 0 ? (
          <Stack spacing={2} alignItems="flex-start">
            <Typography variant="body2" color="text.secondary">
              Run the analysis to see which skills you already match and which you need to build.
            </Typography>
            <Button onClick={onAnalyze} startIcon={<PsychologyAlt />} variant="outlined">
              Run skill gap analysis
            </Button>
          </Stack>
        ) : (
          <Stack spacing={2}>
            {matchedSkills.length > 0 && (
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>Skills you already match</Typography>
                <Stack direction="row" spacing={0.75} flexWrap="wrap" useFlexGap>
                  {matchedSkills.slice(0, 12).map((s) => (
                    <Chip key={s} color="success" size="small" variant="outlined" label={s} />
                  ))}
                </Stack>
              </Box>
            )}
            <Divider />
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>Skills to build ({skillGap.length})</Typography>
              <List dense disablePadding>
                {skillGap.map((g) => (
                  <ListItem key={g.skill} disableGutters sx={{ py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <Chip color={priorityColor[g.priority] || 'default'} label={g.priority} size="small" sx={{ fontWeight: 800, minWidth: 56 }} />
                    </ListItemIcon>
                    <ListItemText primary={g.skill} primaryTypographyProps={{ fontWeight: 600 }} />
                  </ListItem>
                ))}
              </List>
            </Box>
            <Button onClick={onAnalyze} startIcon={<PsychologyAlt />} variant="contained">
              Re-run analysis
            </Button>
          </Stack>
        )}
      </CardContent>
    </Card>
  )
}

function RoadmapCard({ roadmap }) {
  if (!roadmap) {
    return (
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 2 }}>
            <School color="primary" />
            <Typography variant="h6" sx={{ fontWeight: 800 }}>AI learning roadmap</Typography>
          </Stack>
          <Typography variant="body2" color="text.secondary">
            Run the skill gap analysis above to generate a step-by-step AI learning roadmap tailored to your target role.
          </Typography>
        </CardContent>
      </Card>
    )
  }

  const steps = roadmap.learningSequence || roadmap.roadmap_steps || []
  const advice = roadmap.careerAdvice || roadmap.summary || ''

  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
      <CardContent sx={{ p: 3 }}>
        <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 2 }}>
          <School color="primary" />
          <Typography variant="h6" sx={{ fontWeight: 800 }}>AI learning roadmap</Typography>
        </Stack>
        <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
          Target: {roadmap.targetRole || roadmap.target_role || 'Your target role'}
        </Typography>
        {roadmap.summary && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, mb: 2 }}>
            {roadmap.summary}
          </Typography>
        )}
        {steps.length > 0 && (
          <List dense sx={{ bgcolor: 'action.hover', borderRadius: 2, px: 1 }}>
            {steps.slice(0, 8).map((step, idx) => (
              <ListItem key={`${step.skill}-${idx}`} disableGutters sx={{ py: 0.75, alignItems: 'flex-start' }}>
                <ListItemIcon sx={{ minWidth: 34 }}>
                  <Chip color="primary" label={idx + 1} size="small" sx={{ fontWeight: 800, minWidth: 30 }} />
                </ListItemIcon>
                <ListItemText
                  primary={step.skill}
                  secondary={step.description || step.projectRecommendation || step.estimatedDuration || ''}
                  primaryTypographyProps={{ fontWeight: 700 }}
                />
                {step.priority && <Chip color={priorityColor[step.priority] || 'default'} label={step.priority} size="small" />}
              </ListItem>
            ))}
          </List>
        )}
        {roadmap.projectRecommendations?.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>Suggested projects</Typography>
            <Stack spacing={0.5}>
              {roadmap.projectRecommendations.slice(0, 4).map((p, i) => (
                <Typography key={i} variant="body2">• {p}</Typography>
              ))}
            </Stack>
          </Box>
        )}
        {roadmap.certificationRecommendations?.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>Recommended certifications</Typography>
            <Stack spacing={0.5}>
              {roadmap.certificationRecommendations.slice(0, 4).map((c, i) => (
                <Typography key={i} variant="body2">• {c}</Typography>
              ))}
            </Stack>
          </Box>
        )}
        {advice && (
          <Alert severity="success" sx={{ mt: 2 }}>
            {advice}
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}

export function StudentDashboardPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [savingRole, setSavingRole] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [analysisError, setAnalysisError] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const data = await dashboardService.getDashboardData()
      setDashboard(data)
      setAnalysisResult(data.lastAnalysis || null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleSaveRole = async (role) => {
    setSavingRole(true)
    try {
      const saved = await dashboardService.setTargetRole(role)
      setDashboard((prev) => ({ ...prev, targetRole: saved }))
    } finally {
      setSavingRole(false)
    }
  }

  const handleAnalyze = async () => {
    setAnalyzing(true)
    setAnalysisError('')
    try {
      const result = await dashboardService.runAnalysis()
      setAnalysisResult(result)
    } catch (err) {
      setAnalysisError(err?.response?.data?.detail || 'Analysis failed. Please try again.')
    } finally {
      setAnalyzing(false)
    }
  }

  const profile = dashboard?.profile || {
    name: user?.full_name || user?.email?.split('@')[0] || 'Student',
    role: 'Student',
  }
  const targetRole = dashboard?.targetRole || null
  const hasResume = Boolean(dashboard?.hasResume)
  const canAnalyze = hasResume && Boolean(targetRole)

  const skillGap = analysisResult?.skillGap || []
  const matchedSkills = analysisResult?.matchedSkills || []

  const greetingName = profile.name || user?.full_name || 'there'
  const subtitle = useMemo(() => {
    if (!hasResume) return 'Upload your resume to get started.'
    if (!targetRole) return 'Now set your target role so we can build your personalized plan.'
    if (!analysisResult) return 'Run the skill gap analysis to see your plan.'
    return `Here is your personalized plan for ${targetRole}.`
  }, [hasResume, targetRole, analysisResult])

  if (loading && !dashboard) {
    return (
      <Container maxWidth="lg" sx={{ py: 8, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    )
  }

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(180deg, rgba(76,87,232,0.05), rgba(76,87,232,0) 25%)', py: { xs: 2.5, sm: 3.5, md: 5 } }}>
      <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="overline" color="text.secondary">Dashboard</Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, letterSpacing: '-0.05em' }}>
              Welcome, {greetingName}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 760 }}>
              {subtitle}
            </Typography>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <ResumeSummaryCard
                profile={profile}
                hasResume={hasResume}
                parsedSkills={dashboard?.parsedSkills || []}
                personalInfo={dashboard?.personalInfo || {}}
                resumeScore={dashboard?.resumeScore}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TargetRoleCard targetRole={targetRole} onSave={handleSaveRole} saving={savingRole} />
            </Grid>

            <Grid item xs={12} md={6}>
              <SkillGapCard
                skillGap={skillGap}
                matchedSkills={matchedSkills}
                loading={analyzing}
                onAnalyze={handleAnalyze}
                canAnalyze={canAnalyze}
                analysisError={analysisError}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <RoadmapCard roadmap={analysisResult?.roadmap || null} />
            </Grid>
          </Grid>

          {analysisResult && (
            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button component={RouterLink} to="/job-matching" variant="outlined">Browse matched jobs</Button>
              <Button component={RouterLink} to="/resume-analysis" variant="contained">View full resume analysis</Button>
            </Stack>
          )}
        </Stack>
      </Container>
    </Box>
  )
}
