import { Card, CardContent, Stack, Typography } from '@mui/material'

import { Reveal } from '@/shared/ui/motion/Reveal'

export function FeatureCard({ description, icon: Icon, index, title }) {
  return (
    <Reveal delay={index * 0.055}>
      <Card component="article" sx={{ height: '100%', transition: 'border-color 180ms ease, transform 180ms ease', '&:hover': { borderColor: 'primary.main', transform: 'translateY(-3px)' } }}>
        <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
          <Stack spacing={2.5}>
            <Icon color="primary" />
            <Stack spacing={1}>
              <Typography component="h3" variant="h3">{title}</Typography>
              <Typography color="text.secondary" variant="body2">{description}</Typography>
            </Stack>
          </Stack>
        </CardContent>
      </Card>
    </Reveal>
  )
}
