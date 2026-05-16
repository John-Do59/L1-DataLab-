# L1 DataLab Studio — Frontend Premium SaaS Vision

## Vision Produit
Le frontend de **L1 DataLab Studio** doit refléter une plateforme IA moderne, premium et immersive, inspirée des meilleurs produits AI actuels :
* Leonardo.ai
* Vercel
* Linear
* Perplexity
* Arc Browser
* Raycast
* Anthropic Console

L’objectif n’est pas seulement de construire un dashboard football, mais une expérience SaaS haut de gamme orientée :
* IA
* agentic systems
* data visualization
* predictive analytics
* onboarding immersif

---

# Positionnement Produit

## Concept
> “Agentic Analytics as a Service”

L1 DataLab devient :
* une plateforme intelligente,
* capable d’analyser,
* prédire,
* expliquer,
* et assister l’utilisateur dans la compréhension du championnat.

Le frontend doit transmettre :
* sophistication,
* fluidité,
* précision,
* modernité,
* sensation “AI-native”.

---

# Stack Frontend

## Core
* Vue.js 3
* Vite
* TypeScript
* Vue Router
* Pinia
* Axios

## UI / Animation
* TailwindCSS
* GSAP
* ScrollTrigger
* Framer Motion (optionnel)
* Lenis smooth scroll (optionnel)

---

# Direction Artistique

## Palette — “Sunset Mystique”
### Couleurs principales
* Deep Navy (`#20115b`)
* Midnight Purple (`#010108` background absolu)
* Sunset Orange / Pink (`#f6b3e5` Rose cendré)
* Neon Lilas (`#c876ff`)
* Electric Violet (`#7232f2`)

### Ambiance & Style : Apple iOS 26 Liquidglass
L'interface adoptera un look futuriste ultra-premium inspiré d'une hypothétique version "Apple iOS 26 Liquidglass" :
* **Glassmorphism poussé à l'extrême** : Flous d'arrière-plan profonds (backdrop-filter: blur), bordures translucides 1px, et réflexions lumineuses subtiles.
* **Liquid Transitions** : Les éléments ne disparaissent pas, ils se transforment de manière organique (morphing de formes).
* **Typographie** : minimaliste, aérée, sans-serif géométrique très fine avec un tracking précis.
* **Glow & Aura** : Des halos lumineux de couleur `Sunset Mystique` qui suivent les actions de l'utilisateur (hover magnétiques).

---

# Structure Frontend

```text
frontend/
├── src/
│
├── api/
│   ├── auth.ts
│   ├── matches.ts
│   ├── predictions.ts
│
├── stores/
│   ├── auth.ts
│   ├── ui.ts
│
├── layouts/
│   ├── AuthLayout.vue
│   ├── DashboardLayout.vue
│
├── views/
│   ├── LandingView.vue
│   ├── LoginView.vue
│   ├── RegisterView.vue
│   ├── DashboardView.vue
│   ├── MatchView.vue
│
├── components/
│   ├── hero/
│   ├── dashboard/
│   ├── onboarding/
│   ├── animations/
│
├── composables/
├── router/
├── assets/
└── styles/
```

---

# UX Goals

## Objectifs UX
Le frontend doit donner l’impression :
* d’un produit IA premium,
* rapide,
* intelligent,
* élégant,
* vivant,
* fluide.

Le focus UX doit être :
* motion design subtil,
* transitions douces,
* animations GPU-friendly,
* expérience immersive,
* navigation ultra fluide.

---

# Landing Page Premium

## Hero Section
* énorme headline typographique
* gradient animé Liquidglass
* CTA premium avec effet magnétique
* métriques Ligue 1 live
* glow effects subtils en arrière-plan

---

# Scroll Gallery Premium (Leonardo.ai Inspired)

## Vision
Créer une expérience immersive type :
* Leonardo.ai
* Apple product storytelling
* modern AI SaaS showcase

---

# Scroll Animation Requirements

## Comportement
* section sticky en plein écran
* pile d’images / dashboards
* défilement lié au scroll
* transitions fluides
* effet profondeur
* léger scale dynamique
* opacité progressive
* micro-parallax subtil

---

# Architecture Animation

## Structure
* section très haute (300vh+)
* container sticky en 100vh
* images préchargées
* transitions synchronisées au scroll

---

# Technologies recommandées

## Animation Engine
**GSAP + ScrollTrigger**

Pourquoi :
* pinning précis
* scrub fluide
* performance mobile
* timeline complexe
* contrôle cinématique

---

# Effets visuels

## Effets autorisés
* opacity fade
* scale interpolation
* blur léger (Liquidglass)
* translateY subtil
* z-index dynamique
* glow doux
* parallax faible

## Effets interdits
* animations agressives
* zoom excessif
* transitions brutales
* effets “gaming”
* overload visuel

---

# Pages à Développer

## Phase 1 — Foundation
### Landing
* Hero premium
* Scroll gallery
* CTA onboarding

### Auth
* Login
* Register
* JWT integration

---

## Phase 2 — Dashboard
### Dashboard utilisateur
* prochains matchs
* prédictions IA
* probabilités
* classement

### Match Details
* statistiques
* historique
* prédiction détaillée

---

## Phase 3 — AI Experience
### Insights IA
* explications du modèle
* génération de résumés
* assistant IA local

### Agentic UX
* suggestions automatiques
* insights contextualisés
* recommandations intelligentes

---

# API Integration

## Backend connecté
Frontend → App API

L’App API centralise :
* auth JWT
* récupération des matchs
* historique utilisateur
* appels ML API
* insights IA

---

# Sécurité

## Auth Flow
* JWT access token
* protected routes
* axios interceptors
* auto refresh futur

---

# Performance

## Priorités
* lazy loading
* route splitting
* image optimization
* animation GPU accelerated
* mobile first

---

# Mobile Experience
Le design doit être :
* responsive
* tactile
* fluide
* minimaliste
* performant sur mobile

---

# Objectif Final
Transformer L1 DataLab en :
> une plateforme SaaS IA premium de predictive analytics footballistique.

Le frontend doit donner l’impression :
* d’un vrai produit startup,
* d’un SaaS moderne,
* d’une plateforme AI-native,
* et non d’un simple projet étudiant.
