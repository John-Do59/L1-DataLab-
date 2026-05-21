import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../../stores/auth'
import type { SubscriptionTier } from '../plans'
import { planByTier, tierRank } from '../plans'

export interface PricingCtaAction {
  id: string
  label: string
  variant: 'primary' | 'secondary' | 'ghost' | 'status'
  disabled?: boolean
  onClick: () => void
}

export function usePricingCta(targetTier: SubscriptionTier = 'pro') {
  const authStore = useAuthStore()
  const router = useRouter()
  const currentTier = computed(() => authStore.subscriptionTier)
  const currentPlan = computed(() => planByTier(currentTier.value))

  const isCurrentPlan = (tier: SubscriptionTier) =>
    authStore.isAuthenticated && currentTier.value === tier

  const canUpgradeTo = (tier: SubscriptionTier) =>
    !authStore.isAuthenticated || tierRank(tier) > tierRank(currentTier.value)

  const heroActions = computed((): PricingCtaAction[] => {
    if (!authStore.isAuthenticated) {
      return [
        {
          id: 'get-started',
          label: 'Get Started',
          variant: 'primary',
          onClick: () => router.push({ name: 'register' }),
        },
        {
          id: 'upgrade-pro',
          label: 'Upgrade to Pro',
          variant: 'secondary',
          onClick: () => router.push({ name: 'register', query: { plan: 'pro' } }),
        },
      ]
    }

    if (currentTier.value === 'pro' || currentTier.value === 'max') {
      return [
        {
          id: 'current-plan',
          label: `Current Plan: ${currentPlan.value.name}`,
          variant: 'status',
          disabled: true,
          onClick: () => {},
        },
        {
          id: 'manage',
          label: 'Manage Subscription',
          variant: 'ghost',
          onClick: () => {
            // Préparé pour Stripe Customer Portal
            window.open('https://billing.stripe.com', '_blank', 'noopener')
          },
        },
      ]
    }

    return [
      {
        id: 'upgrade-plan',
        label: 'Upgrade Plan',
        variant: 'primary',
        onClick: () => {
          const el = document.getElementById('pricing-plans')
          el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
        },
      },
      {
        id: 'unlock-pro',
        label: 'Unlock Oracle Pro',
        variant: 'secondary',
        onClick: () => {
          const el = document.getElementById('plan-pro')
          el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
        },
      },
    ]
  })

  function planCardAction(tier: SubscriptionTier): PricingCtaAction {
    if (!authStore.isAuthenticated) {
      return {
        id: `cta-${tier}`,
        label: tier === 'free' ? 'Get Started' : `Choisir ${planByTier(tier).name}`,
        variant: tier === 'pro' ? 'primary' : 'secondary',
        onClick: () =>
          router.push({
            name: tier === 'free' ? 'register' : 'register',
            query: tier !== 'free' ? { plan: tier } : undefined,
          }),
      }
    }

    if (isCurrentPlan(tier)) {
      return {
        id: `current-${tier}`,
        label: 'Plan actuel',
        variant: 'status',
        disabled: true,
        onClick: () => {},
      }
    }

    if (!canUpgradeTo(tier)) {
      return {
        id: `included-${tier}`,
        label: 'Inclus dans votre plan',
        variant: 'ghost',
        disabled: true,
        onClick: () => {},
      }
    }

    const target = planByTier(tier)
    return {
      id: `upgrade-${tier}`,
      label: tier === targetTier ? 'Upgrade now' : `Passer à ${target.name}`,
      variant: tier === 'pro' ? 'primary' : 'secondary',
      onClick: () => {
        // Placeholder Stripe Checkout — persiste le tier en dev
        authStore.setSubscriptionTier(tier)
      },
    }
  }

  return {
    currentTier,
    currentPlan,
    heroActions,
    planCardAction,
    isCurrentPlan,
    canUpgradeTo,
  }
}
