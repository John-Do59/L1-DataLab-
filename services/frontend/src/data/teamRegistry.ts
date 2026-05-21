import type { Ligue1Team } from '../types/team'

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

export const LIGUE1_TEAMS: readonly Ligue1Team[] = [
  {
    id: 'angers',
    canonicalName: 'Angers SCO',
    shortName: 'Angers',
    aliases: ['angers sco', 'angers', 'sco angers'],
    logo: angersscoLogo,
    colors: { primary: '#000000', secondary: '#FFFFFF', accent: '#C9A227' },
  },
  {
    id: 'auxerre',
    canonicalName: 'AJ Auxerre',
    shortName: 'Auxerre',
    aliases: ['aj auxerre', 'auxerre', 'aja'],
    logo: ajauxerreLogo,
    colors: { primary: '#0033A0', secondary: '#FFFFFF' },
  },
  {
    id: 'brest',
    canonicalName: 'Stade Brestois 29',
    shortName: 'Brest',
    aliases: ['stade brestois', 'stade brestois 29', 'brest', 'sb29'],
    logo: stadebrestoisLogo,
    colors: { primary: '#D2001F', secondary: '#FFFFFF' },
  },
  {
    id: 'le-havre',
    canonicalName: 'Le Havre AC',
    shortName: 'Le Havre',
    aliases: ['le havre ac', 'le havre', 'havre', 'hac'],
    logo: lehavreacLogo,
    colors: { primary: '#009FE3', secondary: '#75B2DD' },
  },
  {
    id: 'lens',
    canonicalName: 'RC Lens',
    shortName: 'Lens',
    aliases: ['rc lens', 'lens', 'rcl'],
    logo: rclensLogo,
    colors: { primary: '#D2001F', secondary: '#FFDD00' },
  },
  {
    id: 'lille',
    canonicalName: 'LOSC Lille',
    shortName: 'Lille',
    aliases: ['losc lille', 'losc', 'lille'],
    logo: losclilleLogo,
    colors: { primary: '#E2001A', secondary: '#1A2B4C' },
  },
  {
    id: 'lorient',
    canonicalName: 'FC Lorient',
    shortName: 'Lorient',
    aliases: ['fc lorient', 'lorient', 'fcl'],
    logo: fclorientLogo,
    colors: { primary: '#F5811B', secondary: '#000000' },
  },
  {
    id: 'lyon',
    canonicalName: 'Olympique Lyonnais',
    shortName: 'Lyon',
    aliases: ['olympique lyonnais', 'lyon', 'ol', 'olympique lyon'],
    logo: olympiquelyonnaisLogo,
    colors: { primary: '#0033A0', secondary: '#FFFFFF', accent: '#D2001F' },
  },
  {
    id: 'marseille',
    canonicalName: 'Olympique de Marseille',
    shortName: 'Marseille',
    aliases: ['olympique de marseille', 'marseille', 'om', 'olympique marseille'],
    logo: olympiquedemarseilleLogo,
    colors: { primary: '#009FE3', secondary: '#FFFFFF' },
  },
  {
    id: 'metz',
    canonicalName: 'FC Metz',
    shortName: 'Metz',
    aliases: ['fc metz', 'metz', 'fcm'],
    logo: fcmetzLogo,
    colors: { primary: '#6A0032', secondary: '#FFFFFF' },
  },
  {
    id: 'monaco',
    canonicalName: 'AS Monaco FC',
    shortName: 'Monaco',
    aliases: ['as monaco', 'as monaco fc', 'monaco', 'asm'],
    logo: asmonacofcLogo,
    colors: { primary: '#E2001A', secondary: '#FFFFFF' },
  },
  {
    id: 'nantes',
    canonicalName: 'FC Nantes',
    shortName: 'Nantes',
    aliases: ['fc nantes', 'nantes', 'fcn'],
    logo: fcnantesLogo,
    colors: { primary: '#FFDD00', secondary: '#009B3A' },
  },
  {
    id: 'nice',
    canonicalName: 'OGC Nice',
    shortName: 'Nice',
    aliases: ['ogc nice', 'nice', 'ogcn'],
    logo: ogcniceLogo,
    colors: { primary: '#D2001F', secondary: '#000000' },
  },
  {
    id: 'paris-fc',
    canonicalName: 'Paris FC',
    shortName: 'Paris FC',
    aliases: ['paris fc', 'pfc'],
    logo: parisfcLogo,
    colors: { primary: '#0033A0', secondary: '#D2001F' },
  },
  {
    id: 'psg',
    canonicalName: 'Paris Saint-Germain',
    shortName: 'PSG',
    aliases: ['paris saint-germain', 'paris sg', 'psg', 'paris saint germain'],
    logo: parissaintgermainLogo,
    colors: { primary: '#004170', secondary: '#DA291C', accent: '#C7A46A' },
  },
  {
    id: 'rennes',
    canonicalName: 'Stade Rennais FC',
    shortName: 'Rennes',
    aliases: ['stade rennais', 'stade rennais fc', 'rennes', 'srfc'],
    logo: staderennaisfcLogo,
    colors: { primary: '#D2001F', secondary: '#000000' },
  },
  {
    id: 'toulouse',
    canonicalName: 'Toulouse FC',
    shortName: 'Toulouse',
    aliases: ['toulouse fc', 'toulouse', 'tfc'],
    logo: toulousefcLogo,
    colors: { primary: '#582C83', secondary: '#FFFFFF' },
  },
  {
    id: 'strasbourg',
    canonicalName: 'RC Strasbourg Alsace',
    shortName: 'Strasbourg',
    aliases: ['rc strasbourg', 'rc strasbourg alsace', 'strasbourg', 'rcsa'],
    logo: rcstrasbourgalsaceLogo,
    colors: { primary: '#009FE3', secondary: '#FFFFFF' },
  },
] as const

const aliasIndex = new Map<string, Ligue1Team>()

function normalizeName(name: string): string {
  return name
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .trim()
}

function registerAlias(key: string, team: Ligue1Team): void {
  aliasIndex.set(normalizeName(key), team)
}

for (const team of LIGUE1_TEAMS) {
  registerAlias(team.canonicalName, team)
  registerAlias(team.shortName, team)
  for (const alias of team.aliases) {
    registerAlias(alias, team)
  }
}

/** Tous les clubs du registre. */
export function getAllLigue1Teams(): readonly Ligue1Team[] {
  return LIGUE1_TEAMS
}

/** Résout un nom libre (API, LFP, alias) vers une entrée canonique. */
export function resolveLigue1Team(name: string): Ligue1Team | undefined {
  return aliasIndex.get(normalizeName(name))
}

/** Couleurs de marque pour glows / mood engine. */
export function getTeamColors(name: string) {
  return resolveLigue1Team(name)?.colors
}
