import { Alert, AlertTitle, Box, Button, Stack } from '@mui/material'

export function ErrorState({
  title = 'Unable to load this content',
  message = 'Please try again in a moment.',
  actionLabel,
  onAction,
}) {
  return (
    <Box sx={{ display: 'grid', minHeight: 240, placeItems: 'center', p: 3 }}>
      <Stack spacing={2} sx={{ width: '100%', maxWidth: 600 }}>
        <Alert severity="error">
          <AlertTitle>{title}</AlertTitle>
          {message}
        </Alert>
        {onAction && actionLabel ? (
          <Button onClick={onAction} sx={{ alignSelf: 'flex-start' }} variant="outlined">
            {actionLabel}
          </Button>
        ) : null}
      </Stack>
    </Box>
  )
}
