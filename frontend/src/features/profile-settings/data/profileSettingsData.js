export const profileSettingsMockData = {
  profile: {
    firstName: 'Maya',
    lastName: 'Patel',
    email: 'maya.patel@example.com',
    phone: '+1 (415) 555-0192',
    location: 'San Francisco, CA',
    bio: 'Product-minded full stack developer focused on user experience, scalable systems, and measurable business impact.',
    website: 'https://mayapatel.dev',
    linkedIn: 'https://linkedin.com/in/mayapatel',
    education: [
      {
        school: 'University of California, Berkeley',
        degree: 'B.S. Computer Science',
        field: 'Software Engineering',
        graduationYear: '2022',
      },
    ],
    experience: [
      {
        company: 'Northstar Labs',
        role: 'Frontend Engineer',
        period: '2022 - Present',
        summary: 'Built reusable interfaces and dashboards for customer analytics and internal operations.',
      },
      {
        company: 'OrbitWorks',
        role: 'Software Engineer Intern',
        period: '2021 - 2022',
        summary: 'Supported product teams with UI development and API integration work.',
      },
    ],
    skills: ['React', 'TypeScript', 'Node.js', 'SQL', 'AWS', 'System Design'],
    careerPreferences: {
      workArrangement: 'Hybrid',
      jobTypes: ['Full-time', 'Contract'],
      remotePreference: 'Hybrid',
      relocation: 'Open to relocation',
      salaryExpectation: '$120k - $150k',
    },
    targetRoles: ['Full Stack Developer', 'Frontend Engineer', 'Platform Engineer'],
  },
  settings: {
    theme: 'Dark',
    notifications: {
      jobAlerts: true,
      marketingEmails: false,
      weeklyDigest: true,
      resumeTips: true,
    },
    privacy: {
      profileVisible: true,
      showResumeToEmployers: true,
      allowAnalytics: false,
      shareLearningActivity: true,
    },
    account: {
      language: 'English (US)',
      timezone: 'Pacific Time (PT)',
      emailVisible: false,
      twoFactorEnabled: true,
    },
  },
}
