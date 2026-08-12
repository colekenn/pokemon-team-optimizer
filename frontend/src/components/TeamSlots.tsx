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
            className={`relative rounded-2xl border-2 p-3 text-center shadow-lg backdrop-blur transition hover:-translate-y-1 ${
              slot.locked
                ? 'border-pokeyellow bg-yellow-50/95 shadow-yellow-200/70'
                : 'border-white/80 bg-white/90 shadow-sky-200/60'
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
              className="absolute right-2 top-1.5 font-bold text-slate-400 hover:text-pokered"
            >
              ✕
            </button>
            <div className="mx-auto mt-1 flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-b from-sky-100 to-white shadow-inner">
              {slot.species.sprite_url && (
                <img
                  src={slot.species.sprite_url}
                  alt={slot.species.name}
                  className="h-20 w-20 object-contain drop-shadow-md"
                />
              )}
            </div>
            <div className="mt-1.5 text-sm font-extrabold capitalize text-slate-800">
              {slot.species.name}
            </div>
            <div className="mt-1 flex justify-center gap-1">
              {slot.species.types.map((t) => (
                <TypeBadge key={t} type={t} small />
              ))}
            </div>
            <div className="mt-1 text-[10px] font-bold uppercase tracking-wide text-pokeblue/70">
              {slot.species.role}
            </div>
          </div>
        ) : (
          <button
            key={i}
            onClick={() => onPick(i)}
            className={`flex min-h-[150px] flex-col items-center justify-center rounded-2xl border-[3px] border-dashed border-pokeblue/30 bg-white/40 text-pokeblue/60 transition hover:border-pokered/60 hover:bg-white/70 hover:text-pokered ${
              optimizing ? 'animate-pulse' : ''
            }`}
          >
            <span
              aria-hidden
              className="inline-block h-9 w-9 rounded-full border-2 border-current opacity-70"
              style={{
                background:
                  'linear-gradient(180deg, transparent 0 42%, currentColor 42% 58%, transparent 58% 100%)',
              }}
            />
            <span className="mt-2 text-xs font-bold">
              {optimizing ? 'optimizing…' : 'optimizer fills'}
            </span>
          </button>
        ),
      )}
    </div>
  )
}
