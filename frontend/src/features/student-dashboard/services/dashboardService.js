import { apiClient } from '@/shared/api/apiClient'

export const dashboardService = {
  getDashboardData: async () => {
    try {
      const { data } = await apiClient.get('/dashboard')
      if (data?.profile) {
        return data
      }
    } catch (err) {
      console.warn('Backend dashboard API notice, using default state:', err?.message || err)
    }
    throw new Error('Unable to load dashboard data')
  }
}
