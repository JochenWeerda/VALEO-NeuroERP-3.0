/**
 * ArticleImage — zeigt ein Produktbild mit mehrstufigem Fallback:
 * 1. image_url aus der DB (echtes Bild)
 * 2. Kategorie-Icon (SVG) basierend auf Kategorie/Name
 * 3. Generischer Platzhalter
 */

import { useState } from 'react'

// ── Kategorie-Icons (Emoji-Mapping, wird nur als Fallback verwendet) ──────────
const CATEGORY_EMOJI: Record<string, string> = {
  // Getreide
  weizen: '🌾', gerste: '🌾', roggen: '🌾', hafer: '🌾', triticale: '🌾',
  mais: '🌽', körnermais: '🌽', silomais: '🌽',
  // Ölsaaten
  raps: '🌼', sonnenblumen: '🌻', soja: '🫘', sojabohnen: '🫘',
  // Hülsenfrüchte
  erbsen: '🫛', bohnen: '🫘', ackerbohnen: '🫘',
  // Futtermittel
  kraftfutter: '🐄', futtermittel: '🐄', stroh: '🌿', heu: '🌿',
  rinderfutter: '🐄', schweinefutter: '🐷', geflügelfutter: '🐔',
  // Düngemittel
  düngemittel: '⚗️', kalkammon: '⚗️', harnstoff: '⚗️', kalk: '⛰️',
  // Saatgut
  saatgut: '🌱', saat: '🌱',
  // Pflanzenschutz
  pflanzenschutzmittel: '🧪', herbizid: '🧪', fungizid: '🧪', insektizid: '🧪',
  // Garten / Haus
  erde: '🪴', blumenerde: '🪴', substrate: '🪴',
  // Sonstiges
  default: '📦',
}

function getCategoryEmoji(name: string, category?: string): string {
  const text = `${name} ${category ?? ''}`.toLowerCase()
  for (const [key, emoji] of Object.entries(CATEGORY_EMOJI)) {
    if (key !== 'default' && text.includes(key)) return emoji
  }
  return CATEGORY_EMOJI.default
}

// ── Komponente ────────────────────────────────────────────────────────────────

interface ArticleImageProps {
  imageUrl?: string | null
  name: string
  category?: string
  /** Tailwind size class, z.B. "h-16 w-16" */
  size?: string
  className?: string
}

export function ArticleImage({ imageUrl, name, category, size = 'h-16 w-16', className = '' }: ArticleImageProps) {
  const [imgError, setImgError] = useState(false)
  const emoji = getCategoryEmoji(name, category)

  if (imageUrl && !imgError) {
    return (
      <img
        src={imageUrl}
        alt={name}
        className={`${size} object-cover rounded-md bg-gray-50 ${className}`}
        onError={() => setImgError(true)}
        loading="lazy"
      />
    )
  }

  // Emoji-Fallback
  return (
    <div
      className={`${size} flex items-center justify-center rounded-md bg-gray-100 text-4xl select-none ${className}`}
      title={name}
      aria-label={name}
    >
      {emoji}
    </div>
  )
}

/**
 * Große Variante für das POS-Grid (Touch-optimiert)
 */
export function ArticleImageLarge({ imageUrl, name, category, className = '' }: Omit<ArticleImageProps, 'size'>) {
  return (
    <ArticleImage
      imageUrl={imageUrl}
      name={name}
      category={category}
      size="h-24 w-full"
      className={`rounded-t-md ${className}`}
    />
  )
}

/**
 * Kleine Variante für den Warenkorb
 */
export function ArticleImageSmall({ imageUrl, name, category, className = '' }: Omit<ArticleImageProps, 'size'>) {
  return (
    <ArticleImage
      imageUrl={imageUrl}
      name={name}
      category={category}
      size="h-12 w-12"
      className={className}
    />
  )
}
