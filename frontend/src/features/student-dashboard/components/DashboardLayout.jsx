import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Divider,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Paper,
  Skeleton,
  Stack,
  Typography,
  alpha,
} from '@mui/material'
import Grid from '@mui/material/Grid'
import {
  ArrowForward,
  AutoAwesome,
  CheckCircle,
  Insights,
  School,
  Timeline,
  TrendingUp,
  WorkspacePremium,
} from '@mui/icons-material'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export function DashboardLayout({ children, title, subtitle, actions }) {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        background:
          'linear-gradient(180deg, rgba(76, 87, 232, 0.04), rgba(76, 87, 232, 0) 22%), rgba(251, 251, 252, 0.96)',
        py: { xs: 3, md: 5 },
      }}
    >
      <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
        <Stack spacing={3}>
          {(title || subtitle || actions) && (
            <Stack
              direction={{ xs: 'column', md: 'row' }}
              alignItems={{ xs: 'flex-start', md: 'center' }}
              justifyContent="space-between"
              spacing={2}
            >
              <Box>
                {title && (
                  <Typography variant="h4" sx={{ fontWeight: 800, letterSpacing: '-0.04em' }}>
                    {title}
                  </Typography>
                )}
                {subtitle && (
                  <Typography variant="body2" color="text.secondary">
                    {subtitle}
                  </Typography>
                )}
              </Box>
              {actions}
            </Stack>
          )}
          {children}
        </Stack>
      </Container>
    </Box>
  )
}

export function DashboardHeader({ name, role, lastUpdated, focus }) {
  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 2.5, md: 3.5 },
        borderRadius: 4,
        border: '1px solid',
        borderColor: 'divider',
        background:
          'linear-gradient(135deg, rgba(76, 87, 232, 0.10), rgba(109, 211, 232, 0.10)), rgba(255,255,255,0.82)',
      }}
    >
      <Grid container spacing={3} alignItems="center">
        <Grid item xs={12} md={8}>
          <Stack spacing={1.5}>
            <Chip
              size="small"
              label="Student dashboard"
              color="primary"
              sx={{ width: 'fit-content', fontWeight: 700 }}
            />
            <Typography variant="h3" sx={{ fontWeight: 800, letterSpacing: '-0.05em' }}>
              Welcome back, {name}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {role} • {lastUpdated}
            </Typography>
          </Stack>
        </Grid>
        <Grid item xs={12} md={4}>
          <Stack spacing={1.5} alignItems={{ xs: 'flex-start', md: 'flex-end' }}>
            <Chip
              icon={<TrendingUp fontSize="small" />}
              label={`Focus: ${focus}`}
              variant="outlined"
            />
            <Typography variant="body2" color="text.secondary">
              You are moving toward your target role faster than your last review cycle.
            </Typography>
          </Stack>
        </Grid>
      </Grid>
    </Paper>
  )
}

export function MetricCard({ label, value, trend, icon: Icon, tone = 'primary' }) {
  const toneStyles = {
    primary: { color: '#4c57e8', background: '#e9ebff' },
    secondary: { color: '#087e98', background: '#dcf6fb' },
    success: { color: '#17834d', background: '#dff7e9' },
    warning: { color: '#b7791f', background: '#fff4d5' },
  }

  const palette = toneStyles[tone] || toneStyles.primary

  return (
    <Card elevation={0} sx={{ height: '100%', borderColor: 'divider' }}>
      <CardContent sx={{ p: 2.25 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
          <Box
            sx={{
              width: 38,
              height: 38,
              borderRadius: 2,
              display: 'grid',
              placeItems: 'center',
              backgroundColor: alpha(palette.color, 0.12),
              color: palette.color,
            }}
          >
            {Icon ? <Icon fontSize="small" /> : <Insights fontSize="small" />}
          </Box>
          <Chip
            label={trend}
            size="small"
            sx={{
              backgroundColor: alpha(palette.color, 0.12),
              color: palette.color,
              border: 'none',
              fontWeight: 700,
            }}
          />
        </Stack>
        <Typography variant="h4" sx={{ mt: 2, fontWeight: 800, letterSpacing: '-0.05em' }}>
          {value}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
      </CardContent>
    </Card>
  )
}

export function CareerReadinessCard({ readiness }) {
  const overall = readiness.overall

  return (
    <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
      <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
        <Stack spacing={2.5}>
          <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={1}>
            <Box>
              <Typography variant="overline" color="text.secondary">
                Career readiness score
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 800 }}>
                Overall Readiness
              </Typography>
            </Box>
            <Chip label="Strong fit" color="success" variant="outlined" size="small" sx={{ fontWeight: 700 }} />
          </Stack>

          <Grid container spacing={{ xs: 2, md: 3 }} alignItems="center">
            <Grid item xs={12} sm={4} md={3.5}>
              <Box sx={{ display: 'grid', placeItems: 'center', py: { xs: 1, sm: 2 } }}>
                <Box sx={{ position: 'relative', display: 'grid', placeItems: 'center' }}>
                  <CircularProgress
                    variant="determinate"
                    value={overall}
                    size={135}
                    thickness={5.5}
                    sx={{ color: 'primary.main' }}
                  />
                  <Box
                    sx={{
                      position: 'absolute',
                      inset: 0,
                      display: 'grid',
                      placeItems: 'center',
                    }}
                  >
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h3" sx={{ fontWeight: 800, lineHeight: 1 }}>
                        {overall}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 700 }}>
                        / 100
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </Box>
            </Grid>

            <Grid item xs={12} sm={8} md={8.5}>
              <Grid container spacing={1.5}>
                {readiness.metrics.map((metric) => (
                  <Grid key={metric.label} item xs={6} sm={6} md={3}>
                    <MetricCard
                      label={metric.label}
                      value={`${metric.value}`}
                      trend={metric.trend}
                      tone={metric.label.includes('Technical') ? 'primary' : metric.label.includes('Industry') ? 'secondary' : metric.label.includes('Resume') ? 'success' : 'warning'}
                    />
                  </Grid>
                ))}
              </Grid>
            </Grid>
          </Grid>
        </Stack>
      </CardContent>
    </Card>
  )
}

