<template>
  <div class="top-scorers-container liquid-glass p-6 rounded-2xl relative overflow-hidden group">
    <!-- Live Badge -->
    <div class="absolute top-4 right-4 flex items-center gap-2 px-3 py-1 bg-red-500/10 border border-red-500/20 rounded-full z-10">
      <div class="w-2 h-2 rounded-full bg-red-500 animate-pulse-fast"></div>
      <span class="text-xs font-bold text-red-500 tracking-wider">LIVE</span>
    </div>

    <!-- AI Scan Effect -->
    <div class="absolute inset-0 scan-line opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>

    <h2 class="text-xl font-black text-white/90 mb-6 uppercase tracking-wider flex items-center gap-3 relative z-10">
      <svg class="w-5 h-5 text-l1-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
      </svg>
      Top Buteurs
    </h2>

    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="w-8 h-8 border-2 border-l1-primary border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div v-else-if="scorers.length === 0" class="text-center py-8 text-white/50 relative z-10">
      Aucune donnée disponible.
    </div>

    <div v-else class="space-y-4 relative z-10">
      <div v-for="scorer in scorers" :key="scorer.rank" 
           class="scorer-card flex items-center p-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all duration-300 group/card relative overflow-hidden">
        
        <!-- Glowing Orb Effect on Hover -->
        <div class="absolute top-1/2 left-4 w-12 h-12 bg-l1-primary/20 rounded-full blur-xl -translate-y-1/2 opacity-0 group-hover/card:opacity-100 transition-opacity duration-500"></div>

        <div class="rank text-white/40 font-black w-6 text-center text-sm mr-3">
          {{ scorer.rank }}
        </div>

        <div class="relative w-12 h-12 rounded-full overflow-hidden border-2 border-white/10 shrink-0 bg-black/40 mr-4 group-hover/card:border-l1-primary/50 transition-colors">
          <img :src="scorer.photo" :alt="scorer.lastName" class="w-full h-full object-cover object-top" @error="handleImageError" />
        </div>

        <div class="flex-grow min-w-0">
          <h3 class="text-white font-bold truncate text-sm flex items-center gap-2">
            {{ scorer.firstName }} {{ scorer.lastName }}
            <svg v-if="scorer.rank <= 3" class="w-3 h-3 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
            </svg>
          </h3>
          <div class="flex items-center gap-2 mt-1">
            <img :src="scorer.club_logo" class="w-4 h-4 object-contain" />
            <span class="text-xs text-white/50">{{ scorer.matches }} matchs</span>
          </div>
        </div>

        <div class="text-right pl-3 shrink-0">
          <div class="text-2xl font-black text-l1-primary leading-none">{{ scorer.goals }}</div>
          <div class="text-[10px] uppercase text-white/40 font-bold tracking-widest mt-1">Buts</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

interface Scorer {
  rank: number;
  firstName: string;
  lastName: string;
  goals: number;
  matches: number;
  photo: string;
  club_logo: string;
}

const scorers = ref<Scorer[]>([]);
const loading = ref(true);

const defaultImage = 'https://s3.eu-west-1.amazonaws.com/image.mpg/fr.png'; // Fallback image

const handleImageError = (e: Event) => {
  const target = e.target as HTMLImageElement;
  target.src = defaultImage;
};

onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:8002/top-scorers');
    if (response.data && response.data.length > 0) {
      scorers.value = response.data;
    }
  } catch (error) {
    console.error('Failed to fetch top scorers:', error);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.liquid-glass {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}

.scan-line {
  background: linear-gradient(to bottom, 
    transparent 0%, 
    rgba(196, 255, 14, 0.05) 50%, 
    rgba(196, 255, 14, 0.2) 100%);
  height: 20%;
  animation: scan 3s linear infinite;
}

@keyframes scan {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(500%); }
}

.animate-pulse-fast {
  animation: pulse-fast 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse-fast {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: .5; transform: scale(1.2); box-shadow: 0 0 10px rgba(239, 68, 68, 0.8); }
}
</style>
