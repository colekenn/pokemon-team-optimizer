import { create } from 'zustand'
import type { SpeciesOut, Weights } from './api/client'
import { DEFAULT_WEIGHTS } from './api/client'

export interface Slot {
  species: SpeciesOut | null
  locked: boolean
}

interface TeamState {
  formatId: number | null
  slots: Slot[]
  weights: Weights
  setFormat: (id: number) => void
  setSlot: (i: number, species: SpeciesOut | null) => void
  toggleLock: (i: number) => void
  setTeam: (team: SpeciesOut[], lockedIds: Set<number>) => void
  setWeights: (w: Weights) => void
  clear: () => void
}

const emptySlots = (): Slot[] =>
  Array.from({ length: 6 }, () => ({ species: null, locked: false }))

export const useTeamStore = create<TeamState>((set) => ({
  formatId: null,
  slots: emptySlots(),
  weights: DEFAULT_WEIGHTS,
  setFormat: (id) => set({ formatId: id, slots: emptySlots() }),
  setSlot: (i, species) =>
    set((s) => {
      const slots = [...s.slots]
      slots[i] = { species, locked: species ? slots[i].locked : false }
      return { slots }
    }),
  toggleLock: (i) =>
    set((s) => {
      const slots = [...s.slots]
      if (slots[i].species) slots[i] = { ...slots[i], locked: !slots[i].locked }
      return { slots }
    }),
  setTeam: (team, lockedIds) =>
    set(() => ({
      slots: Array.from({ length: 6 }, (_, i) => ({
        species: team[i] ?? null,
        locked: team[i] ? lockedIds.has(team[i].id) : false,
      })),
    })),
  setWeights: (weights) => set({ weights }),
  clear: () => set({ slots: emptySlots() }),
}))
