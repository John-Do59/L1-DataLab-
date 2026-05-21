<script setup lang="ts">
import { PRICING_PLANS } from '../plans'
import { usePricingCta } from '../composables/usePricingCta'
import PlanCard from './PlanCard.vue'

const { planCardAction, isCurrentPlan } = usePricingCta()
</script>

<template>
  <section id="pricing-plans" class="max-w-6xl mx-auto scroll-mt-28">
    <div class="text-center mb-12">
      <p class="text-[10px] font-bold tracking-[0.3em] uppercase text-sunset-primary mb-2">Plans</p>
      <h2 class="text-2xl md:text-3xl font-black text-white">Choisissez votre niveau d’analyse</h2>
      <p class="text-sunset-secondary/75 text-sm mt-2 max-w-xl mx-auto">
        De l’exploration gratuite à l’analytics pro — structure prête pour Stripe Checkout.
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-4 items-stretch">
      <PlanCard
        v-for="plan in PRICING_PLANS"
        :key="plan.id"
        :plan="plan"
        :cta="planCardAction(plan.id)"
        :is-current="isCurrentPlan(plan.id)"
      />
    </div>
  </section>
</template>
