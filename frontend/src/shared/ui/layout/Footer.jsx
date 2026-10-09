import { Box, Container, Divider, Link, Stack, Typography } from '@mui/material'

import { BrandLogo } from '@/shared/ui/layout/BrandLogo'

const footerItems = [
  { href: '#about', label: 'About' },
  { href: '#features', label: 'Features' },
  { href: '#about', label: 'Privacy' },
  { href: '#about', label: 'Terms' },
  { href: '#about', label: 'Contact' },
]

export function Footer() {
  return (
    <Box component="footer" id="about" sx={{ pt: { xs: 7, md: 10 } }}>
      <Container maxWidth="lg">
        <Divider />
        <Stack
          alignItems={{ md: 'center' }}
          direction={{ xs: 'column', md: 'row' }}
          justifyContent="space-between"
          spacing={3}
          sx={{ py: 4 }}
        >
          <Stack spacing={1.25}>
            <BrandLogo />
            <Typography color="text.secondary" variant="body2">
              Clear direction for your next career move.
            </Typography>
          </Stack>
          <Stack direction="row" flexWrap="wrap" gap={{ xs: 2, sm: 3 }}>
            {footerItems.map((item) => (
              <Link color="text.secondary" href={item.href} key={item.label} underline="hover" variant="body2">
                {item.label}
              </Link>
            ))}
          </Stack>
        </Stack>
        <Divider />
        <Typography color="text.secondary" sx={{ py: 3 }} variant="body2">
          © {new Date().getFullYear()} SkillSync AI. Built for ambitious students.
        </Typography>
      </Container>
    </Box>
  )
}
