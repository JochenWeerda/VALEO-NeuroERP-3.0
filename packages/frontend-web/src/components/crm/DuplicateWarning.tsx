import { AlertTriangle, ExternalLink, Loader2, Users } from 'lucide-react'
import { Link } from '@/app/routing/typed-router'
import { type DuplicateCandidate } from '@/hooks/useDuplicateDetection'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface DuplicateWarningProps {
  candidates: DuplicateCandidate[]
  isChecking?: boolean
  onSelect?: (candidate: DuplicateCandidate) => void
  onIgnore?: () => void
  className?: string
}

export function DuplicateWarning({
  candidates,
  isChecking = false,
  onSelect,
  onIgnore,
  className,
}: DuplicateWarningProps) {
  if (isChecking) {
    return (
      <Alert className={cn('border-blue-200 bg-blue-50', className)}>
        <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
        <AlertTitle className="text-blue-800">Duplikat-Prüfung...</AlertTitle>
        <AlertDescription className="text-blue-700">
          Suche nach möglichen Duplikaten im System.
        </AlertDescription>
      </Alert>
    )
  }

  if (candidates.length === 0) {
    return null
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.9) return 'error'
    if (score >= 0.8) return 'warning'
    return 'warning'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 0.9) return 'Sehr hoch'
    if (score >= 0.8) return 'Hoch'
    return 'Möglich'
  }

  return (
    <Alert
      variant="destructive"
      className={cn('warning', className)}
    >
      <AlertTriangle className="h-4 w-4 text-status-warning" />
      <AlertTitle className="text-status-warning flex items-center gap-2">
        Mögliche Duplikate gefunden
        <Badge variant="secondary" className="text-xs">
          {candidates.length} {candidates.length === 1 ? 'Eintrag' : 'Einträge'}
        </Badge>
      </AlertTitle>
      <AlertDescription className="mt-3">
        <div className="space-y-2">
          {candidates.map((candidate) => (
            <div
              key={candidate.id}
              className='warning'
            >
              <div className="flex items-center gap-3">
                <Users className="h-5 w-5 text-status-warning" />
                <div>
                  <div className='muted'>{candidate.name}</div>
                  <div className='muted'>
                    {candidate.email && <span>{candidate.email}</span>}
                    {candidate.phone && <span>{candidate.phone}</span>}
                  </div>
                  <div className="flex gap-1 mt-1">
                    {candidate.matchFields.map((field) => (
                      <Badge key={field} variant="outline" className="text-xs">
                        {field}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={getScoreColor(candidate.matchScore)}>
                  {getScoreLabel(candidate.matchScore)} (
                  {Math.round(candidate.matchScore * 100)}%)
                </Badge>
                {onSelect && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onSelect(candidate)}
                  >
                    Auswählen
                  </Button>
                )}
                <Link to={`/crm/customers/${candidate.id}`}>
                  <Button variant="ghost" size="sm">
                    <ExternalLink className="h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
          ))}
        </div>

        {onIgnore && (
          <div className="mt-4 flex justify-end">
            <Button variant="outline" size="sm" onClick={onIgnore}>
              Warnung ignorieren und fortfahren
            </Button>
          </div>
        )}
      </AlertDescription>
    </Alert>
  )
}
