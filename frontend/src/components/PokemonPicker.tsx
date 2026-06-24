import { useState } from 'react'
import type { SpeciesOut } from '../api/client'
import { TypeBadge } from './TypeBadge'

interface Props {
  pool: SpeciesOut[]
  taken: Set<number>
  onSelect: (s: SpeciesOut) => void
  onClose: () => void
}

export function PokemonPicker({ pool, taken, onSelect, onClose }: Props) {
  const [q, setQ] = useState('')
  const filtered = pool.filter((s) => s.name.includes(q.toLowerCase()) && !taken.has(s.id))

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" onClick={onClose}>
      <div
        className="flex max-h-[80vh] w-full max-w-3xl flex-col rounded-2xl border border-slate-700 bg-slate-900 p-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3 flex items-center gap-3">
          <input
            autoFocus
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search Pokémon…"
            className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm outline-none focus:border-sky-500"
          />
          <button onClick={onClose} className="text-slate-400 hover:text-white">✕</button>
        </div>
        <div className="grid grid-cols-3 gap-2 overflow-y-auto sm:grid-cols-4 md:grid-cols-5">
          {filtered.slice(0, 60).map((s) => (
            <button
              key={s.id}
              onClick={() => onSelect(s)}
              className="rounded-lg border border-slate-800 bg-slate-950 p-2 text-center transition hover:border-sky-500"
            >
              {s.sprite_url && (
                <img src={s.sprite_url} alt={s.name} loading="lazy" className="mx-auto h-14 w-14 object-contain" />
              )}
              <div className="truncate text-xs font-medium capitalize">{s.name}</div>
              <div className="mt-0.5 flex justify-center gap-0.5">
                {s.types.map((t) => <TypeBadge key={t} type={t} small />)}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
