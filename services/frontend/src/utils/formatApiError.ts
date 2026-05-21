import type { AxiosError } from 'axios'

type ValidationError = { msg?: string; loc?: (string | number)[] }

function formatValidationDetail(detail: ValidationError[]): string {
  return detail
    .map((e) => {
      const field = e.loc?.filter((x) => x !== 'body').pop()
      const label = field != null ? String(field) : 'champ'
      return e.msg ? `${label} : ${e.msg}` : 'Données invalides.'
    })
    .join(' ')
}

/** Message lisible à partir d'une erreur API (axios ou réseau). */
export function formatApiError(err: unknown, fallback: string): string {
  const axiosErr = err as AxiosError<{ detail?: string | ValidationError[] }>

  if (!axiosErr.response) {
    return "Impossible de joindre l'API. Démarrez les services avec : docker compose up -d"
  }

  const detail = axiosErr.response.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    return formatValidationDetail(detail)
  }

  return fallback
}
