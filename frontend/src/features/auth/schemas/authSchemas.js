import { z } from 'zod'

const emailSchema = z.string().trim().min(1, 'Email is required.').email('Enter a valid email address.')
const passwordSchema = z
  .string()
  .min(8, 'Password must contain at least 8 characters.')
  .max(128, 'Password must be 128 characters or fewer.')
  .regex(/[A-Z]/, 'Password must include an upper-case letter.')
  .regex(/[a-z]/, 'Password must include a lower-case letter.')
  .regex(/[0-9]/, 'Password must include a number.')

export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required.'),
})

export const registerSchema = z
  .object({
    confirmPassword: z.string().min(1, 'Please confirm your password.'),
    email: emailSchema,
    fullName: z.string().trim().min(2, 'Enter your full name.').max(100, 'Name must be 100 characters or fewer.'),
    password: passwordSchema,
  })
  .refine((values) => values.password === values.confirmPassword, {
    message: 'Passwords do not match.',
    path: ['confirmPassword'],
  })

export const forgotPasswordSchema = z.object({
  email: emailSchema,
})
