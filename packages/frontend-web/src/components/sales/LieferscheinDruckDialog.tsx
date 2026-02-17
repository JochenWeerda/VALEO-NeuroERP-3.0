/**
 * Lieferschein-Druckdialog
 * 1:1 Nachbau der zvoove Druck-Dialog-Maske
 */

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
import { Checkbox } from '@/components/ui/checkbox'
import { MoreHorizontal } from 'lucide-react'

type LieferscheinDruckDialogProps = {
  open: boolean
  onClose: () => void
  onConfirm: (printer: string, template: string) => void
}

export function LieferscheinDruckDialog({
  open,
  onClose,
  onConfirm,
}: LieferscheinDruckDialogProps): JSX.Element {
  const [werbetext, setWerbetext] = useState('')
  const [anzahlDrucke, setAnzahlDrucke] = useState(1)
  const [sortierung, setSortierung] = useState('pos-nr')
  const [druckLieferschein, setDruckLieferschein] = useState(true)
  const [druckAllgemeineAngaben, setDruckAllgemeineAngaben] = useState(false)
  const [druckWegbeschreibung, setDruckWegbeschreibung] = useState(false)
  const [druckLadeInformation, setDruckLadeInformation] = useState(false)
  const [ausgeliefertUndFrei, setAusgeliefertUndFrei] = useState(false)
  const [geschaeftspapierVorschau, setGeschaeftspapierVorschau] = useState(false)
  const [aktuellerDrucker, setAktuellerDrucker] = useState('Standard-Drucker')

  const handleConfirm = (): void => {
    // Hier würde die Drucker- und Template-Auswahl erfolgen
    // Für jetzt verwenden wir Standard-Werte
    onConfirm(aktuellerDrucker, 'standard')
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-auto">
        <DialogHeader>
          <DialogTitle>LIEFERSCHEIN DRUCKEN</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="werbetext">W00005:</Label>
              <div className="flex gap-2">
                <Input id="werbetext" value={werbetext} onChange={(e) => setWerbetext(e.target.value)} />
                <Button variant="ghost" size="sm">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="werbetext2">Werbetext:</Label>
              <div className="flex gap-2">
                <Input value={werbetext} onChange={(e) => setWerbetext(e.target.value)} />
                <Button variant="ghost" size="sm">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="anzahl-drucke">Anzahl Drucke:</Label>
              <Input
                id="anzahl-drucke"
                type="number"
                min="1"
                value={anzahlDrucke}
                onChange={(e) => setAnzahlDrucke(Number(e.target.value))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sortierung">Sortierung:</Label>
              <select
                id="sortierung"
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                value={sortierung}
                onChange={(e) => setSortierung(e.target.value)}
              >
                <option value="pos-nr">Pos.-Nr.</option>
                <option value="artikel-nr">Artikel-Nr.</option>
                <option value="bezeichnung">Bezeichnung</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Druck-Optionen:</Label>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="druck-lieferschein"
                    checked={druckLieferschein}
                    onCheckedChange={(checked) => setDruckLieferschein(checked === true)}
                  />
                  <Label htmlFor="druck-lieferschein" className="text-sm font-normal cursor-pointer">
                    Druck Lieferschein
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="druck-allgemeine-angaben"
                    checked={druckAllgemeineAngaben}
                    onCheckedChange={(checked) => setDruckAllgemeineAngaben(checked === true)}
                  />
                  <Label htmlFor="druck-allgemeine-angaben" className="text-sm font-normal cursor-pointer">
                    Druck Allgemeine Angaben
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="druck-wegbeschreibung"
                    checked={druckWegbeschreibung}
                    onCheckedChange={(checked) => setDruckWegbeschreibung(checked === true)}
                  />
                  <Label htmlFor="druck-wegbeschreibung" className="text-sm font-normal cursor-pointer">
                    Druck Wegbeschreibung
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="druck-lade-information"
                    checked={druckLadeInformation}
                    onCheckedChange={(checked) => setDruckLadeInformation(checked === true)}
                  />
                  <Label htmlFor="druck-lade-information" className="text-sm font-normal cursor-pointer">
                    Druck Lade-Information
                  </Label>
                </div>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Weitere Optionen:</Label>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="ausgeliefert-frei"
                    checked={ausgeliefertUndFrei}
                    onCheckedChange={(checked) => setAusgeliefertUndFrei(checked === true)}
                  />
                  <Label htmlFor="ausgeliefert-frei" className="text-sm font-normal cursor-pointer">
                    ausgeliefert und frei zur Faktur
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="geschaeftspapier-vorschau"
                    checked={geschaeftspapierVorschau}
                    onCheckedChange={(checked) => setGeschaeftspapierVorschau(checked === true)}
                  />
                  <Label htmlFor="geschaeftspapier-vorschau" className="text-sm font-normal cursor-pointer">
                    Geschäftspapier in Vorschau
                  </Label>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Aktueller Drucker:</Label>
            <div className="flex items-center gap-2">
              <Input value={aktuellerDrucker} readOnly />
              <Button variant="outline" size="sm">
                Drucker einrichten
              </Button>
            </div>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              Drucken
            </Button>
            <Button variant="outline" size="sm">
              Vorschau
            </Button>
            <Button variant="outline" size="sm">
              E-Mail
            </Button>
            <Button variant="outline" size="sm">
              Dokumente
            </Button>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Druck nicht OK - abbrechen
          </Button>
          <Button onClick={handleConfirm}>
            Druck OK - beenden
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}


