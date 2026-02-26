import clsx from 'clsx'

const cfg: Record<string, string> = {
  critical: 'bg-red-900/50 text-red-400 border border-red-700/50',
  high: 'bg-orange-900/50 text-orange-400 border border-orange-700/50',
  medium: 'bg-yellow-900/50 text-yellow-400 border border-yellow-700/50',
  low: 'bg-blue-900/50 text-blue-400 border border-blue-700/50',
  info: 'bg-slate-800 text-slate-400 border border-slate-700',
  open: 'bg-red-900/40 text-red-400 border border-red-800/50',
  investigating: 'bg-yellow-900/40 text-yellow-400 border border-yellow-800/50',
  resolved: 'bg-green-900/40 text-green-400 border border-green-800/50',
  false_positive: 'bg-slate-800 text-slate-400 border border-slate-700',
}

export default function AlertBadge({ label, type = 'severity' }: { label: string; type?: string }) {
  return (
    <span className={clsx('px-2 py-0.5 rounded text-xs font-mono uppercase', cfg[label] ?? 'bg-slate-800 text-slate-400')}>
      {label}
    </span>
  )
}
