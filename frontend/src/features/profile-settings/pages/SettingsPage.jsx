import { Alert, Box, Container, Snackbar, Stack, Typography } from '@mui/material'
import { useEffect, useState } from 'react'

import { SettingsForm } from '@/features/profile-settings/components/SettingsForm'
import { profileSettingsService } from '@/features/profile-settings/services/profileSettingsService'

const emptySettings = { theme: 'System', notifications: { jobAlerts: false, marketingEmails: false, weeklyDigest: false, resumeTips: false }, privacy: { profileVisible: false, showResumeToEmployers: false, allowAnalytics: false, shareLearningActivity: false }, account: { language: 'English (US)', timezone: 'UTC', emailVisible: false, twoFactorEnabled: false } }

export function SettingsPage({ settings: initialSettings = emptySettings }) {
  const [settings, setSettings] = useState(initialSettings)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)
  useEffect(() => { profileSettingsService.getSettings().then((data) => setSettings({ ...initialSettings, ...data, notifications: { ...initialSettings.notifications, ...(data.notifications || {}) }, privacy: { ...initialSettings.privacy, ...(data.privacy || {}) }, account: { ...initialSettings.account, ...(data.account || {}) } })).catch((err) => setError(err?.response?.data?.detail || 'Unable to load settings.')) }, [initialSettings])
  const handleSettingsSubmit = async (values) => { try { const data = await profileSettingsService.updateSettings(values); setSettings({ ...settings, ...data }); setSaved(true); setError('') } catch (err) { setError(err?.response?.data?.detail || 'Unable to save settings.') } }

  return (
    <Box sx={{ py: { xs: 2.5, sm: 3.5, md: 5 }, minHeight: '100vh', background: 'linear-gradient(180deg, rgba(76,87,232,0.04), rgba(76,87,232,0) 20%)' }}>
      <Container maxWidth="lg" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="overline" color="text.secondary">
              Preferences
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, letterSpacing: '-0.05em' }}>
              Settings
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Update theme preferences, notifications, privacy controls, and account settings.
            </Typography>
          </Box>

          {error ? <Alert severity="error">{error}</Alert> : null}
          <SettingsForm key={JSON.stringify(settings)} defaultValues={settings} onSubmit={handleSettingsSubmit} />
        </Stack>
      </Container>
      <Snackbar open={saved} autoHideDuration={3000} onClose={() => setSaved(false)} message="Settings saved" />
    </Box>
  )
}
