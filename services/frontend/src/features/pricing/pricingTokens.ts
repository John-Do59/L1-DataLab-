import { tokens } from '../../theme/tokens'
import type { EntityMood } from '../../api/ragStream'
import type { SubscriptionTier } from './plans'

/** Mapping tier → mood Oracle pour glows des cartes */
export const tierOracleMood: Record<SubscriptionTier, EntityMood> = {
  free: 'stable',
  pro: 'risky',
  max: 'uncertain',
}

export function getPlanOracleStyle(mood: EntityMood) {
  const m = tokens.oracle.moods[mood]
  return {
    '--plan-primary': m.primary,
    '--plan-secondary': m.secondary,
    '--plan-glow': m.glow,
    '--plan-label': m.label,
  } as Record<string, string>
}

export const pricingHeroGlow = {
  primary: tokens.colors.brand.primary,
  secondary: tokens.colors.brand.secondary,
  accent: tokens.colors.brand.accent,
  glassPanel: tokens.glass.gradient.panel,
  glassGlow: tokens.glass.gradient.glow,
}
