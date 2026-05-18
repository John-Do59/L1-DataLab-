<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import bgStadium2 from '../assets/backgrounds/bg_stadium_2.jpg'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

const handleRegister = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    await authStore.register(username.value, email.value, password.value)
    router.push('/dashboard')
  } catch (err: any) {
    if (err.response && err.response.data && err.response.data.detail) {
      errorMsg.value = err.response.data.detail
    } else {
      errorMsg.value = "Erreur lors de la création du compte."
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <!-- Background Image with Overlay -->
  <div class="fixed inset-0 z-[-1] pointer-events-none bg-[#010108]">
    <img :src="bgStadium2" alt="Stadium Background" class="w-full h-full object-cover opacity-80" />
    <div class="absolute inset-0 bg-gradient-to-t from-[#010108]/80 via-transparent to-transparent"></div>
  </div>

  <div class="min-h-[80vh] flex items-center justify-center relative z-10">
    
    <!-- Background Decorators -->
    <div class="absolute w-[300px] h-[300px] bg-sunset-primary/30 rounded-full blur-[100px] top-[10%] left-[20%] pointer-events-none"></div>
    <div class="absolute w-[400px] h-[400px] bg-sunset-secondary/20 rounded-full blur-[120px] bottom-[10%] right-[10%] pointer-events-none"></div>

    <!-- Register Card Liquidglass -->
    <div class="liquid-glass-strong w-full max-w-md p-8 rounded-3xl relative z-10 liquid-glow mt-8">
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold text-white tracking-tight">Create Account</h2>
        <p class="text-sunset-secondary/70 text-sm mt-2">Rejoignez le L1 DataLab</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-sunset-accent mb-2">Username</label>
          <input 
            v-model="username"
            type="text" 
            class="w-full bg-sunset-bg/50 border border-sunset-primary/30 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-sunset-secondary transition-colors"
            placeholder="johndoe"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-sunset-accent mb-2">Email</label>
          <input 
            v-model="email"
            type="email" 
            class="w-full bg-sunset-bg/50 border border-sunset-primary/30 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-sunset-secondary transition-colors"
            placeholder="john@example.com"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-sunset-accent mb-2">Password</label>
          <input 
            v-model="password"
            type="password" 
            class="w-full bg-sunset-bg/50 border border-sunset-primary/30 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-sunset-secondary transition-colors"
            placeholder="••••••••"
            required
            minlength="6"
          />
        </div>

        <div v-if="errorMsg" class="text-red-400 text-sm text-center bg-red-400/10 py-2 rounded-lg border border-red-400/20">
          {{ errorMsg }}
        </div>

        <button 
          type="submit" 
          :disabled="loading"
          class="w-full bg-gradient-to-r from-sunset-primary to-sunset-secondary hover:from-sunset-secondary hover:to-sunset-accent text-white font-semibold py-3 rounded-xl transition-all hover:shadow-[0_0_20px_-5px_#c876ff] disabled:opacity-50"
        >
          <span v-if="!loading">Sign Up</span>
          <span v-else class="animate-pulse">Creating account...</span>
        </button>
      </form>
      
      <div class="mt-6 text-center">
        <p class="text-sunset-secondary/60 text-sm">
          Already have an account? 
          <router-link to="/login" class="text-sunset-accent hover:underline">Sign In</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
