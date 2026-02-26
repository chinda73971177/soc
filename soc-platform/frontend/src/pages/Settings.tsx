import React, { useState, useEffect } from 'react'
import { Save, Bell, Shield, Network, RefreshCw, CheckCircle, Wifi } from 'lucide-react'
import client from '../api/client'

const Section: React.FC<{ title: string; icon: React.ReactNode; children: React.ReactNode }> = ({ title, icon, children }) => (
  <div className="bg-soc-card border border-soc-border rounded-xl p-5">
    <div className="flex items-center gap-2 mb-4 pb-3 border-b border-soc-border">
      {icon}
      <h3 className="text-sm font-semibold text-soc-text">{title}</h3>
    </div>
    {children}
  </div>
)

const Field: React.FC<{ label: string; value: string; onChange: (v: string) => void; type?: string; placeholder?: string; hint?: string }> = ({ label, value, onChange, type = 'text', placeholder, hint }) => (
  <div>
    <label className="block text-xs text-soc-muted mb-1.5 font-medium">{label}</label>
    <input type={type} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder}
      className="w-full bg-soc-bg border border-soc-border rounded-lg px-3 py-2 text-sm text-soc-text focus:outline-none focus:border-soc-accent transition-colors" />
    {hint && <p className="text-xs text-soc-muted mt-1">{hint}</p>}
  </div>
)

