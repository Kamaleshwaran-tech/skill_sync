import { Box, Card, CardContent, Stack, Typography } from '@mui/material'

export function AuthFormCard({ children, description, title }) {
  return (
    <Card sx={{ mx: 'auto', width: '100%' }}>
      <CardContent sx={{ p: { xs: 3, sm: 5 }, '&:last-child': { pb: { xs: 3, sm: 5 } } }}>
        <Stack spacing={4}>
          <Stack spacing={1.25}>
            <Typography component="h1" sx={{ fontSize: 'clamp(2rem, 5vw, 2.7rem)', fontWeight: 750, letterSpacing: '-0.05em', lineHeight: 1.06 }}>
              {title}
            </Typography>
            <Typography color="text.secondary" variant="body2">
              {description}
            </Typography>
          </Stack>
          <Box>{children}</Box>
        </Stack>
      </CardContent>
    </Card>
  )
}
