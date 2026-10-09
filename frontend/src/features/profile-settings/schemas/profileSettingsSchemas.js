import { z } from 'zod'

export const profileFormSchema = z.object({
  firstName: z.string().min(1, 'First name is required'),
  lastName: z.string().min(1, 'Last name is required'),
  email: z.email('Enter a valid email address'),
  phone: z.string().min(1, 'Phone number is required'),
  location: z.string().min(1, 'Location is required'),
  bio: z.string().min(10, 'Bio must be at least 10 characters'),
  website: z.string().url('Enter a valid URL').or(z.literal('')),
  linkedIn: z.string().url('Enter a valid URL').or(z.literal('')),
  education: z.array(
    z.object({
      school: z.string().min(1, 'School is required'),
      degree: z.string().min(1, 'Degree is required'),
      field: z.string().min(1, 'Field is required'),
      graduationYear: z.string().min(1, 'Graduation year is required'),
    }),
  ),
  experience: z.array(
    z.object({
      company: z.string().min(1, 'Company is required'),
      role: z.string().min(1, 'Role is required'),
      period: z.string().min(1, 'Period is required'),
      summary: z.string().min(10, 'Summary is required'),
    }),
  ),
  skills: z.array(z.string()).min(1, 'Add at least one skill'),
  careerPreferences: z.object({
    workArrangement: z.string().min(1),
    jobTypes: z.array(z.string()),
    remotePreference: z.string().min(1),
    relocation: z.string().min(1),
    salaryExpectation: z.string().min(1),
  }),
  targetRoles: z.array(z.string()).min(1, 'Add at least one target role'),
})

export const settingsFormSchema = z.object({
  theme: z.enum(['Light', 'Dark', 'System']),
  notifications: z.object({
    jobAlerts: z.boolean(),
    marketingEmails: z.boolean(),
    weeklyDigest: z.boolean(),
    resumeTips: z.boolean(),
  }),
  privacy: z.object({
    profileVisible: z.boolean(),
    showResumeToEmployers: z.boolean(),
    allowAnalytics: z.boolean(),
    shareLearningActivity: z.boolean(),
  }),
  account: z.object({
    language: z.string().min(1),
    timezone: z.string().min(1),
    emailVisible: z.boolean(),
    twoFactorEnabled: z.boolean(),
  }),
})
