<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api/axios'
import HeroPredictionCard from '../components/dashboard/HeroPredictionCard.vue'
import MatchCard from '../components/dashboard/MatchCard.vue'
import InsightPanel from '../components/dashboard/InsightPanel.vue'
import { useAuthStore } from '../stores/auth'
import bgStadium1 from '../assets/backgrounds/bg_stadium_1.jpg'

const authStore = useAuthStore()

interface MatchData {
  id: number | string
  match_date: string
  status: string
  home_team: { name: string }
  away_team: { name: string }
}

interface PredictionData {
  homeTeam: string
  awayTeam: string
  probH: number
  probD: number
  probA: number
}

const matches = ref<MatchData[]>([])
const loadingHero = ref(false)
const topPrediction = ref<PredictionData | null>(null)

const fetchMatches = async () => {
  try {
    const res = await api.get('/matches')
    matches.value = res.data.slice(0, 4) // On prend les 4 prochains matchs
  } catch (e) {
    console.error("Failed to load matches", e)
  }
}

const runPrediction = async (home: string, away: string) => {
  loadingHero.value = true
  try {
    const res = await api.post(`/predict?home_team_name=${encodeURIComponent(home)}&away_team_name=${encodeURIComponent(away)}`)
    topPrediction.value = {
      homeTeam: home,
      awayTeam: away,
      probH: res.data.probabilities.H,
      probD: res.data.probabilities.D,
      probA: res.data.probabilities.A
    }
  } catch (e) {
    console.error("Prediction failed", e)
  } finally {
    loadingHero.value = false
  }
}

onMounted(async () => {
  await fetchMatches()
  
  // Par défaut, on lance la prédiction sur le premier match disponible
  const firstMatch = matches.value[0]
  if (firstMatch) {
    runPrediction(firstMatch.home_team.name, firstMatch.away_team.name)
  }
})
</script>

<template>
  <!-- Background Image with Overlay -->
  <div class="fixed inset-0 z-[-1] pointer-events-none bg-[#010108]">
    <img :src="bgStadium1" alt="Stadium Background" class="w-full h-full object-cover opacity-80" />
    <div class="absolute inset-0 bg-gradient-to-t from-[#010108]/80 via-transparent to-transparent"></div>
  </div>

  <div class="space-y-10 pb-12 w-full max-w-6xl mx-auto pt-8 relative z-10">
    
    <!-- Topbar AI Status -->
    <div class="flex justify-between items-end border-b border-sunset-primary/20 pb-6 relative">
      <div class="absolute -left-20 -top-20 w-64 h-64 bg-sunset-primary/10 blur-[80px] rounded-full pointer-events-none"></div>
      
      <div class="relative z-10">
        <h1 class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-sunset-accent tracking-tight">AI Command Center</h1>
        <p class="text-sunset-secondary mt-1 font-medium">Welcome back, <span class="text-sunset-primary">{{ authStore.user?.username || 'Analyst' }}</span>.</p>
      </div>
      <div class="flex items-center gap-3 liquid-glass px-4 py-2 rounded-xl relative z-10">
        <span class="flex h-3 w-3 relative">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500 shadow-[0_0_8px_#22c55e]"></span>
        </span>
        <span class="text-xs font-semibold text-white/80 uppercase tracking-widest">Neural Engine Online</span>
      </div>
    </div>

    <!-- Hero Section -->
    <div class="w-full">
      <HeroPredictionCard 
        v-if="topPrediction"
        :homeTeam="topPrediction.homeTeam"
        :awayTeam="topPrediction.awayTeam"
        :probH="topPrediction.probH"
        :probD="topPrediction.probD"
        :probA="topPrediction.probA"
        :loading="loadingHero"
      />
      <!-- Loading Skeleton Premium -->
      <div v-else class="h-[280px] w-full liquid-glass rounded-[23px] flex items-center justify-center border border-sunset-primary/10 relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-sunset-primary/10 to-transparent -translate-x-full animate-[shimmer_2s_infinite]"></div>
        <span class="text-sunset-accent/50 font-medium tracking-widest uppercase text-sm animate-pulse">Initializing Interface...</span>
      </div>
    </div>

    <!-- Grid Layout: Matches & Insights -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <!-- Match List -->
      <div class="lg:col-span-2 flex flex-col gap-5">
        <h3 class="text-white font-bold text-xl tracking-wide flex items-center gap-2">
          Upcoming Fixtures
        </h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div 
            v-for="match in matches" 
            :key="match.id" 
            @click="runPrediction(match.home_team.name, match.away_team.name)"
            class="h-full"
          >
            <MatchCard 
              :homeTeam="match.home_team.name"
              :awayTeam="match.away_team.name"
              :date="new Date(match.match_date).toLocaleDateString()"
              :status="match.status"
            />
          </div>
        </div>
      </div>

      <!-- Insight Panel -->
      <div class="lg:col-span-1">
        <InsightPanel 
          insight="Marseille shows strong home form over the last 5 matches. Their xG creation in the final third has increased by 14% since the new tactical adjustment." 
        />
      </div>

    </div>
  </div>
</template>

<style scoped>
@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}
</style>
