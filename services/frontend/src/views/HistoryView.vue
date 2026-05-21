<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'
import ProbabilityBar from '../components/dashboard/ProbabilityBar.vue'
import { useAuthStore } from '../stores/auth'
import { hydrateStandingsLogos, resolveTeamLogo } from '../utils/teamLogos'
import TeamGlow from '../components/ui/TeamGlow.vue'
import bgStadium2 from '../assets/backgrounds/ballon-entite.png'

const authStore = useAuthStore()
const router = useRouter()

interface Team {
  id: number
  name: string
  logo?: string
  elo_rating?: number
}

interface Match {
  id: number
  home_team: Team
  away_team: Team
  match_date: string
  status: string
}

interface PredictionHistory {
  id: number
  match: Match
  predicted_result: 'H' | 'D' | 'A'
  prob_h: number
  prob_d: number
  prob_a: number
  created_at: string
  real_home_score?: number | null
  real_away_score?: number | null
  real_status?: string | null
}

const predictions = ref<PredictionHistory[]>([])
const loading = ref(true)
const fetchError = ref('')
const searchQuery = ref('')
const filterStatus = ref<'all' | 'finished' | 'scheduled'>('all')
const filterResult = ref<'all' | 'correct' | 'incorrect'>('all')

const enrichPredictionLogos = (items: PredictionHistory[]): PredictionHistory[] =>
  items.map((pred) => ({
    ...pred,
    match: {
      ...pred.match,
      home_team: {
        ...pred.match.home_team,
        logo: resolveTeamLogo(pred.match.home_team.name, pred.match.home_team.logo),
      },
      away_team: {
        ...pred.match.away_team,
        logo: resolveTeamLogo(pred.match.away_team.name, pred.match.away_team.logo),
      },
    },
  }))

const fetchHistory = async () => {
  loading.value = true
  fetchError.value = ''
  try {
    await hydrateStandingsLogos()
    const predRes = await api.get<PredictionHistory[]>('/predictions')
    predictions.value = enrichPredictionLogos(predRes.data)
  } catch (e) {
    console.error("Failed to fetch prediction history", e)
    fetchError.value = "Impossible de charger l'historique. Réessayez dans un instant."
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUser()
  }
  await fetchHistory()
})

// Helper to determine if a prediction was correct
const isPredictionCorrect = (pred: PredictionHistory): boolean => {
  if (pred.real_home_score === null || pred.real_home_score === undefined ||
      pred.real_away_score === null || pred.real_away_score === undefined) {
    return false
  }
  
  const home = pred.real_home_score
  const away = pred.real_away_score
  
  if (pred.predicted_result === 'H' && home > away) return true
  if (pred.predicted_result === 'D' && home === away) return true
  if (pred.predicted_result === 'A' && home < away) return true
  
  return false
}

// Helper to check if a match is finished
const isMatchFinished = (pred: PredictionHistory): boolean => {
  return pred.real_home_score !== null && pred.real_home_score !== undefined &&
         pred.real_away_score !== null && pred.real_away_score !== undefined
}

// Stats computations
const totalPredictions = computed(() => predictions.value.length)

const finishedPredictions = computed(() => 
  predictions.value.filter(isMatchFinished)
)

const correctPredictionsCount = computed(() => 
  finishedPredictions.value.filter(isPredictionCorrect).length
)

const successRate = computed(() => {
  if (finishedPredictions.value.length === 0) return 0
  return Math.round((correctPredictionsCount.value / finishedPredictions.value.length) * 100)
})

const averageConfidence = computed(() => {
  if (predictions.value.length === 0) return 0
  const totalConf = predictions.value.reduce((acc, pred) => {
    const maxProb = Math.max(pred.prob_h, pred.prob_d, pred.prob_a)
    return acc + maxProb
  }, 0)
  return Math.round((totalConf / predictions.value.length) * 100)
})

// Filtered predictions
const filteredPredictions = computed(() => {
  return predictions.value.filter(pred => {
    // 1. Search Query
    const matchName = `${pred.match.home_team.name} ${pred.match.away_team.name}`.toLowerCase()
    const matchesSearch = matchName.includes(searchQuery.value.toLowerCase())
    if (!matchesSearch) return false

    // 2. Status Filter
    const finished = isMatchFinished(pred)
    if (filterStatus.value === 'finished' && !finished) return false
    if (filterStatus.value === 'scheduled' && finished) return false

    // 3. Result Filter
    if (filterResult.value !== 'all') {
      if (!finished) return false // can't evaluate correctness of unfinished matches
      const correct = isPredictionCorrect(pred)
      if (filterResult.value === 'correct' && !correct) return false
      if (filterResult.value === 'incorrect' && correct) return false
    }

    return true
  })
})

