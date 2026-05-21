# L1 DataLab — Frontend Implementation

Guide d'implémentation du frontend Vue.js : architecture, design system, intégrations API et branches fonctionnelles.

---

## 1. Stack & boot

| Technologie | Version / rôle |
|-------------|----------------|
| Vue 3 + Vite | SPA, HMR dev `:5173` |
| TypeScript | Typage strict |
| Pinia | Auth store |
| Tailwind v4 | Utility + classes custom Liquidglass |
| GSAP | Landing animations |
| Axios + fetch | REST + SSE RAG |

### Séquence au démarrage (`main.ts`)

```typescript
applyDesignTokens()    // variables CSS :root
initTeamLogoSystem()   // preload logos + hydrate standings
authStore.initAuth()
```

---

## 2. Structure `services/frontend/src/`

```text
src/
├── theme/                  # Design token system
│   ├── tokens.ts           # Agrégation racine
│   ├── colors.ts           # Sunset Mystique
│   ├── glass.ts            # Liquidglass
│   ├── motion.ts           # Durées & easing
│   ├── oracle.ts           # Moods Oracle UI
│   ├── teams.ts            # Pont teamRegistry
│   ├── applyTheme.ts       # Injection CSS vars
│   └── index.ts
├── data/teamRegistry.ts    # 18 clubs Ligue 1 typés
├── types/team.ts           # Ligue1Team, TeamColors
├── utils/
│   ├── teamLogos.ts        # Cache + preload logos
│   └── formatApiError.ts
├── api/
│   ├── axios.ts
│   └── ragStream.ts        # SSE Oracle
├── stores/auth.ts
├── views/                  # Pages (voir routes)
├── components/
│   ├── rag/RagEntity.vue
│   ├── prediction/NeuralCore.vue
│   ├── dashboard/MatchCard.vue
│   └── ui/TeamGlow.vue     # branche team-colors
└── router/index.ts
```

---

## 3. Design token system (`src/theme/`)

Source unique pour cohérence visuelle, maintenance et scalabilité.

### Fichiers

| Fichier | Contenu |
|---------|---------|
| `colors.ts` | `bg`, `brand`, `semantic`, `text` |
| `glass.ts` | opacités, blur, bordures, gradients |
| `motion.ts` | `duration`, `easing`, `stagger` |
| `oracle.ts` | `oracleMoods` (stable/risky/uncertain/glitch) |
| `teams.ts` | réexport `getTeamColors`, `resolveLigue1Team` |
| `tokens.ts` | `export const tokens = { colors, glass, motion, oracle }` |
| `applyTheme.ts` | `applyDesignTokens()` → `--color-*`, `--glass-*`, `--oracle-*` |

### Variables CSS injectées

```css
:root {
  --color-bg-deep: #010108;
  --color-brand-primary: #7232f2;
  --glass-blur-md: 20px;
  --motion-duration-normal: 400ms;
  --oracle-stable-primary: #22d3ee;
  --oracle-stable-glow: rgba(34, 211, 238, 0.35);
}
```

### Usage dans les composants

```typescript
import { tokens, oracleMoods } from '@/theme'
import { glass } from '@/theme/glass'
```

Préférer les variables CSS en SCSS/Tailwind custom plutôt que des couleurs hardcodées.

---

## 4. Registre équipes & logos

### `Ligue1Team` (`types/team.ts`)

```typescript
type Ligue1Team = {
  id: string
  canonicalName: string
  shortName: string
  aliases: string[]
  logo: string
  colors: { primary, secondary, accent? }
}
```

### `teamLogos.ts`

| API | Description |
|-----|-------------|
| `logoCache` | Map mémoire |
| `preloadTeamLogos()` | `new Image()` au boot |
| `hydrateStandingsLogos()` | GET `/standings` unique |
| `resolveTeamLogo(name, apiLogo?)` | cache → API → LFP → local |

---

## 5. Système visuel contextuel par club

**Branche** : `feature/team-colors-visual-system`

| Module | Rôle |
|--------|------|
| `utils/teamVisuals.ts` | `getTeamVisuals`, `getOracleAccent`, `detectTeamInText` |
| `components/ui/TeamGlow.vue` | Anneau logo avec glow club |
| Vues branchées | History, Prediction, MatchCard, RagEntity |

Exemples de rendu :

| Club | Primary | Usage |
|------|---------|-------|
| PSG | `#004170` | Panneau domicile, glow Oracle si question PSG |
| OM | `#009FE3` | Cyan glow Marseille |
| Lens | `#D2001F` | Rouge/orange |
| Monaco | `#E2001A` | Rouge profond |

Fusion mood + équipe : `blendTeamWithMood(teamName, mood)`.

---

## 6. Routes & pages

| Route | Vue | Auth |
|-------|-----|------|
| `/` | HomeView | — |
| `/login`, `/register` | Auth | — |
| `/dashboard` | DashboardView | ✅ |
| `/prediction` | PredictionView + NeuralCore | ✅ |
| `/history` | HistoryView | ✅ |
| `/rag` | RagView + RagEntity | ✅ |
| `/profile` | ProfileView | ✅ |
| `/ai-insights` | AIInsightsView (MLOps) | ✅ |

---

## 7. Intégration Oracle (SSE)

Client : `api/ragStream.ts` → `POST /insights/question/stream`

```typescript
await streamRagQuestion(question, {
  onMeta: (meta) => { mood, confidence, conversation_id },
  onToken: (payload) => { append text },
  onDone: (payload) => { finalize },
  onError: (err) => { ... },
}, conversationId)
```

`RagEntity.vue` : états `idle | listening | generating | responding` + classes `--mood-*`.

---

## 8. Auth & erreurs

- JWT `localStorage.access_token`
- Intercepteur 401 : redirect seulement si session active hors `/login` `/register`
- `formatApiError()` : messages API, réseau, validation FastAPI

---

## 9. Branches fonctionnelles

Toutes les branches de fonctionnalités ont été fusionnées et consolidées de manière transparente dans la branche maîtresse de design/intégration **`feature/design-tokens`**, qui est actuellement la branche la plus à jour et complète du projet.

| Branche | Feature | Statut |
|---------|---------|--------|
| `feature/rag-streaming-memory` | RAG SSE, mémoire, mood engine | ✅ Fusionné |
| `feature/team-colors-visual-system` | Glows dynamiques par club | ✅ Fusionné |
| `feature/pgvector-semantic-rag` | Embeddings 768D + pgvector (backend) | ✅ Fusionné |
| `feature/design-tokens` | `src/theme/` design system + intégration complète | 🏆 **Branche de référence** |

---

## 10. Dev & Docker

```bash
# Dev (HMR)
cd services/frontend && npm run dev

# Type-check
npm run type-check

# Prod Docker
docker compose build frontend && docker compose up -d frontend
```

`VITE_API_URL` → `http://localhost:8002` (défaut).

---

## 11. Documentation liée

- [`design.md`](./design.md) — stratégie produit & DA
- [`FRONTEND-PLAN.md`](./FRONTEND-PLAN.md) — roadmap UX
- [`rag-implementation.md`](./rag-implementation.md) — Oracle backend
- [`backend-implementation.md`](./backend-implementation.md) — App API
