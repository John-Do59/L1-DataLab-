<script setup lang="ts">
import { computed } from 'vue'
import type { PricingPlan } from '../plans'
import { getPlanOracleStyle } from '../pricingTokens'
import type { PricingCtaAction } from '../composables/usePricingCta'

const props = defineProps<{
  plan: PricingPlan
  cta: PricingCtaAction
  isCurrent?: boolean
}>()

const oracleStyle = computed(() => getPlanOracleStyle(props.plan.oracleMood))
</script>

<template>
  <article
    :id="`plan-${plan.id}`"
    class="pricing-plan-card relative flex flex-col rounded-3xl p-6 md:p-8 transition-all duration-500 group"
    :class="[
      plan.highlighted
        ? 'liquid-glass-strong scale-[1.02] md:scale-105 z-10'
        : 'liquid-glass',
      isCurrent ? 'ring-2 ring-emerald-400/50' : '',
    ]"
    :style="oracleStyle"
  >
    <div
      class="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
      :style="{
        background: `radial-gradient(circle at 50% 0%, var(--plan-glow), transparent 65%)`,
      }"
    />
    <div
      class="absolute -inset-px rounded-3xl opacity-60 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
      :style="{
        background: `linear-gradient(145deg, var(--plan-primary), transparent 40%, var(--plan-secondary))`,
        mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
        maskComposite: 'exclude',
        padding: '1px',
        WebkitMaskComposite: 'xor',
      }"
    />

    <div class="relative z-10 flex items-start justify-between gap-2 mb-4">
      <div>
        <span
          v-if="plan.badge"
          class="inline-block text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-full mb-2"
          :style="{
            background: `color-mix(in srgb, var(--plan-primary) 25%, transparent)`,
            color: 'var(--plan-primary)',
            border: `1px solid color-mix(in srgb, var(--plan-primary) 40%, transparent)`,
          }"
        >
          {{ plan.badge }}
        </span>
        <h3 class="text-2xl font-black text-white">{{ plan.name }}</h3>
        <p class="text-sm text-sunset-secondary/80 mt-0.5">{{ plan.tagline }}</p>
      </div>
      <span
        class="text-[10px] uppercase tracking-wider px-2 py-1 rounded-full shrink-0"
        :style="{
          color: 'var(--plan-primary)',
          border: `1px solid color-mix(in srgb, var(--plan-primary) 35%, transparent)`,
        }"
      >
        {{ plan.oracleMood }}
      </span>
    </div>

    <div class="relative z-10 mb-4">
      <div class="flex items-baseline gap-1">
        <span class="text-4xl font-black text-white">{{ plan.price }}</span>
        <span class="text-sm text-sunset-secondary/70">{{ plan.priceDetail }}</span>
      </div>
      <p class="text-xs text-sunset-secondary/75 mt-3 leading-relaxed">{{ plan.usage }}</p>
    </div>

    <div
      class="relative z-10 mb-6 h-1 rounded-full overflow-hidden"
      :style="{ background: 'color-mix(in srgb, var(--plan-glow) 30%, transparent)' }"
    >
      <div
        class="h-full w-2/3 rounded-full transition-all duration-700 group-hover:w-full"
        :style="{
          background: `linear-gradient(90deg, var(--plan-primary), var(--plan-secondary))`,
          boxShadow: `0 0 20px var(--plan-glow)`,
        }"
      />
    </div>

    <button
      type="button"
      class="relative z-10 mt-auto w-full py-3 rounded-xl text-sm font-bold transition-all duration-300"
      :disabled="cta.disabled"
      :class="{
        'text-white hover:shadow-[0_0_25px_var(--plan-glow)] hover:scale-[1.02]': !cta.disabled && cta.variant === 'primary',
        'liquid-glass border text-sunset-accent hover:border-[var(--plan-primary)]': cta.variant === 'secondary',
        'border border-emerald-400/40 bg-emerald-500/10 text-emerald-200 cursor-default': cta.variant === 'status',
        'text-sunset-secondary/60 cursor-default': cta.disabled && cta.variant !== 'status',
      }"
      :style="
        !cta.disabled && cta.variant === 'primary'
          ? {
              background: `linear-gradient(135deg, var(--plan-primary), var(--plan-secondary))`,
            }
          : undefined
      "
      @click="!cta.disabled && cta.onClick()"
    >
      {{ cta.label }}
    </button>
  </article>
</template>

<style scoped>
.pricing-plan-card {
  border: 1px solid color-mix(in srgb, var(--plan-primary) 25%, transparent);
  box-shadow: 0 0 40px -20px var(--plan-glow);
}
.pricing-plan-card:hover {
  box-shadow: 0 0 60px -15px var(--plan-glow);
  transform: translateY(-4px);
}
</style>
