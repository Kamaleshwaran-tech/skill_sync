import { apiClient } from '@/shared/api/apiClient'

export const dashboardService = {
  getDashboardData: async () => {
    const { data } = await apiClient.get('/dashboard')
    return data
  },

  getTargetRole: async () => {
    const { data } = await apiClient.get('/dashboard/target-role')
    return data.targetRole || null
  },

  setTargetRole: async (targetRole) => {
    const { data } = await apiClient.post('/dashboard/target-role', { targetRole })
    return data.targetRole
  },

  runAnalysis: async () => {
    const { data } = await apiClient.post('/dashboard/analyze', null, { timeout: 180_000 })
    return data
  },
}
