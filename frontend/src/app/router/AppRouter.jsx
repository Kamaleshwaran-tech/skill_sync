import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { AuthLayout } from '@/features/auth/components/AuthLayout'
import { ForgotPasswordPage } from '@/features/auth/pages/ForgotPasswordPage'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { ProtectedRoutePlaceholder } from '@/features/auth/pages/ProtectedRoutePlaceholder'
import { RegisterPage } from '@/features/auth/pages/RegisterPage'
import { RequireAuth } from '@/features/auth/routes/RequireAuth'
import { JobMatchingPage } from '@/features/job-matching/pages/JobMatchingPage'
import { LandingPage } from '@/features/landing/pages/LandingPage'
import { LearningRoadmapPage } from '@/features/learning-roadmap/pages/LearningRoadmapPage'
import { ProfilePage } from '@/features/profile-settings/pages/ProfilePage'
import { ResumeAnalysisPage } from '@/features/resume-analysis/pages/ResumeAnalysisPage'
import { ResumeUploadPage } from '@/features/resume-upload/pages/ResumeUploadPage'
import { SettingsPage } from '@/features/profile-settings/pages/SettingsPage'
import { SkillGapAnalysisPage } from '@/features/skill-gap-analysis/pages/SkillGapAnalysisPage'
import { StudentDashboardPage } from '@/features/student-dashboard/pages/StudentDashboardPage'
import { NotFoundPage } from '@/features/system/pages/NotFoundPage'
import { AppLayout } from '@/shared/ui/layout/AppLayout'

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}><Route index element={<LandingPage />} /></Route>
        <Route element={<RequireAuth />}>
          <Route element={<AppLayout />}>
            <Route path="dashboard" element={<StudentDashboardPage />} />
            <Route path="resume-upload" element={<ResumeUploadPage />} />
            <Route path="resume-analysis" element={<ResumeAnalysisPage />} />
            <Route path="job-matching" element={<JobMatchingPage />} />
            <Route path="skill-gap-analysis" element={<SkillGapAnalysisPage />} />
            <Route path="learning-roadmap" element={<LearningRoadmapPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Route>
        <Route element={<AuthLayout />}>
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route path="forgot-password" element={<ForgotPasswordPage />} />
        </Route>
        <Route element={<RequireAuth />}>
          <Route path="protected" element={<ProtectedRoutePlaceholder />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  )
}
