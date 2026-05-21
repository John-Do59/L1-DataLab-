# L1 DataLab Studio — Frontend Premium SaaS Vision

## Vision produit

Plateforme IA premium inspirée de Leonardo.ai, Vercel, Linear, Perplexity.

> **« Agentic Analytics as a Service »** — Ligue 1 predictive analytics.

---

## Stack

Vue 3 · Vite · TypeScript · Pinia · Axios · Tailwind v4 · GSAP · SSE (Oracle)

---

## Structure (`services/frontend/src/`)

```text
src/
├── theme/                  # ✅ Design tokens (feature/design-tokens)
│   ├── tokens.ts
│   ├── colors.ts | glass.ts | motion.ts | oracle.ts | teams.ts
│   └── applyTheme.ts
├── data/teamRegistry.ts
├── types/team.ts
├── utils/teamLogos.ts | formatApiError.ts
├── utils/teamVisuals.ts     # branche team-colors
├── api/axios.ts | ragStream.ts
├── stores/auth.ts
├── views/ (Home, Dashboard, Prediction, History, Rag, Profile, AIInsights)
├── components/
│   ├── rag/RagEntity.vue
│   ├── prediction/NeuralCore.vue
│   ├── dashboard/MatchCard.vue
│   └── ui/TeamGlow.vue
├── router/index.ts
└── main.ts                  # applyDesignTokens() + initTeamLogoSystem()
```

---

## Design token system ✅

| Fichier | Rôle |
|---------|------|
| `colors.ts` | Palette Sunset + sémantique |
| `glass.ts` | Liquidglass (opacity, blur, border, gradient) |
| `motion.ts` | Durées, easing, stagger |
| `oracle.ts` | Moods Oracle + intensités glow |
| `teams.ts` | `getTeamColors`, `resolveLigue1Team` |
| `applyTheme.ts` | Variables CSS `--color-*`, `--glass-*`, `--oracle-*` |

Boot : `applyDesignTokens()` avant `initTeamLogoSystem()`.

---

## Couleurs clubs & mood ✅ (branche séparée)

`feature/team-colors-visual-system` :

- `teamVisuals.ts` — `getTeamVisuals`, `getOracleAccent`, `blendTeamWithMood`
- `TeamGlow.vue` — logos historique
- PredictionView — panneaux domicile/extérieur dynamiques
- RagEntity — accent vars selon club détecté dans la question
- MatchCard — bordures & glow par équipe

---

## Routes

| Route | Auth | Feature |
|-------|------|---------|
| `/` | — | Landing GSAP |
| `/login`, `/register` | — | JWT |
| `/dashboard` | ✅ | LFP live |
| `/prediction` | ✅ | Neural Core |
| `/history` | ✅ | Prédictions user |
| `/rag` | ✅ | Oracle SSE |
| `/profile` | ✅ | Compte |
| `/ai-insights` | ✅ | MLOps |

---

## Phases

### ✅ Livré

- Foundation (auth, landing, tokens, logos)
- Dashboard & prédictions (persist, historique)
- Oracle RAG (SSE, RagEntity, mood)
- Design tokens `src/theme/`
- Messages d'erreur API
- Pricing page (`/pricing`, `src/features/pricing/`)

### 🔜 À venir

- Merger `team-colors` + `pgvector` branches
- Stripe Checkout + Customer Portal
- JWT refresh
- Tests E2E Playwright
- Migration composants 100 % tokens CSS (réduire Tailwind hardcodé)

---

## API

`VITE_API_URL` → `http://localhost:8002`

Endpoints clés : `/predict`, `/predictions`, `/standings`, `/insights/question/stream`

---

## Documentation

| Fichier | Description |
|---------|-------------|
| [`frontend-implementation.md`](./frontend-implementation.md) | Guide implémentation détaillé |
| [`design.md`](./design.md) | Stratégie produit & DA |
| [`rag-implementation.md`](./rag-implementation.md) | Oracle backend |
| [`backend-implementation.md`](./backend-implementation.md) | App API |
| [`DOCKER.md`](./DOCKER.md) | Infra |

---

## Objectif

Plateforme SaaS IA sportive premium — identité visuelle unifiée (tokens + clubs + Oracle), pas un dashboard étudiant générique.
