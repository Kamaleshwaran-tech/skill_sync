import {
  Close,
  Tune,
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
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  Drawer,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import { useEffect, useMemo, useState } from 'react'

import { JobCard } from '@/features/job-matching/components/JobCard'
import { JobDetails } from '@/features/job-matching/components/JobDetails'
import { JobFilterPanel } from '@/features/job-matching/components/JobFilterPanel'
import { JobSearchBar } from '@/features/job-matching/components/JobSearchBar'
import { jobMatchingService } from '@/features/job-matching/services/jobMatchingService'

const getSalaryValue = (salaryText) => {
  const numbers = (salaryText || '').match(/\d+/g) || []
  if (!numbers.length) {
    return 0
  }
  return Math.max(...numbers.map(Number)) * 1000
}

const getPostedOrderValue = (postedDate) => {
  const numberMatch = (postedDate || '').match(/\d+/)
  return numberMatch ? Number(numberMatch[0]) : 99
}

function JobMatchingLoadingState() {
  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
      <CardContent sx={{ p: 4, textAlign: 'center' }}>
        <Stack spacing={2} alignItems="center">
          <CircularProgress />
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            Loading matched jobs...
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Preparing personalized opportunities based on your profile.
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  )
}

function JobMatchingEmptyState({ onReset }) {
  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
      <CardContent sx={{ p: 4, textAlign: 'center' }}>
        <Stack spacing={2} alignItems="center">
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            No jobs match your filters
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 450 }}>
            Try broadening your location, salary range, or experience settings to see more opportunities.
          </Typography>
          {onReset && (
            <Button variant="outlined" size="small" onClick={onReset}>
              Reset Filters
            </Button>
          )}
        </Stack>
      </CardContent>
    </Card>
  )
}

function JobMatchingErrorState() {
  return (
    <Alert severity="error" sx={{ borderRadius: 3 }}>
      We could not load fresh job matches right now. Please try again in a moment.
    </Alert>
  )
}

