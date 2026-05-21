<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const billing = ref<'monthly' | 'yearly'>('monthly')

const plans = [
  {
    id: 'freemium',
    name: 'Freemium',
    tagline: 'Découverte & portfolio cert',
    monthly: 0,
    yearly: 0,
    features: [
      '5 prédictions / jour',
      'Historique 7 jours',
      'RAG Oracle (10 messages / jour)',
      'Dashboard classement LFP',
    ],
    cta: 'Plan actuel',
    highlight: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    tagline: 'Analyste sérieux Ligue 1',
    monthly: 19,
    yearly: 190,
    features: [
      'Prédictions illimitées',
      'Historique complet + export',
      'RAG streaming + mémoire session',
      'Explicabilité SHAP avancée',
      'Support prioritaire',
    ],
    cta: 'Passer Pro',
    highlight: true,
  },
  {
    id: 'max',
    name: 'Max',
    tagline: 'Command Center institutionnel',
    monthly: 49,
    yearly: 490,
    features: [
      'Tout Pro inclus',
      'API access & webhooks',
      'MLOps pipeline insights',
      'Multi-utilisateurs (3 sièges)',
      'SLA & déploiement GCP dédié',
    ],
    cta: 'Contacter sales',
    highlight: false,
  },
]

const price = (plan: (typeof plans)[0]) =>
  billing.value === 'monthly' ? plan.monthly : plan.yearly

const periodLabel = () => (billing.value === 'monthly' ? '/ mois' : '/ an')
</script>

<template>
  <div class="fixed inset-0 z-[-1] pointer-events-none bg-[#010108]">
    <div class="absolute top-[-5%] left-1/2 -translate-x-1/2 w-[80vw] h-[45vh] bg-sunset-primary/20 blur-[130px] rounded-full" />
  </div>

  <div class="max-w-6xl mx-auto pb-16 relative z-10">
    <header class="text-center mb-12">
      <p class="text-xs font-bold tracking-[0.35em] uppercase text-sunset-primary mb-3">
        Tarification
      </p>
      <h1 class="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-sunset-accent to-sunset-secondary">
        Choisissez votre puissance IA
      </h1>
      <p class="text-sunset-secondary/80 mt-4 max-w-2xl mx-auto font-light">
        Freemium pour démarrer, Pro pour l'analyse quotidienne, Max pour les équipes data & media.
      </p>

      <div class="mt-8 inline-flex liquid-glass rounded-xl p-1 border border-sunset-primary/30">
        <button
          type="button"
          class="px-5 py-2 rounded-lg text-sm font-medium transition-all"
          :class="billing === 'monthly' ? 'bg-sunset-primary text-white' : 'text-sunset-secondary'"
          @click="billing = 'monthly'"
        >
          Mensuel
        </button>
        <button
          type="button"
          class="px-5 py-2 rounded-lg text-sm font-medium transition-all"
          :class="billing === 'yearly' ? 'bg-sunset-primary text-white' : 'text-sunset-secondary'"
          @click="billing = 'yearly'"
        >
          Annuel <span class="text-sunset-accent text-xs ml-1">-17%</span>
        </button>
      </div>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
      <div
        v-for="plan in plans"
        :key="plan.id"
        class="relative rounded-3xl p-8 flex flex-col transition-transform duration-300 hover:scale-[1.02]"
        :class="
          plan.highlight
            ? 'liquid-glass-strong border-2 border-sunset-secondary/50 liquid-glow shadow-[0_0_60px_-15px_rgba(200,118,255,0.45)]'
            : 'liquid-glass border border-sunset-primary/25'
        "
      >
        <div
          v-if="plan.highlight"
          class="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-sunset-primary to-sunset-secondary text-white text-[10px] font-bold uppercase tracking-widest"
        >
          Recommandé
        </div>

        <h2 class="text-2xl font-bold text-white">{{ plan.name }}</h2>
        <p class="text-sunset-secondary/70 text-sm mt-1 mb-6">{{ plan.tagline }}</p>

        <div class="mb-6">
          <span class="text-4xl font-black text-sunset-accent">
            {{ price(plan) === 0 ? 'Gratuit' : `${price(plan)}€` }}
          </span>
          <span v-if="price(plan) > 0" class="text-sunset-secondary/60 text-sm">{{ periodLabel() }}</span>
        </div>

        <ul class="space-y-3 flex-1 mb-8">
          <li
            v-for="f in plan.features"
            :key="f"
            class="flex items-start gap-2 text-sm text-white/80"
          >
            <span class="text-sunset-primary mt-0.5">✓</span>
            {{ f }}
          </li>
        </ul>

        <button
          type="button"
          class="w-full py-3 rounded-xl font-semibold text-sm transition-all"
          :class="
            plan.highlight
              ? 'bg-gradient-to-r from-sunset-primary to-sunset-secondary text-white hover:shadow-[0_0_30px_-5px_#c876ff]'
              : 'liquid-glass border border-sunset-secondary/30 text-sunset-accent hover:bg-sunset-primary/20'
          "
          @click="plan.id === 'freemium' ? router.push('/register') : router.push('/login')"
        >
          {{ plan.cta }}
        </button>
      </div>
    </div>

    <p class="text-center text-xs text-white/35 mt-10 max-w-xl mx-auto">
      Paiement Stripe & gestion des abonnements — intégration production à venir.
      Les limites Freemium sont indicatives pour la démo certif.
    </p>
  </div>
</template>
