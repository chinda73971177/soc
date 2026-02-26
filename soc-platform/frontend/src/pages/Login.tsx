import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSOCStore } from '../store'
import client from '../api/client'
import { Shield, Eye, EyeOff } from 'lucide-react'

export default function Login() {
  const navigate = useNavigate()
  const setAuthenticated = useSOCStore((s) => s.setAuthenticated)
  const setUser = useSOCStore((s) => s.setUser)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await client.post('/auth/login', { username, password })
      localStorage.setItem('access_token', res.data.access_token)
      localStorage.setItem('refresh_token', res.data.refresh_token)
      const me = await client.get('/auth/me')
      setUser(me.data)
      setAuthenticated(true)
      navigate('/dashboard')
    } catch {
      setError('Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-soc-bg flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-soc-accent/10 border border-soc-accent/30 rounded-xl mb-4 glow-cyan">
            <Shield size={32} className="text-soc-accent" />
          </div>
          <h1 className="text-xl font-bold text-slate-100">SOC Platform</h1>
          <p className="text-slate-500 text-sm mt-1">Security Operations Center</p>
        </div>

        <form onSubmit={submit} className="bg-soc-panel border border-soc-border rounded-xl p-6 space-y-4">
          {error && (
            <div className="bg-soc-red/10 border border-soc-red/30 text-soc-red text-sm px-3 py-2 rounded">
              {error}
            </div>
          )}

          <div>
            <label className="text-xs text-slate-400 uppercase tracking-wider block mb-1.5">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-soc-bg border border-soc-border rounded px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-soc-accent/60 transition-colors"
              placeholder="admin"
              required
            />
          </div>

          <div>
            <label className="text-xs text-slate-400 uppercase tracking-wider block mb-1.5">Password</label>
            <div className="relative">
              <input
                type={showPw ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-soc-bg border border-soc-border rounded px-3 py-2 pr-10 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-soc-accent/60 transition-colors"
                placeholder="••••••••"
                required
              />
              <button
                type="button"
                onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
              >
                {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-soc-accent/10 hover:bg-soc-accent/20 border border-soc-accent/40 text-soc-accent font-bold py-2.5 rounded text-sm transition-all duration-200 disabled:opacity-50 glow-cyan"
          >
            {loading ? 'Authenticating...' : 'LOGIN'}
          </button>

          <p className="text-center text-xs text-slate-600">Default: admin / admin</p>
        </form>
      </div>
    </div>
  )
}