const formatResult = (res: 'H' | 'D' | 'A') => {
  if (res === 'H') return 'Victoire Domicile (H)'
  if (res === 'A') return 'Victoire Extérieur (A)'
  return 'Match Nul (D)'
}

const getInitials = (name: string) => {
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}
</script>

<template>
  <!-- Futuristic Background Stadium -->
  <div class="fixed inset-0 z-[-1] pointer-events-none bg-[#010108] flex items-center justify-center">
    <img :src="bgStadium2" alt="Stadium" class="w-full h-full object-contain object-center opacity-75 scale-[0.92]" />
    <div class="absolute inset-0 bg-gradient-to-b from-[#010108]/50 via-transparent to-[#010108]/90"></div>
  </div>

  <div class="space-y-10 pb-16 w-full max-w-7xl mx-auto pt-6 relative z-10 px-4 sm:px-6 lg:px-8">
    
    <!-- Top Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-sunset-primary/20 pb-6 relative">
      <div class="absolute -left-20 -top-20 w-64 h-64 bg-purple-600/10 blur-[90px] rounded-full pointer-events-none"></div>
      
      <div class="relative z-10">
        <h1 class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-sunset-accent to-purple-400 tracking-tight uppercase">
          Historique des predictions
        </h1>
        <p class="text-sunset-secondary mt-1 font-medium">
          Historique complet des simulations neuronales pour <span class="text-sunset-primary">{{ authStore.user?.username || 'Analyst' }}</span>.
        </p>
      </div>

      <div class="mt-4 md:mt-0 flex gap-4 relative z-10">
        <button @click="router.push('/prediction')" class="px-6 py-2.5 bg-gradient-to-r from-sunset-primary/30 to-sunset-secondary/30 border border-sunset-secondary/40 text-sunset-accent font-bold rounded-xl shadow-[0_0_15px_rgba(200,118,255,0.2)] hover:scale-105 transition-all">
          ⚡ Nouvelle Simulation
        </button>
        <button @click="router.push('/dashboard')" class="px-6 py-2.5 bg-white/5 border border-white/10 text-white/80 rounded-xl hover:bg-white/10 transition-colors">
          Command Center
        </button>
      </div>
    </div>

    <!-- Stats summary grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      
      <!-- Total Predictions -->
      <div class="liquid-glass rounded-2xl p-6 border border-sunset-primary/10 flex flex-col justify-between h-32 relative overflow-hidden group">
        <div class="absolute -right-8 -top-8 w-24 h-24 bg-cyan-500/5 group-hover:bg-cyan-500/10 rounded-full transition-colors duration-500"></div>
        <span class="text-[10px] font-bold text-sunset-accent/60 uppercase tracking-widest">Simulations Totales</span>
        <div class="flex items-baseline gap-2 mt-2">
          <span class="text-4xl font-black text-white">{{ totalPredictions }}</span>
          <span class="text-xs text-sunset-secondary">predictions</span>
        </div>
      </div>

      <!-- Success Rate -->
      <div class="liquid-glass rounded-2xl p-6 border border-sunset-primary/10 flex flex-col justify-between h-32 relative overflow-hidden group">
        <div class="absolute -right-8 -top-8 w-24 h-24 bg-green-500/5 group-hover:bg-green-500/10 rounded-full transition-colors duration-500"></div>
        <span class="text-[10px] font-bold text-green-400/60 uppercase tracking-widest">Taux de Réussite</span>
        <div class="flex items-baseline gap-2 mt-2">
          <span class="text-4xl font-black text-green-400 drop-shadow-[0_0_8px_rgba(74,222,128,0.3)]">{{ successRate }}%</span>
          <span class="text-xs text-sunset-secondary">{{ correctPredictionsCount }} / {{ finishedPredictions.length }} évalués</span>
        </div>
      </div>

      <!-- Average Confidence -->
      <div class="liquid-glass rounded-2xl p-6 border border-sunset-primary/10 flex flex-col justify-between h-32 relative overflow-hidden group">
        <div class="absolute -right-8 -top-8 w-24 h-24 bg-purple-500/5 group-hover:bg-purple-500/10 rounded-full transition-colors duration-500"></div>
        <span class="text-[10px] font-bold text-purple-400/60 uppercase tracking-widest">Confiance IA Moyenne</span>
        <div class="flex items-baseline gap-2 mt-2">
          <span class="text-4xl font-black text-purple-400 drop-shadow-[0_0_8px_rgba(192,132,252,0.3)]">{{ averageConfidence }}%</span>
          <span class="text-xs text-sunset-secondary">sur la proba maximale</span>
        </div>
      </div>

      <!-- Active Engine -->
      <div class="liquid-glass rounded-2xl p-6 border border-sunset-primary/10 flex flex-col justify-between h-32 relative overflow-hidden group">
        <div class="absolute -right-8 -top-8 w-24 h-24 bg-sunset-primary/5 group-hover:bg-sunset-primary/10 rounded-full transition-colors duration-500"></div>
        <span class="text-[10px] font-bold text-sunset-primary/70 uppercase tracking-widest">Moteur Actif</span>
        <div class="flex flex-col mt-2">
          <span class="text-lg font-black text-white tracking-wide">XGBoost Optimized</span>
          <span class="text-[9px] font-mono text-sunset-accent/60 uppercase mt-0.5">Hot-serving champion_model</span>
        </div>
      </div>

    </div>

    <!-- Filters Panel -->
    <div class="liquid-glass rounded-2xl p-5 border border-white/10 flex flex-col md:flex-row gap-5 items-center justify-between shadow-[0_0_20px_rgba(0,0,0,0.3)] relative z-20">
      
      <!-- Search Input -->
      <div class="relative w-full md:w-80">
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Rechercher une équipe..." 
          class="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-2.5 pl-10 text-white placeholder-white/30 text-sm outline-none focus:border-sunset-accent/50 focus:bg-black/60 transition-all"
        />
        <svg class="absolute left-3.5 top-3 w-4 h-4 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </div>

      <!-- Action Toggles -->
      <div class="flex flex-wrap gap-4 w-full md:w-auto items-center justify-end">
        
        <!-- Status Filter -->
        <div class="flex bg-black/40 border border-white/10 rounded-xl p-1 text-xs">
          <button 
            @click="filterStatus = 'all'"
            :class="filterStatus === 'all' ? 'bg-sunset-accent/20 border-sunset-accent/30 text-white' : 'text-white/40 hover:text-white/80'"
            class="px-3 py-1.5 rounded-lg font-bold border border-transparent transition-all"
          >
            Tous
          </button>
          <button 
            @click="filterStatus = 'finished'"
            :class="filterStatus === 'finished' ? 'bg-sunset-accent/20 border-sunset-accent/30 text-white' : 'text-white/40 hover:text-white/80'"
            class="px-3 py-1.5 rounded-lg font-bold border border-transparent transition-all"
          >
            Terminés
          </button>
          <button 
            @click="filterStatus = 'scheduled'"
            :class="filterStatus === 'scheduled' ? 'bg-sunset-accent/20 border-sunset-accent/30 text-white' : 'text-white/40 hover:text-white/80'"
            class="px-3 py-1.5 rounded-lg font-bold border border-transparent transition-all"
          >
            Planifiés
          </button>
        </div>

        <!-- Result Filter -->
        <div class="flex bg-black/40 border border-white/10 rounded-xl p-1 text-xs">
          <button 
            @click="filterResult = 'all'"
            :class="filterResult === 'all' ? 'bg-sunset-accent/20 border-sunset-accent/30 text-white' : 'text-white/40 hover:text-white/80'"
            class="px-3 py-1.5 rounded-lg font-bold border border-transparent transition-all"
          >
            Tout Résultat
          </button>
          <button 
            @click="filterResult = 'correct'"
            :class="filterResult === 'correct' ? 'bg-green-500/20 border-green-500/30 text-green-300' : 'text-white/40 hover:text-white/80'"
            class="px-3 py-1.5 rounded-lg font-bold border border-transparent transition-all"
          >
            Corrects
          </button>
          <button 
            @click="filterResult = 'incorrect'"
            :class="filterResult === 'incorrect' ? 'bg-red-500/20 border-red-500/30 text-red-300' : 'text-white/40 hover:text-white/80'"
            class="px-3 py-1.5 rounded-lg font-bold border border-transparent transition-all"
          >
            Incorrects
          </button>
        </div>

      </div>

    </div>

    <!-- History items -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-4">
      <svg class="animate-spin w-8 h-8 text-sunset-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
      </svg>
      <span class="text-sm font-semibold tracking-wider text-sunset-secondary">Décryptage du registre neural...</span>
    </div>

    <div v-else-if="fetchError" class="liquid-glass rounded-2xl p-16 border border-red-400/20 text-center flex flex-col items-center gap-4">
      <h3 class="text-xl font-bold text-red-300">Erreur de chargement</h3>
      <p class="text-sm text-sunset-secondary max-w-md">{{ fetchError }}</p>
      <button @click="fetchHistory" class="mt-4 px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-bold rounded-xl">
        Réessayer
      </button>
    </div>

    <div v-else-if="filteredPredictions.length === 0" class="liquid-glass rounded-2xl p-16 border border-white/5 text-center flex flex-col items-center gap-4">
      <div class="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center text-white/20 border border-white/10 text-2xl font-black mb-2">?</div>
      <h3 class="text-xl font-bold text-white">Aucune prédiction enregistrée</h3>
      <p class="text-sm text-sunset-secondary max-w-md">{{ predictions.length === 0 ? 'Lancez une simulation depuis la page Prédictions pour alimenter votre historique.' : 'Aucun résultat ne correspond à vos filtres de recherche.' }}</p>
      <button @click="router.push('/prediction')" class="mt-4 px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-bold rounded-xl shadow-[0_0_15px_rgba(168,85,247,0.4)]">
        Faire une prédiction
      </button>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      
      <!-- Prediction Card -->
      <div 
        v-for="pred in filteredPredictions" 
        :key="pred.id"
        class="liquid-glass rounded-2xl p-6 border transition-all duration-300 relative overflow-hidden group flex flex-col justify-between"
        :class="[
          isMatchFinished(pred) 
            ? (isPredictionCorrect(pred) ? 'border-green-500/20 hover:border-green-500/40 shadow-[0_0_30px_rgba(34,197,94,0.02)]' : 'border-red-500/20 hover:border-red-500/40 shadow-[0_0_30px_rgba(239,68,68,0.02)]')
            : 'border-white/10 hover:border-sunset-accent/40 shadow-lg'
        ]"
      >
        <!-- Subtle Glow status background -->
        <div 
          class="absolute inset-0 pointer-events-none transition-opacity duration-500 opacity-0 group-hover:opacity-100"
          :class="[
            isMatchFinished(pred)
              ? (isPredictionCorrect(pred) ? 'bg-gradient-to-br from-green-500/5 to-transparent' : 'bg-gradient-to-br from-red-500/5 to-transparent')
              : 'bg-gradient-to-br from-sunset-primary/5 to-transparent'
          ]"
        ></div>

        <!-- Card Top Bar -->
        <div class="flex justify-between items-center mb-6 relative z-10 border-b border-white/5 pb-4">
          <div class="flex flex-col">
            <span class="text-[9px] font-mono tracking-widest text-sunset-accent/50 uppercase font-black">Simulation #{{ pred.id }}</span>
            <span class="text-[10px] text-white/40 mt-0.5">{{ new Date(pred.created_at).toLocaleString() }}</span>
          </div>

          <div class="flex items-center gap-2">
            <!-- Correct/Incorrect/Unfinished Status Badge -->
            <template v-if="isMatchFinished(pred)">
              <span 
                v-if="isPredictionCorrect(pred)"
                class="text-[9px] font-black px-2.5 py-1 bg-green-500/10 border border-green-500/30 text-green-400 rounded-md tracking-wider flex items-center gap-1 shadow-[0_0_10px_rgba(34,197,94,0.2)]"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
                CORRECT
              </span>
              <span 
                v-else
                class="text-[9px] font-black px-2.5 py-1 bg-red-500/10 border border-red-500/30 text-red-400 rounded-md tracking-wider flex items-center gap-1 shadow-[0_0_10px_rgba(239,68,68,0.2)]"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-red-400"></span>
                ÉCHEC
              </span>
            </template>
            <template v-else>
              <span class="text-[9px] font-black px-2.5 py-1 bg-purple-500/10 border border-purple-500/30 text-purple-400 rounded-md tracking-wider flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse"></span>
                EN ATTENTE
              </span>
            </template>
          </div>
        </div>

        <!-- Teams Representation -->
        <div class="flex justify-between items-center gap-4 relative z-10 py-2">
          
          <!-- Home -->
          <div class="flex flex-col items-center w-5/12 gap-3">
            <TeamGlow :team-name="pred.match.home_team.name" size="lg" class="group-hover:scale-105 transition-transform duration-300">
              <img
                v-if="pred.match.home_team.logo"
                :src="pred.match.home_team.logo"
                :alt="pred.match.home_team.name"
                class="w-full h-full object-contain p-1"
              />
              <div v-else class="text-xs text-white/50 font-bold font-mono">{{ getInitials(pred.match.home_team.name) }}</div>
            </TeamGlow>
            <span class="text-xs text-white font-bold tracking-wide text-center leading-snug truncate w-full">{{ pred.match.home_team.name }}</span>
            <span v-if="pred.match.home_team.elo_rating" class="text-[9px] text-white/30 font-mono">Elo {{ Math.round(pred.match.home_team.elo_rating) }}</span>
          </div>

          <!-- Score / Central Separator -->
          <div class="w-2/12 flex flex-col items-center justify-center">
            <div 
              v-if="isMatchFinished(pred)" 
              class="flex items-center gap-2 px-3 py-1.5 bg-black/60 rounded-xl border border-white/10 text-white font-black text-base shadow-[0_0_15px_rgba(0,0,0,0.5)]"
            >
              <span>{{ pred.real_home_score }}</span>
              <span class="text-sunset-accent/40 font-normal">:</span>
              <span>{{ pred.real_away_score }}</span>
            </div>
            <span v-else class="text-xs font-bold italic text-sunset-accent/30 tracking-widest uppercase">VS</span>
          </div>

          <!-- Away -->
          <div class="flex flex-col items-center w-5/12 gap-3">
            <TeamGlow :team-name="pred.match.away_team.name" size="lg" class="group-hover:scale-105 transition-transform duration-300">
              <img
                v-if="pred.match.away_team.logo"
                :src="pred.match.away_team.logo"
                :alt="pred.match.away_team.name"
                class="w-full h-full object-contain p-1"
              />
              <div v-else class="text-xs text-white/50 font-bold font-mono">{{ getInitials(pred.match.away_team.name) }}</div>
            </TeamGlow>
            <span class="text-xs text-white font-bold tracking-wide text-center leading-snug truncate w-full">{{ pred.match.away_team.name }}</span>
            <span v-if="pred.match.away_team.elo_rating" class="text-[9px] text-white/30 font-mono">Elo {{ Math.round(pred.match.away_team.elo_rating) }}</span>
          </div>

        </div>

        <!-- Prediction outcome bar -->
        <div class="mt-8 pt-4 border-t border-white/5 relative z-10 space-y-4">
          
          <!-- User Prediction Output -->
          <div class="flex justify-between items-center text-xs">
            <span class="text-white/50">Prédiction Pronostic :</span>
            <span 
              class="font-black tracking-wide uppercase px-2.5 py-1 rounded-md"
              :class="[
                pred.predicted_result === 'H' ? 'bg-sunset-primary/10 border border-sunset-primary/30 text-sunset-primary' : '',
                pred.predicted_result === 'D' ? 'bg-sunset-secondary/10 border border-sunset-secondary/30 text-sunset-secondary' : '',
                pred.predicted_result === 'A' ? 'bg-sunset-accent/10 border border-sunset-accent/30 text-sunset-accent' : ''
              ]"
            >
              {{ formatResult(pred.predicted_result) }}
            </span>
          </div>

          <!-- Probability Bar component -->
          <div class="opacity-95">
            <ProbabilityBar 
              :probH="pred.prob_h" 
              :probD="pred.prob_d" 
              :probA="pred.prob_a"
              :homeLabel="pred.match.home_team.name"
              :awayLabel="pred.match.away_team.name"
            />
          </div>
        </div>

      </div>

    </div>

  </div>
</template>

<style scoped>
</style>
