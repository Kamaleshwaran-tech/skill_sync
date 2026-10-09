import { Bookmark, BookmarkBorder } from '@mui/icons-material'
import { IconButton, Tooltip } from '@mui/material'

export function SavedJobButton({ isSaved, onToggleSave, ariaLabel }) {
  return (
    <Tooltip title={isSaved ? 'Remove saved job' : 'Save job'}>
      <IconButton
        aria-label={ariaLabel || 'save job'}
        color={isSaved ? 'primary' : 'default'}
        onClick={onToggleSave}
      >
        {isSaved ? <Bookmark /> : <BookmarkBorder />}
      </IconButton>
    </Tooltip>
  )
}