export function JobMatchingPage() {
  const theme = useTheme()
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg'))
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchValue, setSearchValue] = useState('')
  const [location, setLocation] = useState('All')
  const [remoteType, setRemoteType] = useState('All')
  const [jobType, setJobType] = useState('All')
  const [experienceLevel, setExperienceLevel] = useState('All')
  const [salaryRange, setSalaryRange] = useState([0, 200000])
  const [sortBy, setSortBy] = useState('match')
  const [selectedJobId, setSelectedJobId] = useState(null)
  const [savedJobs, setSavedJobs] = useState(() => new Set())
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false)
  const [isMobileDetailOpen, setIsMobileDetailOpen] = useState(false)
  const [isResumeMatched, setIsResumeMatched] = useState(false)
  const [hasError, setHasError] = useState(false)
  const [debouncedSearchValue, setDebouncedSearchValue] = useState('')
  const viewState = loading ? 'loading' : hasError ? 'error' : 'ready'

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedSearchValue(searchValue), 400)
    return () => window.clearTimeout(timer)
  }, [searchValue])

  useEffect(() => {
    let isMounted = true
    setHasError(false)
    jobMatchingService.getJobs({ search: debouncedSearchValue || undefined, location: location === 'All' ? undefined : location })
      .then((data) => {
        if (isMounted) {
          const list = Array.isArray(data) ? data : []
          setJobs(list)
          if (list.length > 0) {
            setSelectedJobId(list[0].id)
            setIsResumeMatched(list.some((job) => job.matchPercentage > 0 || job.matchedSkills?.length > 0 || job.missingSkills?.length > 0))
          } else {
            setSelectedJobId(null)
            setIsResumeMatched(false)
          }
        }
      })
      .catch((err) => {
        console.error('Failed to load job matches:', err)
        if (isMounted) {
          setJobs([])
          setHasError(true)
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false)
      })
    return () => {
      isMounted = false
    }
  }, [debouncedSearchValue, location])

  const normalizedJobs = useMemo(
    () =>
      jobs.map((job) => ({
        ...job,
        matchScore: job.matchPercentage ?? job.matchScore ?? 0,
      })),
    [jobs],
  )

  const activeFilterCount = useMemo(() => {
    let count = 0
    if (location !== 'All') count++
    if (remoteType !== 'All') count++
    if (jobType !== 'All') count++
    if (experienceLevel !== 'All') count++
    if (salaryRange[0] > 0 || salaryRange[1] < 200000) count++
    return count
  }, [experienceLevel, jobType, location, remoteType, salaryRange])

  const handleResetFilters = () => {
    setLocation('All')
    setRemoteType('All')
    setJobType('All')
    setExperienceLevel('All')
    setSalaryRange([0, 200000])
    setSearchValue('')
  }

  const filteredJobs = useMemo(() => {
    const query = searchValue.trim().toLowerCase()

    return normalizedJobs
      .filter((job) => {
        const haystack = [job.title, job.company, job.location, job.remoteType, job.jobType, ...(job.requiredSkills || [])]
          .join(' ')
          .toLowerCase()

        const matchesSearch = !query || haystack.includes(query)
        const matchesLocation = location === 'All' || job.location.toLowerCase().includes(location.toLowerCase()) || job.remoteType === location
        const matchesRemoteType = remoteType === 'All' || job.remoteType === remoteType
        const matchesJobType = jobType === 'All' || job.jobType === jobType
        const matchesExperience = experienceLevel === 'All' || !job.experienceLevel || job.experienceLevel === experienceLevel || (experienceLevel === 'Mid' && job.experienceLevel === 'Mid-Senior')
        const salaryValue = getSalaryValue(job.salary)
        const matchesSalary = salaryValue === 0 || (salaryValue >= salaryRange[0] && salaryValue <= salaryRange[1])

        return matchesSearch && matchesLocation && matchesRemoteType && matchesJobType && matchesExperience && matchesSalary
      })
      .sort((a, b) => {
        if (sortBy === 'newest') {
          return getPostedOrderValue(a.postedDate) - getPostedOrderValue(b.postedDate)
        }
        if (sortBy === 'salary') {
          return getSalaryValue(b.salary) - getSalaryValue(a.salary)
        }
        return b.matchScore - a.matchScore
      })
  }, [experienceLevel, jobType, location, normalizedJobs, remoteType, salaryRange, searchValue, sortBy])

  const selectedJob = filteredJobs.find((job) => job.id === selectedJobId) || filteredJobs[0] || null

  const handleToggleSave = (jobId) => {
    setSavedJobs((currentSet) => {
      const nextSet = new Set(currentSet)
      if (nextSet.has(jobId)) {
        nextSet.delete(jobId)
      } else {
        nextSet.add(jobId)
      }
      return nextSet
    })
  }

  const handleSelectJob = (job) => {
    setSelectedJobId(job.id)
    if (!isDesktop) {
      setIsMobileDetailOpen(true)
    }
  }

  return (
    <Box
      sx={{
        py: { xs: 2.5, sm: 3.5, md: 5 },
        background: 'linear-gradient(180deg, rgba(76,87,232,0.04), rgba(76,87,232,0) 30%)',
        minHeight: '100vh',
      }}
    >
      <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
        <Stack spacing={3}>
          {/* Header */}
          <Stack spacing={1}>
            <Typography variant="overline" color="text.secondary">
              Career opportunities
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, letterSpacing: '-0.04em' }}>
              Live job matching
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 700 }}>
              Browse AI-matched opportunities, compare your skill alignment, and identify target positions.
            </Typography>
          </Stack>

          {/* Search & Quick Action Bar */}
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ xs: 'stretch', sm: 'center' }}>
            <Box sx={{ flex: 1 }}>
              <JobSearchBar value={searchValue} onChange={setSearchValue} />
            </Box>

            <Stack direction="row" spacing={1.5} alignItems="center" justifyContent="space-between">
              <Button
                variant={activeFilterCount > 0 ? 'contained' : 'outlined'}
                startIcon={<Tune />}
                onClick={() => setIsMobileFilterOpen(true)}
                sx={{
                  display: { lg: 'none' },
                  whiteSpace: 'nowrap',
                  borderRadius: 2,
                  py: 1,
                  px: 2,
                }}
              >
                Filters {activeFilterCount > 0 ? `(${activeFilterCount})` : ''}
              </Button>

              <FormControl size="small" sx={{ minWidth: 150, flex: { xs: 1, sm: 'none' } }}>
                <InputLabel>Sort by</InputLabel>
                <Select value={sortBy} label="Sort by" onChange={(event) => setSortBy(event.target.value)}>
                  <MenuItem value="match">Best match</MenuItem>
                  <MenuItem value="newest">Newest</MenuItem>
                  <MenuItem value="salary">Highest Salary</MenuItem>
                </Select>
              </FormControl>
            </Stack>
          </Stack>

          {/* Quick Filter Pills */}
          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" alignItems="center">
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 700, mr: 0.5 }}>
              Quick Filters:
            </Typography>
            <Chip
              label="All Locations"
              size="small"
              variant={location === 'All' ? 'filled' : 'outlined'}
              color={location === 'All' ? 'primary' : 'default'}
              onClick={() => setLocation('All')}
            />
            <Chip
              label="Remote Only"
              size="small"
              variant={remoteType === 'Remote' ? 'filled' : 'outlined'}
              color={remoteType === 'Remote' ? 'primary' : 'default'}
              onClick={() => setRemoteType(remoteType === 'Remote' ? 'All' : 'Remote')}
            />
            <Chip
              label="Full-time"
              size="small"
              variant={jobType === 'Full-time' ? 'filled' : 'outlined'}
              color={jobType === 'Full-time' ? 'primary' : 'default'}
              onClick={() => setJobType(jobType === 'Full-time' ? 'All' : 'Full-time')}
            />
            {activeFilterCount > 0 && (
              <Chip
                label="Clear All"
                size="small"
                onDelete={handleResetFilters}
                color="error"
                variant="outlined"
              />
            )}
          </Stack>

          {!isResumeMatched && !loading && (
            <Alert severity="info" sx={{ borderRadius: 3 }}>
              Upload and analyze a resume to see personalized skill-match scores and skill gaps for these live jobs.
            </Alert>
          )}

          {/* Main Content Area */}
          {viewState === 'loading' ? (
            <JobMatchingLoadingState />
          ) : viewState === 'error' ? (
            <JobMatchingErrorState />
          ) : !filteredJobs.length ? (
            <JobMatchingEmptyState onReset={handleResetFilters} />
          ) : (
            <Grid container spacing={3} alignItems="stretch">
              {/* Desktop Filters Column */}
              <Grid item xs={12} lg={3.5} sx={{ display: { xs: 'none', lg: 'block' }, alignSelf: 'flex-start', position: 'sticky', top: 90 }}>
                <JobFilterPanel
                  location={location}
                  onLocationChange={setLocation}
                  jobType={jobType}
                  onJobTypeChange={setJobType}
                  experienceLevel={experienceLevel}
                  onExperienceChange={setExperienceLevel}
                  salaryRange={salaryRange}
                  onSalaryChange={setSalaryRange}
                  remoteType={remoteType}
                  onRemoteTypeChange={setRemoteType}
                />
              </Grid>

              {/* Job Cards Column */}
              <Grid item xs={12} lg={isDesktop && selectedJob ? 4.5 : 8.5} sx={{ minWidth: 0 }}>
                <Stack spacing={2}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Showing <strong>{filteredJobs.length}</strong> matching positions
                  </Typography>

                  <Stack spacing={2}>
                    {filteredJobs.map((job) => {
                      const isSelected = selectedJob?.id === job.id
                      return (
                        <Box
                          key={job.id}
                          onClick={() => handleSelectJob(job)}
                          sx={{
                            cursor: 'pointer',
                            borderRadius: 3,
                            transition: 'box-shadow 0.15s ease',
                            outline: isSelected && isDesktop ? '2px solid' : 'none',
                            outlineOffset: -1,
                            '&:hover': {
                              boxShadow: (theme) => theme.shadows[3],
                            },
                          }}
                        >
                          <JobCard
                            job={job}
                            isSaved={savedJobs.has(job.id)}
                            onToggleSave={() => handleToggleSave(job.id)}
                            onViewDetails={() => handleSelectJob(job)}
                          />
                        </Box>
                      )
                    })}
                  </Stack>
                </Stack>
              </Grid>

              {/* Desktop Sticky Job Details Preview Column */}
              {isDesktop && selectedJob && (
                <Grid item xs={12} lg={4} sx={{ minWidth: 0, alignSelf: 'flex-start', position: 'sticky', top: 90, maxHeight: 'calc(100vh - 110px)', overflowY: 'auto', pr: 0.5 }}>
                  <JobDetails job={selectedJob} />
                </Grid>
              )}
            </Grid>
          )}
        </Stack>
      </Container>

      {/* Mobile / Tablet Filter Drawer */}
      <Drawer
        anchor="bottom"
        open={isMobileFilterOpen}
        onClose={() => setIsMobileFilterOpen(false)}
        PaperProps={{
          sx: {
            borderTopLeftRadius: 20,
            borderTopRightRadius: 20,
            maxHeight: '85vh',
            p: 2.5,
          },
        }}
      >
        <Stack spacing={2}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6" sx={{ fontWeight: 800 }}>
              Filter Jobs
            </Typography>
            <IconButton onClick={() => setIsMobileFilterOpen(false)} size="small">
              <Close />
            </IconButton>
          </Box>
          <Divider />
          <JobFilterPanel
            location={location}
            onLocationChange={setLocation}
            jobType={jobType}
            onJobTypeChange={setJobType}
            experienceLevel={experienceLevel}
            onExperienceChange={setExperienceLevel}
            salaryRange={salaryRange}
            onSalaryChange={setSalaryRange}
            remoteType={remoteType}
            onRemoteTypeChange={setRemoteType}
          />
          <Button variant="contained" fullWidth size="large" onClick={() => setIsMobileFilterOpen(false)}>
            Show {filteredJobs.length} Jobs
          </Button>
        </Stack>
      </Drawer>

      {/* Mobile / Tablet Job Details Modal */}
      {!isDesktop && (
        <Dialog
          fullScreen
          open={isMobileDetailOpen}
          onClose={() => setIsMobileDetailOpen(false)}
        >
          <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pb: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 800 }}>
              Job Opportunity Details
            </Typography>
            <IconButton edge="end" onClick={() => setIsMobileDetailOpen(false)} aria-label="close">
              <Close />
            </IconButton>
          </DialogTitle>
          <Divider />
          <DialogContent sx={{ p: { xs: 2, sm: 3 } }}>
            {selectedJob && <JobDetails job={selectedJob} />}
          </DialogContent>
        </Dialog>
      )}
    </Box>
  )
}
