import { apiClient } from '@/shared/api/apiClient'

export const emptyResumeAnalysis = {
  overview: { fileName: 'Resume', status: 'Awaiting analysis', qualityScore: 0, matchScore: 0, summary: 'Upload and analyze a resume to see extracted insights.' },
  personalInfo: { name: '', email: '', phone: '', location: '', linkedin: '', portfolio: '' },
  education: [], experience: [], projects: [], certifications: [], technicalSkills: [], softSkills: [], skillCategories: [], strengths: [], improvements: [], aiSummary: '',
}

export const resumeAnalysisService = {
  getResumeAnalysis: async (resumeId) => {
    const resumes = resumeId ? null : (await apiClient.get('/resumes/')).data
    const resume = resumeId ? (await apiClient.get(`/resumes/${resumeId}`)).data : resumes?.find((item) => item.is_active) || resumes?.[0]
    if (!resume) return emptyResumeAnalysis
    const analysis = (await apiClient.get(`/resumes/${resume.id}/analysis`)).data
    const profile = analysis.profile || {}
    const technicalSkills = (profile.technical_skills || []).map((item) => item.name || item).filter(Boolean)
    const softSkills = (profile.soft_skills || []).map((item) => (typeof item === 'string' ? item : item.name)).filter(Boolean)
    const personal = profile.personal_info || {}

    return {
      overview: {
        fileName: resume.filename,
        status: resume.status,
        qualityScore: Math.round((analysis.confidence || 0.88) * 100),
        matchScore: 85,
        summary: profile.summary || 'Resume analysis completed successfully.',
      },
      personalInfo: {
        name: profile.name || 'Candidate',
        email: personal.email || (profile.emails || [])[0] || '',
        phone: personal.phone || (profile.phones || [])[0] || '',
        location: personal.location || '',
        linkedin: personal.linkedin || '',
        portfolio: personal.portfolio || '',
      },
      education: profile.education || [],
      experience: profile.experience || [],
      projects: profile.projects || [],
      certifications: profile.certifications || [],
      technicalSkills,
      softSkills,
      skillCategories: profile.skill_categories || [],
      strengths: profile.strengths || [],
      improvements: profile.improvements || [],
      aiSummary: profile.summary || '',
    }
  },
}
