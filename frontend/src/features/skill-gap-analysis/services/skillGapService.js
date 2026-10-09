import { apiClient } from '@/shared/api/apiClient'

export const skillGapService = {
  getSkillGaps: async () => {
    const { data } = await apiClient.get('/dashboard')
    const overview = data.skillOverview || {}
    const current = overview.current || []
    const rawMissing = overview.missing || []
    const skillDemand = data.skillDemand || []

    const demandMap = Object.fromEntries(skillDemand.map((d) => [d.skill, d.demand]))

    const missingSkills = rawMissing.map((skillName, index) => {
      const demand = demandMap[skillName] || Math.max(60, 95 - index * 7)
      const priority = index === 0 ? 'Critical' : index <= 2 ? 'High' : 'Medium'
      return {
        name: skillName,
        priority,
        gapPercentage: Math.max(65, 90 - index * 5),
        industryDemand: demand,
        currentProficiency: 15,
        requiredProficiency: 85,
        recommendedLearningTime: index <= 1 ? '2-3 weeks' : '3-4 weeks',
        difficulty: index % 2 === 0 ? 'Intermediate' : 'Moderate',
      }
    })

    const matchedSkills = current.slice(0, 8)
    const requiredSkills = [...new Set([...matchedSkills, ...rawMissing])]

    const proficiencyComparison = [
      ...current.slice(0, 5).map((skill) => ({
        skill,
        current: 80,
        required: 75,
      })),
      ...missingSkills.slice(0, 3).map((item) => ({
        skill: item.name,
        current: 15,
        required: 85,
      })),
    ]

    const skillPriority = missingSkills.slice(0, 5).map((item, idx) => ({
      skill: item.name,
      priority: Math.max(50, 95 - idx * 10),
    }))

    const overallGap = missingSkills.length
      ? Math.round(
          missingSkills.reduce((acc, curr) => acc + curr.gapPercentage, 0) /
            missingSkills.length,
        )
      : 15

    return {
      currentSkills: current,
      requiredSkills,
      matchedSkills,
      missingSkills,
      proficiencyComparison,
      skillPriority,
      industryDemand: skillDemand,
      summary: {
        skillPriority: missingSkills.length > 2 ? 'High' : 'Moderate',
        industryDemand: 'Strong',
        overallGap,
        learningDifficulty: 'Moderate',
      },
    }
  },
}
