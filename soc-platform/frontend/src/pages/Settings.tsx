import { useState } from 'react'
import client from '../api/client'
import { Save, Send } from 'lucide-react'

export default function Settings() {
  const [telegram, setTelegram] = useState({ token: '', chat_id: '' })
  const [whatsapp, setWhatsapp] = useState({ account_sid: '', auth_token: '', from: '', to: '' })
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')

  const testTelegram = async () => {
    setSaving(true)
    try {
      await client.post('/notifications/test', { provider: 'telegram' })
      setMsg('Telegram test sent')
    } catch { setMsg('Failed to send') } finally {
      setSaving(false)
      setTimeout(() => setMsg(''), 3000)
    }
  }

  const testWhatsapp = async () => {
    setSaving(true)
    try {
      await client.post('/notifications/test', { provider: 'whatsapp' })
      setMsg('WhatsApp test sent')
    } catch { setMsg('Failed to send') } finally {
      setSaving(false)
      setTimeout(() => setMsg(''), 3000)
    }
  }

  const Field = ({ label, value, onChange, type = 'text', placeholder = '' }: { label: string; value: string; onChange: (v: string) => void; type?: string; placeholder?: string }) => (
    <div>
      <label className="text-xs text-slate-500 uppercase block mb-1">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-soc-bg border border-soc-border rounded px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-soc-accent/50"
      />
    </div>
  )

  return (
    <div className="space-y-4 max-w-2xl">
      {msg && <div className="bg-soc-green/10 border border-soc-green/30 text-soc-green text-xs px-3 py-2 rounded">{msg}</div>}

      <div className="bg-soc-panel border border-soc-border rounded-lg p-5">
        <h2 className="text-xs uppercase tracking-widest text-slate-400 mb-4">Telegram Notifications</h2>
        <div className="space-y-3">
          <Field label="Bot Token" value={telegram.token} onChange={(v) => setTelegram((t) => ({ ...t, token: v }))} type="password" placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz" />
          <Field label="Chat ID" value={telegram.chat_id} onChange={(v) => setTelegram((t) => ({ ...t, chat_id: v }))} placeholder="-100123456789" />
          <div className="flex gap-2 pt-1">
            <button onClick={testTelegram} disabled={saving} className="flex items-center gap-2 bg-soc-accent/10 hover:bg-soc-accent/20 border border-soc-accent/30 text-soc-accent px-4 py-1.5 rounded text-xs font-bold transition-all disabled:opacity-50">
              <Send size={11} /> Test
            </button>
            <button className="flex items-center gap-2 bg-soc-bg hover:bg-white/5 border border-soc-border text-slate-400 px-4 py-1.5 rounded text-xs transition-all">
              <Save size={11} /> Save
            </button>
          </div>
        </div>
      </div>

      <div className="bg-soc-panel border border-soc-border rounded-lg p-5">
        <h2 className="text-xs uppercase tracking-widest text-slate-400 mb-4">WhatsApp Notifications (Twilio)</h2>
        <div className="space-y-3">
          <Field label="Account SID" value={whatsapp.account_sid} onChange={(v) => setWhatsapp((w) => ({ ...w, account_sid: v }))} type="password" placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" />
          <Field label="Auth Token" value={whatsapp.auth_token} onChange={(v) => setWhatsapp((w) => ({ ...w, auth_token: v }))} type="password" />
          <Field label="From (WhatsApp)" value={whatsapp.from} onChange={(v) => setWhatsapp((w) => ({ ...w, from: v }))} placeholder="whatsapp:+14155238886" />
          <Field label="To (WhatsApp)" value={whatsapp.to} onChange={(v) => setWhatsapp((w) => ({ ...w, to: v }))} placeholder="whatsapp:+1234567890" />
          <div className="flex gap-2 pt-1">
            <button onClick={testWhatsapp} disabled={saving} className="flex items-center gap-2 bg-soc-green/10 hover:bg-soc-green/20 border border-soc-green/30 text-soc-green px-4 py-1.5 rounded text-xs font-bold transition-all disabled:opacity-50">
              <Send size={11} /> Test
            </button>
            <button className="flex items-center gap-2 bg-soc-bg hover:bg-white/5 border border-soc-border text-slate-400 px-4 py-1.5 rounded text-xs transition-all">
              <Save size={11} /> Save
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
