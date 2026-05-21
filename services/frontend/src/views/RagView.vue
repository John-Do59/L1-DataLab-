<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import RagEntity, { type RagEntityState } from '../components/rag/RagEntity.vue'
import {
  streamRagQuestion,
  type EntityMood,
  type RagStreamMeta,
} from '../api/ragStream'
import { getOracleAccent } from '../utils/teamVisuals'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  model?: string
  streaming?: boolean
}

const authStore = useAuthStore()
const messages = ref<ChatMessage[]>([])
const input = ref('')
const loading = ref(false)
const error = ref('')
const chatEndRef = ref<HTMLElement | null>(null)
const inputFocused = ref(false)
const conversationId = ref<number | null>(null)
const entityMood = ref<EntityMood>('stable')
const streamIntensity = ref(0)
const confidenceScore = ref(0.5)

const entityState = computed<RagEntityState>(() => {
  if (loading.value) return 'generating'
  if (inputFocused.value && input.value.trim().length > 0) return 'listening'
  return 'idle'
})

const isResponding = ref(false)
const displayState = computed<RagEntityState>(() => {
  if (isResponding.value) return 'responding'
  return entityState.value
})

const suggestions = [
  'Qui mène le classement Ligue 1 ?',
  'Analyse tactique PSG vs Marseille',
  'Ce match est-il risqué pour mon pronostic ?',
  'Explique mes dernières prédictions enregistrées',
]

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUser()
  }
  messages.value.push({
    id: 'welcome',
    role: 'assistant',
    content:
      `Bonjour ${authStore.user?.username || 'Analyste'}. Je suis l'Oracle Football L1 DataLab — posez une question ; ma mémoire de session et le flux live s'activent à chaque message.`,
    sources: ['L1 DataLab RAG'],
    model: 'l1-rag',
  })
})

watch(
  () => messages.value.length,
  async () => {
    await nextTick()
    chatEndRef.value?.scrollIntoView({ behavior: 'smooth' })
  }
)

watch(
  () => messages.value.map((m) => m.content).join(),
  async () => {
    await nextTick()
    if (loading.value) chatEndRef.value?.scrollIntoView({ behavior: 'smooth' })
  }
)

const sendMessage = async (text?: string) => {
  const question = (text ?? input.value).trim()
  if (!question || loading.value) return

  error.value = ''
  input.value = ''
  inputFocused.value = false
  streamIntensity.value = 0

  messages.value.push({
    id: `u-${Date.now()}`,
    role: 'user',
    content: question,
  })

  const assistantId = `a-${Date.now()}`
  messages.value.push({
    id: assistantId,
    role: 'assistant',
    content: '',
    streaming: true,
  })

  loading.value = true

  await streamRagQuestion(
    question,
    {
      onMeta: (meta: RagStreamMeta) => {
        conversationId.value = meta.conversation_id
        entityMood.value = meta.mood
        confidenceScore.value = meta.confidence
      },
      onToken: (payload) => {
        streamIntensity.value = Math.min(
          1,
          streamIntensity.value + 0.04 + payload.t.length * 0.008
        )
        if (payload.mood) entityMood.value = payload.mood
        const msg = messages.value.find((m) => m.id === assistantId)
        if (msg) msg.content = payload.full
      },
      onDone: (payload) => {
        const msg = messages.value.find((m) => m.id === assistantId)
        if (msg) {
          msg.content = payload.answer
          msg.sources = payload.sources
          msg.model = payload.model
          msg.streaming = false
        }
        conversationId.value = payload.conversation_id
        entityMood.value = payload.mood
        confidenceScore.value = payload.confidence
        isResponding.value = true
        setTimeout(() => {
          isResponding.value = false
          streamIntensity.value = 0
        }, 1500)
        loading.value = false
      },
      onError: (e) => {
        console.error('RAG stream failed', e)
        error.value = 'Flux interrompu. Vérifiez l\'API ou réessayez.'
        const msg = messages.value.find((m) => m.id === assistantId)
        if (msg) {
          msg.content =
            'Signal interrompu. L\'entité n\'a pas pu terminer la synthèse.'
          msg.streaming = false
        }
        entityMood.value = 'glitch'
        loading.value = false
        streamIntensity.value = 0
      },
    },
    conversationId.value
  )
}

const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const moodBadgeClass = computed(() => {
  const m = entityMood.value
  if (m === 'stable') return 'text-sky-300 border-sky-400/40 bg-sky-500/10'
  if (m === 'risky') return 'text-orange-300 border-orange-400/40 bg-orange-500/10'
  if (m === 'glitch') return 'text-red-300 border-red-400/40 bg-red-500/10'
  return 'text-amber-300 border-amber-400/40 bg-amber-500/10'
})

const oracleContextText = computed(() => {
  const lastUser = [...messages.value].reverse().find((m) => m.role === 'user')
  return [lastUser?.content, input.value].filter(Boolean).join(' ')
})

const oracleAccent = computed(() =>
  getOracleAccent(entityMood.value, oracleContextText.value),
)
</script>

