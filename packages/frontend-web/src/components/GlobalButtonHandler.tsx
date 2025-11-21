/**
 * Globaler Button-Handler für Export/Drucken/Speichern Buttons
 * Automatische Funktionalität für alle Buttons im System
 */

import { useEffect } from 'react'
import { exportToCSV, printTable } from '@/lib/export-utils'
import { useToast } from '@/hooks/use-toast'

export function GlobalButtonHandler(): null {
  const { toast } = useToast()

  useEffect(() => {
    const handleClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      const button = target.closest('button')
      
      if (!button) return

      const buttonText = button.textContent?.trim().toLowerCase() || ''
      const hasIcon = button.querySelector('svg')

      // Export-Button erkennen
      if (buttonText.includes('export') && hasIcon) {
        event.stopPropagation()
        const pageName = window.location.pathname.split('/').pop() || 'unknown'
        console.info(`FB:LEVEL=3 PAGE=${pageName} ACTION=export`)
        handleExportClick(button)
        return
      }

      // Drucken-Button erkennen
      if (buttonText.includes('drucken') && hasIcon) {
        event.stopPropagation()
        const pageName = window.location.pathname.split('/').pop() || 'unknown'
        console.info(`FB:LEVEL=3 PAGE=${pageName} ACTION=print`)
        handlePrintClick(button)
        return
      }

      // Speichern-Button erkennen (nur wenn kein onClick bereits definiert ist)
      if (buttonText.includes('speichern') && !button.onclick && hasIcon) {
        // Nicht unterbrechen - lass die Seite ihren eigenen Handler nutzen falls vorhanden
        // Dies ist nur ein Fallback
        console.info('Speichern-Button erkannt, aber sollte von der Seite selbst behandelt werden')
        return
      }

      // Löschen-Button erkennen  
      if ((buttonText.includes('löschen') || buttonText.includes('delete')) && hasIcon) {
        if (!button.onclick) {
          event.stopPropagation()
          const pageName = window.location.pathname.split('/').pop() || 'unknown'
          console.info(`FB:LEVEL=3 PAGE=${pageName} ACTION=delete`)
          handleDeleteClick(button)
          return
        }
      }
    }

    const handleDeleteClick = (_button: HTMLElement) => {
      const confirmed = window.confirm('Möchten Sie diesen Eintrag wirklich löschen?')
      if (!confirmed) return

      toast({
        title: 'Löschen nicht verfügbar',
        description: 'Diese Funktion muss von der Seite selbst implementiert werden.',
        variant: 'destructive',
      })
    }

    const handleExportClick = (button: HTMLElement) => {
      // Finde die nächste Tabelle
      const table = button.closest('div')?.querySelector('table')
      if (!table) {
        toast({
          title: 'Export nicht möglich',
          description: 'Keine Tabelle zum Exportieren gefunden.',
          variant: 'destructive',
        })
        return
      }

      // Extrahiere Tabellendaten
      const data = extractTableData(table)
      if (data.length === 0) {
        toast({
          title: 'Keine Daten',
          description: 'Die Tabelle enthält keine Daten zum Exportieren.',
          variant: 'destructive',
        })
        return
      }

      // Export
      const filename = `export-${new Date().toISOString().split('T')[0]}.csv`
      exportToCSV(data, filename)
      
      toast({
        title: 'Export erfolgreich',
        description: `${data.length} Zeilen wurden exportiert.`,
      })
    }

    const handlePrintClick = (button: HTMLElement) => {
      // Finde die nächste Tabelle
      const table = button.closest('div')?.querySelector('table')
      if (!table) {
        toast({
          title: 'Drucken nicht möglich',
          description: 'Keine Tabelle zum Drucken gefunden.',
          variant: 'destructive',
        })
        return
      }

      // Extrahiere Tabellendaten
      const data = extractTableData(table)
      if (data.length === 0) {
        toast({
          title: 'Keine Daten',
          description: 'Die Tabelle enthält keine Daten zum Drucken.',
          variant: 'destructive',
        })
        return
      }

      // Finde Seitentitel
      const h1 = document.querySelector('h1')
      const title = h1?.textContent || 'Übersicht'

      // Drucken
      printTable(data, title)
    }

    const extractTableData = (table: HTMLTableElement): Record<string, any>[] => {
      const rows = Array.from(table.querySelectorAll('tbody tr'))
      if (rows.length === 0) return []

      // Header extrahieren
      const headers = Array.from(table.querySelectorAll('thead th')).map(
        th => th.textContent?.trim() || ''
      ).filter(h => h)

      // Daten extrahieren
      return rows.map(row => {
        const cells = Array.from(row.querySelectorAll('td'))
        const rowData: Record<string, any> = {}
        
        cells.forEach((cell, index) => {
          if (index < headers.length) {
            rowData[headers[index]] = cell.textContent?.trim() || ''
          }
        })
        
        return rowData
      })
    }

    // Event Listener registrieren
    document.addEventListener('click', handleClick, true)

    return () => {
      document.removeEventListener('click', handleClick, true)
    }
  }, [toast])

  return null
}

