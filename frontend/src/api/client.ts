const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface SpeciesOut {
  id: number
  name: string
  generation: number
  types: string[]
  stats: Record<string, number>
  bst: number
  sprite_url: string | null
  role: string
}

export interface FormatOut {
  id: number
  name: string
  description: string | null
  pool_size: number
}

export interface Weights {
  offense: number
  defense: number
  shared_weakness: number
  stats: number
  roles: number
  threats: number
}

export const DEFAULT_WEIGHTS: Weights = {
  offense: 1.0,
  defense: 1.0,
  shared_weakness: 0.8,
  stats: 0.6,
  roles: 0.5,
  threats: 1.2,
}

export interface AnalyzeResponse {
  score: number
  breakdown: Record<string, number>
  weakness_matrix: Record<string, number[]>
  member_ids: number[]
  offensive_coverage: Record<string, string[]>
  roles: Record<string, string>
}

export interface Recommendation {
  species: SpeciesOut
  reasons: string[]
  marginal_contribution: Record<string, number>
}

export interface OptimizeResponse {
  team: SpeciesOut[]
  score: number
  breakdown: Record<string, number>
  before_score: number | null
  recommendations: Recommendation[]
  states_evaluated: number
  elapsed_ms: number
  cache_hit: boolean
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`)
  return res.json()
}

export const api = {
  formats: (): Promise<FormatOut[]> =>
    fetch(`${API}/api/v1/formats`).then((r) => r.json()),
  pokemon: (formatId: number): Promise<SpeciesOut[]> =>
    fetch(`${API}/api/v1/pokemon?format_id=${formatId}`).then((r) => r.json()),
  analyze: (body: { species_ids: number[]; format_id: number; weights?: Weights }) =>
    post<AnalyzeResponse>('/api/v1/analyze', body),
  optimize: (body: {
    format_id: number
    locked_ids: number[]
    excluded_ids?: number[]
    weights?: Weights
    algorithm?: string
    seed?: number
  }) => post<OptimizeResponse>('/api/v1/optimize', body),
}
