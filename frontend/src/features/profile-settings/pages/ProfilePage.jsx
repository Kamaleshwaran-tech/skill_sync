import { Alert, Box, Container, Snackbar, Stack, Typography } from '@mui/material'
import { useEffect, useState } from 'react'

import { ProfileForm } from '@/features/profile-settings/components/ProfileForm'
import { profileSettingsService } from '@/features/profile-settings/services/profileSettingsService'

const emptyProfile = { firstName: '', lastName: '', email: '', phone: '', location: '', bio: '', website: '', linkedIn: '', education: [], experience: [], skills: [], careerPreferences: { workArrangement: '', remotePreference: '', relocation: '', salaryExpectation: '' }, targetRoles: [] }

export function ProfilePage({ profile: initialProfile = emptyProfile }) {
  const [profile, setProfile] = useState(initialProfile)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)
  useEffect(() => { profileSettingsService.getProfile().then((data) => setProfile({ ...initialProfile, ...data, education: data.education || [], experience: data.experience || [], skills: data.skills || [], targetRoles: data.targetRoles || [], careerPreferences: { ...initialProfile.careerPreferences, ...(data.careerPreferences || {}) } })).catch((err) => setError(err?.response?.data?.detail || 'Unable to load your profile.')) }, [initialProfile])
  const handleProfileSubmit = async (values) => { try { const data = await profileSettingsService.updateProfile(values); setProfile(data); setSaved(true); setError('') } catch (err) { setError(err?.response?.data?.detail || 'Unable to save your profile.') } }

  return (
    <Box sx={{ py: { xs: 2.5, sm: 3.5, md: 5 }, minHeight: '100vh', background: 'linear-gradient(180deg, rgba(76,87,232,0.04), rgba(76,87,232,0) 20%)' }}>
      <Container maxWidth="lg" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="overline" color="text.secondary">
              Account
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, letterSpacing: '-0.05em' }}>
              Profile
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Maintain your personal information, education, experience, skills, and career preferences.
            </Typography>
          </Box>

          {error ? <Alert severity="error">{error}</Alert> : null}
          <ProfileForm key={JSON.stringify(profile)} defaultValues={profile} onSubmit={handleProfileSubmit} />
        </Stack>
      </Container>
      <Snackbar open={saved} autoHideDuration={3000} onClose={() => setSaved(false)} message="Profile saved" />
    </Box>
  )
}
