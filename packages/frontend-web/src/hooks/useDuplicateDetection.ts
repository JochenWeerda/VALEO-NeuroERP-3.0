import { useCallback, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { authenticatedFetch } from '@/lib/fetch'

export interface DuplicateCandidate {
  id: string
  name: string
  email?: string
  phone?: string
  matchScore: number
  matchFields: string[]
}

interface DuplicateCheckInput {
  name?: string
  email?: string
  phone?: string
  company?: string
}

// Levenshtein distance for fuzzy matching
function levenshtein(a: string, b: string): number {
  const matrix: number[][] = []

  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i]
  }
  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j
  }

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1]
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        )
      }
    }
  }

  return matrix[b.length][a.length]
}

// Calculate similarity (0-1)
function similarity(a: string, b: string): number {
  if (!a || !b) return 0
  const normalizedA = a.toLowerCase().trim()
  const normalizedB = b.toLowerCase().trim()
  if (normalizedA === normalizedB) return 1

  const maxLen = Math.max(normalizedA.length, normalizedB.length)
  if (maxLen === 0) return 1

  const distance = levenshtein(normalizedA, normalizedB)
  return 1 - distance / maxLen
}

// Normalize phone number for comparison
function normalizePhone(phone: string): string {
  return phone.replace(/[\s\-\(\)\.\/]/g, '').replace(/^(\+49|0049|0)/, '')
}

// Normalize email for comparison
function normalizeEmail(email: string): string {
  return email.toLowerCase().trim()
}

interface UseDuplicateDetectionOptions {
  threshold?: number
  enabled?: boolean
}

export function useDuplicateDetection(options: UseDuplicateDetectionOptions = {}) {
  const { threshold = 0.7, enabled = true } = options
  const [input, setInput] = useState<DuplicateCheckInput>({})
  const [isChecking, setIsChecking] = useState(false)

  // Fetch existing customers for comparison
  const { data: customers } = useQuery({
    queryKey: ['customers-for-duplicate-check'],
    queryFn: async () => {
      try {
        const response = await authenticatedFetch('/api/v1/crm/customers?limit=1000')
        const result = await response.json()
        return result.data || result.items || []
      } catch {
        return []
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled,
  })

  const checkDuplicates = useCallback(
    (data: DuplicateCheckInput): DuplicateCandidate[] => {
      if (!customers || !enabled) return []

      const candidates: DuplicateCandidate[] = []

      for (const customer of customers) {
        const matchFields: string[] = []
        let totalScore = 0
        let fieldCount = 0

        // Check name similarity
        if (data.name && customer.name) {
          const nameScore = similarity(data.name, customer.name)
          if (nameScore >= threshold) {
            matchFields.push('Name')
            totalScore += nameScore
          }
          fieldCount++
        }

        // Check company similarity
        if (data.company && customer.company) {
          const companyScore = similarity(data.company, customer.company)
          if (companyScore >= threshold) {
            matchFields.push('Firma')
            totalScore += companyScore
          }
          fieldCount++
        }

        // Check email (exact match after normalization)
        if (data.email && customer.email) {
          const emailA = normalizeEmail(data.email)
          const emailB = normalizeEmail(customer.email)
          if (emailA === emailB) {
            matchFields.push('E-Mail')
            totalScore += 1
          }
          fieldCount++
        }

        // Check phone (exact match after normalization)
        if (data.phone && customer.phone) {
          const phoneA = normalizePhone(data.phone)
          const phoneB = normalizePhone(customer.phone)
          if (phoneA === phoneB || phoneA.endsWith(phoneB) || phoneB.endsWith(phoneA)) {
            matchFields.push('Telefon')
            totalScore += 1
          }
          fieldCount++
        }

        if (matchFields.length > 0) {
          const avgScore = totalScore / Math.max(fieldCount, 1)
          candidates.push({
            id: customer.id,
            name: customer.name || customer.company || 'Unbekannt',
            email: customer.email,
            phone: customer.phone,
            matchScore: avgScore,
            matchFields,
          })
        }
      }

      // Sort by match score (highest first)
      return candidates.sort((a, b) => b.matchScore - a.matchScore).slice(0, 5)
    },
    [customers, threshold, enabled]
  )

  const performCheck = useCallback(
    async (data: DuplicateCheckInput): Promise<DuplicateCandidate[]> => {
      setIsChecking(true)
      setInput(data)

      // Small delay for UX
      await new Promise((resolve) => setTimeout(resolve, 200))

      const result = checkDuplicates(data)
      setIsChecking(false)
      return result
    },
    [checkDuplicates]
  )

  return {
    checkDuplicates: performCheck,
    isChecking,
    lastInput: input,
  }
}
