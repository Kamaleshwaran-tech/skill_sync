import { apiClient } from '@/shared/api/apiClient'

function toRoadmapView(response, dashboard) {
  const skillOverview = dashboard.skillOverview || {}
  const missingSkills = skillOverview.missing || []
  return {
    currentSkillLevel: response.currentSkillLevel,
    targetRole: response.targetRole,
    estimatedDuration: response.learningSequence?.length ? `${response.learningSequence.length} focused steps` : 'Not available',
    requiredSkills: [...new Set([...(skillOverview.current || []), ...missingSkills])],
    missingSkills,
    roadmapItems: (response.learningSequence || []).map((step) => ({
      ...step,
      id: `roadmap-${step.order}-${step.skill}`,
      resources: (step.learningResources || []).map((resource) => resource.title),
    })),
  }
}

export const learningRoadmapService = {
  getRoadmap: async () => {
    const { data: dashboard } = await apiClient.get('/dashboard')
    const skillOverview = dashboard.skillOverview || {}
    const { data } = await apiClient.post('/roadmaps/generate', {
      currentSkills: skillOverview.current || [],
      targetRole: dashboard.profile?.focus || 'Software Engineer',
      missingSkills: skillOverview.missing || [],
      careerReadinessScore: dashboard.careerReadinessScore || 0,
      industryDemand: Object.fromEntries((dashboard.skillDemand || []).map(({ skill, demand }) => [skill, demand / 100])),
    })
    return toRoadmapView(data, dashboard)
  },
}
