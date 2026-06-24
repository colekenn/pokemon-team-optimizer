const TYPE_COLORS: Record<string, string> = {
  normal: '#9ca38f', fire: '#ee7f30', water: '#678fee', electric: '#f7cf2e',
  grass: '#77c850', ice: '#98d5d7', fighting: '#bf3029', poison: '#a040a0',
  ground: '#dfbf69', flying: '#a790ee', psychic: '#f65687', bug: '#a8b720',
  rock: '#b8a038', ghost: '#705797', dragon: '#6f38f6', dark: '#6f5747',
  steel: '#b8b8d0', fairy: '#f0a8ee',
}

export function TypeBadge({ type, small }: { type: string; small?: boolean }) {
  return (
    <span
      className={`inline-block rounded font-semibold uppercase tracking-wide text-white shadow-sm ${
        small ? 'px-1.5 py-0.5 text-[9px]' : 'px-2 py-0.5 text-[11px]'
      }`}
      style={{ backgroundColor: TYPE_COLORS[type] ?? '#666', textShadow: '0 1px 1px rgba(0,0,0,.5)' }}
    >
      {type}
    </span>
  )
}
