<script setup lang="ts">
import { FEATURE_MATRIX } from '../plans'

function cellValue(v: boolean | string): string {
  if (v === true) return '✓'
  if (v === false) return '—'
  return String(v)
}

function cellClass(v: boolean | string, tier: 'free' | 'pro' | 'max') {
  if (v === true) return tier === 'max' ? 'text-purple-300' : tier === 'pro' ? 'text-orange-300' : 'text-cyan-300'
  if (v === false) return 'text-white/20'
  return 'text-sunset-secondary/90 text-xs'
}
</script>

<template>
  <section class="max-w-5xl mx-auto">
    <div class="text-center mb-10">
      <p class="text-[10px] font-bold tracking-[0.3em] uppercase text-sunset-primary mb-2">Capacités IA</p>
      <h2 class="text-2xl md:text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-sunset-accent">
        Comparez l’intelligence Oracle
      </h2>
    </div>

    <div class="liquid-glass-strong rounded-3xl border border-sunset-primary/25 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[640px] text-sm">
          <thead>
            <tr class="border-b border-sunset-primary/20 bg-black/30">
              <th class="text-left py-4 px-5 font-semibold text-sunset-secondary/80">Feature</th>
              <th class="py-4 px-4 text-center font-bold text-cyan-300/90">Free</th>
              <th class="py-4 px-4 text-center font-bold text-orange-300/90">Pro</th>
              <th class="py-4 px-4 text-center font-bold text-purple-300/90">Max</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, i) in FEATURE_MATRIX"
              :key="row.id"
              class="border-b border-sunset-primary/10 transition-colors hover:bg-sunset-primary/5"
              :class="{ 'bg-black/20': i % 2 === 0 }"
            >
              <td class="py-3.5 px-5 text-sunset-accent font-medium">{{ row.label }}</td>
              <td class="py-3.5 px-4 text-center font-semibold" :class="cellClass(row.free, 'free')">
                {{ cellValue(row.free) }}
              </td>
              <td class="py-3.5 px-4 text-center font-semibold" :class="cellClass(row.pro, 'pro')">
                {{ cellValue(row.pro) }}
              </td>
              <td class="py-3.5 px-4 text-center font-semibold" :class="cellClass(row.max, 'max')">
                {{ cellValue(row.max) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>
