import {
  CheckCircle,
  ChevronRight,
  PlayArrow,
  School,
  Timer,
} from '@mui/icons-material'
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Button,
  Chip,
  Divider,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material'

const statusConfig = {
  completed: { label: 'Completed', color: 'success' },
  in_progress: { label: 'In progress', color: 'primary' },
  not_started: { label: 'Not started', color: 'warning' },
}

export function RoadmapItemCard({ item, onToggleStatus, expanded, onToggleExpanded }) {
  const status = statusConfig[item.completionStatus] || statusConfig.not_started

  return (
    <Accordion expanded={expanded} onChange={onToggleExpanded} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3, overflow: 'hidden' }}>
      <AccordionSummary expandIcon={<ChevronRight />} sx={{ px: 2.5 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ xs: 'flex-start', sm: 'center' }} sx={{ width: '100%' }}>
          <Box sx={{ flex: 1 }}>
            <Stack direction="row" alignItems="center" spacing={1}>
              <Typography variant="h6" sx={{ fontWeight: 800 }}>
                {item.skill}
              </Typography>
              <Chip label={item.priority} size="small" color={item.priority === 'Critical' ? 'error' : item.priority === 'High' ? 'warning' : 'primary'} variant="outlined" />
            </Stack>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.75 }}>
              {item.description}
            </Typography>
          </Box>

          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
            <Chip label={status.label} color={status.color} size="small" variant="outlined" />
            <Chip label={item.difficulty} size="small" variant="filled" />
            <Chip label={item.estimatedDuration} size="small" variant="outlined" />
          </Stack>
        </Stack>
      </AccordionSummary>

      <AccordionDetails sx={{ px: { xs: 2, sm: 2.5 }, pb: 2.5 }}>
        <Stack spacing={2}>
          <LinearProgress
            variant="determinate"
            value={item.completionStatus === 'completed' ? 100 : item.completionStatus === 'in_progress' ? 60 : 10}
            sx={{ height: 8, borderRadius: 999 }}
          />

          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: 'repeat(1, 1fr)', sm: 'repeat(3, 1fr)' }, gap: 1.5 }}>
            <Box>
              <Typography variant="caption" color="text.secondary">Difficulty</Typography>
              <Typography variant="body1" sx={{ fontWeight: 700 }}>{item.difficulty}</Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">Estimated duration</Typography>
              <Typography variant="body1" sx={{ fontWeight: 700 }}>{item.estimatedDuration}</Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">Prerequisites</Typography>
              <Typography variant="body1" sx={{ fontWeight: 700 }}>{item.prerequisites.join(', ')}</Typography>
            </Box>
          </Box>

          <Divider />

          <Box>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
              <School fontSize="small" color="primary" />
              <Typography variant="subtitle2" sx={{ fontWeight: 800 }}>Learning resources</Typography>
            </Stack>
            <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
              {item.resources.map((resource) => (
                <Chip key={resource} label={resource} variant="outlined" size="small" />
              ))}
            </Stack>
          </Box>

          <Box>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
              <Timer fontSize="small" color="primary" />
              <Typography variant="subtitle2" sx={{ fontWeight: 800 }}>Project recommendation</Typography>
            </Stack>
            <Typography variant="body2" color="text.secondary">{item.projectRecommendation}</Typography>
          </Box>

          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'flex-end', gap: 1.5 }}>
            <Button
              variant={item.completionStatus === 'not_started' ? 'contained' : 'outlined'}
              startIcon={item.completionStatus === 'completed' ? <CheckCircle /> : <PlayArrow />}
              onClick={() => onToggleStatus(item.id, item.completionStatus === 'completed' ? 'not_started' : 'in_progress')}
              fullWidth={{ xs: true, sm: false }}
            >
              {item.completionStatus === 'completed' ? 'Mark as started' : 'Mark as in progress'}
            </Button>
            <Button
              variant={item.completionStatus === 'completed' ? 'contained' : 'outlined'}
              color="success"
              startIcon={<CheckCircle />}
              onClick={() => onToggleStatus(item.id, 'completed')}
              fullWidth={{ xs: true, sm: false }}
            >
              Mark as completed
            </Button>
          </Box>
        </Stack>
      </AccordionDetails>
    </Accordion>
  )
}
