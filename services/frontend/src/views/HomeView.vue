<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import gsap from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'
import FloatingLogo from '../components/landing/FloatingLogo.vue'
import { useRouter } from 'vue-router'

// Assets - Logos 2025/2026 Monochrome
import angersscoLogo from '../assets/logos/angerssco.png'
import ajauxerreLogo from '../assets/logos/ajauxerre.png'
import stadebrestoisLogo from '../assets/logos/stadebrestois.png'
import lehavreacLogo from '../assets/logos/lehavreac.png'
import rclensLogo from '../assets/logos/rclens.png'
import losclilleLogo from '../assets/logos/losclille.png'
import fclorientLogo from '../assets/logos/fclorient.png'
import olympiquelyonnaisLogo from '../assets/logos/olympiquelyonnais.png'
import olympiquedemarseilleLogo from '../assets/logos/olympiquedemarseille.png'
import fcmetzLogo from '../assets/logos/fcmetz.png'
import asmonacofcLogo from '../assets/logos/asmonacofc.png'
import fcnantesLogo from '../assets/logos/fcnantes.png'
import ogcniceLogo from '../assets/logos/ogcnice.png'
import parisfcLogo from '../assets/logos/parisfc.png'
import parissaintgermainLogo from '../assets/logos/parissaintgermain.png'
import staderennaisfcLogo from '../assets/logos/staderennaisfc.png'
import toulousefcLogo from '../assets/logos/toulousefc.png'
import rcstrasbourgalsaceLogo from '../assets/logos/rcstrasbourgalsace.png'

// Assets - Screenshots
import dashboardImg from '../assets/screenshots/sport-science-insights-banner.png'
import heroPredictionImg from '../assets/screenshots/ballon-ml.jpg'
import insightPanelImg from '../assets/screenshots/ballon-ia2.png'

gsap.registerPlugin(ScrollTrigger)

const router = useRouter()

const teams = [
  { name: "Angers SCO", src: angersscoLogo, size: 'md', class: 'left-[87.5%] top-[50.0%]', delay: 2.5, duration: 7.6 },
  { name: "AJ Auxerre", src: ajauxerreLogo, size: 'sm', class: 'left-[87.8%] top-[62.9%]', delay: 1.9, duration: 9.2 },
  { name: "Stade Brestois 29", src: stadebrestoisLogo, size: 'lg', class: 'left-[80.5%] top-[71.6%]', delay: 0.8, duration: 9.9 },
  { name: "Le Havre AC", src: lehavreacLogo, size: 'lg', class: 'left-[71.1%] top-[79.4%]', delay: 1.3, duration: 7.1 },
  { name: "RC Lens", src: rclensLogo, size: 'md', class: 'left-[57.2%] top-[87.0%]', delay: 2.7, duration: 5.2 },
  { name: "LOSC Lille", src: losclilleLogo, size: 'md', class: 'left-[43.5%] top-[86.6%]', delay: 0.7, duration: 5.6 },
  { name: "FC Lorient", src: fclorientLogo, size: 'md', class: 'left-[31.0%] top-[80.9%]', delay: 1.8, duration: 5.9 },
  { name: "Olympique Lyonnais", src: olympiquelyonnaisLogo, size: 'md', class: 'left-[20.6%] top-[73.0%]', delay: 1.9, duration: 9.3 },
  { name: "Olympique de Marseille", src: olympiquedemarseilleLogo, size: 'lg', class: 'left-[13.6%] top-[62.1%]', delay: 0.5, duration: 9.4 },
  { name: "FC Metz", src: fcmetzLogo, size: 'lg', class: 'left-[10.0%] top-[50.0%]', delay: 1.7, duration: 5.1 },
  { name: "AS Monaco FC", src: asmonacofcLogo, size: 'md', class: 'left-[13.4%] top-[37.4%]', delay: 0.2, duration: 5.0 },
  { name: "FC Nantes", src: fcnantesLogo, size: 'lg', class: 'left-[20.4%] top-[26.1%]', delay: 0.8, duration: 8.4 },
  { name: "OGC Nice", src: ogcniceLogo, size: 'sm', class: 'left-[30.5%] top-[17.7%]', delay: 1.7, duration: 8.1 },
  { name: "Paris FC", src: parisfcLogo, size: 'md', class: 'left-[42.9%] top-[12.6%]', delay: 0.9, duration: 6.6 },
  { name: "Paris Saint-Germain", src: parissaintgermainLogo, size: 'sm', class: 'left-[57.3%] top-[14.7%]', delay: 0.1, duration: 7.2 },
  { name: "Stade Rennais FC", src: staderennaisfcLogo, size: 'md', class: 'left-[69.8%] top-[21.1%]', delay: 1.6, duration: 6.1 },
  { name: "Toulouse FC", src: toulousefcLogo, size: 'md', class: 'left-[78.8%] top-[26.2%]', delay: 2.0, duration: 5.3 },
  { name: "RC Strasbourg Alsace", src: rcstrasbourgalsaceLogo, size: 'lg', class: 'left-[90.4%] top-[38.1%]', delay: 2.3, duration: 9.0 }
]

