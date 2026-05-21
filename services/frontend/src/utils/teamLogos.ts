import api from '../api/axios'
import { LIGUE1_TEAMS, resolveLigue1Team } from '../data/teamRegistry'
import type { Ligue1Team } from '../types/team'

const GENERIC_LOGO_MARKERS = ['Logo_Ligue_1', 'ligue1.com/images/Logo']

/** Cache mémoire : nom normalisé → URL logo résolue. */
export const logoCache = new Map<string, string>()

const standingsLogoByName = new Map<string, string>()
const preloadedUrls = new Set<string>()

let standingsHydrated = false
let standingsHydratePromise: Promise<void> | null = null

function normalizeName(name: string): string {
  return name
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .trim()
}

function isGenericLogo(url?: string | null): boolean {
  if (!url) return true
  return GENERIC_LOGO_MARKERS.some((marker) => url.includes(marker))
}

function cacheLogoKeys(name: string, logo: string): void {
  const key = normalizeName(name)
  logoCache.set(key, logo)

  const team = resolveLigue1Team(name)
  if (team) {
    logoCache.set(normalizeName(team.canonicalName), logo)
    logoCache.set(normalizeName(team.shortName), logo)
    for (const alias of team.aliases) {
      logoCache.set(normalizeName(alias), logo)
    }
  }
}

function preloadUrl(url: string): void {
  if (!url || preloadedUrls.has(url)) return
  preloadedUrls.add(url)
  const img = new Image()
  img.src = url
}

/** Précharge tous les logos du registre au boot (perception fluide, zéro flicker). */
export function preloadTeamLogos(): void {
  for (const team of LIGUE1_TEAMS) {
    cacheLogoKeys(team.canonicalName, team.logo)
    preloadUrl(team.logo)
  }
}

/** Hydrate une seule fois les logos LFP depuis /standings. */
export function hydrateStandingsLogos(): Promise<void> {
  if (standingsHydrated) return Promise.resolve()
  if (standingsHydratePromise) return standingsHydratePromise

  standingsHydratePromise = api
    .get<Array<{ club_name?: string; name?: string; logo?: string }>>('/standings')
    .then((res) => {
      registerStandingsLogos(res.data ?? [])
      standingsHydrated = true
    })
    .catch(() => {
      standingsHydrated = true
    })
    .finally(() => {
      standingsHydratePromise = null
    })

  return standingsHydratePromise
}

/** Enregistre les logos du classement LFP (appel unique). */
export function registerStandingsLogos(
  teams: Array<{ club_name?: string; name?: string; logo?: string }>,
): void {
  for (const team of teams) {
    const name = team.club_name ?? team.name
    if (!name || !team.logo || isGenericLogo(team.logo)) continue

    const normalized = normalizeName(name)
    standingsLogoByName.set(normalized, team.logo)
    cacheLogoKeys(name, team.logo)
    preloadUrl(team.logo)

    const registryTeam = resolveLigue1Team(name)
    if (registryTeam && !logoCache.has(normalizeName(registryTeam.canonicalName))) {
      cacheLogoKeys(registryTeam.canonicalName, team.logo)
    }
  }
}

function resolveFromSources(name: string, apiLogo?: string | null): string | undefined {
  if (!isGenericLogo(apiLogo) && apiLogo) return apiLogo

  const fromStandings = standingsLogoByName.get(normalizeName(name))
  if (fromStandings) return fromStandings

  return resolveLigue1Team(name)?.logo
}

/**
 * Résout le logo d'une équipe avec cache mémoire.
 * Ordre : cache → API → standings → registre local.
 */
export function resolveTeamLogo(name: string, apiLogo?: string | null): string | undefined {
  const cacheKey = normalizeName(name)
  const cached = logoCache.get(cacheKey)
  if (cached) return cached

  const resolved = resolveFromSources(name, apiLogo)
  if (resolved) {
    cacheLogoKeys(name, resolved)
    preloadUrl(resolved)
  }
  return resolved
}

/** Lecture cache uniquement (évite recalculs dans les vues réactives). */
export function getCachedTeamLogo(name: string): string | undefined {
  return logoCache.get(normalizeName(name))
}

/** Métadonnées complètes d'équipe (RAG, mood, analytics). */
export function resolveTeamWithLogo(
  name: string,
  apiLogo?: string | null,
): (Ligue1Team & { logo: string }) | undefined {
  const team = resolveLigue1Team(name)
  const logo = resolveTeamLogo(name, apiLogo)
  if (!logo) return undefined

  if (team) return { ...team, logo }
  return {
    id: normalizeName(name).replace(/\s+/g, '-'),
    canonicalName: name,
    shortName: name,
    aliases: [name],
    logo,
    colors: { primary: '#22d3ee', secondary: '#a855f7' },
  }
}

/** Initialise logos : preload synchrone + standings async. */
export function initTeamLogoSystem(): void {
  preloadTeamLogos()
  void hydrateStandingsLogos()
}
