import { useLocation } from 'react-router-dom'
import { useSOCStore } from '../../store'
import { Wifi, WifiOff, Clock } from 'lucide-react'
import { useState, useEffect } from 'react'

const titles: Record<string, string> = {
  '/dashboard': 'SOC Dashboard',
  '/logs': 'Log Viewer',
  '/ids': 'IDS / IPS Console',
  '/network': 'Network Map',
  '/alerts': 'Security Alerts',
  '/settings': 'Settings',
}

export default function TopBar() {
  const location = useLocation()
  const wsConnected = useSOCStore((s) => s.wsConnected)
  const user = useSOCStore((s) => s.user)
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  return (
    <header className="h-12 bg-soc-panel border-b border-soc-border flex items-center px-4 gap-4 flex-shrink-0">
      <h1 className="text-sm font-bold text-slate-200 flex-1">
        {titles[location.pathname] ?? 'SOC Platform'}
      </h1>

      <div className="flex items-center gap-4 text-xs text-slate-500">
        <div className="flex items-center gap-1.5">
          <Clock size={12} />
          <span className="font-mono">{time.toUTCString().slice(17, 25)} UTC</span>
        </div>

        <div className={`flex items-center gap-1.5 ${wsConnected ? 'text-soc-green' : 'text-soc-red'}`}>
          {wsConnected ? <Wifi size={12} /> : <WifiOff size={12} />}
          <span>{wsConnected ? 'LIVE' : 'OFFLINE'}</span>
        </div>

        {user && (
          <div className="flex items-center gap-2 pl-3 border-l border-soc-border">
            <div className="w-6 h-6 bg-soc-accent/20 border border-soc-accent/40 rounded text-soc-accent text-xs flex items-center justify-center uppercase font-bold">
              {user.username[0]}
            </div>
            <div className="hidden lg:block">
              <div className="text-slate-300 text-xs">{user.username}</div>
              <div className="text-slate-500 text-xs uppercase">{user.role}</div>
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
