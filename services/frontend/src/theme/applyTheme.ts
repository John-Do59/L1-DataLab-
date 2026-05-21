import { tokens } from './tokens'

/** Injecte les design tokens en variables CSS `:root` */
export function applyDesignTokens(): void {
  const root = document.documentElement
  const { colors, glass, motion, oracle } = tokens

  root.style.setProperty('--color-bg-deep', colors.bg.deep)
  root.style.setProperty('--color-bg-midnight', colors.bg.midnight)
  root.style.setProperty('--color-bg-surface', colors.bg.surface)
  root.style.setProperty('--color-brand-primary', colors.brand.primary)
  root.style.setProperty('--color-brand-secondary', colors.brand.secondary)
  root.style.setProperty('--color-brand-accent', colors.brand.accent)

  root.style.setProperty('--glass-blur-md', glass.blur.md)
  root.style.setProperty('--glass-blur-lg', glass.blur.lg)
  root.style.setProperty('--glass-border-subtle', glass.border.subtle)
  root.style.setProperty('--glass-border-glow', glass.border.glow)
  root.style.setProperty('--glass-opacity-strong', String(glass.opacity.strong))

  root.style.setProperty('--motion-duration-normal', motion.duration.normal)
  root.style.setProperty('--motion-duration-slow', motion.duration.slow)
  root.style.setProperty('--motion-easing-standard', motion.easing.standard)

  for (const [mood, cfg] of Object.entries(oracle.moods)) {
    root.style.setProperty(`--oracle-${mood}-primary`, cfg.primary)
    root.style.setProperty(`--oracle-${mood}-glow`, cfg.glow)
  }
}
