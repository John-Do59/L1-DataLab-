const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8002'

export type EntityMood = 'stable' | 'risky' | 'uncertain' | 'glitch'

export interface RagStreamMeta {
  conversation_id: number
  mood: EntityMood
  confidence: number
  sources?: string[]
  model?: string
}

export interface RagStreamDone extends RagStreamMeta {
  answer: string
}

export interface RagStreamHandlers {
  onMeta: (meta: RagStreamMeta) => void
  onToken: (payload: { t: string; full: string; mood?: EntityMood }) => void
  onDone: (payload: RagStreamDone) => void
  onError: (error: Error) => void
}

function parseSseBlock(block: string): { event: string; data: string } | null {
  let event = 'message'
  let data = ''
  for (const line of block.split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim()
    if (line.startsWith('data:')) data += line.slice(5).trim()
  }
  if (!data) return null
  return { event, data }
}

export async function streamRagQuestion(
  question: string,
  handlers: RagStreamHandlers,
  conversationId?: number | null
): Promise<void> {
  const token = localStorage.getItem('access_token')
  const res = await fetch(`${API_BASE}/insights/question/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      question,
      conversation_id: conversationId ?? undefined,
    }),
  })

  if (!res.ok) {
    handlers.onError(new Error(`Stream failed: ${res.status}`))
    return
  }

  const reader = res.body?.getReader()
  if (!reader) {
    handlers.onError(new Error('No response body'))
    return
  }

  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split('\n\n')
      buffer = parts.pop() || ''
      for (const part of parts) {
        const parsed = parseSseBlock(part)
        if (!parsed) continue
        const payload = JSON.parse(parsed.data)
        if (parsed.event === 'meta') handlers.onMeta(payload)
        else if (parsed.event === 'token') handlers.onToken(payload)
        else if (parsed.event === 'done') handlers.onDone(payload)
      }
    }
  } catch (e) {
    handlers.onError(e instanceof Error ? e : new Error(String(e)))
  }
}
