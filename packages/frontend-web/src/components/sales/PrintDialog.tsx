import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'

type PrintDialogProps = {
  open: boolean
  onClose: () => void
  onConfirm: (printer: string, template: string) => void
}

export function PrintDialog({ open, onClose, onConfirm }: PrintDialogProps): JSX.Element {
  const [printer, setPrinter] = useState('')
  const [template, setTemplate] = useState('')

  const handleConfirm = (): void => {
    if (printer && template) {
      onConfirm(printer, template)
      setPrinter('')
      setTemplate('')
      onClose()
    }
  }

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Lieferschein drucken</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="printer">Drucker:</Label>
            <select
              id="printer"
              className="w-full rounded-md border border-input bg-background px-3 py-2"
              value={printer}
              onChange={(e) => setPrinter(e.target.value)}
            >
              <option value="">Bitte wählen</option>
              <option value="default">Standard-Drucker</option>
              <option value="printer1">Drucker 1</option>
              <option value="printer2">Drucker 2</option>
            </select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="template">Formularvorlage:</Label>
            <select
              id="template"
              className="w-full rounded-md border border-input bg-background px-3 py-2"
              value={template}
              onChange={(e) => setTemplate(e.target.value)}
            >
              <option value="">Bitte wählen</option>
              <option value="standard">Standard-Lieferschein</option>
              <option value="detailed">Detaillierter Lieferschein</option>
              <option value="compact">Kompakter Lieferschein</option>
            </select>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Abbrechen
          </Button>
          <Button onClick={handleConfirm} disabled={!printer || !template}>
            OK
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}


