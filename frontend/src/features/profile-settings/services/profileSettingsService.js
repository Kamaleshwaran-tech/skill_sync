import { apiClient } from '@/shared/api/apiClient'

export const profileSettingsService = {
  getProfile: async () => {
    const { data } = await apiClient.get('/profile')
    return data
  },
  updateProfile: async (profile) => {
    const { data } = await apiClient.put('/profile', profile)
    return data
  },
  getSettings: async () => {
    const { data } = await apiClient.get('/profile/settings')
    return data
  },
  updateSettings: async (settings) => {
    const { data } = await apiClient.put('/profile/settings', settings)
    return data
  },
}
