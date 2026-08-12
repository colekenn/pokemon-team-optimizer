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
    <div className="card p-4">
      <div className="flex items-baseline gap-3">
        <h3 className="text-sm font-extrabold uppercase tracking-wide text-pokeblue-dark">
          Team score
        </h3>
        <span className="text-3xl font-black text-pokered">{score.toFixed(2)}</span>
        {beforeScore != null && (
          <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-bold text-emerald-700">
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
              <span className="w-44 shrink-0 font-semibold text-slate-600">{label}</span>
              <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-slate-200">
                <div
                  className={`h-full rounded-full ${
                    penalty
                      ? 'bg-gradient-to-r from-rose-400 to-pokered'
                      : 'bg-gradient-to-r from-pokeyellow to-amber-400'
                  }`}
                  style={{ width: `${Math.min(100, v * 100)}%` }}
                />
              </div>
              <span className="w-10 text-right font-bold tabular-nums text-slate-700">
                {v.toFixed(2)}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
