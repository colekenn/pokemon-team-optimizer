import type { AnalyzeResponse } from '../api/client'
import { TypeBadge } from './TypeBadge'

export function OffensiveCoverage({ analysis }: { analysis: AnalyzeResponse }) {
  const entries = Object.entries(analysis.offensive_coverage)
  const covered = entries.filter(([, who]) => who.length > 0).length
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-3">
      <h3 className="mb-2 text-sm font-semibold text-slate-300">
        Offensive coverage <span className="text-slate-500">({covered}/18 types hit super-effectively)</span>
      </h3>
      <div className="flex flex-wrap gap-1.5">
        {entries.map(([t, who]) => (
          <div
            key={t}
            title={who.length ? `Covered by ${who.join(', ')}` : 'Not covered'}
            className={`rounded-lg p-0.5 ${who.length ? '' : 'opacity-30 grayscale'}`}
          >
            <TypeBadge type={t} />
          </div>
        ))}
      </div>
    </div>
  )
}
