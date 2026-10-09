import { CloudUpload, Delete, UploadFile } from '@mui/icons-material'
import {
  Alert,
  Box,
  Button,
  Chip,
  Divider,
  IconButton,
  Stack,
  Typography,
  alpha,
} from '@mui/material'
import { useRef } from 'react'

export function ResumeDropzone({
  file,
  error,
  helperText,
  onFilesSelected,
  onRemoveFile,
  maxFileSizeBytes,
}) {
  const inputRef = useRef(null)

  const handleDrop = (event) => {
    event.preventDefault()
    const droppedFiles = Array.from(event.dataTransfer.files)
    if (droppedFiles.length > 0) {
      onFilesSelected(droppedFiles[0])
    }
  }

  const handleBrowseClick = (event) => {
    event?.stopPropagation()
    inputRef.current?.click()
  }

  return (
    <Stack spacing={2}>
      <Box
        onDragOver={(event) => event.preventDefault()}
        onDragEnter={(event) => event.preventDefault()}
        onDrop={handleDrop}
        onClick={handleBrowseClick}
        sx={{
          border: '2px dashed',
          borderColor: error ? 'error.main' : 'divider',
          borderRadius: 4,
          backgroundColor: (theme) =>
            error ? alpha(theme.palette.error.main, 0.04) : alpha(theme.palette.primary.main, 0.03),
          px: 3,
          py: 5,
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: (theme) => alpha(theme.palette.primary.main, 0.05),
          },
        }}
      >
        <input
          ref={inputRef}
          type="file"
          hidden
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={(event) => {
            const nextFile = event.target.files?.[0]
            if (nextFile) {
              onFilesSelected(nextFile)
            }
            event.target.value = ''
          }}
        />

        <Stack alignItems="center" spacing={1.5}>
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              display: 'grid',
              placeItems: 'center',
              backgroundColor: alpha('#4c57e8', 0.12),
              color: 'primary.main',
            }}
          >
            <CloudUpload fontSize="large" />
          </Box>

          <Typography variant="h6" sx={{ fontWeight: 800 }}>
            Drag and drop your resume here
          </Typography>

          <Typography variant="body2" color="text.secondary">
            PDF or DOCX files only • up to {Math.round(maxFileSizeBytes / (1024 * 1024))} MB
          </Typography>

          <Button variant="contained" startIcon={<UploadFile />} onClick={(event) => handleBrowseClick(event)}>
            Browse files
          </Button>
        </Stack>
      </Box>

      {file ? (
        <Box>
          <Divider sx={{ my: 1 }} />
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} alignItems={{ xs: 'flex-start', sm: 'center' }} justifyContent="space-between">
            <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
              <Chip color="primary" label={file.name} />
              <Chip variant="outlined" label={file.size > 0 ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : '0 MB'} />
            </Stack>

            <Stack direction="row" spacing={1} alignItems="center">
              <Button variant="text" size="small" onClick={(event) => handleBrowseClick(event)}>
                Replace
              </Button>
              <IconButton
                aria-label="remove selected resume"
                color="error"
                onClick={(event) => {
                  event.stopPropagation()
                  onRemoveFile()
                }}
              >
                <Delete />
              </IconButton>
            </Stack>
          </Stack>
        </Box>
      ) : null}

      {error ? (
        <Alert severity="error">{error}</Alert>
      ) : helperText ? (
        <Typography variant="body2" color="text.secondary">
          {helperText}
        </Typography>
      ) : null}
    </Stack>
  )
}
