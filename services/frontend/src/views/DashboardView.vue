<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'
import MatchCard from '../components/dashboard/MatchCard.vue'
import LeagueStandings from '../components/dashboard/LeagueStandings.vue'
import TopScorers from '../components/dashboard/TopScorers.vue'
import { useAuthStore } from '../stores/auth'
import bgStadium1 from '../assets/backgrounds/bg_stadium_1.jpg'

const authStore = useAuthStore()
const router = useRouter()

interface MatchData {
  id: number | string
  match_date: string
  status: string
  home_team: { name: string }
  away_team: { name: string }
  home_score?: number | null
  away_score?: number | null
}

const matches = ref<MatchData[]>([])
const currentGameweek = ref<number>(0)

const fetchMatches = async () => {
  try {
    const res = await api.get('/current-matchday')
    matches.value = res.data.matches
    currentGameweek.value = res.data.gameweek
  } catch (e) {
    console.error("Failed to load matches", e)
  }
}

const runPrediction = (home: string, away: string) => {
  router.push({ path: '/prediction', query: { home, away } })
}

onMounted(async () => {
  await fetchMatches()
})
</script>

<template>
  <div class="fixed inset-0 z-[-1] pointer-events-none bg-[#010108]">
    <img :src="bgStadium1" alt="Stadium Background" class="w-full h-full object-cover opacity-80" />
    <div class="absolute inset-0 bg-gradient-to-t from-[#010108]/80 via-transparent to-transparent"></div>
  </div>

  <div class="space-y-10 pb-12 w-full max-w-7xl mx-auto pt-8 relative z-10 px-4 sm:px-6 lg:px-8">
    
    <!-- Topbar AI Status -->
    <div class="flex justify-between items-end border-b border-sunset-primary/20 pb-6 relative">
      <div class="absolute -left-20 -top-20 w-64 h-64 bg-sunset-primary/10 blur-[80px] rounded-full pointer-events-none"></div>
      
      <div class="relative z-10">
        <h1 class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-sunset-accent tracking-tight">AI Command Center</h1>
        <p class="text-sunset-secondary mt-1 font-medium mb-4">Welcome back, <span class="text-sunset-primary">{{ authStore.user?.username || 'Analyst' }}</span>.</p>
        <button @click="router.push('/prediction')" class="px-6 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-bold rounded-xl shadow-[0_0_15px_rgba(168,85,247,0.4)] hover:scale-105 transition-transform">
          Accéder au Neural Core (Prédiction)
        </button>
      </div>
      <div class="flex items-center gap-3 liquid-glass px-4 py-2 rounded-xl relative z-10 shadow-[0_0_15px_rgba(187,134,252,0.1)]">
        <span class="flex h-3 w-3 relative">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500 shadow-[0_0_8px_#22c55e]"></span>
        </span>
        <span class="text-xs font-semibold text-white/80 uppercase tracking-widest">Neural Engine Online</span>
      </div>
    </div>

    <!-- Grid Layout: Matches & Standings -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
      
      <!-- Match List -->
      <div class="xl:col-span-2 flex flex-col gap-5">
        <div class="flex items-center justify-between">
            <h3 class="text-white font-bold text-xl tracking-wide flex items-center gap-2">
            Matchday {{ currentGameweek > 0 ? currentGameweek : 'Fixtures' }}
            </h3>
            <div class="flex items-center gap-2 px-3 py-1 bg-red-500/10 border border-red-500/20 rounded-full z-10">
              <div class="w-2 h-2 rounded-full bg-red-500 animate-pulse-fast"></div>
              <span class="text-xs font-bold text-red-500 tracking-wider">LIVE API</span>
            </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div 
            v-for="match in matches" 
            :key="match.id" 
            @click="runPrediction(match.home_team.name, match.away_team.name)"
            class="h-full cursor-pointer group relative"
          >
            <!-- AI Scan Effect Wrapper -->
            <div class="absolute inset-0 z-20 pointer-events-none overflow-hidden rounded-[20px] opacity-0 group-hover:opacity-100 transition-opacity duration-300">
               <div class="absolute inset-0 bg-gradient-to-b from-transparent via-sunset-accent/30 to-transparent h-[30%] w-full animate-[scan_2s_ease-in-out_infinite] blur-sm"></div>
               <div class="absolute inset-0 border-2 border-sunset-accent/40 rounded-[20px]"></div>
            </div>
            
            <MatchCard 
              :homeTeam="match.home_team.name"
              :awayTeam="match.away_team.name"
              :date="new Date(match.match_date).toLocaleDateString()"
              :status="match.status"
              :homeScore="match.home_score"
              :awayScore="match.away_score"
            />
          </div>
        </div>
      </div>

      <!-- Live Standings Panel -->
      <div class="xl:col-span-1 flex flex-col gap-8">
        <div class="h-[600px]">
          <LeagueStandings />
        </div>
        <TopScorers />
      </div>

    </div>
  </div>
</template>

<style scoped>
@keyframes scan {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(400%); }
}

.animate-pulse-fast {
  animation: pulse-fast 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse-fast {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: .5; transform: scale(1.2); box-shadow: 0 0 10px rgba(239, 68, 68, 0.8); }
}
</style>
