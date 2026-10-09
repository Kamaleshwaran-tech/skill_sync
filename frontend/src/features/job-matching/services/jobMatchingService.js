import { apiClient } from '@/shared/api/apiClient'

export const jobMatchingService = {
  getJobs: async (params = {}) => {
    const { data } = await apiClient.get('/jobs/', { params })
    if (!Array.isArray(data) || !data.length) {
      return []
    }

    const jobs = data.map((job) => {
      const isRemote = (job.location && /remote/i.test(job.location)) ||
                       (job.description && /remote/i.test(job.description)) ||
                       (job.title && /remote/i.test(job.title))
      const rawJobType = (job.job_type || '').toLowerCase()
      const jobType = rawJobType && rawJobType !== 'unknown' ? job.job_type : 'Full-time'

      const titleLower = (job.title || '').toLowerCase()
      const descLower = (job.description || '').toLowerCase()
      let experienceLevel = 'Mid'
      if (titleLower.includes('senior') || titleLower.includes('lead') || titleLower.includes('architect') || titleLower.includes('principal')) {
        experienceLevel = 'Senior'
      } else if (titleLower.includes('intern') || titleLower.includes('trainee') || titleLower.includes('junior') || titleLower.includes('entry') || descLower.includes('entry level')) {
        experienceLevel = 'Entry'
      } else if (titleLower.includes('mid') || titleLower.includes('associate')) {
        experienceLevel = 'Mid'
      }

      return {
        id: String(job.id || job.external_id),
        originalId: job.id,
        title: job.title || 'Untitled Role',
        company: job.company || 'Tech Employer',
        location: job.location || 'India',
        remoteType: isRemote ? 'Remote' : 'On-site',
        jobType,
        experienceLevel,
        salary: job.salary_min && job.salary_max ? `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}` : 'Salary not disclosed',
        salaryRange: job.salary_min && job.salary_max ? `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}` : 'Salary not disclosed',
        postedDate: job.posted_date || 'Recently',
        url: job.url || '',
        matchScore: job.match_score || 0,
        matchPercentage: job.match_score || 0,
        requiredSkills: job.required_skills || [],
        preferredSkills: job.preferred_skills || [],
        missingSkills: job.missing_skills || [],
        matchedSkills: job.matched_skills || [],
        description: job.description || 'No description provided by the employer.',
        responsibilities: [],
        requirements: (job.required_skills || []).map((s) => `Proficiency in ${s}`),
        benefits: [],
      }
    })

    // Fetch active resume to calculate personalized match scores
    try {
      const { data: resumes } = await apiClient.get('/resumes/')
      const resume = resumes?.find((item) => item.is_active && item.status === 'COMPLETED')
        || resumes?.find((item) => item.status === 'COMPLETED')
      if (!resume) {
        return jobs
      }

      const matches = await Promise.allSettled(jobs.map(async (job) => {
        const match = await jobMatchingService.matchResumeToJob(resume.id, job.originalId)
        return {
          ...job,
          matchScore: match.overall_match_score,
          matchPercentage: match.overall_match_score,
          matchedSkills: match.matched_skills || [],
          missingSkills: match.missing_skills || [],
        }
      }))

      return matches.map((result, index) => result.status === 'fulfilled' ? result.value : jobs[index])
    } catch (err) {
      console.warn('Could not compute personalized match scores:', err)
      return jobs
    }
  },

  matchResumeToJob: async (resumeId, jobId) => {
    const { data } = await apiClient.post('/jobs/match', { resume_id: resumeId, job_id: jobId })
    return data
  }
}
