import { Search } from '@mui/icons-material'
import { Box, InputAdornment, TextField } from '@mui/material'

export function JobSearchBar({ value, onChange, placeholder = 'Search jobs or skills' }) {
  return (
    <Box sx={{ width: '100%' }}>
      <TextField
        fullWidth
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Search color="action" />
            </InputAdornment>
          ),
        }}
      />
    </Box>
  )
}
