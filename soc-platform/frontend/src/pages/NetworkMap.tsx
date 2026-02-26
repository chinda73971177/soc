import { useEffect, useState, useCallback } from 'react'
import { getAssets, startScan, getNetworkChanges, ackChange } from '../api/network'
import type { Asset, NetworkChange } from '../types'
import PortBadge from '../components/network/PortBadge'
import AlertBadge from '../components/alerts/AlertBadge'
import { Search, RefreshCw, Monitor, Server, Globe, CheckCircle } from 'lucide-react'

export default function NetworkMap() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [changes, setChanges] = useState<NetworkChange[]>([])
  const [selected, setSelected] = useState<Asset | null>(null)
  const [scanTarget, setScanTarget] = useState('')
  const [scanType, setScanType] = useState('standard')
  const [scanning, setScanning] = useState(false)
  const [loading, setLoading] = useState(false)
  const [filter, setFilter] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [a, c] = await Promise.all([getAssets(), getNetworkChanges()])
      setAssets(a.data)
      setChanges(c.data)
    } catch {} finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const scan = async () => {
    if (!scanTarget) return
    setScanning(true)
    try {
      await startScan(scanTarget, scanType)
      setTimeout(load, 3000)
    } catch {} finally {
      setScanning(false)
    }
  }

  const handleAck = async (id: string) => {
    try {
      await ackChange(id)
      setChanges((prev) => prev.map((c) => c.id === id ? { ...c, acknowledged: true } : c))
    } catch {}
  }

  const filtered = assets.filter((a) =>
    !filter || a.ip_address.includes(filter) || (a.hostname?.toLowerCase().includes(filter.toLowerCase()))
  )

  const AssetIcon = ({ type }: { type?: string }) => {
    if (type === 'server') return <Server size={14} />
    if (type === 'network') return <Globe size={14} />
    return <Monitor size={14} />
  }

  return (
    <div className="space-y-4">
      <div className="bg-soc-panel border border-soc-border rounded-lg p-4 flex flex-wrap gap-3 items-end">
        <div>
          <label className="text-xs text-slate-500 uppercase block mb-1">Target</label>
          <input
            value={scanTarget}
            onChange={(e) => setScanTarget(e.target.value)}
            placeholder="192.168.1.0/24 or host"
            className="bg-soc-bg border border-soc-border rounded px-3 py-1.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-soc-accent/50 w-52"
          />
        </div>
        <div>
          <label className="text-xs text-slate-500 uppercase block mb-1">Type</label>
          <select
            value={scanType}
            onChange={(e) => setScanType(e.target.value)}
            className="bg-soc-bg border border-soc-border rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-soc-accent/50"
          >
            <option value="quick">Quick (ping)</option>
            <option value="standard">Standard</option>
            <option value="full">Full</option>
            <option value="vuln">Vuln Scan</option>
          </select>
        </div>
        <button
          onClick={scan}
          disabled={scanning || !scanTarget}
          className="flex items-center gap-2 bg-soc-accent/10 hover:bg-soc-accent/20 border border-soc-accent/30 text-soc-accent px-4 py-1.5 rounded text-xs font-bold transition-all disabled:opacity-50"
        >
          <Search size={12} className={scanning ? 'animate-spin' : ''} />
          {scanning ? 'SCANNING...' : 'SCAN'}
        </button>
        <div className="ml-auto flex items-center gap-2">
          <input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter assets..."
            className="bg-soc-bg border border-soc-border rounded px-3 py-1.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-soc-accent/50 w-40"
          />
          <button onClick={load} className="text-slate-500 hover:text-soc-accent transition-colors">
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-2 bg-soc-panel border border-soc-border rounded-lg overflow-hidden">
          <div className="px-4 py-2.5 border-b border-soc-border text-xs text-slate-400 uppercase tracking-wider">
            Assets ({filtered.length})
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-soc-border text-slate-500 uppercase tracking-wider">
                  {['IP Address', 'Hostname', 'OS', 'Type', 'Criticality', 'Last Seen', 'Open Ports'].map((h) => (
                    <th key={h} className="px-3 py-2 text-left font-medium whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((asset, i) => (
                  <tr
                    key={asset.id ?? i}
                    onClick={() => setSelected(selected?.id === asset.id ? null : asset)}
                    className={`border-b border-soc-border/40 cursor-pointer transition-colors ${selected?.id === asset.id ? 'bg-soc-accent/5' : 'hover:bg-white/[0.02]'}`}
                  >
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-2">
                        <span className={`w-1.5 h-1.5 rounded-full ${asset.is_active ? 'bg-soc-green' : 'bg-soc-red'}`} />
                        <span className="text-soc-accent font-mono">{asset.ip_address}</span>
                      </div>
                    </td>
                    <td className="px-3 py-2 text-slate-300">{asset.hostname ?? '-'}</td>
                    <td className="px-3 py-2 text-slate-400">{asset.os_type ?? '-'}</td>
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-1 text-slate-400">
                        <AssetIcon type={asset.asset_type} />
                        <span>{asset.asset_type ?? 'unknown'}</span>
                      </div>
                    </td>
                    <td className="px-3 py-2"><AlertBadge label={asset.criticality} /></td>
                    <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{asset.last_seen?.slice(0, 10) ?? '-'}</td>
                    <td className="px-3 py-2 text-soc-green">{asset.ports?.filter((p) => p.state === 'open').length ?? 0}</td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr><td colSpan={7} className="px-3 py-10 text-center text-slate-600">No assets found. Run a scan to discover hosts.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="space-y-4">
          {selected && (
            <div className="bg-soc-panel border border-soc-accent/20 rounded-lg p-4">
              <h3 className="text-xs uppercase tracking-widest text-soc-accent mb-3">{selected.ip_address}</h3>
              <div className="space-y-1.5 text-xs mb-3">
                {[['Hostname', selected.hostname], ['OS', selected.os_type], ['Type', selected.asset_type], ['Criticality', selected.criticality]].map(([k, v]) => v && (
                  <div key={k} className="flex justify-between">
                    <span className="text-slate-500">{k}</span>
                    <span className="text-slate-300">{v}</span>
                  </div>
                ))}
              </div>
              {selected.ports && selected.ports.length > 0 && (
                <div>
                  <p className="text-xs text-slate-500 uppercase mb-2">Ports</p>
                  <div className="flex flex-wrap gap-1">
                    {selected.ports.map((p, i) => <PortBadge key={i} {...p} />)}
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="bg-soc-panel border border-soc-border rounded-lg overflow-hidden">
            <div className="px-4 py-2.5 border-b border-soc-border text-xs text-slate-400 uppercase tracking-wider">
              Network Changes
            </div>
            <div className="max-h-64 overflow-y-auto">
              {changes.map((c, i) => (
                <div key={c.id ?? i} className={`px-3 py-2.5 border-b border-soc-border/40 text-xs ${c.acknowledged ? 'opacity-40' : ''}`}>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-slate-400 uppercase">{c.change_type}</span>
                      <div className="text-slate-500 mt-0.5">{c.detected_at?.slice(0, 19).replace('T', ' ')}</div>
                    </div>
                    {!c.acknowledged && (
                      <button onClick={() => handleAck(c.id)} className="text-slate-600 hover:text-soc-green transition-colors flex-shrink-0">
                        <CheckCircle size={14} />
                      </button>
                    )}
                  </div>
                </div>
              ))}
              {changes.length === 0 && <p className="text-xs text-slate-600 text-center py-4">No changes detected</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
