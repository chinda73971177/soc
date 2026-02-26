import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  Shield,
  Network,
  Bell,
  Settings,
  LogOut,
} from 'lucide-react'
import { useSOCStore } from '../../store'

const nav = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/logs', icon: FileText, label: 'Logs' },
  { to: '/ids', icon: Shield, label: 'IDS/IPS' },
  { to: '/network', icon: Network, label: 'Network' },
  { to: '/alerts', icon: Bell, label: 'Alerts' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
  const setAuthenticated = useSOCStore((s) => s.setAuthenticated)
  const setUser = useSOCStore((s) => s.setUser)

  const logout = () => {
    localStorage.clear()
    setAuthenticated(false)
    setUser(null)
    window.location.href = '/login'
  }

  return (
    <aside className="w-16 lg:w-56 bg-soc-panel border-r border-soc-border flex flex-col">
      <div className="p-4 border-b border-soc-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-soc-accent rounded flex items-center justify-center text-soc-bg font-bold text-sm flex-shrink-0">
            S
          </div>
          <span className="hidden lg:block text-soc-accent font-bold text-sm tracking-widest uppercase">
            SOC Platform
          </span>
        </div>
      </div>

      <nav className="flex-1 p-2 space-y-1">
        {nav.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded text-sm transition-all duration-150 ${
                isActive
                  ? 'bg-soc-accent/10 text-soc-accent border border-soc-accent/30 glow-cyan'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              }`
            }
          >
            <Icon size={16} className="flex-shrink-0" />
            <span className="hidden lg:block">{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-2 border-t border-soc-border">
        <button
          onClick={logout}
          className="flex items-center gap-3 px-3 py-2.5 w-full rounded text-sm text-slate-400 hover:text-soc-red hover:bg-soc-red/10 transition-all"
        >
          <LogOut size={16} className="flex-shrink-0" />
          <span className="hidden lg:block">Logout</span>
        </button>
      </div>
    </aside>
  )
}
