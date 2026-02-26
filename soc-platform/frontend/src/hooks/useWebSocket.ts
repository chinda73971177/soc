import { useEffect, useRef, useCallback } from 'react'
import { useSOCStore } from '../store'

export function useWebSocket(channel: 'events' | 'alerts', onMessage?: (data: unknown) => void) {
  const ws = useRef<WebSocket | null>(null)
  const setWsConnected = useSOCStore((s) => s.setWsConnected)

  const connect = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${window.location.host}/ws/${channel}`
    ws.current = new WebSocket(url)

    ws.current.onopen = () => setWsConnected(true)
    ws.current.onclose = () => {
      setWsConnected(false)
      setTimeout(connect, 3000)
    }
    ws.current.onerror = () => ws.current?.close()
    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage?.(data)
      } catch {}
    }
  }, [channel, onMessage, setWsConnected])

  useEffect(() => {
    connect()
    return () => {
      ws.current?.close()
    }
  }, [connect])

  return ws
}
