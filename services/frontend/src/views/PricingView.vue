<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import PricingHero from '../features/pricing/components/PricingHero.vue'
import PricingPlansGrid from '../features/pricing/components/PricingPlansGrid.vue'
import FeatureMatrix from '../features/pricing/components/FeatureMatrix.vue'
import { usePricingCta } from '../features/pricing/composables/usePricingCta'

const authStore = useAuthStore()
const { heroActions } = usePricingCta()

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUser()
  }
})
</script>

<template>
  <div class="pricing-page max-w-[1400px] mx-auto pb-24 -mt-8">
    <PricingHero :actions="heroActions" />

    <div class="relative my-16 md:my-24">
      <div
        class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-3xl h-px bg-gradient-to-r from-transparent via-sunset-secondary/40 to-transparent"
        aria-hidden="true"
      />
    </div>

    <PricingPlansGrid />

    <div class="my-20 md:my-28">
      <FeatureMatrix />
    </div>

    <footer class="text-center liquid-glass rounded-2xl px-6 py-8 border border-sunset-primary/20 max-w-2xl mx-auto">
      <p class="text-xs text-sunset-secondary/70 leading-relaxed">
        Paiements Stripe à venir — les CTA d’upgrade simulent le tier en local pour valider le parcours produit.
        Votre identité visuelle Sunset · Liquidglass · Oracle reste cohérente sur toute la plateforme.
      </p>
    </footer>
  </div>
</template>