<template>
  <div class="fixed inset-0 z-[-1] pointer-events-none bg-[#010108]">
    <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[70vw] h-[40vh] bg-sunset-primary/15 blur-[120px] rounded-full" />
    <div class="absolute bottom-0 right-0 w-[40vw] h-[30vh] bg-sunset-secondary/10 blur-[100px] rounded-full" />
  </div>

  <div class="max-w-4xl mx-auto pb-10 relative z-10 min-h-[calc(100vh-8rem)] flex flex-col">
    <header class="text-center mb-6">
      <p class="text-xs font-bold tracking-[0.3em] uppercase text-sunset-primary mb-2">
        AI Football Oracle
      </p>
      <h1 class="text-3xl md:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-sunset-accent to-sunset-secondary">
        Oracle Halo
      </h1>
      <p class="text-sunset-secondary/80 text-sm mt-2 font-light max-w-lg mx-auto">
        Vortex lumineux · streaming RAG · humeur synchronisée
      </p>
      <div class="mt-3 flex justify-center gap-3 flex-wrap">
        <span
          class="text-[10px] uppercase tracking-widest px-3 py-1 rounded-full border"
          :class="moodBadgeClass"
        >
          {{ entityMood }}
        </span>
        <span class="text-[10px] uppercase tracking-widest px-3 py-1 rounded-full border border-sunset-primary/30 text-sunset-secondary/80">
          confiance {{ Math.round(confidenceScore * 100) }}%
        </span>
      </div>
    </header>

    <section
      class="mb-6 relative flex flex-col items-center justify-center py-4 transition-[filter] duration-300"
      :class="{ 'drop-shadow-[0_0_60px_rgba(114,50,242,0.35)]': loading }"
    >
      <RagEntity
        :state="displayState"
        :mood="entityMood"
        :stream-intensity="streamIntensity"
        :accent-vars="oracleAccent.cssVars"
      />
    </section>

    <section class="flex-1 flex flex-col liquid-glass-strong rounded-3xl border border-sunset-secondary/20 overflow-hidden min-h-[320px]">
      <div class="flex-1 overflow-y-auto p-5 md:p-6 space-y-4 max-h-[42vh]">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="flex"
          :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div
            class="max-w-[88%] rounded-2xl px-4 py-3 text-sm leading-relaxed"
            :class="
              msg.role === 'user'
                ? 'bg-gradient-to-br from-sunset-primary/40 to-sunset-secondary/30 border border-sunset-secondary/40 text-white'
                : 'bg-black/40 border border-sunset-primary/25 text-sunset-accent/95'
            "
          >
            <p class="whitespace-pre-wrap">
              {{ msg.content }}<span
                v-if="msg.streaming"
                class="inline-block w-2 h-4 ml-0.5 bg-sunset-accent/80 animate-pulse align-middle"
              />
            </p>
            <div
              v-if="msg.role === 'assistant' && !msg.streaming && (msg.sources?.length || msg.model)"
              class="mt-2 pt-2 border-t border-white/10 flex flex-wrap gap-2"
            >
              <span
                v-for="src in msg.sources"
                :key="src"
                class="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-sunset-primary/20 text-sunset-secondary"
              >
                {{ src }}
              </span>
              <span v-if="msg.model" class="text-[10px] text-white/30 font-mono">{{ msg.model }}</span>
            </div>
          </div>
        </div>
        <div ref="chatEndRef" />
      </div>

      <div v-if="messages.length <= 2" class="px-5 pb-3 flex flex-wrap gap-2">
        <button
          v-for="s in suggestions"
          :key="s"
          type="button"
          @click="sendMessage(s)"
          :disabled="loading"
          class="text-xs px-3 py-1.5 rounded-full liquid-glass border border-sunset-primary/30 text-sunset-secondary hover:text-sunset-accent hover:border-sunset-secondary/50 transition-all disabled:opacity-40"
        >
          {{ s }}
        </button>
      </div>

      <div v-if="error" class="px-5 pb-2 text-red-300/90 text-xs text-center">{{ error }}</div>

      <div class="p-4 border-t border-sunset-primary/20 bg-black/30">
        <div class="flex gap-3 items-end">
          <textarea
            v-model="input"
            rows="2"
            placeholder="Posez votre question à l'Oracle…"
            class="flex-1 resize-none bg-sunset-bg/60 border border-sunset-primary/30 rounded-xl px-4 py-3 text-white text-sm placeholder:text-white/30 focus:outline-none focus:border-sunset-secondary transition-colors"
            :disabled="loading"
            @focus="inputFocused = true"
            @blur="inputFocused = false"
            @keydown="onKeydown"
          />
          <button
            type="button"
            :disabled="loading || !input.trim()"
            @click="sendMessage()"
            class="shrink-0 px-5 py-3 rounded-xl bg-gradient-to-r from-sunset-primary to-sunset-secondary text-white font-semibold text-sm hover:shadow-[0_0_25px_-5px_#c876ff] transition-all disabled:opacity-40 disabled:cursor-not-allowed min-w-[100px]"
          >
            <span
              v-if="loading"
              class="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto"
            />
            <span v-else>Envoyer</span>
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
