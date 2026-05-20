<template>
  <div class="mt-12 space-y-6">
    <div class="flex justify-between items-end mb-6">
      <div>
        <h2 class="text-2xl font-black text-white">Prediction Timeline</h2>
        <p class="text-white/50 text-sm mt-1">AI Performance Tracking & Model Validation</p>
      </div>
      <div class="bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm flex items-center gap-3">
        <span class="text-white/60">Global Accuracy</span>
        <span class="text-cyan-400 font-bold">71.4%</span>
      </div>
    </div>

    <div v-if="predictions.length === 0" class="text-center py-10 bg-white/5 rounded-xl border border-white/10">
      <p class="text-white/40 italic">No predictions recorded yet.</p>
    </div>

    <div v-else class="grid gap-4">
      <div v-for="pred in predictions" :key="pred.id" 
           class="liquid-glass p-5 rounded-xl border flex items-center justify-between transition-all"
           :class="pred.isCorrect ? 'border-green-500/30 bg-green-500/5' : (pred.real_status === 'played' ? 'border-red-500/30 bg-red-500/5' : 'border-white/10 hover:border-white/20')">
        
        <!-- Match Info -->
        <div class="flex items-center gap-6 w-1/3">
          <div class="flex flex-col items-center gap-2">
            <span class="text-xs text-white/50">{{ new Date(pred.created_at).toLocaleDateString() }}</span>
            <span v-if="pred.real_status === 'played'" class="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider"
                  :class="pred.isCorrect ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'">
              {{ pred.isCorrect ? 'VALIDATED' : 'FAILED' }}
            </span>
            <span v-else class="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider bg-purple-500/20 text-purple-400">
              PENDING
            </span>
          </div>
          <div class="flex flex-col font-bold">
            <span class="text-white">{{ pred.match.home_team.name }}</span>
            <span class="text-white/40 text-xs italic">vs</span>
            <span class="text-white">{{ pred.match.away_team.name }}</span>
          </div>
        </div>

        <!-- Prediction -->
        <div class="flex flex-col items-center justify-center w-1/3 px-4 border-l border-r border-white/10">
          <span class="text-[10px] uppercase tracking-widest text-white/50 mb-1">AI Prediction</span>
          <div class="flex items-center gap-3">
            <span class="text-xl font-black" :class="pred.predicted_result === 'H' ? 'text-cyan-400' : (pred.predicted_result === 'A' ? 'text-purple-400' : 'text-gray-300')">
              {{ pred.predictedWinnerName }}
            </span>
            <span class="bg-white/10 px-2 py-1 rounded text-xs font-mono text-white/80">
              {{ pred.confidence }}%
            </span>
          </div>
        </div>

        <!-- Real Result -->
        <div class="flex flex-col items-end justify-center w-1/3 pr-4">
          <span class="text-[10px] uppercase tracking-widest text-white/50 mb-1">Real Result</span>
          <div v-if="pred.real_status === 'played'" class="flex items-center gap-2">
            <span class="text-2xl font-black text-white">{{ pred.real_home_score }}</span>
            <span class="text-white/30">-</span>
            <span class="text-2xl font-black text-white">{{ pred.real_away_score }}</span>
          </div>
          <div v-else class="text-white/30 italic text-sm">
            Waiting for match...
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../api/axios'

interface Prediction {
  id: number
  created_at: string
  predicted_result: string
  prob_h: number
  prob_d: number
  prob_a: number
  match: {
    home_team: { name: string }
    away_team: { name: string }
  }
  real_home_score?: number
  real_away_score?: number
  real_status?: string
  predictedWinnerName?: string
  confidence?: number
  isCorrect?: boolean
}

const predictions = ref<Prediction[]>([])

onMounted(async () => {
  try {
    const res = await api.get('/predictions')
    predictions.value = res.data.map((p: any) => {
      let predictedWinnerName = 'DRAW'
      let confidence = Math.round(p.prob_d * 100)
      if (p.predicted_result === 'H') {
        predictedWinnerName = p.match.home_team.name
        confidence = Math.round(p.prob_h * 100)
      } else if (p.predicted_result === 'A') {
        predictedWinnerName = p.match.away_team.name
        confidence = Math.round(p.prob_a * 100)
      }

      let isCorrect = false
      if (p.real_status === 'played') {
        const h = p.real_home_score || 0
        const a = p.real_away_score || 0
        if (h > a && p.predicted_result === 'H') isCorrect = true
        if (h < a && p.predicted_result === 'A') isCorrect = true
        if (h === a && p.predicted_result === 'D') isCorrect = true
      }

      return {
        ...p,
        predictedWinnerName,
        confidence,
        isCorrect
      }
    })
  } catch (e) {
    console.error("Failed to load prediction history", e)
  }
})
</script>

<style scoped>
.liquid-glass {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
</style>
