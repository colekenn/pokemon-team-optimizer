import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { api } from './api/client'
import type { AnalyzeResponse, OptimizeResponse, SpeciesOut } from './api/client'
import { useTeamStore } from './store'
import { TeamSlots } from './components/TeamSlots'
import { PokemonPicker } from './components/PokemonPicker'
import { WeaknessMatrix } from './components/WeaknessMatrix'
import { OffensiveCoverage } from './components/OffensiveCoverage'
import { ScorePanel } from './components/ScorePanel'
import { RecommendationCards } from './components/RecommendationCards'

export default function App() {
  const { formatId, slots, weights, setFormat, setSlot, toggleLock, setTeam } = useTeamStore()
  const [pickerSlot, setPickerSlot] = useState<number | null>(null)
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null)
  const [optResult, setOptResult] = useState<OptimizeResponse | null>(null)

  const formats = useQuery({ queryKey: ['formats'], queryFn: api.formats })
  useEffect(() => {
    if (formats.data?.length && formatId == null) setFormat(formats.data[0].id)
  }, [formats.data, formatId, setFormat])

  const pool = useQuery({
    queryKey: ['pokemon', formatId],
    queryFn: () => api.pokemon(formatId!),
    enabled: formatId != null,
  })

  const memberIds = useMemo(
    () => slots.filter((s) => s.species).map((s) => s.species!.id),
    [slots],
  )
  const memberNames = slots.filter((s) => s.species).map((s) => s.species!.name)
  const lockedIds = slots.filter((s) => s.species && s.locked).map((s) => s.species!.id)

  useEffect(() => {
    if (formatId == null || memberIds.length === 0) {
      setAnalysis(null)
      return
    }
    const t = setTimeout(() => {
      api.analyze({ species_ids: memberIds, format_id: formatId, weights }).then(setAnalysis).catch(() => {})
    }, 300)
    return () => clearTimeout(t)
  }, [formatId, JSON.stringify(memberIds), JSON.stringify(weights)])

  const optimize = useMutation({
    mutationFn: (excluded: number[]) =>
      api.optimize({
        format_id: formatId!,
        locked_ids: lockedIds.length ? lockedIds : memberIds,
        excluded_ids: excluded,
        weights,
      }),
    onSuccess: (data, excluded) => {
      const locked = new Set(lockedIds.length ? lockedIds : memberIds)
      setTeam(data.team, locked)
      setOptResult(data)
      void excluded
    },
  })

  const takenIds = new Set(memberIds)

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      <header className="mb-6 flex flex-wrap items-center justify-center gap-4 text-center">
        <h1 className="flex items-center gap-2.5 text-2xl font-black tracking-tight text-pokeblue-dark">
          <span
            aria-hidden
            className="inline-block h-8 w-8 rounded-full border-[3px] border-slate-800 shadow-md"
            style={{
              background:
                'linear-gradient(180deg, #ee1515 0 44%, #1f2937 44% 56%, #fff 56% 100%)',
            }}
          />
          Pokémon <span className="text-pokered">Team Optimizer</span>
        </h1>
        <select
          value={formatId ?? ''}
          onChange={(e) => {
            setFormat(Number(e.target.value))
            setAnalysis(null)
            setOptResult(null)
          }}
          className="rounded-full border-2 border-pokeblue/40 bg-white px-4 py-1.5 text-sm font-bold text-pokeblue-dark shadow-sm outline-none focus:border-pokeblue"
        >
          {formats.data?.map((f) => (
            <option key={f.id} value={f.id}>
              {f.name} ({f.pool_size})
            </option>
          ))}
        </select>
      </header>

      <div className="mb-6 flex justify-center">
        <button
          onClick={() => optimize.mutate([])}
          disabled={optimize.isPending || formatId == null}
          className="pokeball-btn px-8 py-2.5 text-sm"
        >
          {optimize.isPending ? 'Optimizing…' : 'Optimize team'}
        </button>
      </div>

      <TeamSlots
        slots={slots}
        optimizing={optimize.isPending}
        onPick={(i) => setPickerSlot(i)}
        onRemove={(i) => {
          setSlot(i, null)
          setOptResult(null)
        }}
        onToggleLock={toggleLock}
      />

      {optResult && (
        <p className="mt-2 text-xs font-semibold text-pokeblue/70">
          {optResult.cache_hit
            ? 'cached result'
            : `evaluated ${optResult.states_evaluated.toLocaleString()} team configurations in ${(optResult.elapsed_ms / 1000).toFixed(2)}s`}
        </p>
      )}

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        {analysis && (
          <>
            <div className="space-y-4">
              <ScorePanel
                breakdown={analysis.breakdown}
                score={analysis.score}
                beforeScore={optResult?.before_score}
              />
              <OffensiveCoverage analysis={analysis} />
            </div>
            <WeaknessMatrix analysis={analysis} memberNames={memberNames} />
          </>
        )}
      </div>

      {optResult && (
        <div className="mt-6">
          <RecommendationCards
            recommendations={optResult.recommendations}
            onReplace={(id) => optimize.mutate([id])}
          />
        </div>
      )}

      {pickerSlot != null && pool.data && (
        <PokemonPicker
          pool={pool.data}
          taken={takenIds}
          onClose={() => setPickerSlot(null)}
          onSelect={(s: SpeciesOut) => {
            setSlot(pickerSlot, s)
            setPickerSlot(null)
            setOptResult(null)
          }}
        />
      )}
    </div>
  )
}
