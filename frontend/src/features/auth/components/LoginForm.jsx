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
import { useAuth } from '@/features/auth/context/useAuth'
import { loginSchema } from '@/features/auth/schemas/authSchemas'

export function LoginForm() {
  const navigate = useNavigate()
  const { establishSession } = useAuth()
  const [submissionError, setSubmissionError] = useState('')
  const { formState: { errors }, handleSubmit, register } = useForm({
    defaultValues: { email: '', password: '' },
    mode: 'onBlur',
    resolver: zodResolver(loginSchema),
  })

  const loginMutation = useMutation({
    mutationFn: authService.signIn,
    onSuccess: (user) => {
      establishSession(user)
      navigate('/dashboard', { replace: true })
    },
    onError: (error) => {
      const serverDetail = error?.response?.data?.detail
      const message = error?.code === 'ERR_NETWORK'
        ? 'Unable to reach the SkillSync API. Start the backend on port 8000 and try again.'
        : typeof serverDetail === 'string' 
        ? serverDetail 
        : (Array.isArray(serverDetail) && serverDetail[0]?.msg ? serverDetail[0].msg : (error instanceof Error ? error.message : 'Unable to sign in. Please try again.'))
      setSubmissionError(message)
    },
  })

  const submitLogin = async (values) => {
    setSubmissionError('')
    loginMutation.mutate(values)
  }

  return (
    <AuthFormCard description="Use your SkillSync AI account to continue your career journey." title="Welcome back">
      <Stack component="form" noValidate onSubmit={handleSubmit(submitLogin)} spacing={2.25}>
        <SubmissionError message={submissionError} />
        <TextField autoComplete="email" error={Boolean(errors.email)} fullWidth helperText={errors.email?.message} label="Email address" {...register('email')} />
        <PasswordField error={errors.password} helperText={errors.password?.message} inputProps={{ autoComplete: 'current-password' }} label="Password" {...register('password')} />
        <Link component={RouterLink} sx={{ alignSelf: 'flex-start' }} to="/forgot-password" underline="hover" variant="body2">
          Forgot password?
        </Link>
        <Button disabled={loginMutation.isPending} startIcon={loginMutation.isPending ? <CircularProgress color="inherit" size={18} /> : null} type="submit" variant="contained">
          {loginMutation.isPending ? 'Signing in…' : 'Sign in'}
        </Button>
        <Typography align="center" color="text.secondary" variant="body2">
          New to SkillSync AI?{' '}
          <Link component={RouterLink} to="/register" underline="hover">Create an account</Link>
        </Typography>
      </Stack>
    </AuthFormCard>
  )
}
