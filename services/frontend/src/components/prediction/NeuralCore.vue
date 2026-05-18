<template>
  <div class="relative w-[250px] h-[250px] flex items-center justify-center orb-container">
    
    <!-- Outer glow rings -->
    <div class="absolute w-full h-full rounded-full border border-cyan-500/20 shadow-[0_0_50px_rgba(34,211,238,0.2)]" :class="{'animate-[spin_8s_linear_infinite]': state === 'loading'}">
      <div class="absolute top-[-4px] left-1/2 w-2 h-2 bg-cyan-400 rounded-full shadow-[0_0_15px_#22d3ee]"></div>
      <div class="absolute bottom-[-4px] left-1/2 w-2 h-2 bg-purple-400 rounded-full shadow-[0_0_15px_#c084fc]"></div>
    </div>
    
    <div class="absolute w-[220px] h-[220px] rounded-full border-[3px] border-dashed border-cyan-500/30" :class="{'animate-[spin_15s_linear_infinite_reverse]': state === 'loading'}"></div>
    <div class="absolute w-[180px] h-[180px] rounded-full border-2 border-purple-500/40"></div>
    
    <!-- Inner glowing AI orb -->
    <div class="absolute w-[150px] h-[150px] rounded-full bg-[#050510] border-2 border-cyan-400/80 shadow-[0_0_50px_rgba(34,211,238,0.8),_inset_0_0_40px_rgba(34,211,238,0.6)] flex items-center justify-center overflow-hidden">
      <!-- Hexagonal pattern overlay -->
      <div class="absolute inset-0 hex-pattern opacity-60 bg-center bg-cover"></div>
      
      <!-- Central IA text -->
      <span class="relative z-10 text-[56px] font-black text-white tracking-widest drop-shadow-[0_0_20px_#22d3ee]">IA</span>
    </div>

    <!-- Energy burst -->
    <div v-if="state === 'loading'" class="absolute w-[300px] h-[300px] pointer-events-none">
      <div class="absolute inset-0 bg-gradient-to-r from-cyan-400/0 via-cyan-400/20 to-purple-400/0 rounded-full blur-2xl animate-pulse"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  state: 'idle' | 'loading' | 'reveal'
}>()
</script>

<style scoped>
.hex-pattern {
  background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+PHBhdGggZD0iTTIwIDAgTDIwIDIwIEw0MCAzMCBMMjAgMjAifSBzdHJva2U9InJnYmEoMzQsIDIxMSwgMjM4LCAwLjI1KSIgZmlsbD0ibm9uZSIvPjwvc3ZnPg==');
}

.orb-container {
  filter: drop-shadow(0 0 30px rgba(34, 211, 238, 0.4));
}
</style>
