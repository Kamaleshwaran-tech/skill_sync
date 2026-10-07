import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { CircularProgress, Button, Link, Stack, TextField, Typography } from '@mui/material'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link as RouterLink, useNavigate } from 'react-router-dom'

import { authService } from '@/features/auth/api/authService'
import { AuthFormCard } from '@/features/auth/components/AuthFormCard'
import { PasswordField } from '@/features/auth/components/PasswordField'
import { SubmissionError } from '@/features/auth/components/SubmissionError'
import { registerSchema } from '@/features/auth/schemas/authSchemas'

export function RegisterForm() {
  const navigate = useNavigate()
  const [submissionError, setSubmissionError] = useState('')
  const { formState: { errors }, handleSubmit, register } = useForm({
    defaultValues: { confirmPassword: '', email: '', fullName: '', password: '' },
    mode: 'onBlur',
    resolver: zodResolver(registerSchema),
  })

  const registerMutation = useMutation({
    mutationFn: async (values) => {
      const registration = { ...values }
      delete registration.confirmPassword
      return authService.signUp(registration)
    },
    onSuccess: () => {
      navigate('/login', { replace: true })
    },
    onError: (error) => {
      const serverDetail = error?.response?.data?.detail
      const message = error?.code === 'ERR_NETWORK'
        ? 'Unable to reach the SkillSync API. Start the backend on port 8000 and try again.'
        : typeof serverDetail === 'string' 
        ? serverDetail 
        : (Array.isArray(serverDetail) && serverDetail[0]?.msg ? serverDetail[0].msg : (error instanceof Error ? error.message : 'Unable to create your account. Please try again.'))
      setSubmissionError(message)
    },
  })

  const submitRegistration = async (values) => {
    setSubmissionError('')
    registerMutation.mutate(values)
  }

  return (
    <AuthFormCard description="Create an account to begin building your career direction." title="Create your account">
      <Stack component="form" noValidate onSubmit={handleSubmit(submitRegistration)} spacing={2.25}>
        <SubmissionError message={submissionError} />
        <TextField autoComplete="name" error={Boolean(errors.fullName)} fullWidth helperText={errors.fullName?.message} label="Full name" {...register('fullName')} />
        <TextField autoComplete="email" error={Boolean(errors.email)} fullWidth helperText={errors.email?.message} label="Email address" {...register('email')} />
        <PasswordField error={errors.password} helperText={errors.password?.message} inputProps={{ autoComplete: 'new-password' }} label="Password" {...register('password')} />
        <PasswordField error={errors.confirmPassword} helperText={errors.confirmPassword?.message} inputProps={{ autoComplete: 'new-password' }} label="Confirm password" {...register('confirmPassword')} />
        <Button disabled={registerMutation.isPending} startIcon={registerMutation.isPending ? <CircularProgress color="inherit" size={18} /> : null} type="submit" variant="contained">
          {registerMutation.isPending ? 'Creating account…' : 'Create account'}
        </Button>
        <Typography align="center" color="text.secondary" variant="body2">
          Already have an account?{' '}
          <Link component={RouterLink} to="/login" underline="hover">Sign in</Link>
        </Typography>
      </Stack>
    </AuthFormCard>
  )
}
