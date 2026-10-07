import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Box, Card, CardContent, Chip, Divider, LinearProgress, Stack, Typography } from '@mui/material'

export function SkillPillList({ title, items, color = 'primary' }) {
  return (
    <Box>
      <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
        {title}
      </Typography>
      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
        {items.map((item) => (
          <Chip key={item} label={item} color={color} variant="outlined" size="small" />
        ))}
      </Stack>
    </Box>
  )
}

export function SummaryStatCard({ label, value, tone = 'primary' }) {
  return (
    <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
      <CardContent sx={{ p: 2.5 }}>
        <Typography variant="overline" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h5" sx={{ fontWeight: 800, mt: 0.75, color: `${tone}.main` }}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  )
}

export function CurrentVsRequiredChart({ data }) {
  return (
    <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
      <CardContent sx={{ p: { xs: 2, sm: 2.5 } }}>
        <Typography variant="h6" sx={{ fontWeight: 800, mb: 1.5 }}>
          Current vs required proficiency
        </Typography>
        <Box sx={{ width: '100%', height: { xs: 240, sm: 280 } }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="skill" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="current" name="Current" fill="#5c6efb" radius={[6, 6, 0, 0]} />
              <Bar dataKey="required" name="Required" fill="#1e88e5" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  )
}

export function SkillDemandChart({ data }) {
  return (
    <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
      <CardContent sx={{ p: { xs: 2, sm: 2.5 } }}>
        <Typography variant="h6" sx={{ fontWeight: 800, mb: 1.5 }}>
          Skill demand
        </Typography>
        <Box sx={{ width: '100%', height: { xs: 240, sm: 280 } }}>
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={data} outerRadius="70%">
              <PolarGrid />
              <PolarAngleAxis dataKey="skill" tick={{ fontSize: 11 }} />
              <Tooltip />
              <Radar name="Demand" dataKey="demand" stroke="#6d4c41" fill="#6d4c41" fillOpacity={0.4} />
            </RadarChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  )
}

export function SkillPriorityChart({ data }) {
  const colors = ['#7c4dff', '#26a69a', '#ffb300', '#ff7043', '#5c6efb']

  return (
    <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
      <CardContent sx={{ p: { xs: 2, sm: 2.5 } }}>
        <Typography variant="h6" sx={{ fontWeight: 800, mb: 1.5 }}>
          Skill priority
        </Typography>
        <Box sx={{ width: '100%', height: { xs: 240, sm: 280 } }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 10, left: 0, right: 15, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
              <YAxis dataKey="skill" type="category" width={80} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="priority" name="Priority" radius={[0, 6, 6, 0]}>
                {data.map((entry, index) => (
                  <Cell key={entry.skill} fill={colors[index % colors.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  )
}

export function MissingSkillCard({ skill }) {
  return (
    <Card elevation={0} sx={{ height: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
      <CardContent sx={{ p: { xs: 2, sm: 2.5 } }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
          <Typography variant="h6" sx={{ fontWeight: 800 }}>
            {skill.name}
          </Typography>
          <Chip
            label={skill.priority}
            color={skill.priority === 'Critical' ? 'error' : skill.priority === 'High' ? 'warning' : 'primary'}
            size="small"
            variant="outlined"
            sx={{ fontWeight: 700 }}
          />
        </Stack>

        <Stack spacing={2} sx={{ mt: 2 }}>
          <Box>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="body2" color="text.secondary">Gap percentage</Typography>
              <Typography variant="body2" sx={{ fontWeight: 700 }}>{skill.gapPercentage}%</Typography>
            </Stack>
            <LinearProgress variant="determinate" value={skill.gapPercentage} color="warning" sx={{ mt: 1, height: 8, borderRadius: 999 }} />
          </Box>

          <Divider />

          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: 'repeat(2, 1fr)', sm: 'repeat(4, 1fr)' }, gap: 1.5 }}>
            <Box>
              <Typography variant="caption" color="text.secondary">Industry demand</Typography>
              <Typography variant="body1" sx={{ fontWeight: 700 }}>{skill.industryDemand}%</Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">Current</Typography>
              <Typography variant="body1" sx={{ fontWeight: 700 }}>{skill.currentProficiency}%</Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">Required</Typography>
              <Typography variant="body1" sx={{ fontWeight: 700 }}>{skill.requiredProficiency}%</Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">Learn time</Typography>
              <Typography variant="body1" sx={{ fontWeight: 700 }}>{skill.recommendedLearningTime}</Typography>
            </Box>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary">Estimated learning difficulty</Typography>
            <Typography variant="body2" sx={{ fontWeight: 700, mt: 0.5 }}>{skill.difficulty}</Typography>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  )
}
