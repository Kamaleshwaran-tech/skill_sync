import { Business, CalendarToday, LocationOn, OpenInNew, Work } from '@mui/icons-material'
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  Stack,
  Typography,
} from '@mui/material'
import { JobMatchScore } from './JobMatchScore'
import { MatchedSkills } from './MatchedSkills'
import { MissingSkills } from './MissingSkills'
import { SavedJobButton } from './SavedJobButton'

export function JobCard({ job, isSaved, onToggleSave, onViewDetails }) {
  if (!job) {
    return null
  }

  return (
    <Card
      elevation={0}
    sx={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 3,
        transition: 'box-shadow 0.2s ease',
        '&:hover': {
          boxShadow: 3,
        },
      }}
    >
      <CardContent sx={{ p: { xs: 2, sm: 2.5 }, display: 'flex', flexDirection: 'column', flex: 1, boxSizing: 'border-box' }}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={1}>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.4, minHeight: 44 }}>
              {job.title}
            </Typography>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mt: 0.75, color: 'text.secondary' }}>
              <Business fontSize="small" />
              <Typography variant="body2">{job.company}</Typography>
            </Stack>
          </Box>
          <SavedJobButton isSaved={isSaved} onToggleSave={onToggleSave} ariaLabel={`save ${job.title}`} />
        </Stack>

        <Stack spacing={1.25} sx={{ mt: 2 }}>
          <Stack direction="row" spacing={1} alignItems="center" color="text.secondary">
            <LocationOn fontSize="small" />
            <Typography variant="body2">{job.location}</Typography>
          </Stack>

          <Stack direction="row" spacing={1} alignItems="center" color="text.secondary">
            <Work fontSize="small" />
            <Typography variant="body2">{job.jobType}</Typography>
          </Stack>

          {job.salary && (
            <Typography variant="body2" color="text.secondary">
              {job.salary}
            </Typography>
          )}

          <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={1}>
            <Typography variant="caption" color="text.secondary">
              <CalendarToday fontSize="inherit" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
              {job.postedDate}
            </Typography>
            <JobMatchScore score={job.matchPercentage ?? job.matchScore ?? 0} />
          </Stack>
        </Stack>

        <Divider sx={{ my: 2 }} />

        <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mb: 2, minHeight: 32, alignContent: 'flex-start' }}>
          {job.requiredSkills?.slice(0, 4).map((skill) => (
            <Chip key={skill} label={skill} size="small" variant="outlined" />
          ))}
        </Stack>


        <MatchedSkills skills={job.matchedSkills} />
        <Box sx={{ mt: 1.5 }}>
          <MissingSkills skills={job.missingSkills} />
        </Box>

        <Stack direction="row" spacing={1.5} sx={{ mt: 'auto', pt: 2 }}>
          <Button
            fullWidth
            variant="outlined"
            onClick={() => onViewDetails?.(job)}
          >
            Details
          </Button>
          <Button
            fullWidth
            variant="contained"
            endIcon={<OpenInNew />}
            component={job.url ? 'a' : 'button'}
            href={job.url || undefined}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => {
              if (job.url) {
                e.stopPropagation()
              } else {
                onViewDetails?.(job)
              }
            }}
          >
            Apply
          </Button>
        </Stack>
      </CardContent>
    </Card>
  )
}
