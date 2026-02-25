import { useEffect, useState, useCallback } from 'react'
import { getDashboardSummary, getTimeline, getTopThreats, getTopSources } from '../api/dashboard'
import { useSOCStore } from '../store'
import { useWebSocket } from '../hooks/useWebSocket'
import type { DashboardSummary, TimelinePoint } from '../types'
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { AlertTriangle, Activity, Server, Shield, FileText, Zap } from 'lucide-react'
import AlertBadge from '../components/alerts/AlertBadge'

const KPICard = ({ title, value, icon: Icon, color }: { title: string; value: string | number; icon: React.ElementType; color: string }) => (
  <div className={`bg-soc-panel border border-soc-border rounded-lg p-4 flex items-start gap-3`}>
    <div className={`p-2 rounded ${color} flex-shrink-0`}>
      <Icon size={18} />
    </div>
    <div>
      <p className="text-slate-500 text-xs uppercase tracking-wider">{title}</p>
      <p className="text-2xl font-bold text-slate-100 mt-0.5">{value}</p>
    </div>
  </div>
)

const SEVERITY_COLORS: Record<string, string> = {
  critical: '#ff3366',
  high: '#ff8c00',
  medium: '#ffd700',
  low: '#00d4ff',
}

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [timeline, setTimeline] = useState<TimelinePoint[]>([])
  const [threats, setThreats] = useState<Array<{ type: string; count: number; severity: string }>>([])
  const [sources, setSources] = useState<Array<{ ip: string; count: number }>>([])
  const setDashboardSummary = useSOCStore((s) => s.setDashboardSummary)

  const load = useCallback(async () => {
    try {
      const [s, t, th, so] = await Promise.all([getDashboardSummary(), getTimeline(), getTopThreats(), getTopSources()])
      setSummary(s.data)
      setDashboardSummary(s.data)
      setTimeline(t.data)
      setThreats(th.data)
      setSources(so.data)
    } catch {}
  }, [setDashboardSummary])

  useEffect(() => { load() }, [load])
  useWebSocket('events', () => load())

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
        <KPICard title="Alerts Today" value={summary?.alerts_today ?? 0} icon={AlertTriangle} color="bg-red-900/40 text-soc-red" />
        <KPICard title="Critical" value={summary?.critical_alerts ?? 0} icon={Zap} color="bg-red-900/60 text-red-300" />
        <KPICard title="Open" value={summary?.open_alerts ?? 0} icon={Shield} color="bg-orange-900/40 text-soc-orange" />
        <KPICard title="IDS Alerts" value={summary?.ids_alerts_today ?? 0} icon={Activity} color="bg-purple-900/40 text-purple-400" />
        <KPICard title="Assets" value={summary?.total_assets ?? 0} icon={Server} color="bg-blue-900/40 text-soc-accent" />
        <KPICard title="Logs Today" value={summary?.logs_today?.toLocaleString() ?? 0} icon={FileText} color="bg-green-900/40 text-soc-green" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-2 bg-soc-panel border border-soc-border rounded-lg p-4">
          <h2 className="text-xs uppercase tracking-widest text-slate-400 mb-4">Alert Timeline (24h)</h2>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={timeline}>
              <defs>
                <linearGradient id="timelineGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="time" tick={{ fill: '#475569', fontSize: 10 }} tickFormatter={(v) => v.slice(11, 16)} />
              <YAxis tick={{ fill: '#475569', fontSize: 10 }} />
              <Tooltip contentStyle={{ background: '#0f1629', border: '1px solid #1e2d4a', borderRadius: 4, fontSize: 11 }} labelStyle={{ color: '#94a3b8' }} />
              <Area type="monotone" dataKey="count" stroke="#00d4ff" fill="url(#timelineGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-soc-panel border border-soc-border rounded-lg p-4">
          <h2 className="text-xs uppercase tracking-widest text-slate-400 mb-4">Top Threats</h2>
          <div className="space-y-2">
            {threats.slice(0, 8).map((t, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 min-w-0">
                  <AlertBadge label={t.severity} />
                  <span className="text-slate-300 truncate">{t.type}</span>
                </div>
                <span className="text-slate-400 flex-shrink-0 ml-2">{t.count}</span>
              </div>
            ))}
            {threats.length === 0 && <p className="text-slate-600 text-xs text-center py-4">No threats detected</p>}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <div className="bg-soc-panel border border-soc-border rounded-lg p-4">
          <h2 className="text-xs uppercase tracking-widest text-slate-400 mb-4">Top Source IPs</h2>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={sources.slice(0, 8)} layout="vertical">
              <XAxis type="number" tick={{ fill: '#475569', fontSize: 10 }} />
              <YAxis type="category" dataKey="ip" tick={{ fill: '#94a3b8', fontSize: 10 }} width={110} />
              <Tooltip contentStyle={{ background: '#0f1629', border: '1px solid #1e2d4a', borderRadius: 4, fontSize: 11 }} />
              <Bar dataKey="count" radius={[0, 3, 3, 0]}>
                {sources.slice(0, 8).map((_, i) => (
                  <Cell key={i} fill={`hsl(${200 + i * 15}, 80%, 55%)`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-soc-panel border border-soc-border rounded-lg p-4">
          <h2 className="text-xs uppercase tracking-widest text-slate-400 mb-4">Live Feed</h2>
          <div className="space-y-2 max-h-44 overflow-y-auto">
            {threats.map((t, i) => (
              <div key={i} className="flex items-start gap-2 text-xs border-b border-soc-border/50 pb-1.5">
                <span className={`w-1.5 h-1.5 rounded-full mt-1 flex-shrink-0 pulse-dot ${
                  t.severity === 'critical' ? 'bg-soc-red' :
                  t.severity === 'high' ? 'bg-soc-orange' :
                  t.severity === 'medium' ? 'bg-soc-yellow' : 'bg-soc-accent'
                }`} />
                <div>
                  <span className="text-slate-300">{t.type}</span>
                  <span className="text-slate-600 ml-2">×{t.count}</span>
                </div>
              </div>
            ))}
            {threats.length === 0 && <p className="text-slate-600 text-center py-6">No activity</p>}
          </div>
        </div>
      </div>
    </div>
  )
}
