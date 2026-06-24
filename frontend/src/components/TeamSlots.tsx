import type { Slot } from '../store'
import { TypeBadge } from './TypeBadge'

interface Props {
  slots: Slot[]
  optimizing: boolean
  onPick: (i: number) => void
  onRemove: (i: number) => void
  onToggleLock: (i: number) => void
}

export function TeamSlots({ slots, optimizing, onPick, onRemove, onToggleLock }: Props) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      {slots.map((slot, i) =>
        slot.species ? (
          <div
            key={i}
            className={`relative rounded-xl border p-3 text-center transition ${
              slot.locked
                ? 'border-amber-400/70 bg-amber-400/5'
                : 'border-slate-700 bg-slate-900'
            }`}
          >
            <button
              onClick={() => onToggleLock(i)}
              title={slot.locked ? 'Unlock' : 'Lock into team'}
              className="absolute left-2 top-2 text-sm opacity-80 hover:opacity-100"
            >
              {slot.locked ? '🔒' : '🔓'}
            </button>
            <button
              onClick={() => onRemove(i)}
              title="Remove"
              className="absolute right-2 top-1.5 text-slate-500 hover:text-red-400"
            >
              ✕
            </button>
            {slot.species.sprite_url && (
              <img
                src={slot.species.sprite_url}
                alt={slot.species.name}
                className="mx-auto h-20 w-20 object-contain drop-shadow"
              />
            )}
            <div className="mt-1 text-sm font-semibold capitalize">{slot.species.name}</div>
            <div className="mt-1 flex justify-center gap-1">
              {slot.species.types.map((t) => (
                <TypeBadge key={t} type={t} small />
              ))}
            </div>
            <div className="mt-1 text-[10px] uppercase tracking-wide text-slate-400">
              {slot.species.role}
            </div>
          </div>
        ) : (
          <button
            key={i}
            onClick={() => onPick(i)}
            className={`flex min-h-[150px] flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-700 text-slate-500 transition hover:border-slate-500 hover:text-slate-300 ${
              optimizing ? 'animate-pulse' : ''
            }`}
          >
            <span className="text-3xl">＋</span>
            <span className="mt-1 text-xs">{optimizing ? 'optimizing…' : 'optimizer fills'}</span>
          </button>
        ),
      )}
    </div>
  )
}
