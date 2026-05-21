import type { EntityMood } from '../../api/ragStream'

/** Tiers prêts pour intégration Stripe */
export type SubscriptionTier = 'free' | 'pro' | 'max'

export interface PlanFeatureRow {
  id: string
  label: string
  free: boolean | string
  pro: boolean | string
  max: boolean | string
}

export interface PricingPlan {
  id: SubscriptionTier
  name: string
  tagline: string
  price: string
  priceDetail: string
  usage: string
  oracleMood: EntityMood
  highlighted?: boolean
  badge?: string
}

export const PRICING_PLANS: PricingPlan[] = [
  {
    id: 'free',
    name: 'Free',
    tagline: 'Découvrez l’Oracle',
    price: '0 €',
    priceDetail: 'pour toujours',
    usage: 'Prédictions limitées · Oracle restreint',
    oracleMood: 'stable',
  },
  {
    id: 'pro',
    name: 'Pro',
    tagline: 'Oracle avancé',
    price: '29 €',
    priceDetail: '/ mois',
    usage: 'Oracle complet · RAG mémoire · Live match',
    oracleMood: 'risky',
    highlighted: true,
    badge: 'Recommandé',
  },
  {
    id: 'max',
    name: 'Max',
    tagline: 'Analytics & mémoire IA',
    price: '79 €',
    priceDetail: '/ mois',
    usage: 'Tout Pro + analytics avancés · priorité API',
    oracleMood: 'uncertain',
    badge: 'Équipes & pros',
  },
]

export const FEATURE_MATRIX: PlanFeatureRow[] = [
  { id: 'predictions', label: 'Prédictions ML', free: true, pro: true, max: true },
  { id: 'oracle', label: 'AI Oracle', free: 'Limité', pro: true, max: true },
  { id: 'rag', label: 'RAG Memory', free: false, pro: true, max: true },
  { id: 'live', label: 'Live Match Analysis', free: false, pro: true, max: true },
  { id: 'analytics', label: 'Advanced Analytics', free: false, pro: false, max: true },
  { id: 'history', label: 'Historique illimité', free: '30 jours', pro: true, max: true },
  { id: 'api', label: 'Accès API prioritaire', free: false, pro: false, max: true },
]

export function tierRank(tier: SubscriptionTier): number {
  return { free: 0, pro: 1, max: 2 }[tier]
}

export function planByTier(tier: SubscriptionTier): PricingPlan {
  const plan = PRICING_PLANS.find((p) => p.id === tier)
  return plan ?? PRICING_PLANS[0]!
}
