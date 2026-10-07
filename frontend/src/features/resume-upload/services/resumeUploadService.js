import { apiClient } from '@/shared/api/apiClient'

export const MAX_RESUME_FILE_SIZE_BYTES = 5 * 1024 * 1024
export const ALLOWED_RESUME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]

export function formatFileSize(fileSizeInBytes) {
  if (fileSizeInBytes === 0) {
    return '0 B'
  }

  const units = ['B', 'KB', 'MB', 'GB']
  const unitIndex = Math.min(Math.floor(Math.log(fileSizeInBytes) / Math.log(1024)), units.length - 1)
  const value = fileSizeInBytes / 1024 ** unitIndex

  return `${value >= 10 || unitIndex === 0 ? value.toFixed(0) : value.toFixed(1)} ${units[unitIndex]}`
}

export function validateResumeFile(file, maxFileSizeBytes = MAX_RESUME_FILE_SIZE_BYTES) {
  if (!file) {
    return {
      valid: false,
      code: 'NO_FILE',
      message: 'Please select a resume file to continue.',
    }
  }

  const isSupportedType = ALLOWED_RESUME_TYPES.includes(file.type)
  const isPdfExtension = file.name.toLowerCase().endsWith('.pdf')
  const isDocxExtension = file.name.toLowerCase().endsWith('.docx')

  if (!isSupportedType && !(isPdfExtension || isDocxExtension)) {
    return {
      valid: false,
      code: 'INVALID_TYPE',
      message: 'Unsupported file type. Please upload a PDF or DOCX document.',
    }
  }

  if (file.size > maxFileSizeBytes) {
    return {
      valid: false,
      code: 'FILE_TOO_LARGE',
      message: `File exceeds the ${formatFileSize(maxFileSizeBytes)} limit. Please choose a smaller resume.`,
    }
  }

  return { valid: true }
}

export const resumeUploadService = {
  uploadResume: async ({ file, onProgress, signal } = {}) => {
    if (!file) {
      throw new Error('No resume file selected.')
    }

    const formData = new FormData()
    formData.append('file', file)

    const { data } = await apiClient.post('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120_000,
      onUploadProgress: (progressEvent) => {
        if (typeof onProgress === 'function' && progressEvent.total) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percent)
        }
      },
      signal,
    })

    // Kick off AI analysis (best-effort). Analysis can take several seconds for
    // parsing + semantic job matching + Gemini calls, so we don't await it — the
    // upload endpoint returns immediately and the analysis page will fetch the
    // result (or retry) when the user navigates there.
    if (data?.id) {
      apiClient.post(`/resumes/${data.id}/analyze`, null, { timeout: 180_000 })
        .catch((err) => {
          // Non-fatal: resume is saved; analysis can be retried from the results page.
          console.warn('Resume analysis request failed:', err?.response?.data?.detail || err?.message)
        })
    }

    return {
      id: data.id,
      fileName: data.filename || file.name,
      status: 'processing',
    }
  },

  cancelUpload: () => {
    return { cancelled: true }
  },
}
