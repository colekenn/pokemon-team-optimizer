import { useEffect, useState } from 'react'

const MESSAGES = [
  'Throwing a Poké Ball at the server…',
  'A wild SERVER appeared!',
  'Snorlax is blocking the path…',
  'Using WAKE-UP SLAP…',
  'Professor Oak is booting up the lab…',
  'Feeding the server a Rare Candy…',
  'Nurse Joy is healing the database…',
  "It's super effective!",
]

interface Props {
  error: boolean
  ready: boolean
  onRetry: () => void
}

export function BootScreen({ error, ready, onRetry }: Props) {
  const [tick, setTick] = useState(0)
  const [elapsed, setElapsed] = useState(0)
  const [progress, setProgress] = useState(4)

  useEffect(() => {
    const m = setInterval(() => setTick((t) => t + 1), 3000)
    const e = setInterval(() => setElapsed((s) => s + 1), 1000)
    return () => {
      clearInterval(m)
      clearInterval(e)
    }
  }, [])

  useEffect(() => {
    if (ready) {
      setProgress(100)
      return
    }

    const delays = [420, 760, 330, 1100, 540, 1450, 680]
    const timer = setTimeout(() => {
      setProgress((current) => {
        if (current >= 94) return current
        const remaining = 94 - current
        const step = Math.max(0.35, remaining * (0.08 + ((tick + current) % 5) * 0.025))
        return Math.min(94, current + step)
      })
    }, delays[(tick + Math.floor(progress)) % delays.length])

    return () => clearTimeout(timer)
  }, [progress, ready, tick])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <div className="flex flex-col items-center">
        <div style={{ animation: 'pokeball-bob 1.5s ease-in-out infinite' }}>
          <div className="pokeball-loader" role="status" aria-label="Connecting to server" />
        </div>
        <div className="pokeball-shadow mt-3" aria-hidden />
      </div>

      <h1 className="mt-8 text-2xl font-black tracking-tight text-pokeblue-dark">
        Pokémon <span className="text-pokered">Team Optimizer</span>
      </h1>

      {error ? (
        <>
          <p className="mt-3 text-sm font-bold text-pokered">
            Critical hit! The server didn&apos;t respond.
          </p>
          <button onClick={onRetry} className="pokeball-btn mt-4 px-6 py-2 text-sm">
            Try again
          </button>
        </>
      ) : (
        <>
          <p className="mt-3 min-h-5 text-sm font-bold text-pokeblue/80" aria-live="polite">
            {ready ? 'Ready!' : elapsed >= 8 ? 'Almost done…' : MESSAGES[tick % MESSAGES.length]}
          </p>
          <div
            className="boot-track mt-5 w-64"
            role="progressbar"
            aria-label="Connecting to server"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={Math.round(progress)}
          >
            <div className="boot-progress" style={{ width: `${progress}%` }} />
          </div>
          <p className="mt-2 text-xs font-extrabold tabular-nums text-pokeblue/60">
            {Math.round(progress)}%
          </p>
        </>
      )}
    </div>
  )
}
