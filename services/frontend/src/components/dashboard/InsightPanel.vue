<script setup lang="ts">
defineProps<{
  insight: string
}>()
</script>

<template>
  <div class="liquid-glass rounded-2xl p-6 border border-sunset-primary/20 flex flex-col h-full relative overflow-hidden group">
    <!-- Glow Decorator -->
    <div class="absolute -right-12 -top-12 w-40 h-40 bg-sunset-accent/20 blur-[50px] rounded-full group-hover:bg-sunset-primary/30 transition-colors duration-700 pointer-events-none"></div>
    
    <div class="flex items-center gap-4 mb-6 relative z-10">
      <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-sunset-primary to-sunset-secondary flex items-center justify-center shadow-[0_0_15px_-3px_#f6b3e5]">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <h3 class="text-white font-bold text-lg tracking-wide">AI Insights</h3>
    </div>
    
    <div class="flex-1 flex flex-col gap-4 relative z-10">
      <div class="p-5 rounded-xl bg-black/40 border border-white/5 backdrop-blur-md text-sm text-white/80 leading-relaxed shadow-inner font-light">
        "{{ insight }}"
      </div>
      
      <!-- Footer status -->
      <div class="mt-auto pt-4 border-t border-white/5 text-xs text-sunset-accent/60 flex items-center gap-2 font-medium">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-sunset-accent opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-sunset-accent"></span>
        </span>
        LLM Agent Ready
      </div>
    </div>
  </div>
</template>
