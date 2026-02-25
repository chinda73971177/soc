import { useState, useCallback } from 'react'
import { searchLogs, LogSearchParams } from '../api/logs'
import type { LogEntry } from '../types'
import AlertBadge from '../components/alerts/AlertBadge'
import { Search, Filter, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react'

const Input = ({ label, value, onChange, placeholder }: { label: string; value: string; onChange: (v: string) => void; placeholder?: string }) => (
  <div>
    <label className="text-xs text-slate-500 uppercase block mb-1">{label}</label>
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full bg-soc-bg border border-soc-border rounded px-2.5 py-1.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-soc-accent/50"
    />
  </div>
)

const Select = ({ label, value, onChange, options }: { label: string; value: string; onChange: (v: string) => void; options: string[] }) => (
  <div>
    <label className="text-xs text-slate-500 uppercase block mb-1">{label}</label>
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full bg-soc-bg border border-soc-border rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-soc-accent/50"
    >
      <option value="">All</option>
      {options.map((o) => <option key={o} value={o}>{o}</option>)}
    </select>
  </div>
)

export default function LogViewer() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState<LogEntry | null>(null)

  const [filters, setFilters] = useState<LogSearchParams>({
    query: '', severity: '', log_source: '', log_type: '', src_ip: '', dst_ip: '', protocol: '', service: '', page: 1, page_size: 50
  })

  const search = useCallback(async (p = 1) => {
    setLoading(true)
    try {
      const res = await searchLogs({ ...filters, page: p })
      setLogs(res.data.logs)
      setTotal(res.data.total)
      setPage(p)
    } catch {} finally {
      setLoading(false)
    }
  }, [filters])

  const setF = (key: keyof LogSearchParams) => (val: string) => setFilters((f) => ({ ...f, [key]: val }))

  const totalPages = Math.ceil(total / (filters.page_size ?? 50))

  return (
    <div className="space-y-4">
      <div className="bg-soc-panel border border-soc-border rounded-lg p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3 mb-3">
          <div className="col-span-2">
            <Input label="Search" value={filters.query ?? ''} onChange={setF('query')} placeholder="keyword..." />
          </div>
          <Select label="Severity" value={filters.severity ?? ''} onChange={setF('severity')} options={['critical', 'high', 'medium', 'low', 'info']} />
          <Select label="Type" value={filters.log_type ?? ''} onChange={setF('log_type')} options={['system', 'network', 'application', 'firewall']} />
          <Input label="Source IP" value={filters.src_ip ?? ''} onChange={setF('src_ip')} placeholder="192.168.1.1" />
          <Input label="Dest IP" value={filters.dst_ip ?? ''} onChange={setF('dst_ip')} placeholder="10.0.0.1" />
          <Select label="Protocol" value={filters.protocol ?? ''} onChange={setF('protocol')} options={['TCP', 'UDP', 'ICMP']} />
          <Input label="Service" value={filters.service ?? ''} onChange={setF('service')} placeholder="ssh, http..." />
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => search(1)}
            className="flex items-center gap-2 bg-soc-accent/10 hover:bg-soc-accent/20 border border-soc-accent/30 text-soc-accent px-4 py-1.5 rounded text-xs font-bold transition-all"
          >
            <Search size={12} /> SEARCH
          </button>
          <button
            onClick={() => { setFilters({ query: '', severity: '', log_source: '', log_type: '', src_ip: '', dst_ip: '', protocol: '', service: '', page: 1, page_size: 50 }); setLogs([]); setTotal(0) }}
            className="flex items-center gap-2 bg-soc-bg hover:bg-white/5 border border-soc-border text-slate-400 px-4 py-1.5 rounded text-xs transition-all"
          >
            <Filter size={12} /> RESET
          </button>
        </div>
      </div>

      <div className="bg-soc-panel border border-soc-border rounded-lg overflow-hidden">
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-soc-border">
          <span className="text-xs text-slate-400">{total.toLocaleString()} results</span>
          <button onClick={() => search(page)} className="text-slate-500 hover:text-soc-accent transition-colors">
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-soc-border text-slate-500 uppercase tracking-wider">
                {['Timestamp', 'Severity', 'Host', 'Source', 'Type', 'Program', 'Message'].map((h) => (
                  <th key={h} className="px-3 py-2 text-left font-medium whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {logs.map((log, i) => (
                <tr
                  key={log.id ?? i}
                  onClick={() => setSelected(selected?.id === log.id ? null : log)}
                  className={`border-b border-soc-border/40 cursor-pointer transition-colors ${selected?.id === log.id ? 'bg-soc-accent/5' : 'hover:bg-white/[0.02]'}`}
                >
                  <td className="px-3 py-1.5 text-slate-500 whitespace-nowrap font-mono">{log.timestamp?.slice(0, 19).replace('T', ' ') ?? '-'}</td>
                  <td className="px-3 py-1.5"><AlertBadge label={log.severity ?? 'info'} /></td>
                  <td className="px-3 py-1.5 text-slate-300 font-mono">{log.host_name ?? '-'}</td>
                  <td className="px-3 py-1.5 text-soc-accent font-mono">{log.src_ip ?? '-'}</td>
                  <td className="px-3 py-1.5 text-slate-400">{log.log_type ?? '-'}</td>
                  <td className="px-3 py-1.5 text-slate-400">{log.program ?? '-'}</td>
                  <td className="px-3 py-1.5 text-slate-300 max-w-sm truncate">{log.message ?? '-'}</td>
                </tr>
              ))}
              {logs.length === 0 && !loading && (
                <tr><td colSpan={7} className="px-3 py-10 text-center text-slate-600">Run a search to view logs</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {total > 0 && (
          <div className="flex items-center justify-between px-4 py-2 border-t border-soc-border">
            <span className="text-xs text-slate-500">Page {page} of {totalPages}</span>
            <div className="flex gap-1">
              <button disabled={page === 1} onClick={() => search(page - 1)} className="p-1 rounded border border-soc-border text-slate-400 hover:text-soc-accent disabled:opacity-30 transition-colors"><ChevronLeft size={14} /></button>
              <button disabled={page >= totalPages} onClick={() => search(page + 1)} className="p-1 rounded border border-soc-border text-slate-400 hover:text-soc-accent disabled:opacity-30 transition-colors"><ChevronRight size={14} /></button>
            </div>
          </div>
        )}
      </div>

      {selected && (
        <div className="bg-soc-panel border border-soc-accent/20 rounded-lg p-4">
          <h3 className="text-xs uppercase tracking-widest text-soc-accent mb-3">Log Detail</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            {Object.entries(selected).filter(([, v]) => v !== null && v !== undefined && v !== '').map(([k, v]) => (
              <div key={k}>
                <p className="text-slate-500 uppercase text-xs mb-0.5">{k.replace(/_/g, ' ')}</p>
                <p className="text-slate-200 font-mono break-all">{String(v)}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
