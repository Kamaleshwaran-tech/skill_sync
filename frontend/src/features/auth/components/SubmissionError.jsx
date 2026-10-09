import { Alert } from '@mui/material'

export function SubmissionError({ message }) {
  if (!message) {
    return null
  }

  return <Alert severity="error">{message}</Alert>
}
