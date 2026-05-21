import type { EntityMood } from '../api/ragStream'

/** Glows & couleurs Oracle (mood engine UI) */
export const oracleMoods: Record<
  EntityMood,
  { primary: string; secondary: string; glow: string; label: string }
> = {
  stable: {
    primary: '#22d3ee',
    secondary: '#0891b2',
    glow: 'rgba(34, 211, 238, 0.35)',
    label: 'Signal stable',
  },
  risky: {
    primary: '#f97316',
    secondary: '#ea580c',
    glow: 'rgba(249, 115, 22, 0.4)',
    label: 'Match à risque',
  },
  uncertain: {
    primary: '#a855f7',
    secondary: '#7c3aed',
    glow: 'rgba(168, 85, 247, 0.35)',
    label: 'Incertitude tactique',
  },
  glitch: {
    primary: '#94a3b8',
    secondary: '#64748b',
    glow: 'rgba(148, 163, 184, 0.25)',
    label: 'Données partielles',
  },
}

export const oracle = {
  moods: oracleMoods,
  glowIntensity: {
    idle: 0.25,
    listening: 0.45,
    generating: 0.75,
    responding: 1,
  },
  streamRamp: 0.04,
} as const
