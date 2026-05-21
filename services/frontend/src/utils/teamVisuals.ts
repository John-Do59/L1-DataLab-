import type { EntityMood } from '../api/ragStream'
import type { TeamColors } from '../types/team'
import { getTeamColors, resolveLigue1Team, LIGUE1_TEAMS } from '../data/teamRegistry'

export interface TeamVisualStyle {
  teamId?: string
  canonicalName?: string
  primary: string
  secondary: string
  accent: string
  cssVars: Record<string, string>
  panelStyle: Record<string, string>
  glowFilter: string
  textClass: string
}

const MOOD_ACCENTS: Record<EntityMood, TeamColors> = {
  stable: { primary: '#22d3ee', secondary: '#0891b2', accent: '#67e8f9' },
  risky: { primary: '#ef4444', secondary: '#b91c1c', accent: '#f87171' },
  uncertain: { primary: '#a855f7', secondary: '#7c3aed', accent: '#c084fc' },
  glitch: { primary: '#94a3b8', secondary: '#64748b', accent: '#e2e8f0' },
}

function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const h = hex.replace('#', '')
  if (h.length !== 6) return null
  return {
    r: parseInt(h.slice(0, 2), 16),
    g: parseInt(h.slice(2, 4), 16),
    b: parseInt(h.slice(4, 6), 16),
  }
}

export function hexToRgba(hex: string, alpha: number): string {
  const rgb = hexToRgb(hex)
  if (!rgb) return `rgba(200, 118, 255, ${alpha})`
  return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`
}

export function buildTeamVisualStyle(
  colors: TeamColors,
  meta?: { teamId?: string; canonicalName?: string },
): TeamVisualStyle {
  const accent = colors.accent ?? colors.secondary
  const cssVars: Record<string, string> = {
    '--tv-primary': colors.primary,
    '--tv-secondary': colors.secondary,
    '--tv-accent': accent,
    '--tv-glow': hexToRgba(colors.primary, 0.35),
    '--tv-glow-strong': hexToRgba(colors.primary, 0.55),
    '--tv-border': hexToRgba(colors.primary, 0.5),
    '--tv-surface': hexToRgba(colors.primary, 0.08),
  }
  return {
    teamId: meta?.teamId,
    canonicalName: meta?.canonicalName,
    primary: colors.primary,
    secondary: colors.secondary,
    accent,
    cssVars,
    panelStyle: {
      borderColor: hexToRgba(colors.primary, 0.5),
      boxShadow: `0 0 50px ${hexToRgba(colors.primary, 0.18)}, inset 0 0 20px ${hexToRgba(colors.primary, 0.08)}`,
      background: `linear-gradient(145deg, ${hexToRgba(colors.primary, 0.06)} 0%, rgba(6, 11, 25, 0.92) 55%)`,
    },
    glowFilter: `drop-shadow(0 0 12px ${hexToRgba(colors.primary, 0.65)})`,
    textClass: '',
  }
}

/** Styles visuels complets pour un nom d'équipe. */
export function getTeamVisuals(teamName: string): TeamVisualStyle | null {
  const team = resolveLigue1Team(teamName)
  const colors = getTeamColors(teamName)
  if (!colors) return null
  return buildTeamVisualStyle(colors, {
    teamId: team?.id,
    canonicalName: team?.canonicalName ?? teamName,
  })
}

/** Détecte la première équipe mentionnée dans un texte (alias longest-match). */
export function detectTeamInText(text: string): string | undefined {
  const normalized = text.toLowerCase()
  let best: { name: string; len: number } | undefined

  for (const team of LIGUE1_TEAMS) {
    const candidates = [team.canonicalName, team.shortName, ...team.aliases]
    for (const c of candidates) {
      if (normalized.includes(c.toLowerCase()) && (!best || c.length > best.len)) {
        best = { name: team.canonicalName, len: c.length }
      }
    }
  }
  return best?.name
}

/** Accent Oracle : équipe détectée prioritaire, sinon mood. */
export function getOracleAccent(
  mood: EntityMood,
  contextText?: string,
): TeamVisualStyle {
  const teamName = contextText ? detectTeamInText(contextText) : undefined
  if (teamName) {
    const v = getTeamVisuals(teamName)
    if (v) return v
  }
  return buildTeamVisualStyle(MOOD_ACCENTS[mood], { teamId: `mood-${mood}` })
}

/** Fusion mood + équipe pour cartes prédiction (domicile = primary team). */
export function blendTeamWithMood(
  teamName: string,
  mood: EntityMood,
  weightTeam = 0.85,
): TeamVisualStyle {
  const team = getTeamVisuals(teamName)
  const moodColors = MOOD_ACCENTS[mood]
  if (!team) return buildTeamVisualStyle(moodColors)

  const mix = (a: string, b: string) => {
    const ra = hexToRgb(a)
    const rb = hexToRgb(b)
    if (!ra || !rb) return a
    const w = weightTeam
    const ch = (x: number, y: number) =>
      Math.round(x * w + y * (1 - w))
        .toString(16)
        .padStart(2, '0')
    return `#${ch(ra.r, rb.r)}${ch(ra.g, rb.g)}${ch(ra.b, rb.b)}`
  }

  return buildTeamVisualStyle(
    {
      primary: mix(team.primary, moodColors.primary),
      secondary: mix(team.secondary, moodColors.secondary),
      accent: mix(team.accent, moodColors.accent ?? moodColors.secondary),
    },
    { teamId: team.teamId, canonicalName: team.canonicalName },
  )
}

export function getMoodAccent(mood: EntityMood): TeamVisualStyle {
  return buildTeamVisualStyle(MOOD_ACCENTS[mood], { teamId: `mood-${mood}` })
}
