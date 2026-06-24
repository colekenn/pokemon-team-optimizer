const LABELS: Record<string, string> = {
  offense: 'Offense',
  defense: 'Defense',
  shared_weakness: 'Shared weakness (penalty)',
  stats: 'Base stats',
  roles: 'Role diversity',
  threats: 'Threat coverage',
}

export function ScorePanel({
  breakdown,
  score,
  beforeScore,
}: {
  breakdown: Record<string, number>
  score: number
  beforeScore?: number | null
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
      <div className="flex items-baseline gap-3">
        <h3 className="text-sm font-semibold text-slate-300">Team score</h3>
        <span className="text-2xl font-bold text-sky-400">{score.toFixed(2)}</span>
        {beforeScore != null && (
          <span className="text-xs text-emerald-400">
            ▲ +{(score - beforeScore).toFixed(2)} vs locked-only
          </span>
        )}
      </div>
      <div className="mt-3 space-y-2">
        {Object.entries(LABELS).map(([k, label]) => {
          const v = breakdown[k] ?? 0
          const penalty = k === 'shared_weakness'
          return (
            <div key={k} className="flex items-center gap-2 text-xs">
              <span className="w-44 shrink-0 text-slate-400">{label}</span>
              <div className="h-2 flex-1 overflow-hidden rounded bg-slate-800">
                <div
                  className={`h-full rounded ${penalty ? 'bg-rose-500' : 'bg-sky-500'}`}
                  style={{ width: `${Math.min(100, v * 100)}%` }}
                />
              </div>
              <span className="w-10 text-right tabular-nums text-slate-300">{v.toFixed(2)}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
