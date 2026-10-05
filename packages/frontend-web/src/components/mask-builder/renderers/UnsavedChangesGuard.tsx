import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { useUnsavedChanges } from '@/hooks/useUnsavedChanges'

/**
 * Mount only while the form is dirty: the router blocker also arms the
 * browser's beforeunload prompt, which must not fire for a clean mask.
 * Saving is not offered here because a failed save would still let the
 * navigation continue.
 */
export function UnsavedChangesGuard(): JSX.Element | null {
  const blocker = useUnsavedChanges(true)
  if (blocker.state !== 'blocked') return null

  return (
    <AlertDialog open onOpenChange={(open) => { if (!open) blocker.reset?.() }}>
      <AlertDialogContent data-testid="unsaved-changes-dialog">
        <AlertDialogHeader>
          <AlertDialogTitle>Ungespeicherte Änderungen</AlertDialogTitle>
          <AlertDialogDescription>
            Wenn Sie die Maske jetzt verlassen, gehen Ihre Änderungen verloren.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={() => blocker.reset?.()}>Zurück zur Maske</AlertDialogCancel>
          <AlertDialogAction onClick={() => blocker.proceed?.()}>Änderungen verwerfen</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
