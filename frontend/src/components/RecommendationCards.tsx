import type { Recommendation } from '../api/client'
import { TypeBadge } from './TypeBadge'

export function RecommendationCards({
  recommendations,
  onReplace,
}: {
  recommendations: Recommendation[]
  onReplace: (speciesId: number) => void
}) {
  if (!recommendations.length) return null
  return (
    <div>
      <h3 className="mb-2 text-sm font-semibold text-slate-300">Why these picks</h3>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {recommendations.map((r) => (
          <div key={r.species.id} className="rounded-xl border border-slate-800 bg-slate-900 p-3">
            <div className="flex items-center gap-3">
              {r.species.sprite_url && (
                <img src={r.species.sprite_url} alt={r.species.name} className="h-14 w-14 object-contain" />
              )}
              <div>
                <div className="text-sm font-semibold capitalize">{r.species.name}</div>
                <div className="mt-0.5 flex gap-1">
                  {r.species.types.map((t) => <TypeBadge key={t} type={t} small />)}
                </div>
                <div className="mt-0.5 text-[10px] uppercase text-slate-500">{r.species.role}</div>
              </div>
              <button
                onClick={() => onReplace(r.species.id)}
                title="Re-optimize without this Pokémon"
                className="ml-auto rounded-lg border border-slate-700 px-2 py-1 text-xs text-slate-400 hover:border-rose-500 hover:text-rose-400"
              >
                Replace
              </button>
            </div>
            <ul className="mt-2 space-y-1 text-xs text-slate-400">
              {r.reasons.map((reason, i) => (
                <li key={i} className="flex gap-1.5">
                  <span className="text-sky-500">▸</span>
                  {reason}
                </li>
              ))}
            </ul>
            <div className="mt-2 text-[10px] text-slate-500">
              net score contribution:{' '}
              <span className={r.marginal_contribution.total >= 0 ? 'text-emerald-400' : 'text-rose-400'}>
                {r.marginal_contribution.total >= 0 ? '+' : ''}
                {r.marginal_contribution.total?.toFixed(2)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