export function CareerMatchCard({ role, match, skillGapCount, focus }) {
  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2.5}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={2}>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                {role}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {focus}
              </Typography>
            </Box>
            <Chip
              label={`${match}% match`}
              color="primary"
              sx={{ fontWeight: 700, borderRadius: 2 }}
            />
          </Stack>

          <Divider />

          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="body2" color="text.secondary">
              Skill gaps
            </Typography>
            <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
              {skillGapCount}
            </Typography>
          </Stack>

          <Button
            endIcon={<ArrowForward />}
            variant="text"
            sx={{ alignSelf: 'flex-start', px: 0, fontWeight: 700 }}
          >
            View details
          </Button>
        </Stack>
      </CardContent>
    </Card>
  )
}

export function SkillOverview({ skillOverview }) {
  const groups = [
    { title: 'Current skills', items: skillOverview.current },
    { title: 'Strong skills', items: skillOverview.strong },
    { title: 'Developing skills', items: skillOverview.developing },
    { title: 'Missing skills', items: skillOverview.missing },
  ]

  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2.5}>
          <Typography variant="h5" sx={{ fontWeight: 800 }}>
            Skill Overview
          </Typography>

          <Grid container spacing={2}>
            {groups.map((group) => (
              <Grid key={group.title} item xs={12} sm={6}>
                <Box
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    backgroundColor: 'background.paper',
                    height: '100%',
                  }}
                >
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5 }}>
                    {group.title}
                  </Typography>
                  <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                    {group.items.length ? (
                      group.items.map((skill) => (
                        <Chip
                          key={skill}
                          label={skill}
                          size="small"
                          variant={group.title === 'Missing skills' ? 'outlined' : 'filled'}
                          color={group.title === 'Missing skills' ? 'default' : 'primary'}
                          sx={{
                            fontWeight: 600,
                            backgroundColor:
                              group.title === 'Current skills'
                                ? 'rgba(76, 87, 232, 0.10)'
                                : group.title === 'Strong skills'
                                  ? 'rgba(23, 131, 77, 0.12)'
                                  : group.title === 'Developing skills'
                                    ? 'rgba(180, 108, 0, 0.12)'
                                    : 'rgba(128, 128, 128, 0.08)',
                          }}
                        />
                      ))
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No skills added yet.
                      </Typography>
                    )}
                  </Stack>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Stack>
      </CardContent>
    </Card>
  )
}

export function JobRecommendationCard({ job }) {
  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={2}>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                {job.title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {job.company}
              </Typography>
            </Box>
            <Chip label={`${job.match}% match`} color="success" />
          </Stack>

          <Typography variant="body2" color="text.secondary">
            {job.location}
          </Typography>

          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
            {job.requiredSkills.map((skill) => (
              <Chip key={skill} label={skill} size="small" variant="outlined" />
            ))}
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  )
}

