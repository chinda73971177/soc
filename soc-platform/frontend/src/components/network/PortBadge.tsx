import clsx from 'clsx'

const stateColors: Record<string, string> = {
  open: 'text-soc-green border-green-700/40 bg-green-900/20',
  closed: 'text-slate-500 border-slate-700 bg-slate-800/40',
  filtered: 'text-yellow-400 border-yellow-700/40 bg-yellow-900/20',
}

export default function PortBadge({ port, protocol, service, state }: { port: number; protocol: string; service?: string; state: string }) {
  return (
    <span className={clsx('inline-flex items-center gap-1 px-2 py-0.5 rounded border text-xs font-mono', stateColors[state] ?? stateColors.filtered)}>
      <span>{port}/{protocol}</span>
      {service && <span className="text-slate-400">({service})</span>}
    </span>
  )
}
