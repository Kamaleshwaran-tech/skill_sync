import { VisibilityOffOutlined, VisibilityOutlined } from '@mui/icons-material'
import { IconButton, InputAdornment, TextField, Tooltip } from '@mui/material'
import { useState } from 'react'

export function PasswordField({ error, helperText, inputProps, label, ...field }) {
  const [isVisible, setIsVisible] = useState(false)
  const nextVisibilityLabel = isVisible ? 'Hide password' : 'Show password'

  return (
    <TextField
      {...field}
      autoComplete={inputProps?.autoComplete}
      error={Boolean(error)}
      fullWidth
      helperText={helperText}
      label={label}
      type={isVisible ? 'text' : 'password'}
      slotProps={{
        htmlInput: inputProps,
        input: {
          endAdornment: (
            <InputAdornment position="end">
              <Tooltip title={nextVisibilityLabel}>
                <IconButton aria-label={nextVisibilityLabel} edge="end" onClick={() => setIsVisible((value) => !value)}>
                  {isVisible ? <VisibilityOffOutlined /> : <VisibilityOutlined />}
                </IconButton>
              </Tooltip>
            </InputAdornment>
          ),
        },
      }}
    />
  )
}
