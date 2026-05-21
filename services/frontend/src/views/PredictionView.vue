<template>
  <div class="fixed inset-0 z-[-1] pointer-events-none bg-[#050510]">
    <img src="../assets/backgrounds/bg_stadium_3.jpg" alt="Stadium" class="w-full h-full object-cover opacity-80" />
    <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900/20 via-[#050510]/40 to-[#050510]"></div>
  </div>

  <div class="max-w-[1400px] mx-auto pt-6 px-4 pb-12 relative z-10 min-h-screen flex flex-col">
    
    <!-- Header -->
    <div class="flex justify-between items-start mb-4">
      <div>
        <h1 class="text-3xl font-black text-white tracking-widest uppercase mb-1">
          Prédiction IA <span class="ml-4 text-xs font-semibold px-3 py-1 rounded-full border border-purple-500/50 text-purple-400 bg-purple-500/10">Mode IA Avancé</span>
        </h1>
        <p class="text-sm text-gray-400">{{ predictionState === 'idle' ? 'En attente de configuration...' : (predictionState === 'loading' ? 'Analyse en cours...' : 'Simulation terminée.') }}</p>
      </div>
      <button @click="$router.push('/dashboard')" class="flex items-center gap-2 px-4 py-2 border border-white/20 rounded-lg text-white/70 hover:bg-white/5 transition-colors">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
        Retour
      </button>
    </div>

    <div
      v-if="predictionState === 'reveal' && savedToHistory"
      class="mb-4 flex flex-wrap items-center justify-between gap-3 liquid-glass rounded-xl px-5 py-3 border border-sunset-primary/40"
    >
      <p class="text-sm text-sunset-accent">
        Prédiction enregistrée dans votre historique.
      </p>
      <button
        type="button"
        @click="router.push('/history')"
        class="text-sm font-semibold px-4 py-2 rounded-lg bg-gradient-to-r from-sunset-primary to-sunset-secondary text-white hover:shadow-[0_0_15px_rgba(200,118,255,0.35)] transition-all"
      >
        Voir l'historique →
      </button>
    </div>

    <!-- Main Data Link Container -->
    <div class="relative w-full flex-1 flex flex-col items-center justify-center mt-8">
      
      <!-- Energy Lines (SVG Background) -->
      <svg class="absolute inset-0 w-full h-full pointer-events-none z-0 opacity-60" :class="{'animate-pulse': predictionState === 'loading'}">
        <defs>
          <linearGradient id="grad-cyan" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#00f2fe" stop-opacity="0" />
            <stop offset="100%" stop-color="#4facfe" stop-opacity="0.8" />
          </linearGradient>
          <linearGradient id="grad-purple" x1="100%" y1="0%" x2="0%" y2="0%">
            <stop offset="0%" stop-color="#f093fb" stop-opacity="0" />
            <stop offset="100%" stop-color="#f5576c" stop-opacity="0.8" />
          </linearGradient>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="8" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>
        
        <!-- Center coordinate ~700, 250. Left panel ~250. Right panel ~1150 -->
        <g transform="translate(0, -30)">
          <!-- Left to Center lines -->
          <path d="M 300 250 C 500 250, 450 250, 700 250" fill="none" stroke="url(#grad-cyan)" stroke-width="3" filter="url(#glow)"/>
          <path d="M 300 150 C 500 150, 500 250, 700 250" fill="none" stroke="url(#grad-cyan)" stroke-width="1.5" stroke-dasharray="4 4" class="animate-[dash_20s_linear_infinite]"/>
          <path d="M 300 350 C 500 350, 500 250, 700 250" fill="none" stroke="url(#grad-cyan)" stroke-width="1.5" stroke-dasharray="4 4" class="animate-[dash_20s_linear_infinite]"/>
          
          <!-- Right to Center lines -->
          <path d="M 1100 250 C 900 250, 950 250, 700 250" fill="none" stroke="url(#grad-purple)" stroke-width="3" filter="url(#glow)"/>
          <path d="M 1100 150 C 900 150, 900 250, 700 250" fill="none" stroke="url(#grad-purple)" stroke-width="1.5" stroke-dasharray="4 4" class="animate-[dash_20s_linear_infinite_reverse]"/>
          <path d="M 1100 350 C 900 350, 900 250, 700 250" fill="none" stroke="url(#grad-purple)" stroke-width="1.5" stroke-dasharray="4 4" class="animate-[dash_20s_linear_infinite_reverse]"/>
        </g>
      </svg>

      <!-- 3 Columns Layout: Home, Orb, Away -->
      <div class="flex items-center justify-between w-full max-w-[1250px] relative z-10 gap-4 h-[500px]">
        
        <!-- Left Panel: Home Team -->
        <div class="w-[340px] h-[480px] relative rounded-3xl border border-cyan-500/50 bg-[#060b19]/80 backdrop-blur-md flex flex-col items-center p-6 shadow-[0_0_50px_rgba(34,211,238,0.15),_inset_0_0_20px_rgba(34,211,238,0.1)] overflow-hidden">
          <div class="absolute top-0 right-0 w-24 h-24 bg-cyan-500/10" style="clip-path: polygon(100% 0, 0 0, 100% 100%);"></div>
          <div class="absolute bottom-0 left-0 w-24 h-24 bg-cyan-500/10" style="clip-path: polygon(0 100%, 0 0, 100% 100%);"></div>

          <!-- Logo & Dropdown -->
          <div class="relative w-32 h-32 mt-4 mb-4">
             <div class="absolute inset-0 bg-cyan-500/20 blur-[30px] rounded-full"></div>
             <img v-if="homeTeamObj?.logo" :src="homeTeamObj.logo" class="relative z-10 w-full h-full object-contain drop-shadow-[0_0_15px_rgba(34,211,238,0.5)]" />
             <div v-else class="relative z-10 w-full h-full border-2 border-dashed border-cyan-500/50 rounded-full flex items-center justify-center text-cyan-500 font-bold">Logo</div>
          </div>
          
          <div class="relative w-full mb-2 group">
            <select v-model="homeTeam" class="w-full bg-transparent border-none text-center text-[22px] leading-tight font-black text-white uppercase tracking-wider outline-none appearance-none cursor-pointer hover:text-cyan-300 transition-colors">
              <option value="" class="bg-black" disabled>DOMICILE</option>
              <option v-for="team in availableHomeTeams" :key="team.club_name" :value="team.club_name" class="bg-[#050510] text-sm">
                {{ team.club_name }}
              </option>
            </select>
          </div>
          
          <div class="px-3 py-1 bg-cyan-500/10 border border-cyan-500/30 rounded-md text-cyan-400 text-[10px] font-bold tracking-widest mb-6 flex items-center gap-1">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path></svg>
            DOMICILE
          </div>

          <!-- Stats -->
          <div class="w-full text-center space-y-4 transition-opacity duration-500" :class="predictionState === 'reveal' ? 'opacity-100' : 'opacity-20'">
            <div>
              <div class="text-[40px] leading-none font-black text-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.8)]">{{ result.homeProb ? (result.homeProb * 100).toFixed(1) : '--' }}%</div>
              <div class="text-[10px] text-cyan-200/50 uppercase tracking-widest mt-1">Probabilité de Victoire</div>
            </div>
            <div class="h-px w-full bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent"></div>
            <div>
              <div class="text-2xl font-bold text-white">{{ (homeStats.xg).toFixed(2) }}</div>
              <div class="text-[10px] text-cyan-200/50 uppercase tracking-widest">xG Moyen</div>
            </div>
            <div class="flex items-center justify-center gap-4 mt-4">
              <span class="text-[10px] text-cyan-200/50 uppercase tracking-widest">Forme</span>
              <div class="flex gap-1">
                <div v-for="i in 5" :key="i" class="w-5 h-2 rounded-[2px]" :class="i <= homeStats.form ? 'bg-cyan-400 shadow-[0_0_5px_rgba(34,211,238,0.8)]' : 'bg-white/10'"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Floating Data Badges Left -->
        <div class="flex flex-col gap-8 w-28 relative z-20 items-end">
          <div class="px-4 py-1.5 bg-[#060b19]/80 backdrop-blur-md rounded-lg border border-cyan-500/40 text-[10px] font-bold tracking-widest uppercase text-center shadow-[0_0_15px_rgba(0,0,0,0.5)] whitespace-nowrap text-cyan-100">xG {{ homeStats.xg.toFixed(2) }}</div>
          <div class="px-4 py-1.5 bg-[#060b19]/80 backdrop-blur-md rounded-lg border border-cyan-500/40 text-[10px] font-bold tracking-widest uppercase text-center shadow-[0_0_15px_rgba(0,0,0,0.5)] whitespace-nowrap text-cyan-100">Possession {{ homeStats.possession }}%</div>
          <div class="px-4 py-1.5 bg-[#060b19]/80 backdrop-blur-md rounded-lg border border-cyan-500/40 text-[10px] font-bold tracking-widest uppercase text-center shadow-[0_0_15px_rgba(0,0,0,0.5)] whitespace-nowrap text-cyan-100">Forme +{{ homeStats.form * 3 }}%</div>
          <div class="px-4 py-1.5 bg-[#060b19]/80 backdrop-blur-md rounded-lg border border-cyan-500/40 text-[10px] font-bold tracking-widest uppercase text-center shadow-[0_0_15px_rgba(0,0,0,0.5)] whitespace-nowrap text-cyan-100">Attaque {{ homeStats.attack }}</div>
          <div class="px-4 py-1.5 bg-[#060b19]/80 backdrop-blur-md rounded-lg border border-cyan-500/40 text-[10px] font-bold tracking-widest uppercase text-center shadow-[0_0_15px_rgba(0,0,0,0.5)] whitespace-nowrap text-cyan-100">Défense {{ homeStats.defense }}</div>
        </div>

        <!-- Central Orb Area -->
        <div class="w-[300px] h-[300px] flex items-center justify-center relative z-30">
          <div class="absolute top-[-60px] text-[12px] font-bold tracking-[0.2em] text-white/70 w-full text-center uppercase">
            {{ predictionState === 'idle' ? 'EN ATTENTE' : (predictionState === 'loading' ? 'ANALYSE EN COURS' : 'PRÉDICTION IA TERMINÉE') }}
          </div>
          
          <NeuralCore :state="predictionState" />

          <div class="absolute bottom-[-60px] w-64 flex flex-col items-center opacity-100 transition-opacity" :class="{'opacity-0': predictionState === 'idle'}">
            <span class="text-[10px] font-bold tracking-[0.2em] text-cyan-400 mb-2">SIMULATION EN COURS {{ loadingProgress }}%</span>
            <div class="w-full h-[3px] bg-white/10 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-cyan-500 to-purple-500 transition-all duration-300 shadow-[0_0_10px_#22d3ee]" :style="`width: ${loadingProgress}%`"></div>
            </div>
          </div>
        </div>

        <!-- Floating Data Badges Right -->
        <div class="flex flex-col gap-8 w-28 relative z-20 items-start">
          <div class="px-4 py-1.5 bg-[#060b19]/80 backdrop-blur-md rounded-lg border border-purple-500/40 text-[10px] font-bold tracking-widest uppercase text-center shadow-[0_0_15px_rgba(0,0,0,0.5)] whitespace-nowrap text-purple-100">xG {{ awayStats.xg.toFixed(2) }}</div>
          <div class="px-4 py-1.5 bg-[#060b19]/80 backdrop-blur-md rounded-lg border border-purple-500/40 text-[10px] font-bold tracking-widest uppercase text-center shadow-[0_0_15px_rgba(0,0,0,0.5)] whitespace-nowrap text-purple-100">Possession {{ awayStats.possession }}%</div>
          <div class="px-4 py-1.5 bg-[#060b19]/80 backdrop-blur-md rounded-lg border border-purple-500/40 text-[10px] font-bold tracking-widest uppercase text-center shadow-[0_0_15px_rgba(0,0,0,0.5)] whitespace-nowrap text-purple-100">Forme -{{ awayStats.form * 2 }}%</div>
          <div class="px-4 py-1.5 bg-[#060b19]/80 backdrop-blur-md rounded-lg border border-purple-500/40 text-[10px] font-bold tracking-widest uppercase text-center shadow-[0_0_15px_rgba(0,0,0,0.5)] whitespace-nowrap text-purple-100">Attaque {{ awayStats.attack }}</div>
          <div class="px-4 py-1.5 bg-[#060b19]/80 backdrop-blur-md rounded-lg border border-purple-500/40 text-[10px] font-bold tracking-widest uppercase text-center shadow-[0_0_15px_rgba(0,0,0,0.5)] whitespace-nowrap text-purple-100">Défense {{ awayStats.defense }}</div>
        </div>

        <!-- Right Panel: Away Team -->
        <div class="w-[340px] h-[480px] relative rounded-3xl border border-purple-500/50 bg-[#060b19]/80 backdrop-blur-md flex flex-col items-center p-6 shadow-[0_0_50px_rgba(168,85,247,0.15),_inset_0_0_20px_rgba(168,85,247,0.1)] overflow-hidden">
          <div class="absolute top-0 left-0 w-24 h-24 bg-purple-500/10" style="clip-path: polygon(0 0, 100% 0, 0 100%);"></div>
          <div class="absolute bottom-0 right-0 w-24 h-24 bg-purple-500/10" style="clip-path: polygon(100% 100%, 0 100%, 100% 0);"></div>

          <!-- Logo & Dropdown -->
          <div class="relative w-32 h-32 mt-4 mb-4">
             <div class="absolute inset-0 bg-purple-500/20 blur-[30px] rounded-full"></div>
             <img v-if="awayTeamObj?.logo" :src="awayTeamObj.logo" class="relative z-10 w-full h-full object-contain drop-shadow-[0_0_15px_rgba(168,85,247,0.5)]" />
             <div v-else class="relative z-10 w-full h-full border-2 border-dashed border-purple-500/50 rounded-full flex items-center justify-center text-purple-500 font-bold">Logo</div>
          </div>
          
          <div class="relative w-full mb-2 group">
            <select v-model="awayTeam" class="w-full bg-transparent border-none text-center text-[22px] leading-tight font-black text-white uppercase tracking-wider outline-none appearance-none cursor-pointer hover:text-purple-300 transition-colors">
              <option value="" class="bg-black" disabled>EXTÉRIEUR</option>
              <option v-for="team in availableAwayTeams" :key="team.club_name" :value="team.club_name" class="bg-[#050510] text-sm">
                {{ team.club_name }}
              </option>
            </select>
          </div>
          
          <div class="px-3 py-1 bg-purple-500/10 border border-purple-500/30 rounded-md text-purple-400 text-[10px] font-bold tracking-widest mb-6 flex items-center gap-1">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"></path></svg>
            EXTÉRIEUR
          </div>

          <!-- Stats -->
          <div class="w-full text-center space-y-4 transition-opacity duration-500" :class="predictionState === 'reveal' ? 'opacity-100' : 'opacity-20'">
            <div>
              <div class="text-[40px] leading-none font-black text-purple-400 drop-shadow-[0_0_10px_rgba(168,85,247,0.8)]">{{ result.awayProb ? (result.awayProb * 100).toFixed(1) : '--' }}%</div>
              <div class="text-[10px] text-purple-200/50 uppercase tracking-widest mt-1">Probabilité de Victoire</div>
            </div>
            <div class="h-px w-full bg-gradient-to-r from-transparent via-purple-500/30 to-transparent"></div>
            <div>
              <div class="text-2xl font-bold text-white">{{ (awayStats.xg).toFixed(2) }}</div>
              <div class="text-[10px] text-purple-200/50 uppercase tracking-widest">xG Moyen</div>
            </div>
            <div class="flex items-center justify-center gap-4 mt-4">
              <span class="text-[10px] text-purple-200/50 uppercase tracking-widest">Forme</span>
              <div class="flex gap-1">
                <div v-for="i in 5" :key="i" class="w-5 h-2 rounded-[2px]" :class="i <= awayStats.form ? 'bg-purple-400 shadow-[0_0_5px_rgba(168,85,247,0.8)]' : 'bg-white/10'"></div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Bottom Action Row -->
    <div class="flex justify-between items-end w-full max-w-[1250px] mt-10">
      
      <!-- Facteurs Clés -->
      <div class="w-[300px] h-[140px] bg-[#060b19]/80 border border-white/10 rounded-2xl p-5 backdrop-blur-md shadow-[0_0_20px_rgba(0,0,0,0.5)]">
        <h4 class="text-[10px] font-bold text-white/50 uppercase tracking-widest mb-3">Facteurs Clés</h4>
        <ul class="space-y-2">
          <li v-for="(val, key) in (result.explainability || mockFactors)" :key="key" class="flex items-center gap-2 text-[11px] text-white/90">
            <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" :class="val.toString().trim().startsWith('+') ? 'bg-cyan-400 shadow-[0_0_6px_#22d3ee]' : (val.toString().trim().startsWith('-') ? 'bg-purple-500 shadow-[0_0_6px_#a855f7]' : 'bg-slate-400')"></span>
            <span class="truncate" :class="val.toString().trim().startsWith('+') ? 'text-cyan-200 font-medium' : (val.toString().trim().startsWith('-') ? 'text-purple-300 font-medium' : 'text-white/80')">
              {{ val }}
            </span>
          </li>
        </ul>
      </div>

      <!-- Predict Button & Model Info -->
      <div class="flex flex-col items-center gap-2">
        <button 
          @click="runPrediction"
          :disabled="!canPredict || predictionState === 'loading'"
          class="relative w-[500px] h-16 rounded-2xl border border-white/20 bg-gradient-to-b from-[#111936] to-[#060b19] overflow-hidden group hover:border-cyan-400/50 transition-colors disabled:opacity-50"
        >
          <div class="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="relative z-10 flex items-center justify-center gap-4 h-full">
            <svg class="w-5 h-5 text-white/70" :class="{'animate-spin text-cyan-400': predictionState === 'loading'}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
            <span class="text-xl font-bold text-white tracking-[0.4em] uppercase">{{ predictionState === 'reveal' ? 'REDIRE' : 'PRÉDIRE' }}</span>
          </div>
        </button>
        <div v-if="predictionState === 'reveal' && result.model" class="text-[9px] font-mono tracking-wider text-white/40 uppercase">
          Moteur Actif: <span class="text-cyan-400 font-bold">{{ result.model }}</span> (<span class="text-purple-400 font-bold">{{ result.version }}</span>)
        </div>
      </div>

      <!-- Confidence Gauge -->
      <div class="w-[300px] h-[140px] bg-[#060b19]/80 border border-white/10 rounded-2xl p-5 backdrop-blur-md flex items-center justify-between shadow-[0_0_20px_rgba(0,0,0,0.5)]">
        <h4 class="text-[10px] font-bold text-white/50 uppercase tracking-widest w-24">Confiance IA</h4>
        <div class="relative w-24 h-24 flex items-center justify-center">
          <svg class="absolute inset-0 w-full h-full transform -rotate-90">
            <circle cx="48" cy="48" r="40" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="6" />
            <circle cx="48" cy="48" r="40" fill="none" :stroke="predictionState === 'reveal' ? '#22d3ee' : 'transparent'" stroke-width="6" stroke-dasharray="251.2" :stroke-dashoffset="251.2 - (251.2 * (result.confidence || 0)) / 100" class="transition-all duration-1000 ease-out drop-shadow-[0_0_10px_rgba(34,211,238,0.8)]" />
          </svg>
          <div class="flex flex-col items-center mt-1">
            <span class="text-2xl font-black text-white leading-none">{{ predictionState === 'reveal' ? result.confidence : '--' }}%</span>
            <span class="text-[8px] text-cyan-400 font-bold uppercase tracking-widest mt-1" v-if="predictionState === 'reveal'">{{ (result.confidence || 0) > 75 ? 'Élevée' : 'Moyenne' }}</span>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/axios'
import NeuralCore from '../components/prediction/NeuralCore.vue'

interface Team {
  club_name: string
  wins: number
  losses: number
  logo?: string
  [key: string]: unknown
}

interface PredictionResult {
  homeProb?: number
  awayProb?: number
  drawProb?: number
  confidence?: number
  explainability?: string[]
  model?: string
  version?: string
}

const route = useRoute()
const router = useRouter()
const savedToHistory = ref(false)
const teams = ref<Team[]>([])
const homeTeam = ref(route.query.home as string || '')
const awayTeam = ref(route.query.away as string || '')

const predictionState = ref<'idle' | 'loading' | 'reveal'>('idle')
const result = ref<PredictionResult>({})
const loadingProgress = ref(0)

const mockFactors = [
  "Avantage à domicile",
  "Meilleure forme offensive",
  "xG supérieur",
  "Fatigue défensive adversaire"
]

const homeStats = computed(() => {
  const team = teams.value.find(t => t.club_name === homeTeam.value)
  if (!team) return { xg: 1.89, possession: 62, form: 4, attack: 86, defense: 78 }
  return {
    xg: 1.0 + (team.wins * 0.1),
    possession: 50 + (team.wins - team.losses),
    form: Math.min(5, Math.max(1, Math.round(team.wins / 3))),
    attack: 70 + team.wins,
    defense: 90 - team.losses
  }
})

const awayStats = computed(() => {
  const team = teams.value.find(t => t.club_name === awayTeam.value)
  if (!team) return { xg: 1.12, possession: 38, form: 2, attack: 72, defense: 65 }
  return {
    xg: 1.0 + (team.wins * 0.1),
    possession: 50 + (team.wins - team.losses),
    form: Math.min(5, Math.max(1, Math.round(team.wins / 3))),
    attack: 70 + team.wins,
    defense: 90 - team.losses
  }
})

onMounted(async () => {
  try {
    const res = await api.get('/standings')
    teams.value = res.data
    if (!homeTeam.value && teams.value.length > 0) homeTeam.value = teams.value[0]?.club_name || ''
    if (!awayTeam.value && teams.value.length > 1) awayTeam.value = teams.value[1]?.club_name || ''
  } catch (e) {
    console.error("Failed to load teams", e)
  }
})

const availableHomeTeams = computed(() => teams.value.filter(t => t.club_name !== awayTeam.value))
const availableAwayTeams = computed(() => teams.value.filter(t => t.club_name !== homeTeam.value))

const homeTeamObj = computed(() => teams.value.find(t => t.club_name === homeTeam.value))
const awayTeamObj = computed(() => teams.value.find(t => t.club_name === awayTeam.value))

const canPredict = computed(() => homeTeam.value && awayTeam.value && homeTeam.value !== awayTeam.value)

const runPrediction = async () => {
  savedToHistory.value = false
  predictionState.value = 'loading'
  loadingProgress.value = 0
  
  const interval = setInterval(() => {
    loadingProgress.value += Math.floor(Math.random() * 5) + 2
    if (loadingProgress.value >= 100) {
      loadingProgress.value = 100
      clearInterval(interval)
    }
  }, 100)

  try {
    await new Promise(r => setTimeout(r, 2000))
    const res = await api.post(`/predict?home_team_name=${encodeURIComponent(homeTeam.value)}&away_team_name=${encodeURIComponent(awayTeam.value)}`)
    const data = res.data
    const probs = data.probabilities
    
    result.value = {
      homeProb: probs.H,
      awayProb: probs.A,
      drawProb: probs.D,
      confidence: data.confidence_score || Math.round(Math.max(probs.H, probs.D, probs.A) * 100),
      explainability: data.explainability || mockFactors,
      model: data.model,
      version: data.version
    }
    predictionState.value = 'reveal'
    savedToHistory.value = true
    loadingProgress.value = 100
  } catch (e) {
    console.error("Prediction failed:", e)
    predictionState.value = 'idle'
  } finally {
    clearInterval(interval)
  }
}
</script>

<style scoped>

@keyframes dash {
  to { stroke-dashoffset: -100; }
}
</style>
