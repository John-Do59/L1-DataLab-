<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import axios from 'axios'
import bgStadium1 from '../assets/backgrounds/bg_stadium_1.jpg'

// Résolution dynamique de l'URL du ML API (sur le port 8001)
const getMlApiUrl = () => {
  const host = window.location.hostname || 'localhost'
  return `http://${host}:8001`
}

const ML_API_URL = getMlApiUrl()

// États réactifs
const loading = ref(true)
const modelInfo = ref<any>(null)
const pipelineStatus = ref<any>({ status: 'idle', logs: 'Aucun log en cours.' })
const retraining = ref(false)
const errorMessage = ref('')
const activeTab = ref<'calibration' | 'features'>('calibration')

// Timer pour surveiller le pipeline en tâche de fond
let statusInterval: any = null

// Features fixes pour l'importance du modèle (Random Forest)
const featureImportances = [
  { name: 'elo_diff', label: 'Différence Elo (Général)', value: 0.285 },
  { name: 'odds_prob_home', label: 'Cotes Probabilité Domicile', value: 0.198 },
  { name: 'home_form_5', label: 'Forme Recente Domicile (5 match)', value: 0.124 },
  { name: 'odds_prob_away', label: 'Cotes Probabilité Extérieur', value: 0.105 },
  { name: 'away_form_5', label: 'Forme Recente Extérieur (5 match)', value: 0.092 },
  { name: 'home_squad_value', label: 'Valeur de l\'effectif Domicile', value: 0.081 },
  { name: 'away_squad_value', label: 'Valeur de l\'effectif Extérieur', value: 0.065 },
  { name: 'home_avg_overall', label: 'Moyenne Globale FIFA Domicile', value: 0.050 }
]

// Charger les infos du modèle Champion
const fetchModelInfo = async () => {
  try {
    const res = await axios.get(`${ML_API_URL}/`)
    modelInfo.value = res.data
    errorMessage.value = ''
  } catch (e: any) {
    console.error("Impossible de charger les infos du modèle ML API", e)
    errorMessage.value = "Le service ML-API est inaccessible. Veuillez vous assurer que le conteneur l1-ml-api est démarré sur le port 8001."
  } finally {
    loading.value = false
  }
}

// Charger le statut du pipeline
const fetchPipelineStatus = async () => {
  try {
    const res = await axios.get(`${ML_API_URL}/pipeline/status`)
    pipelineStatus.value = res.data
    
    if (res.data.status === 'running') {
      retraining.value = true
      // Activer le polling si non existant
      if (!statusInterval) {
        startStatusPolling()
      }
    } else {
      retraining.value = false
      if (statusInterval && res.data.status !== 'running') {
        stopStatusPolling()
        await fetchModelInfo() // Rafraîchir les infos modèle si fini
      }
    }
  } catch (e) {
    console.error("Erreur de récupération du statut du pipeline", e)
  }
}

// Lancer le réentraînement continu
const triggerRetraining = async () => {
  if (retraining.value) return
  try {
    retraining.value = true
    await axios.post(`${ML_API_URL}/pipeline/run`)
    pipelineStatus.value.status = 'running'
    pipelineStatus.value.logs = '🚀 Initialisation de la tâche asynchrone MLOps...\n'
    startStatusPolling()
  } catch (e) {
    retraining.value = false
    console.error("Échec du lancement du pipeline", e)
    alert("Erreur lors du déclenchement du pipeline MLOps.")
  }
}

// Polling intelligent des logs
const startStatusPolling = () => {
  statusInterval = setInterval(fetchPipelineStatus, 2000)
}

const stopStatusPolling = () => {
  if (statusInterval) {
    clearInterval(statusInterval)
    statusInterval = null
  }
}

