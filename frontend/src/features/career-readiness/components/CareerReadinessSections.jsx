import { ExpandMore, TrendingUp } from '@mui/icons-material'
import { Accordion, AccordionDetails, AccordionSummary, Box, Chip, Stack, Typography } from '@mui/material'

export function StrengthsList({ items }) {
  return (
    <Box>
      <Typography variant="h6" sx={{ fontWeight: 800, mb: 1.5 }}>Strengths</Typography>
      <Stack spacing={1.25}>
        {items.map((item) => (
          <Chip key={item} label={item} color="success" variant="outlined" sx={{ justifyContent: 'flex-start' }} />
        ))}
      </Stack>
    </Box>
  )
}

export function WeaknessesList({ items }) {
  return (
    <Box>
      <Typography variant="h6" sx={{ fontWeight: 800, mb: 1.5 }}>Weaknesses</Typography>
      <Stack spacing={1.25}>
        {items.map((item) => (
          <Chip key={item} label={item} color="warning" variant="outlined" sx={{ justifyContent: 'flex-start' }} />
        ))}
      </Stack>
    </Box>
  )
}

export function RecommendedActionsList({ items }) {
  return (
    <Box>
      <Typography variant="h6" sx={{ fontWeight: 800, mb: 1.5 }}>Recommended actions</Typography>
      <Stack spacing={1.25}>
        {items.map((item) => (
          <Chip key={item} label={item} color="info" variant="outlined" sx={{ justifyContent: 'flex-start' }} />
        ))}
      </Stack>
    </Box>
  )
}

export function OpportunityList({ items }) {
  return (
    <Box>
      <Typography variant="h6" sx={{ fontWeight: 800, mb: 1.5 }}>Career improvement opportunities</Typography>
      <Stack spacing={1.25}>
        {items.map((item) => (
          <Chip key={item} label={item} color="secondary" variant="outlined" sx={{ justifyContent: 'flex-start' }} />
        ))}
      </Stack>
    </Box>
  )
}

export function ExplanationAccordion({ title, body }) {
  return (
    <Accordion defaultExpanded sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3, overflow: 'hidden' }}>
      <AccordionSummary expandIcon={<ExpandMore />} sx={{ px: 2 }}>
        <Stack direction="row" spacing={1.5} alignItems="center">
          <TrendingUp color="primary" />
          <Typography variant="h6" sx={{ fontWeight: 800 }}>{title}</Typography>
        </Stack>
      </AccordionSummary>
      <AccordionDetails sx={{ px: 2, pb: 2 }}>
        <Typography variant="body1" color="text.secondary">{body}</Typography>
      </AccordionDetails>
    </Accordion>
  )
}
