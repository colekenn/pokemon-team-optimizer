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
      <header className="mb-6 flex flex-wrap items-center gap-4">
        <h1 className="text-xl font-bold tracking-tight">
          ⚡ Pokémon <span className="text-sky-400">Team Optimizer</span>
        </h1>
        <select
          value={formatId ?? ''}
          onChange={(e) => {
            setFormat(Number(e.target.value))
            setAnalysis(null)
            setOptResult(null)
          }}
          className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm"
        >
          {formats.data?.map((f) => (
            <option key={f.id} value={f.id}>
              {f.name} ({f.pool_size})
            </option>
          ))}
        </select>
        <button
          onClick={() => optimize.mutate([])}
          disabled={optimize.isPending || formatId == null}
          className="ml-auto rounded-lg bg-sky-600 px-5 py-2 text-sm font-semibold shadow transition hover:bg-sky-500 disabled:opacity-50"
        >
          {optimize.isPending ? 'Optimizing…' : 'Optimize team'}
        </button>
      </header>

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
        <p className="mt-2 text-xs text-slate-500">
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