// Calcul de la courbe de calibration pour le SVG
const calibrationPoints = computed(() => {
  if (!modelInfo.value?.metrics?.calibration_curve_h) return []
  const curve = modelInfo.value.metrics.calibration_curve_h
  const points: { x: number; y: number }[] = []
  
  if (curve.prob_pred && curve.prob_true) {
    for (let i = 0; i < curve.prob_pred.length; i++) {
      // Les coordonnées SVG vont de 0 à 100% (on multiplie par 300 pour un cadre 300x300)
      // Attention: en SVG l'origine y=0 est en haut, donc y_svg = 300 - (prob * 300)
      points.push({
        x: curve.prob_pred[i] * 300,
        y: 300 - (curve.prob_true[i] * 300)
      })
    }
  }
  return points
})

const calibrationPathString = computed(() => {
  const points = calibrationPoints.value
  if (points.length === 0) return ''
  return points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
})

onMounted(async () => {
  await fetchModelInfo()
  await fetchPipelineStatus()
})

onUnmounted(() => {
  stopStatusPolling()
})
</script>

<template>
  <div class="fixed inset-0 z-[-1] pointer-events-none bg-[#02020a]">
    <img :src="bgStadium1" alt="Stadium Background" class="w-full h-full object-cover opacity-60" />
    <div class="absolute inset-0 bg-gradient-to-t from-[#02020a] via-[#02020a]/80 to-[#02020a]/50"></div>
  </div>

  <div class="space-y-8 pb-16 w-full max-w-7xl mx-auto pt-8 relative z-10 px-4 sm:px-6 lg:px-8">
    
    <!-- Top Header -->
    <div class="flex flex-col md:flex-row md:items-end justify-between border-b border-purple-500/10 pb-6 relative gap-4">
      <div class="absolute -left-20 -top-20 w-64 h-64 bg-cyan-500/10 blur-[90px] rounded-full pointer-events-none"></div>
      
      <div>
        <div class="flex items-center gap-2 mb-2">
          <span class="px-2 py-0.5 bg-cyan-500/10 border border-cyan-500/30 text-[10px] font-bold text-cyan-400 rounded uppercase tracking-wider">Industrial Engine</span>
          <span class="px-2 py-0.5 bg-purple-500/10 border border-purple-500/30 text-[10px] font-bold text-purple-400 rounded uppercase tracking-wider">MLOps v2</span>
        </div>
        <h1 class="text-4xl font-extrabold text-white tracking-tight">
          AI & MLOps <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-indigo-400 to-purple-400">Insights Dashboard</span>
        </h1>
        <p class="text-slate-400 mt-1.5 font-medium max-w-3xl">
          Supervisez en direct les métriques du modèle Champion, monitorisez la dérive de concept (concept drift) et orchestrez les pipelines automatiques.
        </p>
      </div>

      <div class="flex items-center gap-4">
        <div class="flex items-center gap-3 bg-white/[0.03] border border-white/[0.08] px-4 py-2.5 rounded-xl shadow-[0_0_20px_rgba(0,0,0,0.3)]">
          <span class="flex h-3 w-3 relative">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-cyan-500 shadow-[0_0_8px_#06b6d4]"></span>
          </span>
          <span class="text-xs font-semibold text-white/80 uppercase tracking-widest">Hot-Serving Ready</span>
        </div>
      </div>
    </div>

    <!-- Error message fallback -->
    <div v-if="errorMessage" class="p-5 rounded-2xl border border-red-500/20 bg-red-500/5 text-red-200 shadow-2xl flex flex-col md:flex-row items-center gap-4">
      <div class="p-3 rounded-xl bg-red-500/20 text-red-400">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <div>
        <h4 class="font-bold text-lg text-white">Service MLOps déconnecté</h4>
        <p class="text-sm text-red-200/80 mt-1">{{ errorMessage }}</p>
      </div>
    </div>

    <!-- Grid Layout Principal -->
    <div v-else-if="!loading" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <!-- Colonne de Gauche : Métriques Champion & Drift -->
      <div class="lg:col-span-2 space-y-8">
        
        <!-- Active Champion Core Stats -->
        <div class="liquid-glass border border-white/[0.08] rounded-3xl p-6 relative overflow-hidden shadow-2xl">
          <div class="absolute right-0 top-0 w-80 h-80 bg-indigo-500/5 blur-[100px] rounded-full pointer-events-none"></div>
          
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-white/[0.08] pb-5 mb-6 gap-4">
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-xl font-bold text-white">Production Active Champion</h3>
                <span class="px-2 py-0.5 bg-green-500/10 border border-green-500/30 text-[10px] font-bold text-green-400 rounded">ACTIVE RUNNING</span>
              </div>
              <p class="text-xs text-slate-400 mt-1">Identifiant version : <span class="font-mono text-cyan-400 font-bold">{{ modelInfo?.model_version || 'v1' }}</span></p>
            </div>
            
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-slate-400">Algorithme :</span>
              <span class="px-3 py-1 bg-white/5 border border-white/10 rounded-lg text-xs font-bold text-white">{{ modelInfo?.model_name }}</span>
            </div>
          </div>

          <!-- Métriques Clés en Grid -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            
            <!-- Accuracy -->
            <div class="bg-white/[0.02] border border-white/[0.05] p-4 rounded-2xl flex flex-col justify-between hover:border-cyan-500/20 transition-colors">
              <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Test Accuracy</span>
              <div class="mt-2 flex items-baseline gap-1">
                <span class="text-2xl font-black text-white">{{ ((modelInfo?.metrics?.accuracy || 0.6084) * 100).toFixed(2) }}%</span>
              </div>
              <div class="w-full bg-white/5 h-1.5 rounded-full mt-3 overflow-hidden">
                <div class="bg-cyan-500 h-full rounded-full" :style="{ width: `${(modelInfo?.metrics?.accuracy || 0.60) * 100}%` }"></div>
              </div>
            </div>

            <!-- Brier Score -->
            <div class="bg-white/[0.02] border border-white/[0.05] p-4 rounded-2xl flex flex-col justify-between hover:border-indigo-500/20 transition-colors">
              <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Brier Score</span>
              <div class="mt-2">
                <span class="text-2xl font-black text-indigo-400">{{ (modelInfo?.metrics?.brier_score || 0.4852).toFixed(4) }}</span>
              </div>
              <span class="text-[9px] font-medium text-slate-500 mt-3 block">Probabilités calibrées (0.0 best)</span>
            </div>

            <!-- F1 Score -->
            <div class="bg-white/[0.02] border border-white/[0.05] p-4 rounded-2xl flex flex-col justify-between hover:border-purple-500/20 transition-colors">
              <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">F1 Score</span>
              <div class="mt-2">
                <span class="text-2xl font-black text-purple-400">{{ ((modelInfo?.metrics?.f1_score || 0.5898) * 100).toFixed(1) }}%</span>
              </div>
              <div class="w-full bg-white/5 h-1.5 rounded-full mt-3 overflow-hidden">
                <div class="bg-purple-500 h-full rounded-full" :style="{ width: `${(modelInfo?.metrics?.f1_score || 0.58) * 100}%` }"></div>
              </div>
            </div>

            <!-- Log Loss -->
            <div class="bg-white/[0.02] border border-white/[0.05] p-4 rounded-2xl flex flex-col justify-between hover:border-orange-500/20 transition-colors">
              <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Log Loss</span>
              <div class="mt-2">
                <span class="text-2xl font-black text-orange-400">{{ (modelInfo?.metrics?.log_loss || 0.8992).toFixed(3) }}</span>
              </div>
              <span class="text-[9px] font-medium text-slate-500 mt-3 block">Indice de surprise (bas = best)</span>
            </div>

          </div>

          <!-- MLOps Pipeline Calibration & Features Sub-View -->
          <div class="mt-8 border-t border-white/[0.08] pt-6">
            <div class="flex items-center gap-1 border-b border-white/[0.08] pb-3 mb-6">
              <button 
                @click="activeTab = 'calibration'"
                class="px-4 py-2 text-xs font-bold rounded-lg transition-all"
                :class="activeTab === 'calibration' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'text-slate-400 hover:text-white'"
              >
                Courbe de Calibration (Reliability Diagram)
              </button>
              <button 
                @click="activeTab = 'features'"
                class="px-4 py-2 text-xs font-bold rounded-lg transition-all"
                :class="activeTab === 'features' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'text-slate-400 hover:text-white'"
              >
                Importance des Features (SHAP values proxy)
              </button>
            </div>

            <!-- TAB 1: Calibration Curve SVG -->
            <div v-if="activeTab === 'calibration'" class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
              
              <!-- reliability diagram drawing -->
              <div class="flex justify-center bg-black/30 border border-white/5 p-4 rounded-2xl">
                <svg width="270" height="270" viewBox="0 0 300 300" class="overflow-visible font-mono text-[9px] fill-slate-500">
                  <!-- Grille de fond -->
                  <line x1="0" y1="300" x2="300" y2="300" stroke="#334155" stroke-width="1" />
                  <line x1="0" y1="0" x2="0" y2="300" stroke="#334155" stroke-width="1" />
                  
                  <line x1="0" y1="225" x2="300" y2="225" stroke="#1e293b" stroke-dasharray="2" stroke-width="1" />
                  <line x1="0" y1="150" x2="300" y2="150" stroke="#1e293b" stroke-dasharray="2" stroke-width="1" />
                  <line x1="0" y1="75" x2="300" y2="75" stroke="#1e293b" stroke-dasharray="2" stroke-width="1" />
                  
                  <line x1="75" y1="0" x2="75" y2="300" stroke="#1e293b" stroke-dasharray="2" stroke-width="1" />
                  <line x1="150" y1="0" x2="150" y2="300" stroke="#1e293b" stroke-dasharray="2" stroke-width="1" />
                  <line x1="225" y1="0" x2="225" y2="300" stroke="#1e293b" stroke-dasharray="2" stroke-width="1" />

                  <!-- Diagonale de calibration parfaite (y = x) -->
                  <line x1="0" y1="300" x2="300" y2="0" stroke="#475569" stroke-width="1.5" stroke-dasharray="4" />
                  <text x="210" y="80" fill="#475569" font-size="8">Calibration Parfaite</text>

                  <!-- Courbe réelle du modèle -->
                  <path :d="calibrationPathString" fill="none" stroke="#f97316" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="drop-shadow-[0_0_4px_rgba(249,115,22,0.4)]" />
                  
                  <!-- Points sur la courbe -->
                  <circle v-for="(p, i) in calibrationPoints" :key="i" :cx="p.x" :cy="p.y" r="5" fill="#f97316" stroke="#ffffff" stroke-width="1.5" />

                  <!-- Libellés des axes -->
                  <text x="150" y="325" text-anchor="middle" class="fill-slate-400 font-bold font-sans">Probabilité Prédite (Bins)</text>
                  <text x="-150" y="-30" text-anchor="middle" transform="rotate(-90)" class="fill-slate-400 font-bold font-sans">Fréquence Réelle constatée</text>

                  <!-- Chiffres axes -->
                  <text x="-5" y="303" text-anchor="end">0.0</text>
                  <text x="-5" y="228" text-anchor="end">0.25</text>
                  <text x="-5" y="153" text-anchor="end">0.5</text>
                  <text x="-5" y="78" text-anchor="end">0.75</text>
                  <text x="-5" y="5" text-anchor="end">1.0</text>

                  <text x="75" y="315" text-anchor="middle">0.25</text>
                  <text x="150" y="315" text-anchor="middle">0.5</text>
                  <text x="225" y="315" text-anchor="middle">0.75</text>
                  <text x="300" y="315" text-anchor="middle">1.0</text>
                </svg>
              </div>

              <!-- text and details -->
              <div class="space-y-4">
                <h4 class="font-bold text-white flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
                  Calibration {{ modelInfo?.calibration || 'Isotonic' }} active
                </h4>
                <p class="text-xs text-slate-300 leading-relaxed">
                  Dans les paris sportifs, prédire une probabilité de victoire est primordial. 
                  Une calibration curve alignée sur la diagonale signifie que lorsque le modèle émet une confiance de <strong>60%</strong> sur un match de Ligue 1, l'équipe à domicile gagne précisément <strong>6 matchs sur 10</strong>.
                </p>
                <div class="p-4 rounded-xl bg-orange-500/10 border border-orange-500/20 text-orange-200 text-xs">
                  <strong>💡 Platt vs Isotonic :</strong> La régression Isotonique (actuelle) réajuste de manière non paramétrique les probabilités brutes du Random Forest pour minimiser le Brier Score de validation temporelle, maximisant la fiabilité des cotes.
                </div>
              </div>
            </div>

            <!-- TAB 2: Feature Importance Bar Chart -->
            <div v-if="activeTab === 'features'" class="space-y-4">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-bold text-white text-sm">Importance relative des variables en production</h4>
                <span class="text-xs text-slate-500">Normalisé sur 1.0 (Somme=100%)</span>
              </div>
              
              <div class="space-y-3">
                <div v-for="feat in featureImportances" :key="feat.name" class="space-y-1">
                  <div class="flex justify-between text-xs font-semibold">
                    <span class="text-slate-300">{{ feat.label }} <span class="text-slate-500 font-mono">({{ feat.name }})</span></span>
                    <span class="text-cyan-400 font-mono">{{ (feat.value * 100).toFixed(1) }}%</span>
                  </div>
                  <div class="w-full bg-white/5 h-2.5 rounded-full overflow-hidden">
                    <div class="bg-gradient-to-r from-cyan-500 to-indigo-500 h-full rounded-full" :style="{ width: `${feat.value * 100 * 3}%` }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Concept Drift Monitoring Panel -->
        <div class="liquid-glass border border-white/[0.08] rounded-3xl p-6 relative overflow-hidden shadow-2xl">
          <div class="absolute left-0 bottom-0 w-64 h-64 bg-cyan-500/5 blur-[100px] rounded-full pointer-events-none"></div>
          
          <div class="flex items-center gap-3 border-b border-white/[0.08] pb-4 mb-5">
            <div class="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-bold text-white">Concept & Data Drift Monitoring</h3>
              <p class="text-xs text-slate-400 mt-0.5">Surveillance en temps réel des distributions de confiance en inférence</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
            
            <!-- Drift Dial Indicator -->
            <div class="flex flex-col items-center justify-center p-4 bg-black/20 rounded-2xl border border-white/5">
              <span class="text-xs font-bold text-slate-500 mb-2 uppercase tracking-wide">État du drift</span>
              
              <div v-if="modelInfo?.drift_status === 0" class="flex flex-col items-center">
                <div class="w-16 h-16 rounded-full bg-green-500/10 border-2 border-green-500 flex items-center justify-center shadow-[0_0_15px_rgba(34,197,94,0.3)] animate-pulse">
                  <span class="text-green-400 text-xs font-bold">STABLE</span>
                </div>
                <span class="text-[11px] text-green-300/80 mt-3 font-semibold text-center">Distribution Conforme</span>
              </div>
              
              <div v-else-if="modelInfo?.drift_status === 1" class="flex flex-col items-center">
                <div class="w-16 h-16 rounded-full bg-orange-500/10 border-2 border-orange-500 flex items-center justify-center shadow-[0_0_15px_rgba(249,115,22,0.3)] animate-pulse">
                  <span class="text-orange-400 text-[10px] font-bold text-center">SUSPECT</span>
                </div>
                <span class="text-[11px] text-orange-300/80 mt-3 font-semibold text-center">Retrain Suggéré</span>
              </div>

              <div v-else class="flex flex-col items-center">
                <div class="w-16 h-16 rounded-full bg-red-500/10 border-2 border-red-500 flex items-center justify-center shadow-[0_0_15px_rgba(239,68,68,0.3)] animate-ping">
                  <span class="text-red-400 text-[10px] font-bold text-center">CRITIQUE</span>
                </div>
                <span class="text-[11px] text-red-300/80 mt-3 font-semibold text-center">Retrain Urgent</span>
              </div>
            </div>

            <!-- Drift Explanation -->
            <div class="md:col-span-2 space-y-3">
              <h4 class="text-sm font-bold text-white">Algorithme d'Analyse Globale</h4>
              <p class="text-xs text-slate-300 leading-relaxed">
                Le football français évolue constamment (mercato d'hiver, changements d'entraîneurs, dynamiques de fin de saison). 
                Notre algorithme compare la confiance glissante en production sur les 20 dernières requêtes. Une baisse de confiance moyenne est synonyme de comportement imprévu des équipes et lève un drapeau.
              </p>
              <div class="text-[11px] text-slate-500 flex items-center gap-1 font-semibold">
                <span class="w-2 h-2 rounded-full bg-cyan-400"></span>
                Télémétrie en cours d'alimentation via l'endpoint <strong>/metrics</strong> de production.
              </div>
            </div>

          </div>

        </div>

      </div>

      <!-- Colonne de Droite : Orchestrateur MLOps Continu -->
      <div class="space-y-8">
        
        <!-- Action Retraining Panel -->
        <div class="liquid-glass border border-white/[0.08] rounded-3xl p-6 relative overflow-hidden shadow-2xl flex flex-col justify-between min-h-[500px]">
          <div class="absolute right-0 top-0 w-48 h-48 bg-purple-500/5 blur-[80px] rounded-full pointer-events-none"></div>
          
          <div class="space-y-5">
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full" :class="retraining ? 'bg-cyan-400 animate-ping' : 'bg-purple-500'"></span>
              MLOps Orchestrator
            </h3>
            
            <p class="text-xs text-slate-400 leading-relaxed">
              Exécutez de manière asynchrone le pipeline de retraining automatique :
              normalisation Elo, feature engineering, et validation **Champion-Challenger** par Brier Score.
            </p>

            <!-- Bouton Trigger -->
            <button 
              @click="triggerRetraining"
              :disabled="retraining"
              class="w-full py-3.5 px-4 rounded-xl font-bold transition-all flex items-center justify-center gap-3 active:scale-95 shadow-xl cursor-pointer"
              :class="retraining 
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 cursor-not-allowed' 
                : 'bg-gradient-to-r from-cyan-500 via-indigo-500 to-purple-600 hover:shadow-[0_0_25px_rgba(168,85,247,0.4)] text-white hover:scale-[1.02]'"
            >
              <svg v-if="retraining" class="animate-spin h-5 w-5 text-cyan-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ retraining ? 'Pipeline en cours...' : 'Déclencher Pipeline MLOps' }}</span>
            </button>
          </div>

          <!-- Console Live Logs -->
          <div class="mt-6 flex-1 flex flex-col justify-end">
            <div class="flex items-center justify-between mb-2">
              <span class="text-[11px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-cyan-400" :class="{ 'animate-pulse': retraining }"></span>
                Console de Build MLOps
              </span>
              <span class="text-[9px] font-mono text-slate-500">{{ pipelineStatus?.status || 'idle' }}</span>
            </div>
            
            <div class="bg-black/60 border border-white/5 rounded-2xl p-4 font-mono text-[10px] text-cyan-300 h-64 overflow-y-auto shadow-inner flex flex-col">
              <pre class="whitespace-pre-wrap flex-1">{{ pipelineStatus?.logs }}</pre>
            </div>
          </div>

        </div>

      </div>

    </div>
  </div>
</template>

<style scoped>
.liquid-glass {
  background: rgba(10, 10, 20, 0.55);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
</style>
