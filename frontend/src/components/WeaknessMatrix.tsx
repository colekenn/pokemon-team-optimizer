import type { AnalyzeResponse } from '../api/client'
import { TypeBadge } from './TypeBadge'

function cellStyle(m: number): { bg: string; label: string } {
  if (m === 0) return { bg: 'bg-emerald-500 text-white', label: '0' }
  if (m === 0.25) return { bg: 'bg-emerald-300 text-emerald-900', label: '¼' }
  if (m === 0.5) return { bg: 'bg-emerald-200 text-emerald-800', label: '½' }
  if (m === 2) return { bg: 'bg-rose-300 text-rose-900', label: '2' }
  if (m >= 4) return { bg: 'bg-rose-500 text-white', label: '4' }
  return { bg: 'bg-slate-100', label: '' }
}

export function WeaknessMatrix({ analysis, memberNames }: { analysis: AnalyzeResponse; memberNames: string[] }) {
  const types = Object.keys(analysis.weakness_matrix)
  return (
    <div className="card overflow-x-auto p-3">
      <h3 className="mb-2 text-sm font-extrabold uppercase tracking-wide text-pokeblue-dark">
        Defensive matrix
      </h3>
      <table className="w-full border-separate border-spacing-0.5 text-center text-xs">
        <thead>
          <tr>
            <th />
            {memberNames.map((n) => (
              <th key={n} className="max-w-16 truncate px-1 pb-1 font-bold capitalize text-slate-600">{n}</th>
            ))}
            <th className="px-1 pb-1 font-bold text-slate-600">weak</th>
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
                  return <td key={i} className={`h-6 w-9 rounded-md font-bold ${bg}`}>{label}</td>
                })}
                <td className={`w-10 rounded-md font-extrabold ${weakCount >= 3 ? 'bg-pokered text-white' : weakCount === 2 ? 'bg-rose-200 text-rose-800' : 'text-slate-400'}`}>
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