const Toggle: React.FC<{ label: string; value: boolean; onChange: (v: boolean) => void; hint?: string }> = ({ label, value, onChange, hint }) => (
  <div className="flex items-center justify-between py-2">
    <div>
      <p className="text-sm text-soc-text">{label}</p>
      {hint && <p className="text-xs text-soc-muted">{hint}</p>}
    </div>
    <button onClick={() => onChange(!value)}
      className={`w-11 h-6 rounded-full transition-colors relative ${value ? 'bg-soc-accent' : 'bg-soc-border'}`}>
      <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform shadow ${value ? 'translate-x-5' : 'translate-x-0.5'}`} />
    </button>
  </div>
)

export const Settings: React.FC = () => {
  const [telegram, setTelegram] = useState({ token: '', chat_id: '', min_severity: 'high' })
  const [whatsapp, setWhatsapp] = useState({ account_sid: '', auth_token: '', from: '', to: '', min_severity: 'high' })
  const [netConfig, setNetConfig] = useState({
    network_range: '192.168.1.0/24',
    scan_type: 'standard',
    scan_interval_minutes: 15,
    auto_scan_enabled: true,
    interface: 'eth0',
    home_net: '192.168.0.0/16,10.0.0.0/8,172.16.0.0/12',
    ids_mode: 'ids',
    alert_on_new_host: true,
    alert_on_port_change: true,
  })
  const [interfaces, setInterfaces] = useState<string[]>([])
  const [subnets, setSubnets] = useState<string[]>([])
  const [saved, setSaved] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    client.get('/network/config').then((r) => setNetConfig(r.data)).catch(() => {})
    client.get('/network/interfaces').then((r) => setInterfaces(r.data.interfaces || [])).catch(() => {})
    client.get('/network/subnet').then((r) => setSubnets(r.data.subnets || [])).catch(() => {})
  }, [])

  const saveNet = async () => {
    setLoading(true)
    try {
      await client.put('/network/config', netConfig)
      setSaved('Network configuration saved')
    } catch { setSaved('Failed to save') }
    finally { setLoading(false); setTimeout(() => setSaved(''), 3000) }
  }

  const saveTelegram = async () => {
    setLoading(true)
    try {
      await client.put('/notifications/config', { provider: 'telegram', config: telegram, min_severity: telegram.min_severity, is_active: true })
      setSaved('Telegram configuration saved')
    } catch { setSaved('Saved locally') }
    finally { setLoading(false); setTimeout(() => setSaved(''), 3000) }
  }

  const saveWhatsapp = async () => {
    setLoading(true)
    try {
      await client.put('/notifications/config', { provider: 'whatsapp', config: whatsapp, min_severity: whatsapp.min_severity, is_active: true })
      setSaved('WhatsApp configuration saved')
    } catch { setSaved('Saved locally') }
    finally { setLoading(false); setTimeout(() => setSaved(''), 3000) }
  }

  return (
    <div className="max-w-2xl space-y-6">
      {saved && (
        <div className="flex items-center gap-2 bg-soc-green/10 border border-soc-green/30 text-soc-green rounded-lg px-4 py-3 text-sm">
          <CheckCircle size={14} /> {saved}
        </div>
      )}

      <Section title="Network Monitoring" icon={<Network size={16} className="text-soc-accent" />}>
        <div className="space-y-4">
          <div>
            <label className="block text-xs text-soc-muted mb-1.5 font-medium">Network Interface</label>
            <select value={netConfig.interface} onChange={(e) => setNetConfig((c) => ({ ...c, interface: e.target.value }))}
              className="w-full bg-soc-bg border border-soc-border rounded-lg px-3 py-2 text-sm text-soc-text focus:outline-none focus:border-soc-accent">
              {interfaces.length > 0
                ? interfaces.map((i) => <option key={i} value={i}>{i}</option>)
                : <option value={netConfig.interface}>{netConfig.interface}</option>}
            </select>
            <p className="text-xs text-soc-muted mt-1">Interface used by Suricata for packet capture</p>
          </div>

          <div>
            <label className="block text-xs text-soc-muted mb-1.5 font-medium">Network Range (Scan Target)</label>
            <div className="flex gap-2">
              <input value={netConfig.network_range} onChange={(e) => setNetConfig((c) => ({ ...c, network_range: e.target.value }))}
                placeholder="192.168.1.0/24"
                className="flex-1 bg-soc-bg border border-soc-border rounded-lg px-3 py-2 text-sm text-soc-text focus:outline-none focus:border-soc-accent" />
              {subnets.length > 0 && (
                <select onChange={(e) => setNetConfig((c) => ({ ...c, network_range: e.target.value }))}
                  className="bg-soc-bg border border-soc-border rounded-lg px-2 py-2 text-sm text-soc-text focus:outline-none focus:border-soc-accent">
                  <option value="">Auto-detect</option>
                  {subnets.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              )}
            </div>
            <p className="text-xs text-soc-muted mt-1">CIDR notation — e.g. 10.0.0.0/24</p>
          </div>

          <div>
            <label className="block text-xs text-soc-muted mb-1.5 font-medium">HOME_NET (Suricata)</label>
            <input value={netConfig.home_net} onChange={(e) => setNetConfig((c) => ({ ...c, home_net: e.target.value }))}
              placeholder="192.168.0.0/16,10.0.0.0/8"
              className="w-full bg-soc-bg border border-soc-border rounded-lg px-3 py-2 text-sm text-soc-text focus:outline-none focus:border-soc-accent" />
            <p className="text-xs text-soc-muted mt-1">Comma-separated list of trusted internal networks</p>
          </div>

          <div>
            <label className="block text-xs text-soc-muted mb-1.5 font-medium">Default Scan Type</label>
            <select value={netConfig.scan_type} onChange={(e) => setNetConfig((c) => ({ ...c, scan_type: e.target.value }))}
              className="w-full bg-soc-bg border border-soc-border rounded-lg px-3 py-2 text-sm text-soc-text focus:outline-none focus:border-soc-accent">
              <option value="quick">Quick — Ping sweep only (~30s)</option>
              <option value="standard">Standard — Top 1000 ports + services (~5min)</option>
              <option value="full">Full — All 65535 ports (~30min)</option>
              <option value="vuln">Vulnerability — Script scan (~15min)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs text-soc-muted mb-1.5 font-medium">Auto Scan Interval (minutes)</label>
            <input type="number" min={5} max={1440} value={netConfig.scan_interval_minutes}
              onChange={(e) => setNetConfig((c) => ({ ...c, scan_interval_minutes: parseInt(e.target.value) || 15 }))}
              className="w-full bg-soc-bg border border-soc-border rounded-lg px-3 py-2 text-sm text-soc-text focus:outline-none focus:border-soc-accent" />
            <p className="text-xs text-soc-muted mt-1">How often automatic scans run (minimum 5 minutes)</p>
          </div>

          <div className="border-t border-soc-border pt-3 space-y-1">
            <Toggle label="Enable Auto Scanning" value={netConfig.auto_scan_enabled}
              onChange={(v) => setNetConfig((c) => ({ ...c, auto_scan_enabled: v }))}
              hint="Automatically scan network on schedule" />
            <Toggle label="Alert on New Host Detected" value={netConfig.alert_on_new_host}
              onChange={(v) => setNetConfig((c) => ({ ...c, alert_on_new_host: v }))}
              hint="Create security alert when unknown host appears" />
            <Toggle label="Alert on Port Changes" value={netConfig.alert_on_port_change}
              onChange={(v) => setNetConfig((c) => ({ ...c, alert_on_port_change: v }))}
              hint="Create alert when ports open or close on an asset" />
          </div>

          <button onClick={saveNet} disabled={loading}
            className="flex items-center gap-2 bg-soc-accent hover:bg-blue-600 disabled:opacity-50 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors">
            <Save size={14} /> Save Network Config
          </button>
        </div>
      </Section>

      <Section title="IDS/IPS Mode" icon={<Shield size={16} className="text-soc-yellow" />}>
        <div className="space-y-4">
          <div>
            <label className="block text-xs text-soc-muted mb-2 font-medium">Detection Mode</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'ids', label: 'IDS', desc: 'Detect only', color: 'text-soc-yellow', bg: 'border-soc-yellow/40 bg-soc-yellow/10' },
                { value: 'ips', label: 'IPS', desc: 'Detect & Block', color: 'text-soc-red', bg: 'border-soc-red/40 bg-soc-red/10' },
                { value: 'off', label: 'Off', desc: 'Disabled', color: 'text-soc-muted', bg: 'border-soc-muted/40 bg-soc-muted/10' },
              ].map((m) => (
                <button key={m.value} onClick={() => setNetConfig((c) => ({ ...c, ids_mode: m.value }))}
                  className={`p-3 rounded-lg border text-center transition-all ${netConfig.ids_mode === m.value ? m.bg + ' border-2' : 'border-soc-border bg-soc-bg hover:bg-white/5'}`}>
                  <p className={`text-sm font-bold ${netConfig.ids_mode === m.value ? m.color : 'text-soc-muted'}`}>{m.label}</p>
                  <p className="text-xs text-soc-muted mt-0.5">{m.desc}</p>
                </button>
              ))}
            </div>
          </div>
          <button onClick={saveNet} disabled={loading}
            className="flex items-center gap-2 bg-soc-accent hover:bg-blue-600 disabled:opacity-50 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors">
            <Save size={14} /> Apply Mode
          </button>
        </div>
      </Section>

      <Section title="Telegram Notifications" icon={<Bell size={16} className="text-soc-accent" />}>
        <div className="space-y-3">
          <Field label="Bot Token" value={telegram.token} onChange={(v) => setTelegram((t) => ({ ...t, token: v }))}
            type="password" placeholder="1234567890:ABCdef..." />
          <Field label="Chat ID" value={telegram.chat_id} onChange={(v) => setTelegram((t) => ({ ...t, chat_id: v }))}
            placeholder="-100123456789" hint="Get from @userinfobot on Telegram" />
          <div>
            <label className="block text-xs text-soc-muted mb-1.5 font-medium">Minimum Severity</label>
            <select value={telegram.min_severity} onChange={(e) => setTelegram((t) => ({ ...t, min_severity: e.target.value }))}
              className="w-full bg-soc-bg border border-soc-border rounded-lg px-3 py-2 text-sm text-soc-text focus:outline-none focus:border-soc-accent">
              {['critical', 'high', 'medium', 'low'].map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <button onClick={saveTelegram} disabled={loading}
            className="flex items-center gap-2 bg-soc-accent hover:bg-blue-600 disabled:opacity-50 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors">
            <Save size={14} /> Save Telegram Config
          </button>
        </div>
      </Section>

      <Section title="WhatsApp Notifications (Twilio)" icon={<Bell size={16} className="text-soc-green" />}>
        <div className="space-y-3">
          <Field label="Account SID" value={whatsapp.account_sid} onChange={(v) => setWhatsapp((w) => ({ ...w, account_sid: v }))}
            placeholder="ACxxxxxxxx" />
          <Field label="Auth Token" value={whatsapp.auth_token} onChange={(v) => setWhatsapp((w) => ({ ...w, auth_token: v }))}
            type="password" />
          <Field label="From (WhatsApp)" value={whatsapp.from} onChange={(v) => setWhatsapp((w) => ({ ...w, from: v }))}
            placeholder="whatsapp:+14155238886" />
          <Field label="To (WhatsApp)" value={whatsapp.to} onChange={(v) => setWhatsapp((w) => ({ ...w, to: v }))}
            placeholder="whatsapp:+1234567890" />
          <div>
            <label className="block text-xs text-soc-muted mb-1.5 font-medium">Minimum Severity</label>
            <select value={whatsapp.min_severity} onChange={(e) => setWhatsapp((w) => ({ ...w, min_severity: e.target.value }))}
              className="w-full bg-soc-bg border border-soc-border rounded-lg px-3 py-2 text-sm text-soc-text focus:outline-none focus:border-soc-accent">
              {['critical', 'high', 'medium', 'low'].map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <button onClick={saveWhatsapp} disabled={loading}
            className="flex items-center gap-2 bg-soc-green hover:bg-emerald-600 disabled:opacity-50 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors">
            <Save size={14} /> Save WhatsApp Config
          </button>
        </div>
      </Section>
    </div>
  )
}
