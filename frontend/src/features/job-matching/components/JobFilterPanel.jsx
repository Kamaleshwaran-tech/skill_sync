import { FilterList } from '@mui/icons-material'
import {
  Box,
  Card,
  CardContent,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Slider,
  Stack,
  Typography,
} from '@mui/material'

const locationOptions = ['All', 'Remote', 'Hybrid', 'On-site']
const typeOptions = ['All', 'Full-time', 'Contract', 'Part-time']
const experienceOptions = ['All', 'Entry', 'Mid', 'Mid-Senior', 'Senior']

export function JobFilterPanel({
  location,
  onLocationChange,
  jobType,
  onJobTypeChange,
  experienceLevel,
  onExperienceChange,
  salaryRange,
  onSalaryChange,
  remoteType,
  onRemoteTypeChange,
  minSalary = 0,
  maxSalary = 200000,
}) {
  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
        <Stack spacing={2.5}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <FilterList color="primary" />
            <Typography variant="h6" sx={{ fontWeight: 800 }}>
              Filters
            </Typography>
          </Stack>

          <Divider />

          <FormControl fullWidth size="small">
            <InputLabel>Location</InputLabel>
            <Select value={location} label="Location" onChange={(event) => onLocationChange(event.target.value)}>
              {locationOptions.map((option) => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth size="small">
            <InputLabel>Remote / On-site / Hybrid</InputLabel>
            <Select value={remoteType} label="Remote / On-site / Hybrid" onChange={(event) => onRemoteTypeChange(event.target.value)}>
              {['All', 'Remote', 'Hybrid', 'On-site'].map((option) => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth size="small">
            <InputLabel>Job type</InputLabel>
            <Select value={jobType} label="Job type" onChange={(event) => onJobTypeChange(event.target.value)}>
              {typeOptions.map((option) => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth size="small">
            <InputLabel>Experience level</InputLabel>
            <Select value={experienceLevel} label="Experience level" onChange={(event) => onExperienceChange(event.target.value)}>
              {experienceOptions.map((option) => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Salary range: ${salaryRange[0].toLocaleString()} - ${salaryRange[1].toLocaleString()}
            </Typography>
            <Slider
              value={salaryRange}
              onChange={(_, nextValue) => onSalaryChange(nextValue)}
              min={minSalary}
              max={maxSalary}
              valueLabelDisplay="auto"
              step={5000}
              disableSwap
            />
          </Box>
        </Stack>
      </CardContent>
    </Card>
  )
}
