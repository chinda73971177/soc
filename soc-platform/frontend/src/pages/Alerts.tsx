import { useEffect, useState, useCallback } from 'react'
import { getAlerts, updateAlertStatus } from '../api/alerts'
import type { SecurityAlert } from '../types'
import AlertBadge from '../components/alerts/AlertBadge'
import { RefreshCw, Bell } from 'lucide-react'

export default function Alerts() {
  const [alerts, setAlerts] = useState<SecurityAlert[]>([])
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState<SecurityAlert | null>(null)
  const [filterSev, setFilterSev] = useState('')
  const [filterStatus, setFilterStatus] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getAlerts({ severity: filterSev || undefined, status: filterStatus || undefined, limit: 200 })
      setAlerts(res.data)
    } catch {} finally {
      setLoading(false)
    }
  }, [filterSev, filterStatus])

  useEffect(() => { load() }, [load])

  const changeStatus = async (id: string, status: string) => {
    try {
      await updateAlertStatus(id, status)
      setAlerts((prev) => prev.map((a) => a.id === id ? { ...a, status } : a))
      if (selected?.id === id) setSelected((s) => s ? { ...s, status } : s)
    } catch {}
  }

  return (
    <div className="space-y-4">
      <div className="bg-soc-panel border border-soc-border rounded-lg p-3 flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <Bell size={13} />
          <span className="uppercase tracking-wider">Filters</span>
        </div>
        <select
          value={filterSev}
          onChange={(e) => setFilterSev(e.target.value)}
          className="bg-soc-bg border border-soc-border rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-soc-accent/50"
        >
          <option value="">All Severities</option>
          {['critical', 'high', 'medium', 'low', 'info'].map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="bg-soc-bg border border-soc-border rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-soc-accent/50"
        >
          <option value="">All Statuses</option>
          {['open', 'investigating', 'resolved', 'false_positive'].map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <span className="text-xs text-slate-500 ml-auto">{alerts.length} alerts</span>
        <button onClick={load} className="text-slate-500 hover:text-soc-accent transition-colors">
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-2 bg-soc-panel border border-soc-border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-soc-border text-slate-500 uppercase tracking-wider">
                  {['Time', 'Severity', 'Type', 'Title', 'Source', 'Dest', 'Status'].map((h) => (
                    <th key={h} className="px-3 py-2 text-left font-medium whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {alerts.map((a, i) => (
                  <tr
                    key={a.id ?? i}
                    onClick={() => setSelected(selected?.id === a.id ? null : a)}
                    className={`border-b border-soc-border/40 cursor-pointer transition-colors ${selected?.id === a.id ? 'bg-soc-accent/5' : 'hover:bg-white/[0.02]'}`}
                  >
                    <td className="px-3 py-2 text-slate-500 font-mono whitespace-nowrap">{a.created_at?.slice(0, 19).replace('T', ' ') ?? '-'}</td>
                    <td className="px-3 py-2"><AlertBadge label={a.severity} /></td>
                    <td className="px-3 py-2 text-slate-400">{a.alert_type}</td>
                    <td className="px-3 py-2 text-slate-200 max-w-xs truncate">{a.title}</td>
                    <td className="px-3 py-2 text-soc-accent font-mono">{a.source_ip ?? '-'}</td>
                    <td className="px-3 py-2 text-slate-300 font-mono">{a.destination_ip ?? '-'}</td>
                    <td className="px-3 py-2"><AlertBadge label={a.status} /></td>
                  </tr>
                ))}
                {alerts.length === 0 && !loading && (
                  <tr><td colSpan={7} className="px-3 py-10 text-center text-slate-600">No alerts found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {selected && (
          <div className="bg-soc-panel border border-soc-accent/20 rounded-lg p-4">
            <h3 className="text-xs uppercase tracking-widest text-soc-accent mb-3">Alert Detail</h3>
            <div className="space-y-3 text-xs">
              <div><p className="text-slate-500 uppercase mb-0.5">Title</p><p className="text-slate-200">{selected.title}</p></div>
              {selected.description && <div><p className="text-slate-500 uppercase mb-0.5">Description</p><p className="text-slate-300">{selected.description}</p></div>}
              <div className="grid grid-cols-2 gap-2">
                {[['Type', selected.alert_type], ['Severity', selected.severity], ['Protocol', selected.protocol], ['Service', selected.service], ['Source IP', selected.source_ip], ['Source Port', selected.source_port], ['Dest IP', selected.destination_ip], ['Dest Port', selected.destination_port], ['Rule', selected.rule_id]].map(([k, v]) => v && (
                  <div key={String(k)}>
                    <p className="text-slate-500 uppercase text-xs mb-0.5">{k}</p>
                    <p className="text-slate-300 font-mono">{String(v)}</p>
                  </div>
                ))}
              </div>
              <div>
                <p className="text-slate-500 uppercase mb-2">Actions</p>
                <div className="flex flex-wrap gap-1.5">
                  {['investigating', 'resolved', 'false_positive'].map((s) => (
                    <button
                      key={s}
                      onClick={() => changeStatus(selected.id!, s)}
                      disabled={selected.status === s}
                      className="px-2.5 py-1 rounded border border-soc-border text-slate-400 hover:text-soc-accent hover:border-soc-accent/40 text-xs transition-all disabled:opacity-30 uppercase"
                    >
                      {s.replace('_', ' ')}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
