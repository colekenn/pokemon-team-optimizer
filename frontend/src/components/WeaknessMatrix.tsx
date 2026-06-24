import type { AnalyzeResponse } from '../api/client'
import { TypeBadge } from './TypeBadge'

function cellStyle(m: number): { bg: string; label: string } {
  if (m === 0) return { bg: 'bg-emerald-600/80', label: '0' }
  if (m === 0.25) return { bg: 'bg-emerald-500/50', label: '¼' }
  if (m === 0.5) return { bg: 'bg-emerald-500/30', label: '½' }
  if (m === 2) return { bg: 'bg-rose-500/50', label: '2' }
  if (m >= 4) return { bg: 'bg-rose-600/80', label: '4' }
  return { bg: 'bg-slate-800/40', label: '' }
}

export function WeaknessMatrix({ analysis, memberNames }: { analysis: AnalyzeResponse; memberNames: string[] }) {
  const types = Object.keys(analysis.weakness_matrix)
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900 p-3">
      <h3 className="mb-2 text-sm font-semibold text-slate-300">Defensive matrix</h3>
      <table className="w-full border-separate border-spacing-0.5 text-center text-xs">
        <thead>
          <tr>
            <th />
            {memberNames.map((n) => (
              <th key={n} className="max-w-16 truncate px-1 pb-1 font-medium capitalize text-slate-400">{n}</th>
            ))}
            <th className="px-1 pb-1 font-medium text-slate-400">weak</th>
          </tr>
        </thead>
        <tbody>
          {types.map((t) => {
            const row = analysis.weakness_matrix[t]
            const weakCount = row.filter((m) => m >= 2).length
            return (
              <tr key={t}>
                <td className="pr-1 text-left"><TypeBadge type={t} small /></td>
                {row.map((m, i) => {
                  const { bg, label } = cellStyle(m)
                  return <td key={i} className={`h-6 w-9 rounded ${bg}`}>{label}</td>
                })}
                <td className={`w-10 rounded font-semibold ${weakCount >= 3 ? 'bg-rose-700/70' : weakCount === 2 ? 'bg-rose-500/40' : 'text-slate-500'}`}>
                  {weakCount || ''}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
