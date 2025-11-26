/**
 * Generische Zurück-Button-Komponente
 * Automatische Navigation zurück zur vorherigen Seite oder explizite Route
 */

import { useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface BackButtonProps {
  /**
   * Explizite Ziel-Route (optional)
   * Falls nicht angegeben, wird history.back() verwendet
   */
  to?: string
  
  /**
   * Label für den Button (optional)
   */
  label?: string
  
  /**
   * Variante (default: 'outline')
   */
  variant?: 'default' | 'outline' | 'ghost' | 'link'
  
  /**
   * Größe (default: 'default')
   */
  size?: 'default' | 'sm' | 'lg' | 'icon'
  
  /**
   * Zusätzliche CSS-Klassen
   */
  className?: string
}

export function BackButton({
  to,
  label = 'Zurück',
  variant = 'outline',
  size = 'default',
  className = '',
}: BackButtonProps) {
  const navigate = useNavigate()

  const handleClick = () => {
    if (to) {
      navigate(to)
    } else {
      navigate(-1)
    }
  }

  return (
    <Button
      variant={variant}
      size={size}
      onClick={handleClick}
      className={className}
      data-testid="back-button"
    >
      <ArrowLeft className="mr-2 h-4 w-4" />
      {label}
    </Button>
  )
}

/**
 * Kompakte Variante (nur Icon)
 */
export function BackButtonIcon({
  to,
  className = '',
}: Pick<BackButtonProps, 'to' | 'className'>) {
  const navigate = useNavigate()

  const handleClick = () => {
    if (to) {
      navigate(to)
    } else {
      navigate(-1)
    }
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={handleClick}
      className={className}
      data-testid="back-button-icon"
      aria-label="Zurück"
    >
      <ArrowLeft className="h-5 w-5" />
    </Button>
  )
}