export function SkillDemandChart({ data }) {
  return (
    <Card elevation={0} sx={{ height: '100%', width: '100%' }}>
      <CardContent sx={{ p: 2.5, height: '100%', boxSizing: 'border-box' }}>
        <Stack spacing={2.5} sx={{ width: '100%', minWidth: 0 }}>
          <Typography variant="h5" sx={{ fontWeight: 800 }}>
            Skill Demand
          </Typography>

          {!data?.length ? (
            <Box sx={{ minHeight: 280, display: 'grid', placeItems: 'center', textAlign: 'center', px: 2 }}>
              <Typography variant="body2" color="text.secondary">Skill demand will appear after your resume is analyzed.</Typography>
            </Box>
          ) : <Box sx={{ height: 280, minWidth: 0 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} margin={{ top: 12, right: 8, left: 0, bottom: 8 }}>
                <CartesianGrid vertical={false} strokeDasharray="3 3" />
                <XAxis dataKey="skill" tickLine={false} axisLine={false} fontSize={12} />
                <YAxis domain={[0, 100]} tickLine={false} axisLine={false} fontSize={12} />
                <Tooltip
                  cursor={{ fill: 'rgba(76, 87, 232, 0.08)' }}
                  formatter={(value) => [`${value}%`, 'Demand']}
                />
                <Bar dataKey="demand" radius={[8, 8, 0, 0]}>
                  {data.map((entry, index) => (
                    <Cell
                      key={entry.skill}
                      fill={index % 2 === 0 ? '#4c57e8' : '#6dd3e8'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Box>}
        </Stack>
      </CardContent>
    </Card>
  )
}

export function LearningProgressCard({ learningProgress }) {
  const completion = learningProgress.totalSkills > 0
    ? Math.round((learningProgress.completedSkills / learningProgress.totalSkills) * 100)
    : 0

  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2.5}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
            <Box>
              <Typography variant="overline" color="text.secondary">
                Learning progress
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 800 }}>
                {learningProgress.roadmap}
              </Typography>
            </Box>
            <Chip icon={<School />} label={`${completion}%`} color="primary" />
          </Stack>

          <Stack spacing={1.5}>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="body2" color="text.secondary">
                Completed skills
              </Typography>
              <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                {learningProgress.completedSkills} / {learningProgress.totalSkills}
              </Typography>
            </Stack>
            <LinearProgress variant="determinate" value={completion} sx={{ height: 10, borderRadius: 999 }} />
          </Stack>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <MetricCard
                label="Skills in progress"
                value={learningProgress.skillsInProgress}
                trend="Active"
                icon={Timeline}
                tone="secondary"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <MetricCard
                label="Next recommended skill"
                value={learningProgress.nextRecommendedSkill}
                trend="Next"
                icon={AutoAwesome}
                tone="warning"
              />
            </Grid>
          </Grid>
        </Stack>
      </CardContent>
    </Card>
  )
}

export function ProjectRecommendationCard({ project }) {
  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              {project.title}
            </Typography>
            <Chip label={project.difficulty} size="small" variant="outlined" />
          </Stack>

          <Typography variant="body2" color="text.secondary">
            {project.description}
          </Typography>

          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
            {project.stack.map((tech) => (
              <Chip key={tech} label={tech} size="small" color="primary" variant="outlined" />
            ))}
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  )
}

export function CertificationCard({ certification }) {
  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                {certification.title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {certification.provider}
              </Typography>
            </Box>
            <WorkspacePremium color="primary" />
          </Stack>

          <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
            <Typography variant="body2" color="text.secondary">
              Duration
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {certification.duration}
            </Typography>
          </Stack>

          <Chip label={`Relevance: ${certification.relevance}`} color="success" size="small" />
        </Stack>
      </CardContent>
    </Card>
  )
}

export function RecentActivity({ activityItems }) {
  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2.5}>
          <Typography variant="h5" sx={{ fontWeight: 800 }}>
            Recent Activity
          </Typography>

          <List disablePadding>
            {activityItems.map((item) => (
              <ListItem key={item.title} disablePadding sx={{ py: 1.25 }}>
                <Stack direction="row" spacing={1.5} alignItems="flex-start" sx={{ width: '100%' }}>
                  <Box
                    sx={{
                      width: 10,
                      height: 10,
                      borderRadius: '50%',
                      backgroundColor:
                        item.type === 'learning'
                          ? 'primary.main'
                          : item.type === 'resume'
                            ? 'secondary.main'
                            : item.type === 'project'
                              ? 'success.main'
                              : 'warning.main',
                      mt: 0.7,
                    }}
                  />
                  <ListItemText
                    primary={item.title}
                    secondary={item.time}
                    primaryTypographyProps={{ fontWeight: 600 }}
                    secondaryTypographyProps={{ color: 'text.secondary' }}
                  />
                </Stack>
              </ListItem>
            ))}
          </List>
        </Stack>
      </CardContent>
    </Card>
  )
}

