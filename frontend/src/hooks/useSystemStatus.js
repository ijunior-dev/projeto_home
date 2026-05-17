import { useState, useEffect } from 'react'

const STATUS_URL = 'http://localhost:8000/status'
const POLL_INTERVAL = 5000

const DEFAULT_STATUS = {
  api: 'unknown',
  database: 'unknown',
  supabase: 'unknown',
  tcp_server: 'unknown',
}

export function useSystemStatus() {
  const [status, setStatus] = useState(DEFAULT_STATUS)

  useEffect(() => {
    let cancelled = false

    const fetchStatus = async () => {
      try {
        const res = await fetch(STATUS_URL, { signal: AbortSignal.timeout(4000) })
        if (cancelled) return
        if (res.ok) {
          const data = await res.json()
          setStatus(data)
        } else {
          setStatus({ ...DEFAULT_STATUS, api: 'offline' })
        }
      } catch {
        if (!cancelled) {
          setStatus({ api: 'offline', database: 'unknown', supabase: 'unknown', tcp_server: 'unknown' })
        }
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, POLL_INTERVAL)
    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [])

  return status
}
