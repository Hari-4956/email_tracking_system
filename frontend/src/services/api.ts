import axios, { AxiosError } from 'axios'

const configuredBase = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

export const api = axios.create({
  baseURL: configuredBase,
  timeout: 30000,
  headers: {
    Accept: 'application/json',
  },
})

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const ax = error as AxiosError<{ detail?: string | Array<{ msg?: string }> }>

    if (ax.code === 'ECONNABORTED') {
      return `${fallback} The request timed out.`
    }
    if (ax.code === 'ERR_NETWORK') {
      return `${fallback} Check that FastAPI is running and reachable.`
    }

    const status = ax.response?.status
    if (status === 404) {
      return 'Resource not found.'
    }
    if (status === 422) {
      return 'Invalid request parameters.'
    }
    if (status && status >= 500) {
      return `${fallback} The server reported an error.`
    }

    const detail = ax.response?.data?.detail
    if (typeof detail === 'string') {
      // Only surface short, safe API messages (already sanitized by FastAPI routes).
      if (detail.length <= 200 && !detail.toLowerCase().includes('password')) {
        return detail
      }
    }
  }
  return fallback
}
