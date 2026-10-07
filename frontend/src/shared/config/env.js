function getOptionalValue(value) {
  return typeof value === 'string' && value.trim() ? value.trim() : undefined
}

function normalizeBaseUrl(value) {
  return getOptionalValue(value)?.replace(/\/+$/, '')
}

export const env = Object.freeze({
  appName: getOptionalValue(import.meta.env.VITE_APP_NAME) ?? 'SkillSync AI',
  apiBaseUrl: normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL) ?? '/api/v1',
})
