import { useState } from 'react'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'
import { Button } from '@/components/ui/button'
import { NativeSelect } from '@/components/ui/native-select'
import { useToast } from '@/hooks/use-toast'
import { useTouchDevice } from '@/hooks/useTouchDevice'

type FreightDocumentRole = 'versand' | 'disposition' | 'it' | 'leitung'

const freightDocumentRoles = [
  { id: 'versand', label: 'Versand', description: 'Prueft Lieferschein, Dokumentart, Drucker und Vorschau, bevor die Ware rausgeht.' },
  { id: 'disposition', label: 'Disposition', description: 'Klaert, ob Frachtbrief, Fahrer und Tour trotz Druckfehler weiterlaufen koennen.' },
  { id: 'it', label: 'IT', description: 'Bearbeitet technische Stopper wie fehlende Vorschaupfade oder Druckerprobleme.' },
  { id: 'leitung', label: 'Leitung', description: 'Sieht, ob Versand oder Dokumentnachweis blockiert ist.' },
] satisfies Array<{ id: FreightDocumentRole; label: string; description: string }>

export default function FrachtDokuPage(): JSX.Element {
  const [roleFocus, setRoleFocus] = useState<FreightDocumentRole>('versand')
  const isTouch = useTouchDevice()
  const { toast } = useToast()
  const hasPrintStopper = true
  const documentOptions = [{ value: 'CMR', label: 'CMR' }]

  const handlePrintUnavailable = (action: string) => {
    toast({
      title: `${action} nicht angebunden`,
      description: 'Der Druckdienst hat keinen MCP-/API-Vertrag. Der Vorschaupfad bleibt ein technischer Stopper.',
      variant: 'destructive',
    })
  }

  return (
    <div className="min-h-full space-y-4 bg-background p-3 text-foreground md:p-6">
      <div>
        <h1 className="text-2xl font-bold md:text-3xl">Frachtdokumente drucken</h1>
        <p className="text-muted-foreground">Lieferschein 2601092, Dokument CMR — Druckpfad klaeren</p>
      </div>
      {!isTouch ? (
      <div className="mx-auto mb-6 max-w-6xl space-y-4">
        <RoleFocusBar roles={freightDocumentRoles} value={roleFocus} onChange={setRoleFocus} title="Wer klaert den Frachtdokument-Stopper?" />
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
          <ManagementDecisionPanel
            decision={{
              allowed: !hasPrintStopper,
              allowedLabel: 'Dokumentdruck bereit',
              blockedLabel: 'Druck blockiert',
              summary:
                'Der CMR-Druck ist aktuell blockiert, weil der Vorschaupfad nicht erstellt werden kann. Ohne Ersatznachweis oder technischen Fix darf der Versand nicht stillschweigend abgeschlossen werden.',
              blockerCount: 1,
              nextFocus: 'Preview-Pfad und Druckvorlage pruefen',
              template: { label: 'Frachtdokument-Fehlerprotokoll', href: '/docs/logistik/frachtdokument-fehlerprotokoll.md' },
            }}
          />
          <div className="space-y-4">
            <NextActionPanel action="IT prueft den Vorschaupfad, Versand haelt den Lieferschein offen und dokumentiert, ob ein Ersatzdruck noetig ist." tone="red" />
            <EvidenceTemplateLink link={{ label: 'Frachtbrief- und Drucknachweis', href: '/docs/logistik/frachtbrief-drucknachweis.md' }} />
          </div>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <OperationalTaskPlan
            title="Pruefplan bei Frachtdokument-Fehler"
            items={[
              { label: 'Lieferschein pruefen', done: true, hint: 'Lieferschein 2601092 ist der betroffene Versandvorgang.' },
              { label: 'Dokumentart pruefen', done: true, hint: 'CMR ist als Frachtdokument ausgewaehlt.' },
              { label: 'Druckpfad klaeren', done: false, hint: 'Preview-Pfad kann nicht erstellt werden und blockiert den Druck.' },
              { label: 'Ersatznachweis entscheiden', done: false, hint: 'Bei dringendem Versand muss ein freigegebener Ersatzdruck dokumentiert werden.' },
            ]}
          />
          <CrudCapabilityChecklist
            capabilities={[
              { key: 'read', label: 'Versandvorgang lesen', available: true, hint: 'Lieferschein, Kunde, Formular und Drucker sind sichtbar.' },
              { key: 'update', label: 'Druckeinstellung aendern', available: true, hint: 'Drucker und Formular koennen fachlich geprueft werden.' },
              { key: 'evidence', label: 'Nachweis ablegen', available: true, hint: 'Fehler- und Drucknachweis sind als Vorlage verlinkt.' },
              { key: 'approve', label: 'Ersatzdruck freigeben', available: false, hint: 'Noch keine eigene Freigabeaktion; Entscheidung muss im Nachweis dokumentiert werden.' },
              { key: 'audit', label: 'Fehler nachvollziehen', available: true, hint: 'Fehlermeldung und betroffener Pfad sind sichtbar.' },
            ]}
          />
        </div>
      </div>
      ) : null}

      <div className="space-y-3">
        <NativeSelect
          ariaLabel="Dokument"
          value="CMR"
          options={documentOptions}
        />
        <p className="text-sm text-status-error">
          Datei-Vorschau kann nicht erstellt werden. Das System findet den angegebenen Pfad nicht.
        </p>
        <div className="flex flex-col gap-2 sm:flex-row">
          <Button className="min-h-touch touch-manipulation" onClick={() => handlePrintUnavailable('Drucken')}>Drucken</Button>
          <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => handlePrintUnavailable('Vorschau')}>Vorschau</Button>
          <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => handlePrintUnavailable('Drucker einrichten')}>Drucker einrichten</Button>
        </div>
      </div>

      {!isTouch ? (
      <div className="mx-auto w-[470px] space-y-2">
        <div className="border border-[#8f8f8f] bg-[#efefef] shadow-[0_10px_24px_rgba(0,0,0,0.15)]">
          <div className="flex items-center justify-between border-b border-[#b8b8b8] bg-[#f4f4f4] px-3 py-2 text-[#5b5b5b]">
            <span>Frachtdokumente drucken</span>
            <button className="h-5 w-5 text-center leading-none">x</button>
          </div>

          <div className="space-y-3 p-3">
            <div className="grid grid-cols-[108px_78px_24px_1fr] items-center gap-2">
              <label>Lieferschein-Nr.:</label>
              <input value="2601092" readOnly className="h-6 border border-[#a8a8a8] bg-white px-1" />
              <button className="h-6 border border-[#a8a8a8] bg-[#ececec]">...</button>
              <div />
              <label>Kunden-Name:</label>
              <span className="col-span-3">Weerda Jochen</span>
            </div>

            <div className="h-px bg-[#c3c3c3]" />

            <div className="grid grid-cols-[108px_1fr_126px_86px] items-center gap-2">
              <label>Dokument:</label>
              <select className="h-6 border border-[#a8a8a8] bg-white px-1">
                <option>CMR</option>
              </select>
              <label className="justify-self-end">Druck-Datum:</label>
              <input value="25.02.2026" readOnly className="h-6 border border-[#a8a8a8] bg-white px-1" />

              <label>Formular:</label>
              <div className="grid grid-cols-[72px_24px] gap-1">
                <input value="W25001" readOnly className="h-6 border border-[#a8a8a8] bg-white px-1" />
                <button className="h-6 border border-[#a8a8a8] bg-[#ececec]">...</button>
              </div>
              <div />
              <div />

              <label>Anzahl Drucke:</label>
              <input value="1" readOnly className="h-6 w-[64px] border border-[#a8a8a8] bg-white px-1 text-center" />
              <div />
              <div />

              <label>Drucker:</label>
              <span className="col-span-3">Groothusen/Kyocera M3540dn Fach 1</span>
            </div>

            <div className="h-px bg-[#c3c3c3]" />

            <div className="flex items-center justify-between">
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Drucker einrichten</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-6">Drucken</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-6">Vorschau</button>
            </div>

            <div className="flex justify-end">
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-5">Beenden</button>
            </div>
          </div>
        </div>

        <div className="border border-[#2b77c5] bg-[#efefef] shadow-[0_10px_24px_rgba(0,0,0,0.18)]">
          <div className="flex items-center justify-between bg-[#0078d7] px-3 py-1 text-white">
            <span>Anwendungsfehler</span>
            <button className="h-5 w-5 text-center leading-none">x</button>
          </div>

          <div className="grid grid-cols-[1fr_34px] gap-3 p-3">
            <div className="leading-tight">
              Datei "C:\Program Files (x86)\SERP\L3\Preview\PreviewDESKTOP-P2FLPU30" kann nicht erstellt werden. Das System kann den angegebenen Pfad nicht finden
            </div>
            <div className="grid h-8 w-8 place-items-center rounded-full border border-[#6aa0d9] bg-white text-[18px] text-[#0d66c1]">i</div>
          </div>

          <div className="flex items-center justify-between px-3 pb-3">
            <div className="flex gap-2">
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Details</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">In Zwischenablage kopieren</button>
            </div>
            <button className="h-6 border border-[#2b7bd8] bg-white px-4">Schliessen</button>
          </div>
        </div>
      </div>
      ) : null}
    </div>
  )
}
