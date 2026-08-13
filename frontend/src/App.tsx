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
import { BootScreen } from './components/BootScreen'

export default function App() {
  const { formatId, slots, weights, setFormat, setSlot, toggleLock, setTeam } = useTeamStore()
  const [pickerSlot, setPickerSlot] = useState<number | null>(null)
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null)
  const [optResult, setOptResult] = useState<OptimizeResponse | null>(null)
  const [bootFinished, setBootFinished] = useState(false)

  const formats = useQuery({
    queryKey: ['formats'],
    queryFn: api.formats,
    retry: 10,
    retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 5000),
  })
  useEffect(() => {
    if (formats.data?.length && formatId == null) setFormat(formats.data[0].id)
  }, [formats.data, formatId, setFormat])
  useEffect(() => {
    if (!formats.data) return
    const timer = setTimeout(() => setBootFinished(true), 700)
    return () => clearTimeout(timer)
  }, [formats.data])

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

  if (!formats.data || !bootFinished) {
    return (
      <BootScreen
        error={formats.isError && !formats.isFetching}
        ready={Boolean(formats.data)}
        onRetry={() => formats.refetch()}
      />
    )
  }

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center px-4 py-10">
      <div aria-hidden className="deco-ball -left-40 -top-40 h-[26rem] w-[26rem]" />
      <div aria-hidden className="deco-ball -bottom-36 -right-36 h-[22rem] w-[22rem]" />

      <div className="relative z-10 w-full max-w-6xl">
        <header className="mb-8 flex flex-col items-center gap-3 text-center">
          <h1 className="flex items-center gap-3 text-3xl font-black tracking-tight text-pokeblue-dark sm:text-4xl">
            <span
              aria-hidden
              className="inline-block h-9 w-9 rounded-full border-[3px] border-slate-800 shadow-md"
              style={{
                background:
                  'linear-gradient(180deg, #ee1515 0 44%, #1f2937 44% 56%, #fff 56% 100%)',
              }}
            />
            Pokémon <span className="text-pokered">Team Optimizer</span>
          </h1>
          <p className="text-sm font-semibold text-pokeblue/70">
            assemble the strongest six
          </p>

          <div className="mt-2 flex flex-wrap items-center justify-center gap-3">
            <select
              value={formatId ?? ''}
              onChange={(e) => {
                setFormat(Number(e.target.value))
                setAnalysis(null)
                setOptResult(null)
              }}
              className="rounded-full border-2 border-pokeblue/40 bg-white px-4 py-2 text-sm font-bold text-pokeblue-dark shadow-sm outline-none focus:border-pokeblue"
            >
              {formats.data.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.name} ({f.pool_size})
                </option>
              ))}
            </select>
            <button
              onClick={() => optimize.mutate([])}
              disabled={optimize.isPending || formatId == null}
              className="pokeball-btn flex items-center gap-2 px-8 py-2 text-sm"
            >
              <span
                aria-hidden
                className="inline-block h-4 w-4 rounded-full border-2 border-white/90"
                style={{
                  background:
                    'linear-gradient(180deg, transparent 0 40%, rgba(255,255,255,.9) 40% 60%, transparent 60% 100%)',
                  animation: optimize.isPending ? 'pokeball-spin 0.8s linear infinite' : undefined,
                }}
              />
              {optimize.isPending ? 'Simulating battles…' : 'Optimize team'}
            </button>
          </div>
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
          <p className="mt-2 text-center text-xs font-semibold text-pokeblue/70">
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
    </div>
  )
}