// Multiplication des logos pour créer un effet de tunnel continu (72 logos)
const allTeams = [...teams, ...teams, ...teams, ...teams]

const mainContainer = ref<HTMLElement | null>(null)
let ctx: gsap.Context

onMounted(() => {
  ctx = gsap.context(() => {
    
    // SCÈNE 1 : HERO & CONSTELLATION
    // État initial : les logos sont invisibles, au centre, mais éparpillés très très loin en profondeur (Starfield effect)
    gsap.set('.constellation-logo-wrapper', { 
      opacity: 0, 
      scale: 0.1,
      x: () => (Math.random() - 0.5) * window.innerWidth * 1.5,
      y: () => (Math.random() - 0.5) * window.innerHeight * 1.5,
      z: () => -1000 - Math.random() * 2000,
      rotationZ: () => (Math.random() - 0.5) * 180
    })

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: '.hero-section',
        start: 'top top',
        end: '+=400%', // Durée rallongée pour l'effet tunnel
        pin: true,
        scrub: 1,
      }
    })

    // Le titre recule et s'efface
    tl.to('.hero-content', { opacity: 0, scale: 0.5, z: -1000, duration: 1 })
      
      // Les logos foncent vers la caméra (l'inverse du titre)
      .to('.constellation-logo-wrapper', {
        opacity: () => 0.6 + Math.random() * 0.4,
        scale: () => 1.5 + Math.random() * 2,
        z: () => 500 + Math.random() * 1000, // Ils dépassent la caméra
        duration: 4, // Longue traversée
        stagger: {
          each: 0.05,
          from: "random" // Flux ininterrompu
        },
        ease: 'none'
      }, "<")
      
      // Ils disparaissent juste avant ou au moment de toucher l'écran (disparition individuelle)
      .to('.constellation-logo-wrapper', {
        opacity: 0,
        duration: 0.5,
        stagger: {
          each: 0.05,
          from: "random"
        }
      }, "-=3")
      
      // Le Dashboard émerge du vide à la fin
      .to('.dashboard-preview', {
        y: 0,
        opacity: 1,
        rotateX: 0,
        scale: 1,
        duration: 2,
        ease: 'power3.out'
      }, "-=1.5")
      
      // SÉCURITÉ : on fait disparaître tout le conteneur des logos pour être sûr qu'aucun ne reste collé
      .to('.constellation-container', {
        opacity: 0,
        duration: 1
      }, "<")


    // SCÈNE 2 : PANELS HORIZONTAUX (Scroll Gallery)
    const panels = gsap.utils.toArray('.narrative-panel')
    
    gsap.to(panels, {
      xPercent: -100 * (panels.length - 1),
      ease: "none",
      scrollTrigger: {
        trigger: ".panels-container",
        pin: true,
        scrub: 1,
        // Aligne parfaitement chaque panel lors de l'arrêt du scroll
        snap: 1 / (panels.length - 1),
        end: () => "+=" + (document.querySelector(".panels-container") as HTMLElement)?.offsetWidth
      }
    });

  }, mainContainer.value!) // Limite la portée GSAP à ce composant
})

onUnmounted(() => {
  if (ctx) ctx.revert() // Cleanup strict pour éviter les bugs au changement de page
})

const goDashboard = () => {
  router.push('/login')
}
</script>

