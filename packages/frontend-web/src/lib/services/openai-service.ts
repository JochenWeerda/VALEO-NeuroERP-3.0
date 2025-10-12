/**
 * OpenAI Service for Ask VALEO
 * Direct OpenAI integration (Quick Win - ohne MCP-Server)
 */

import OpenAI from 'openai'

const API_KEY = import.meta.env.VITE_OPENAI_API_KEY || ''

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: API_KEY,
  dangerouslyAllowBrowser: true, // For development - in production use backend proxy
})

export type VALEOMessage = {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export type VALEOContext = {
  currentPage?: string
  userRoles?: string[]
  tenantId?: string
  recentActions?: string[]
}

/**
 * Ask VALEO - Send message to AI
 */
export async function askVALEO(
  userMessage: string,
  context?: VALEOContext,
  conversationHistory: VALEOMessage[] = []
): Promise<string> {
  if (!API_KEY) {
    return '⚠️ OpenAI API-Key nicht konfiguriert. Bitte VITE_OPENAI_API_KEY in .env setzen.'
  }

  const systemPrompt = buildSystemPrompt(context)

  const messages: VALEOMessage[] = [
    { role: 'system', content: systemPrompt },
    ...conversationHistory,
    { role: 'user', content: userMessage }
  ]

  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: messages.map((m) => ({ role: m.role, content: m.content })),
      temperature: 0.7,
      max_tokens: 1000,
    })

    const assistantMessage = response.choices[0]?.message?.content ?? 'Keine Antwort erhalten.'

    return assistantMessage
  } catch (error) {
    console.error('OpenAI API Error:', error)
    
    if (error instanceof Error) {
      return `❌ Fehler: ${error.message}`
    }
    
    return '❌ Ein unbekannter Fehler ist aufgetreten.'
  }
}

/**
 * Build system prompt with context
 */
function buildSystemPrompt(context?: VALEOContext): string {
  let prompt = `Du bist VALEO, der intelligente ERP-Assistent für VALEO NeuroERP 3.0.

Deine Aufgabe ist es, dem Benutzer bei ERP-Aufgaben zu helfen, wie:
- Kunden-Informationen finden
- Artikel-Stammdaten abrufen
- Prozesse erklären (Belegfluss, Finanzbuchungen)
- Compliance-Fragen beantworten (PSM, ENNI, TRACES)
- Workflow-Empfehlungen geben

Antworte immer auf Deutsch, präzise und hilfreich.
Wenn du nicht sicher bist, sage das ehrlich.`

  if (context?.currentPage) {
    prompt += `\n\nAktueller Kontext:\n- Seite: ${context.currentPage}`
  }

  if (context?.userRoles && context.userRoles.length > 0) {
    prompt += `\n- Benutzer-Rollen: ${context.userRoles.join(', ')}`
  }

  if (context?.tenantId) {
    prompt += `\n- Mandant: ${context.tenantId}`
  }

  return prompt
}

/**
 * Search for customers (Tool/Function calling)
 */
export async function searchCustomers(query: string): Promise<string> {
  // This would call the actual API in production
  // For now, return mock response
  return `Kunden gefunden für "${query}":
1. Schmidt GmbH (K-12345)
2. Müller Landhandel (K-12346)
3. Agrar Schmidt & Co (K-12347)

Möchtest du Details zu einem Kunden?`
}

/**
 * Get article price (Tool/Function calling)
 */
export async function getArticlePrice(articleNumber: string): Promise<string> {
  // This would call the actual API in production
  return `Artikel ${articleNumber}:
- Bezeichnung: Weizen Premium A
- Preis: 285,00 € / t
- Lagerbestand: 450 t
- EK: 265,00 € / t
- Marge: 7,5%`
}

/**
 * Check if OpenAI is configured
 */
export function isOpenAIConfigured(): boolean {
  return !!API_KEY && API_KEY.length > 0
}

