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
      <h3 className="mb-2 text-sm font-extrabold uppercase tracking-wide text-pokeblue-dark">
        Why these picks
      </h3>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {recommendations.map((r) => (
          <div key={r.species.id} className="card p-3">
            <div className="flex items-center gap-3">
              {r.species.sprite_url && (
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-gradient-to-b from-sky-100 to-white shadow-inner">
                  <img src={r.species.sprite_url} alt={r.species.name} className="h-14 w-14 object-contain" />
                </div>
              )}
              <div>
                <div className="text-sm font-extrabold capitalize text-slate-800">{r.species.name}</div>
                <div className="mt-0.5 flex gap-1">
                  {r.species.types.map((t) => <TypeBadge key={t} type={t} small />)}
                </div>
                <div className="mt-0.5 text-[10px] font-bold uppercase text-pokeblue/70">{r.species.role}</div>
              </div>
              <button
                onClick={() => onReplace(r.species.id)}
                title="Re-optimize without this Pokémon"
                className="ml-auto rounded-full border-2 border-slate-300 px-3 py-1 text-xs font-bold text-slate-500 transition hover:border-pokered hover:text-pokered"
              >
                Replace
              </button>
            </div>
            <ul className="mt-2 space-y-1 text-xs text-slate-600">
              {r.reasons.map((reason, i) => (
                <li key={i} className="flex gap-1.5">
                  <span className="font-bold text-pokeyellow">▸</span>
                  {reason}
                </li>
              ))}
            </ul>
            <div className="mt-2 text-[10px] font-semibold text-slate-500">
              net score contribution:{' '}
              <span className={r.marginal_contribution.total >= 0 ? 'text-emerald-600' : 'text-pokered'}>
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