<template>
  <div ref="mainContainer" class="bg-[#010108] text-white min-h-screen overflow-hidden relative selection:bg-sunset-accent selection:text-black">
    
    <!-- Cinematic Noise Overlay (Astuce UX Premium) -->
    <div class="fixed inset-0 pointer-events-none opacity-[0.03] mix-blend-overlay z-50 bg-[url('https://grainy-gradients.vercel.app/noise.svg')]"></div>

    <!-- Background Glow -->
    <div class="fixed top-0 left-1/2 -translate-x-1/2 w-[80vw] h-[50vh] bg-sunset-primary/20 blur-[150px] rounded-full pointer-events-none z-0"></div>

    <!-- ============================================== -->
    <!-- SECTION 1 : HERO OPENING & CONSTELLATION     -->
    <!-- ============================================== -->
    <section class="hero-section relative h-screen flex flex-col items-center justify-center perspective-[1000px] z-10">
      
      <!-- Titre Central -->
      <div class="hero-content text-center z-20 flex flex-col items-center gap-6">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-sunset-primary/30 bg-sunset-primary/10 text-sunset-primary text-xs font-bold tracking-widest uppercase mb-4 backdrop-blur-md shadow-[0_0_20px_rgba(246,179,229,0.2)]">
          <span class="w-2 h-2 rounded-full bg-sunset-primary animate-pulse"></span>
          Ligue 1 2025/2026 Ready
        </div>
        <h1 class="text-6xl md:text-8xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-white via-white to-sunset-accent leading-tight drop-shadow-2xl">
          L1 DataLab
        </h1>
        <p class="text-xl md:text-2xl text-sunset-secondary/90 font-medium max-w-2xl mt-2 tracking-wide font-light">
          Agentic Football Intelligence Platform.
        </p>
        <p class="text-xs text-white/30 mt-16 tracking-[0.3em] uppercase animate-pulse flex flex-col items-center gap-2">
          Scroll to explore
          <span class="text-lg">↓</span>
        </p>
      </div>

      <!-- Logos Flottants : Tunnel Spatial -->
      <div class="constellation-container absolute inset-0 pointer-events-none z-10 flex items-center justify-center perspective-[2000px] transform-style-3d">
        <div 
          v-for="(team, index) in allTeams" 
          :key="index"
          class="constellation-logo-wrapper absolute"
        >
          <FloatingLogo 
            :name="team.name" 
            :imgSrc="team.src" 
            :size="team.size as any" 
            :delay="Math.random() * 5" 
            :duration="5 + Math.random() * 5" 
          />
        </div>
      </div>

      <!-- Dashboard Mockup caché initialement (Apparaît au scroll) -->
      <div class="dashboard-preview absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] md:w-[75vw] h-[70vh] liquid-glass rounded-[2rem] border border-sunset-primary/30 shadow-[0_0_100px_-20px_rgba(200,118,255,0.4)] opacity-0 translate-y-32 rotate-x-[15deg] scale-90 z-30 flex flex-col items-center justify-center overflow-hidden bg-black/40 backdrop-blur-3xl">
        <img :src="dashboardImg" alt="Dashboard Preview" class="absolute inset-0 w-full h-full object-cover opacity-60 mix-blend-screen" />
        <div class="absolute inset-0 bg-gradient-to-tr from-sunset-primary/10 to-transparent"></div>
      </div>
    </section>

    <!-- ============================================== -->
    <!-- SECTION 2 : SCROLL GALLERY NARRATIVE         -->
    <!-- ============================================== -->
    <section class="panels-container relative h-screen flex w-[400vw] z-20">
      
      <!-- Panel 1: Predictive AI -->
      <div class="narrative-panel w-screen h-screen flex items-center justify-center p-8 md:p-12 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-sunset-primary/20 blur-[120px] rounded-full pointer-events-none"></div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-7xl w-full items-center">
          <div>
            <h2 class="text-5xl md:text-7xl font-black mb-6 text-white leading-tight">Predictive AI<br><span class="text-transparent bg-clip-text bg-gradient-to-r from-sunset-primary to-sunset-accent">Engine</span>.</h2>
            <p class="text-lg md:text-xl text-white/60 leading-relaxed mb-8 font-light">
              Notre modèle XGBoost analyse plus de 150 métriques en temps réel pour générer des probabilités dynamiques avant chaque match. La puissance des mathématiques au service du jeu.
            </p>
          </div>
          <div class="liquid-glass rounded-3xl h-[300px] md:h-[450px] border border-sunset-primary/30 relative overflow-hidden flex items-center justify-center shadow-[0_0_50px_rgba(200,118,255,0.15)] group">
             <img :src="heroPredictionImg" alt="Predictive Analytics" class="w-full h-full object-cover opacity-90 transition-transform duration-700 group-hover:scale-105" />
             <div class="absolute inset-0 bg-gradient-to-br from-sunset-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
          </div>
        </div>
      </div>

      <!-- Panel 2: Agentic Insights -->
      <div class="narrative-panel w-screen h-screen flex items-center justify-center p-8 md:p-12 relative overflow-hidden">
        <div class="absolute bottom-0 left-0 w-[500px] h-[500px] bg-sunset-secondary/20 blur-[120px] rounded-full pointer-events-none"></div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-7xl w-full items-center">
          <div class="order-2 md:order-1 liquid-glass rounded-3xl h-[300px] md:h-[450px] border border-white/10 relative overflow-hidden flex items-center justify-center shadow-2xl">
             <img :src="insightPanelImg" alt="Insight Panel" class="w-full h-full object-cover opacity-70" />
             <!-- Overlay IA text façon Agent -->
             <div class="absolute inset-x-8 bottom-8 p-6 bg-black/60 backdrop-blur-2xl rounded-2xl border border-sunset-accent/40 text-sm text-white/90 shadow-[0_0_30px_rgba(200,118,255,0.2)]">
                <span class="text-sunset-accent font-bold mb-2 block text-xs tracking-widest uppercase">Agent Output</span>
                "Monaco's xG production drops by 20% against high-pressing defensive blocks. Expect a tightly contested midfield battle."
             </div>
          </div>
          <div class="order-1 md:order-2">
            <h2 class="text-5xl md:text-7xl font-black mb-6 text-white leading-tight">Agentic<br><span class="text-sunset-secondary">Insights</span>.</h2>
            <p class="text-lg md:text-xl text-white/60 leading-relaxed font-light">
              Ne regardez plus de simples chiffres. Nos agents LLM contextualisent la donnée (RAG) pour vous fournir des narrations tactiques exploitables instantanément.
            </p>
          </div>
        </div>
      </div>

      <!-- Panel 3: Infrastructure -->
      <div class="narrative-panel w-screen h-screen flex items-center justify-center p-8 md:p-12 relative overflow-hidden">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-7xl w-full items-center">
          <div>
            <h2 class="text-5xl md:text-7xl font-black mb-6 text-white leading-tight">Production<br><span class="text-blue-400">Ready</span>.</h2>
            <p class="text-lg md:text-xl text-white/60 leading-relaxed mb-8 font-light">
              Une architecture micro-services distribuée (FastAPI, Docker, PostgreSQL) supervisée par Grafana et OpenTelemetry. Pensée pour la résilience SRE et le MLOps.
            </p>
          </div>
          <div class="liquid-glass rounded-3xl h-[300px] md:h-[450px] border border-white/10 relative overflow-hidden flex flex-col p-6 shadow-2xl">
             <!-- Fake Grafana skeleton -->
             <div class="w-full flex gap-4 mb-4">
               <div class="h-24 flex-1 bg-green-500/10 border border-green-500/20 rounded-xl"></div>
               <div class="h-24 flex-1 bg-blue-500/10 border border-blue-500/20 rounded-xl"></div>
               <div class="h-24 flex-1 bg-sunset-primary/10 border border-sunset-primary/20 rounded-xl"></div>
             </div>
             <div class="flex-1 bg-black/40 rounded-xl border border-white/5 flex items-center justify-center relative overflow-hidden">
               <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+CjxwYXRoIGQ9Ik0wIDIwaDQwTTIwIDB2NDAiIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjA1KSIgc3Ryb2tlLXdpZHRoPSIxIi8+Cjwvc3ZnPg==')]"></div>
               <span class="text-white/40 text-sm font-medium tracking-widest uppercase relative z-10">Screenshot: Grafana Traces</span>
             </div>
          </div>
        </div>
      </div>

      <!-- Panel 4: Call To Action -->
      <div class="narrative-panel w-screen h-screen flex items-center justify-center p-8 md:p-12 relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-t from-sunset-primary/20 via-[#010108] to-[#010108] pointer-events-none z-0"></div>
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-sunset-accent/10 blur-[150px] rounded-full pointer-events-none z-0"></div>
        
        <div class="text-center max-w-3xl relative z-10">
          <div class="w-24 h-24 mx-auto mb-10 liquid-glass rounded-full flex items-center justify-center border border-sunset-accent/40 shadow-[0_0_80px_rgba(200,118,255,0.4)] animate-[float_4s_ease-in-out_infinite]">
            <span class="text-4xl text-sunset-accent font-black">L1</span>
          </div>
          <h2 class="text-5xl md:text-7xl font-black mb-8 text-white tracking-tight">Experience Realtime<br>Intelligence.</h2>
          <p class="text-xl text-white/60 mb-12 font-light">
            Déployé. Entraîné. Prêt pour la saison. Connectez-vous pour accéder au Command Center et générer vos propres prédictions dynamiques.
          </p>
          <button @click="goDashboard" class="bg-white text-black font-black text-lg px-12 py-5 rounded-2xl hover:bg-sunset-accent hover:text-white hover:shadow-[0_0_40px_-10px_#f6b3e5] transition-all hover:scale-105 duration-300">
            Access Neural Engine
          </button>
        </div>
      </div>

    </section>
  </div>
</template>
