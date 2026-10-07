import {
  Business,
  CalendarToday,
  CheckCircle,
  LocationOn,
  OpenInNew,
  Paid,
  Work,
} from '@mui/icons-material'
import {
  Box,
  Button,
  Chip,
  Divider,
  Grid,
  Stack,
  Typography,
} from '@mui/material'
import { JobMatchScore } from './JobMatchScore'
import { MatchedSkills } from './MatchedSkills'
import { MissingSkills } from './MissingSkills'

export function JobDetails({ job }) {
  if (!job) {
    return null
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 3 }, border: '1px solid', borderColor: 'divider', borderRadius: 3, bgcolor: 'background.paper', overflow: 'hidden' }}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" spacing={2}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>{job.title}</Typography>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mt: 1, color: 'text.secondary' }}>
            <Business fontSize="small" />
            <Typography variant="subtitle1">{job.company}</Typography>
          </Stack>
        </Box>
        <JobMatchScore score={job.matchPercentage ?? job.matchScore ?? 0} large />
      </Stack>

      <Grid container spacing={2} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Stack direction="row" spacing={1} alignItems="center" color="text.secondary">
            <LocationOn fontSize="small" />
            <Typography variant="body2">{job.location}</Typography>
          </Stack>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Stack direction="row" spacing={1} alignItems="center" color="text.secondary">
            <Work fontSize="small" />
            <Typography variant="body2">{job.jobType}</Typography>
          </Stack>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Stack direction="row" spacing={1} alignItems="center" color="text.secondary">
            <Paid fontSize="small" />
            <Typography variant="body2">{job.salary || 'Salary not disclosed'}</Typography>
          </Stack>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Stack direction="row" spacing={1} alignItems="center" color="text.secondary">
            <CalendarToday fontSize="small" />
            <Typography variant="body2">Posted {job.postedDate}</Typography>
          </Stack>
        </Grid>
      </Grid>

      <Divider sx={{ my: 3 }} />

      <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5 }}>Required skills</Typography>
      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mb: 3 }}>
        {job.requiredSkills?.map((skill) => (
          <Chip key={skill} label={skill} variant="outlined" />
        ))}
      </Stack>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <MatchedSkills skills={job.matchedSkills} />
        </Grid>
        <Grid item xs={12} md={6}>
          <MissingSkills skills={job.missingSkills} />
        </Grid>
      </Grid>

      <Divider sx={{ my: 3 }} />

      <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5 }}>Why this role matches</Typography>
      <Stack spacing={1.5}>
        {job.matchedSkills?.map((skill) => (
          <Stack key={skill} direction="row" spacing={1} alignItems="center">
            <CheckCircle color="success" fontSize="small" />
            <Typography variant="body2">Strong alignment for {skill}</Typography>
          </Stack>
        ))}
      </Stack>

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mt: 4 }}>
        <Button component="a" href={job.url || undefined} target="_blank" rel="noreferrer" variant="contained" size="large" endIcon={<OpenInNew />} disabled={!job.url}>
          Apply on company site
        </Button>
        <Button variant="outlined" size="large">
          Save job
        </Button>
      </Stack>
    </Box>
  )
}