export function DashboardEmptyState({ title, description }) {
  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3, textAlign: 'center' }}>
        <Stack spacing={1.5} alignItems="center">
          <Box
            sx={{
              width: 48,
              height: 48,
              display: 'grid',
              placeItems: 'center',
              borderRadius: '50%',
              backgroundColor: alpha('#4c57e8', 0.12),
              color: 'primary.main',
            }}
          >
            <CheckCircle />
          </Box>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            {title}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {description}
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  )
}

export function DashboardHeaderSkeleton() {
  return (
    <Card elevation={0}>
      <CardContent sx={{ p: 3 }}>
        <Stack spacing={2}>
          <Skeleton variant="text" width={120} height={28} />
          <Skeleton variant="text" width="55%" height={48} />
          <Skeleton variant="text" width="35%" height={24} />
        </Stack>
      </CardContent>
    </Card>
  )
}

export function CareerReadinessSkeleton() {
  return (
    <Card elevation={0}>
      <CardContent sx={{ p: 3 }}>
        <Stack spacing={3}>
          <Skeleton variant="text" width={180} height={24} />
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <Skeleton variant="circular" width={160} height={160} />
            </Grid>
            <Grid item xs={12} md={8}>
              <Grid container spacing={2}>
                {[1, 2, 3, 4].map((item) => (
                  <Grid key={item} item xs={6} sm={3}>
                    <Skeleton variant="rectangular" height={96} sx={{ borderRadius: 2 }} />
                  </Grid>
                ))}
              </Grid>
            </Grid>
          </Grid>
        </Stack>
      </CardContent>
    </Card>
  )
}

export function CareerMatchesSkeleton() {
  return (
    <Card elevation={0}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2}>
          <Skeleton variant="text" width={180} height={32} />
          {[1, 2, 3].map((item) => (
            <Skeleton key={item} variant="rectangular" height={140} sx={{ borderRadius: 2 }} />
          ))}
        </Stack>
      </CardContent>
    </Card>
  )
}

export function SkillOverviewSkeleton() {
  return (
    <Card elevation={0}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2}>
          <Skeleton variant="text" width={180} height={32} />
          <Grid container spacing={2}>
            {[1, 2, 3, 4].map((item) => (
              <Grid key={item} item xs={12} sm={6}>
                <Skeleton variant="rectangular" height={110} sx={{ borderRadius: 2 }} />
              </Grid>
            ))}
          </Grid>
        </Stack>
      </CardContent>
    </Card>
  )
}

export function JobRecommendationsSkeleton() {
  return (
    <Card elevation={0}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2}>
          <Skeleton variant="text" width={220} height={32} />
          {[1, 2, 3].map((item) => (
            <Skeleton key={item} variant="rectangular" height={140} sx={{ borderRadius: 2 }} />
          ))}
        </Stack>
      </CardContent>
    </Card>
  )
}

export function SkillDemandSkeleton() {
  return (
    <Card elevation={0}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2}>
          <Skeleton variant="text" width={140} height={32} />
          <Skeleton variant="rectangular" height={260} sx={{ borderRadius: 2 }} />
        </Stack>
      </CardContent>
    </Card>
  )
}

export function LearningProgressSkeleton() {
  return (
    <Card elevation={0}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2}>
          <Skeleton variant="text" width={200} height={30} />
          <Skeleton variant="rectangular" height={18} sx={{ borderRadius: 999 }} />
          <Grid container spacing={2}>
            {[1, 2].map((item) => (
              <Grid key={item} item xs={12} sm={6}>
                <Skeleton variant="rectangular" height={90} sx={{ borderRadius: 2 }} />
              </Grid>
            ))}
          </Grid>
        </Stack>
      </CardContent>
    </Card>
  )
}

export function ProjectsSkeleton() {
  return (
    <Card elevation={0}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2}>
          <Skeleton variant="text" width={180} height={32} />
          {[1, 2, 3].map((item) => (
            <Skeleton key={item} variant="rectangular" height={120} sx={{ borderRadius: 2 }} />
          ))}
        </Stack>
      </CardContent>
    </Card>
  )
}

export function CertificationsSkeleton() {
  return (
    <Card elevation={0}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2}>
          <Skeleton variant="text" width={200} height={32} />
          {[1, 2, 3].map((item) => (
            <Skeleton key={item} variant="rectangular" height={120} sx={{ borderRadius: 2 }} />
          ))}
        </Stack>
      </CardContent>
    </Card>
  )
}

export function RecentActivitySkeleton() {
  return (
    <Card elevation={0}>
      <CardContent sx={{ p: 2.5 }}>
        <Stack spacing={2}>
          <Skeleton variant="text" width={180} height={32} />
          {[1, 2, 3, 4].map((item) => (
            <Skeleton key={item} variant="text" width="100%" height={28} />
          ))}
        </Stack>
      </CardContent>
    </Card>
  )
}
