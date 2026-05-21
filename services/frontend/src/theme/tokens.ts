import { colors } from './colors'
import { glass } from './glass'
import { motion } from './motion'
import { oracle } from './oracle'

/** Design tokens racine — source unique de vérité UI */
export const tokens = {
  colors,
  glass,
  motion,
  oracle,
} as const

export type DesignTokens = typeof tokens
