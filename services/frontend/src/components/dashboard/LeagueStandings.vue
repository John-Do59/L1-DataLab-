<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../api/axios'

interface Standing {
  rank: number
  club_name: string
  logo?: string
  points: number
  played: number
  wins: number
  draws: number
  losses: number
  goal_diff: number
}

const standings = ref<Standing[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('/standings')
    standings.value = res.data
  } catch (error) {
    console.error("Failed to load standings", error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="liquid-glass-strong rounded-3xl p-6 relative overflow-hidden h-full flex flex-col min-h-[400px] max-h-[600px]">
    <!-- Decorative glow -->
    <div class="absolute top-0 right-0 w-64 h-64 bg-sunset-accent/10 blur-[60px] rounded-full pointer-events-none"></div>
    
    <div class="flex items-center justify-between mb-6 relative z-10">
      <h3 class="text-xl font-bold text-white tracking-wide flex items-center gap-3">
        Live Standings
        <img src="https://ligue1.com/images/Logo_Ligue_1.webp" class="h-6 w-auto opacity-80" alt="Ligue 1" />
      </h3>
      <div class="flex items-center gap-2 px-3 py-1 bg-red-500/10 rounded-full border border-red-500/20 shadow-[0_0_10px_rgba(239,68,68,0.2)]">
        <span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
        <span class="text-xs font-bold tracking-wider text-red-500">LIVE API</span>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto pr-2 relative z-10 custom-scrollbar">
      <div v-if="loading" class="flex items-center justify-center h-full min-h-[200px]">
        <span class="text-sunset-accent animate-pulse font-medium tracking-widest text-sm uppercase">Loading LFP Live Data...</span>
      </div>
      
      <table v-else class="w-full text-left text-sm text-sunset-secondary">
        <thead class="sticky top-0 bg-[#060313]/90 backdrop-blur-md z-20">
          <tr class="text-xs uppercase tracking-wider text-white/50 border-b border-white/10">
            <th class="pb-3 font-semibold pl-2">Pos</th>
            <th class="pb-3 font-semibold">Club</th>
            <th class="pb-3 font-semibold text-center px-4">P</th>
            <th class="pb-3 font-semibold text-center px-4 hidden sm:table-cell">W</th>
            <th class="pb-3 font-semibold text-center px-4 hidden sm:table-cell">D</th>
            <th class="pb-3 font-semibold text-center px-4 hidden sm:table-cell">L</th>
            <th class="pb-3 font-semibold text-right text-white pr-2">Pts</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          <tr 
            v-for="team in standings" 
            :key="team.rank"
            class="hover:bg-white/[0.04] transition-all duration-300 group cursor-default"
          >
            <td class="py-3 pl-2 font-medium" :class="{'text-sunset-accent': team.rank <= 3, 'text-red-400': team.rank >= 16}">
              {{ team.rank }}
            </td>
            <td class="py-3 text-white font-medium group-hover:text-sunset-accent transition-colors flex items-center gap-2">
              <img v-if="team.logo" :src="team.logo" class="w-5 h-5 object-contain" />
              {{ team.club_name }}
            </td>
            <td class="py-3 text-center px-4">{{ team.played }}</td>
            <td class="py-3 text-center px-4 hidden sm:table-cell">{{ team.wins }}</td>
            <td class="py-3 text-center px-4 hidden sm:table-cell">{{ team.draws }}</td>
            <td class="py-3 text-center px-4 hidden sm:table-cell">{{ team.losses }}</td>
            <td class="py-3 pr-2 text-right font-bold text-white group-hover:text-sunset-secondary transition-colors text-base">
              {{ team.points }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(187, 134, 252, 0.2);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(187, 134, 252, 0.5);
}
</style>
