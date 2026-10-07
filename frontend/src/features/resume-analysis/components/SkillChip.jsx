import { Chip } from '@mui/material'

export function SkillChip({ label, color = 'primary', variant = 'filled' }) {
  return <Chip label={label} color={color} variant={variant} sx={{ fontWeight: 600 }} />
}
