import { useEffect, useState, useCallback } from 'react'
import { getIDSStatus, getIDSAlerts, setIDSMode } from '../api/ids'
import type { IDSAlert, IDSStatus } from '../types'
import AlertBadge from '../components/alerts/AlertBadge'
import { Shield, ShieldOff, ShieldAlert, RefreshCw, Activity } from 'lucide-react'

export default function IDSConsole() {
  const [status, setStatus] = useState<IDSStatus | null>(null)
  const [alerts, setAlerts] = useState<IDSAlert[]>([])
  const [loading, setLoading] = useState(false)
  const [modeLoading, setModeLoading] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [s, a] = await Promise.all([getIDSStatus(), getIDSAlerts(100)])
      setStatus(s.data)
      setAlerts(a.data)
    } catch {} finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const changeMode = async (mode: string) => {
    setModeLoading(true)
    try {
      await setIDSMode(mode)
      await load()
    } catch {} finally {
      setModeLoading(false)
    }
  }

  const modeBtn = (mode: string, icon: React.ReactNode, color: string) => (
    <button
      onClick={() => changeMode(mode)}
      disabled={modeLoading || status?.mode === mode}
      className={`flex items-center gap-2 px-4 py-2 rounded border text-xs font-bold uppercase transition-all disabled:opacity-50 ${
        status?.mode === mode
          ? `${color} opacity-100`
          : 'bg-soc-bg border-soc-border text-slate-400 hover:text-slate-200 hover:border-slate-500'
      }`}
    >
      {icon} {mode}
    </button>
  )

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-soc-panel border border-soc-border rounded-lg p-4">
          <h2 className="text-xs uppercase tracking-widest text-slate-400 mb-3">Mode</h2>
          <div className="flex flex-wrap gap-2 mb-4">
            {modeBtn('ids', <Shield size={13} />, 'bg-blue-900/40 border-blue-500/40 text-blue-400')}
            {modeBtn('ips', <ShieldAlert size={13} />, 'bg-red-900/40 border-red-500/40 text-soc-red')}
            {modeBtn('off', <ShieldOff size={13} />, 'bg-slate-700 border-slate-500 text-slate-300')}
          </div>
          <div className="text-xs text-slate-500">
            Interface: <span className="text-slate-300">{status?.interface ?? 'eth0'}</span>
          </div>
        </div>

        <div className="bg-soc-panel border border-soc-border rounded-lg p-4">
          <h2 className="text-xs uppercase tracking-widest text-slate-400 mb-2">Status</h2>
          <div className="flex items-center gap-2 mb-3">
            <span className={`w-2 h-2 rounded-full pulse-dot ${status?.is_running ? 'bg-soc-green' : 'bg-soc-red'}`} />
            <span className="text-sm font-bold text-slate-200">{status?.is_running ? 'RUNNING' : 'STOPPED'}</span>
          </div>
          <div className="text-2xl font-bold text-soc-red">{status?.alerts_today ?? 0}</div>
          <div className="text-xs text-slate-500 mt-0.5">Alerts today</div>
        </div>

        <div className="bg-soc-panel border border-soc-border rounded-lg p-4">
          <h2 className="text-xs uppercase tracking-widest text-slate-400 mb-3">Top Categories</h2>
          <div className="space-y-1.5">
            {(status?.top_categories ?? []).map((c, i) => (
              <div key={i} className="flex justify-between text-xs">
                <span className="text-slate-300 truncate">{c.category}</span>
                <span className="text-soc-accent">{c.count}</span>
              </div>
            ))}
            {(status?.top_categories?.length ?? 0) === 0 && <p className="text-slate-600 text-xs">No data</p>}
          </div>
        </div>
      </div>

      <div className="bg-soc-panel border border-soc-border rounded-lg overflow-hidden">
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-soc-border">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Activity size={13} />
            <span className="uppercase tracking-wider">IDS Alerts</span>
            <span className="text-slate-600">({alerts.length})</span>
          </div>
          <button onClick={load} className="text-slate-500 hover:text-soc-accent transition-colors">
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-soc-border text-slate-500 uppercase tracking-wider">
                {['Timestamp', 'Severity', 'Category', 'Source', 'Destination', 'Protocol', 'Action', 'Rule', 'Message'].map((h) => (
                  <th key={h} className="px-3 py-2 text-left font-medium whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {alerts.map((a, i) => (
                <tr key={a.id ?? i} className="border-b border-soc-border/40 hover:bg-white/[0.02] transition-colors">
                  <td className="px-3 py-1.5 text-slate-500 font-mono whitespace-nowrap">{a.timestamp?.slice(0, 19).replace('T', ' ') ?? '-'}</td>
                  <td className="px-3 py-1.5"><AlertBadge label={a.severity ?? 'info'} /></td>
                  <td className="px-3 py-1.5 text-slate-400">{a.category ?? '-'}</td>
                  <td className="px-3 py-1.5 text-soc-accent font-mono">{a.src_ip ?? '-'}:{a.src_port ?? ''}</td>
                  <td className="px-3 py-1.5 text-slate-300 font-mono">{a.dst_ip ?? '-'}:{a.dst_port ?? ''}</td>
                  <td className="px-3 py-1.5 text-slate-400">{a.protocol ?? '-'}</td>
                  <td className="px-3 py-1.5">
                    <span className={`text-xs font-mono ${a.action === 'drop' ? 'text-soc-red' : 'text-soc-accent'}`}>{a.action ?? 'alert'}</span>
                  </td>
                  <td className="px-3 py-1.5 text-slate-500 font-mono">{a.rule_id ?? '-'}</td>
                  <td className="px-3 py-1.5 text-slate-300 max-w-xs truncate">{a.message ?? '-'}</td>
                </tr>
              ))}
              {alerts.length === 0 && !loading && (
                <tr><td colSpan={9} className="px-3 py-10 text-center text-slate-600">No IDS alerts</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
