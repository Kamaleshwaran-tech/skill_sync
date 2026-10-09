import { CheckCircle, RestartAlt, UploadFile } from '@mui/icons-material'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Stack,
  Typography,
} from '@mui/material'
import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { FilePreview } from '@/features/resume-upload/components/FilePreview'
import { ResumeDropzone } from '@/features/resume-upload/components/ResumeDropzone'
import { ResumeProcessingState } from '@/features/resume-upload/components/ResumeProcessingState'
import { UploadErrorState } from '@/features/resume-upload/components/UploadErrorState'
import { UploadProgress } from '@/features/resume-upload/components/UploadProgress'
import { UploadSuccessState } from '@/features/resume-upload/components/UploadSuccessState'
import {
  MAX_RESUME_FILE_SIZE_BYTES,
  validateResumeFile,
} from '@/features/resume-upload/services/resumeUploadService'
import { resumeUploadService } from '@/features/resume-upload/services/resumeUploadService'

const uploadStages = {
  idle: 'idle',
  ready: 'ready',
  uploading: 'uploading',
  processing: 'processing',
  success: 'success',
  error: 'error',
}

export function ResumeUploadPage() {
  const navigate = useNavigate()
  const uploadTimerRef = useRef(null)
  const abortControllerRef = useRef(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadState, setUploadState] = useState(uploadStages.idle)
  const [errorMessage, setErrorMessage] = useState('')
  const [progress, setProgress] = useState(0)

  const clearUploadTimer = () => {
    if (uploadTimerRef.current) {
      window.clearInterval(uploadTimerRef.current)
      uploadTimerRef.current = null
    }
  }

  useEffect(() => () => clearUploadTimer(), [])

  const handleSelectFile = (file) => {
    const validation = validateResumeFile(file, MAX_RESUME_FILE_SIZE_BYTES)

    if (!validation.valid) {
      setSelectedFile(null)
      setUploadState(uploadStages.error)
      setErrorMessage(validation.message)
      return
    }

    setSelectedFile(file)
    setErrorMessage('')
    setUploadState(uploadStages.ready)
    setProgress(0)
  }

  const handleRemoveFile = () => {
    clearUploadTimer()
    abortControllerRef.current?.abort()
    setSelectedFile(null)
    setUploadState(uploadStages.idle)
    setErrorMessage('')
    setProgress(0)
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      return
    }

    clearUploadTimer()
    setErrorMessage('')
    setUploadState(uploadStages.uploading)
    setProgress(0)

    abortControllerRef.current = new AbortController()
    try {
      await resumeUploadService.uploadResume({ file: selectedFile, signal: abortControllerRef.current.signal, onProgress: setProgress })
      setUploadState(uploadStages.success)
    } catch (error) {
      if (error?.code === 'ERR_CANCELED' || error?.name === 'CanceledError') return
      setErrorMessage(error?.response?.data?.detail || error?.message || 'Resume upload failed.')
      setUploadState(uploadStages.error)
    }
  }

  const handleCancelUpload = () => {
    clearUploadTimer()
    abortControllerRef.current?.abort()
    setUploadState(uploadStages.ready)
    setProgress(0)
  }

  const handleRetryUpload = () => {
    if (selectedFile) {
      handleUpload()
    } else {
      setUploadState(uploadStages.idle)
      setErrorMessage('')
    }
  }

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(180deg, rgba(76,87,232,0.04), rgba(76,87,232,0) 20%)', py: { xs: 2.5, sm: 3.5, md: 5 } }}>
      <Container maxWidth="lg" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="overline" color="text.secondary">
              Professional profile
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, letterSpacing: '-0.05em' }}>
              Resume upload
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Upload your resume to unlock role-fit analysis and personalized recommendations.
            </Typography>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} lg={8}>
              <Card elevation={0} sx={{ height: '100%' }}>
                <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
                  <Stack spacing={3}>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }}>
                      <Box>
                        <Typography variant="h5" sx={{ fontWeight: 800 }}>
                          Add your resume
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Supported formats: PDF and DOCX
                        </Typography>
                      </Box>

                      <Button
                        variant="outlined"
                        startIcon={<RestartAlt />}
                        onClick={handleRemoveFile}
                        disabled={!selectedFile && uploadState === 'idle'}
                      >
                        Reset
                      </Button>
                    </Stack>

                    <ResumeDropzone
                      file={selectedFile}
                      error={uploadState === 'error' ? errorMessage : ''}
                      helperText="PDF and DOCX files are uploaded securely and analyzed after submission."
                      onFilesSelected={handleSelectFile}
                      onRemoveFile={handleRemoveFile}
                      maxFileSizeBytes={MAX_RESUME_FILE_SIZE_BYTES}
                    />

                    {selectedFile && uploadState === 'ready' ? (
                      <FilePreview file={selectedFile} onReplace={handleRemoveFile} onRemove={handleRemoveFile} />
                    ) : null}

                    {uploadState === 'uploading' ? <UploadProgress progress={progress} onCancel={handleCancelUpload} /> : null}

                    {uploadState === 'processing' ? <ResumeProcessingState /> : null}

                    {uploadState === 'success' && selectedFile ? (
                      <UploadSuccessState
                        fileName={selectedFile.name}
                        onReview={() => navigate('/resume-analysis')}
                        onViewDashboard={() => navigate('/dashboard')}
                        onUploadAnother={handleRemoveFile}
                      />
                    ) : null}

                    {uploadState === 'error' && !selectedFile ? (
                      <UploadErrorState
                        title="Invalid file"
                        message={errorMessage}
                        onRetry={handleRetryUpload}
                        onRemove={handleRemoveFile}
                      />
                    ) : null}

                    {selectedFile && (uploadState === 'ready' || uploadState === 'error') ? (
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                        <Button variant="contained" size="large" startIcon={<UploadFile />} onClick={handleUpload}>
                          Upload resume
                        </Button>
                      </Box>
                    ) : null}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} lg={4}>
              <Stack spacing={2.5}>
                <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
                  <CardContent sx={{ p: 2.5 }}>
                    <Typography variant="h6" sx={{ fontWeight: 800, mb: 2 }}>
                      Resume requirements
                    </Typography>
                    <List disablePadding>
                      {[
                        'PDF or DOCX file type',
                        'Maximum size of 5 MB',
                        'Readable text and structured headings',
                        'Clear experience and education sections',
                      ].map((item) => (
                        <ListItem disableGutters key={item} sx={{ py: 0.75 }}>
                          <ListItemIcon sx={{ minWidth: 30 }}>
                            <CheckCircle color="success" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary={item} primaryTypographyProps={{ fontSize: '0.95rem' }} />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>

                <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
                  <CardContent sx={{ p: 2.5 }}>
                    <Typography variant="h6" sx={{ fontWeight: 800, mb: 1.5 }}>
                      Upload checklist
                    </Typography>
                    <Stack spacing={1.5}>
                      <Alert severity="info">Your uploaded resume is private to your account.</Alert>
                      <Alert severity="success">Analysis starts automatically after upload.</Alert>
                    </Stack>
                  </CardContent>
                </Card>
              </Stack>
            </Grid>
          </Grid>
        </Stack>
      </Container>
    </Box>
  )
}
