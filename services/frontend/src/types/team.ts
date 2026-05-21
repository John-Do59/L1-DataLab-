/** Palette de marque d'un club (RAG, mood engine, glows dynamiques). */
export type TeamColors = {
  primary: string
  secondary: string
  accent?: string
}

/** Entrée canonique du registre Ligue 1. */
export type Ligue1Team = {
  /** Slug stable (ex. `psg`, `om`). */
  id: string
  canonicalName: string
  shortName: string
  aliases: string[]
  logo: string
  colors: TeamColors
}

/** Équipe enrichie après résolution (logo cache + registre). */
export type ResolvedTeam = Ligue1Team & {
  logo: string
  resolvedFrom: 'cache' | 'api' | 'standings' | 'registry'
}
