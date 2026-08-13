import { useCallback, useEffect, useState } from 'react'
import { getApiErrorMessage } from '../services/api'

interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: string | null
  reload: () => void
}

export function useAsyncData<T>(
  loader: () => Promise<T>,
  deps: unknown[],
  fallbackError: string,
): AsyncState<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tick, setTick] = useState(0)

  const reload = useCallback(() => setTick((value) => value + 1), [])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    loader()
      .then((result) => {
        if (!cancelled) {
          setData(result)
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setData(null)
          setError(getApiErrorMessage(err, fallbackError))
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick, ...deps])

  return { data, loading, error, reload }
}
