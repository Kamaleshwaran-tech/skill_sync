import { Controller, useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from '@mui/material'

import { profileFormSchema } from '@/features/profile-settings/schemas/profileSettingsSchemas'

export function ProfileForm({ defaultValues, onSubmit }) {
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues,
    resolver: zodResolver(profileFormSchema),
  })

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <Stack spacing={3}>
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
          <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
            <Typography variant="h5" sx={{ fontWeight: 800, mb: 2 }}>
              Personal information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="firstName"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="First name" error={!!errors.firstName} helperText={errors.firstName?.message} />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="lastName"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Last name" error={!!errors.lastName} helperText={errors.lastName?.message} />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="email"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth type="email" label="Email address" error={!!errors.email} helperText={errors.email?.message} />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="phone"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Phone" error={!!errors.phone} helperText={errors.phone?.message} />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="location"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Location" error={!!errors.location} helperText={errors.location?.message} />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="bio"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth multiline minRows={4} label="Professional bio" error={!!errors.bio} helperText={errors.bio?.message} />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="website"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Website" error={!!errors.website} helperText={errors.website?.message} />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="linkedIn"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="LinkedIn" error={!!errors.linkedIn} helperText={errors.linkedIn?.message} />
                  )}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
          <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
            <Typography variant="h5" sx={{ fontWeight: 800, mb: 2 }}>
              Education
            </Typography>
            <Stack spacing={2}>
              {defaultValues.education.map((item, index) => (
                <Grid key={`${item.school}-${index}`} container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Controller
                      name={`education.${index}.school`}
                      control={control}
                      render={({ field }) => <TextField {...field} fullWidth label="School" />}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Controller
                      name={`education.${index}.degree`}
                      control={control}
                      render={({ field }) => <TextField {...field} fullWidth label="Degree" />}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Controller
                      name={`education.${index}.field`}
                      control={control}
                      render={({ field }) => <TextField {...field} fullWidth label="Field of study" />}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Controller
                      name={`education.${index}.graduationYear`}
                      control={control}
                      render={({ field }) => <TextField {...field} fullWidth label="Graduation year" />}
                    />
                  </Grid>
                </Grid>
              ))}
            </Stack>
          </CardContent>
        </Card>

        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
          <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
            <Typography variant="h5" sx={{ fontWeight: 800, mb: 2 }}>
              Experience
            </Typography>
            <Stack spacing={2}>
              {defaultValues.experience.map((item, index) => (
                <Grid key={`${item.company}-${index}`} container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Controller
                      name={`experience.${index}.company`}
                      control={control}
                      render={({ field }) => <TextField {...field} fullWidth label="Company" />}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Controller
                      name={`experience.${index}.role`}
                      control={control}
                      render={({ field }) => <TextField {...field} fullWidth label="Role" />}
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Controller
                      name={`experience.${index}.period`}
                      control={control}
                      render={({ field }) => <TextField {...field} fullWidth label="Period" />}
                    />
                  </Grid>
                  <Grid item xs={12} sm={8}>
                    <Controller
                      name={`experience.${index}.summary`}
                      control={control}
                      render={({ field }) => <TextField {...field} fullWidth multiline minRows={3} label="Summary" />}
                    />
                  </Grid>
                </Grid>
              ))}
            </Stack>
          </CardContent>
        </Card>

        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
          <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
            <Typography variant="h5" sx={{ fontWeight: 800, mb: 2 }}>
              Skills & preferences
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Controller
                  name="skills"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Skills"
                      value={field.value.join(', ')}
                      onChange={(event) => field.onChange(event.target.value.split(',').map((skill) => skill.trim()).filter(Boolean))}
                      error={!!errors.skills}
                      helperText={errors.skills?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="careerPreferences.workArrangement"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Work arrangement</InputLabel>
                      <Select {...field} label="Work arrangement">
                        <MenuItem value="Remote">Remote</MenuItem>
                        <MenuItem value="Hybrid">Hybrid</MenuItem>
                        <MenuItem value="On-site">On-site</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="careerPreferences.remotePreference"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Remote preference</InputLabel>
                      <Select {...field} label="Remote preference">
                        <MenuItem value="Remote">Remote</MenuItem>
                        <MenuItem value="Hybrid">Hybrid</MenuItem>
                        <MenuItem value="On-site">On-site</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="careerPreferences.relocation"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Relocation" />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="careerPreferences.salaryExpectation"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Salary expectation" />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="targetRoles"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Target roles"
                      value={field.value.join(', ')}
                      onChange={(event) => field.onChange(event.target.value.split(',').map((role) => role.trim()).filter(Boolean))}
                      error={!!errors.targetRoles}
                      helperText={errors.targetRoles?.message}
                    />
                  )}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {Object.keys(errors).length ? (
          <Alert severity="error">Please correct the highlighted fields before saving.</Alert>
        ) : null}

        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={isSubmitting}
            sx={{ width: { xs: '100%', sm: 'auto' }, py: 1.25 }}
          >
            Save profile
          </Button>
        </Box>
      </Stack>
    </Box>
  )
}
