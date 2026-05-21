# L1 DataLab Studio — Frontend Premium SaaS Vision

## Vision produit

Le frontend de **L1 DataLab Studio** reflète une plateforme IA moderne, premium et immersive, inspirée de :

* Leonardo.ai · Vercel · Linear · Perplexity · Arc Browser · Raycast · Anthropic Console

> **« Agentic Analytics as a Service »** — analyser, prédire, expliquer et assister sur le championnat Ligue 1.

---

## Stack frontend

| Couche | Technologies |
|--------|----------------|
| Core | Vue.js 3, Vite, TypeScript, Vue Router, Pinia, Axios |
| UI | TailwindCSS v4, Liquidglass custom classes |
| Motion | GSAP, ScrollTrigger |
| API | App API (`localhost:8002`), JWT Bearer |

---

## Structure actuelle (`services/frontend/src/`)

```text
src/
├── api/
│   ├── axios.ts          # Intercepteurs JWT + gestion 401
│   └── ragStream.ts      # Client SSE Oracle RAG
├── data/
│   └── teamRegistry.ts   # 18 clubs Ligue 1 (canonique, aliases, colors)
├── types/
│   └── team.ts           # Ligue1Team, TeamColors, ResolvedTeam
├── utils/
│   ├── teamLogos.ts      # Cache, preload, hydrate standings
│   └── formatApiError.ts # Messages d'erreur lisibles
├── stores/
│   └── auth.ts           # login, register, fetchUser, JWT
├── views/
│   ├── HomeView.vue      # Landing GSAP + constellation logos
│   ├── LoginView.vue
│   ├── RegisterView.vue
│   ├── DashboardView.vue
│   ├── PredictionView.vue   # Neural Core + POST /predict
│   ├── HistoryView.vue      # GET /predictions + logos enrichis
│   ├── RagView.vue          # AI Oracle SSE
│   ├── ProfileView.vue
│   └── AIInsightsView.vue   # MLOps pipeline
├── components/
│   ├── prediction/       # NeuralCore, PredictionHistory
│   ├── dashboard/      # MatchCard, LeagueStandings, TopScorers
│   └── landing/          # FloatingLogo
├── router/index.ts
├── main.ts               # initTeamLogoSystem() au boot
└── App.vue               # Nav glass + auth menu
```

---

## Routes & auth

| Route | Auth | Description |
|-------|------|-------------|
| `/` | — | Landing premium |
| `/login`, `/register` | — | JWT OAuth2 form |
| `/dashboard` | ✅ | Matchs, classement, buteurs |
| `/prediction` | ✅ | Prédiction IA + Neural Core |
| `/history` | ✅ | Historique utilisateur |
| `/rag` | ✅ | AI Oracle (streaming) |
| `/profile` | ✅ | Profil + déconnexion |
| `/ai-insights` | ✅ | MLOps / pipeline ML |

Guard global : `meta.requiresAuth` → redirect `/login`.

---

## Système logos (implémenté)

### Boot (`main.ts`)

```typescript
initTeamLogoSystem()
// → preloadTeamLogos()      // new Image() pour tous les assets
// → hydrateStandingsLogos()   // un seul GET /standings
```

### API publique (`utils/teamLogos.ts`)

| Fonction | Rôle |
|----------|------|
| `logoCache` | Map mémoire nom → URL |
| `resolveTeamLogo(name, apiLogo?)` | Résolution avec cache |
| `getCachedTeamLogo(name)` | Lecture cache seule |
| `resolveTeamWithLogo(name)` | Métadonnées complètes (RAG futur) |
| `preloadTeamLogos()` | Préchargement images |
| `hydrateStandingsLogos()` | Hydratation LFP unique |

### Registre (`data/teamRegistry.ts`)

- 18 équipes Ligue 1 2025/26
- `resolveLigue1Team()`, `getTeamColors()`, `getAllLigue1Teams()`
- Aliases couvrant noms backend (`Marseille`, `PSG`, `Lens`…)

---

## Pages — état d'avancement

### ✅ Phase 1 — Foundation

- [x] Landing Hero + constellation GSAP
- [x] Login / Register + JWT
- [x] Messages d'erreur API explicites (`formatApiError`)
- [x] Intercepteur 401 intelligent

### ✅ Phase 2 — Dashboard & prédictions

- [x] Dashboard (matchday, standings, top scorers)
- [x] PredictionView + Neural Core (idle/loading/reveal)
- [x] Persistance prédictions (`POST /predict`)
- [x] HistoryView avec logos, filtres, stats
- [x] Bannière « enregistré dans l'historique »

### ✅ Phase 3 — AI Experience

- [x] RagView — Oracle conversationnel
- [x] Streaming SSE (`/insights/question/stream`)
- [x] ProfileView
- [x] AIInsightsView (MLOps)

### 🔜 Phase 4 — Premium polish

- [ ] Glows dynamiques par `TeamColors` sur cartes historique
- [ ] Pricing page (branche `feature/frontend-pricing` à merger)
- [ ] Auto-refresh JWT
- [ ] `resolveTeamWithLogo` dans PredictionView + RAG
- [ ] Tests E2E Playwright auth + predict + history

---

## Intégration API

```text
Frontend (8080 / 5173)
    ↓ Axios + JWT
App API (8002)
    ├── /auth/login, /users, /users/me
    ├── /predict, /predictions
    ├── /standings, /current-matchday, /top-scorers
    └── /insights/question, /insights/question/stream
```

Variable : `VITE_API_URL` (défaut `http://localhost:8002`).

---

## Sécurité frontend

- Token JWT dans `localStorage` (`access_token`)
- Injection automatique `Authorization: Bearer`
- 401 : purge token + redirect uniquement si session existante hors pages auth
- Routes protégées via guard router

---

## Performance

- Lazy routes (`HistoryView`, `RagView`, `ProfileView`)
- Préchargement logos au boot (zéro flicker historique)
- Cache mémoire logos (pas de refetch standings par navigation)
- Images locales bundlées (Vite) pour fallback offline

---

## Docker & dev local

| Mode | Commande |
|------|----------|
| **Dev HMR** | `cd services/frontend && npm run dev` → `:5173` |
| **Prod Docker** | `docker compose build frontend && docker compose up -d frontend` → `:8080` |

Le conteneur `frontend` sert des assets statiques Nginx (pas de volume hot-reload).

---

## Objectif final

Transformer L1 DataLab en plateforme SaaS IA premium de predictive analytics footballistique :

- Vrai produit startup, pas projet étudiant
- AI-native (Oracle, Neural Core, explainability)
- Identité visuelle cohérente (Sunset Mystique + Liquidglass)
- Socle données clubs typé pour RAG, mood engine et analytics
