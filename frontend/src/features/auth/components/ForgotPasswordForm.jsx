import { zodResolver } from '@hookform/resolvers/zod'
import { CircularProgress, Button, Link, Stack, TextField, Typography } from '@mui/material'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link as RouterLink } from 'react-router-dom'

import { authService } from '@/features/auth/api/authService'
import { AuthFormCard } from '@/features/auth/components/AuthFormCard'
import { SubmissionError } from '@/features/auth/components/SubmissionError'
import { forgotPasswordSchema } from '@/features/auth/schemas/authSchemas'

export function ForgotPasswordForm() {
  const [submissionError, setSubmissionError] = useState('')
  const { formState: { errors, isSubmitting }, handleSubmit, register } = useForm({
    defaultValues: { email: '' },
    mode: 'onBlur',
    resolver: zodResolver(forgotPasswordSchema),
  })

  const submitRequest = async (values) => {
    setSubmissionError('')

    try {
      await authService.requestPasswordReset(values)
    } catch (error) {
      setSubmissionError(error instanceof Error ? error.message : 'Unable to request a password reset. Please try again.')
    }
  }

  return (
    <AuthFormCard description="Enter your email address and we will help you reset your password when authentication is connected." title="Reset your password">
      <Stack component="form" noValidate onSubmit={handleSubmit(submitRequest)} spacing={2.25}>
        <SubmissionError message={submissionError} />
        <TextField autoComplete="email" error={Boolean(errors.email)} fullWidth helperText={errors.email?.message} label="Email address" {...register('email')} />
        <Button disabled={isSubmitting} startIcon={isSubmitting ? <CircularProgress color="inherit" size={18} /> : null} type="submit" variant="contained">
          {isSubmitting ? 'Sending request…' : 'Send reset link'}
        </Button>
        <Typography align="center" color="text.secondary" variant="body2">
          <Link component={RouterLink} to="/login" underline="hover">Back to sign in</Link>
        </Typography>
      </Stack>
    </AuthFormCard>
  )
}
