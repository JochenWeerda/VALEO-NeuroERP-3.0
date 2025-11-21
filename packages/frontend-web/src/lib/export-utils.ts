/**
 * Export Utilities für CSV, Excel und PDF Export
 */

export type ExportFormat = 'csv' | 'xlsx' | 'pdf'

/**
 * Konvertiert Daten zu CSV
 */
export function exportToCSV<T extends Record<string, any>>(
  data: T[],
  filename: string,
  columns?: { key: keyof T; label: string }[]
): void {
  if (data.length === 0) {
    alert('Keine Daten zum Exportieren vorhanden')
    return
  }

  // Spalten bestimmen
  const cols = columns || Object.keys(data[0]).map(key => ({ key, label: key }))
  
  // CSV Header
  const headers = cols.map(col => col.label).join(',')
  
  // CSV Rows
  const rows = data.map(item => {
    return cols.map(col => {
      const value = item[col.key]
      // Escape CSV values
      if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
        return `"${value.replace(/"/g, '""')}"`
      }
      return value ?? ''
    }).join(',')
  })
  
  const csvContent = [headers, ...rows].join('\n')
  
  // Download
  downloadFile(csvContent, filename, 'text/csv;charset=utf-8;')
}

/**
 * Konvertiert Daten zu Excel (CSV mit Excel-kompatiblem Format)
 */
export function exportToExcel<T extends Record<string, any>>(
  data: T[],
  filename: string,
  columns?: { key: keyof T; label: string }[]
): void {
  // Für echtes Excel würde man xlsx library nutzen
  // Hier nutzen wir CSV mit .xlsx Extension für einfache Kompatibilität
  exportToCSV(data, filename.replace('.csv', '.xlsx'), columns)
}

/**
 * Erstellt einen HTML-Print-Dialog für Tabellen
 */
export function printTable<T extends Record<string, any>>(
  data: T[],
  title: string,
  columns?: { key: keyof T; label: string }[]
): void {
  if (data.length === 0) {
    alert('Keine Daten zum Drucken vorhanden')
    return
  }

  const cols = columns || Object.keys(data[0]).map(key => ({ key, label: key }))
  
  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    alert('Pop-up wurde blockiert. Bitte Pop-ups für diese Seite erlauben.')
    return
  }
  
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>${title}</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { background: #f0f0f0; padding: 12px; text-align: left; border: 1px solid #ddd; font-weight: bold; }
        td { padding: 8px; border: 1px solid #ddd; }
        tr:nth-child(even) { background: #f9f9f9; }
        @media print {
          button { display: none; }
        }
      </style>
    </head>
    <body>
      <h1>${title}</h1>
      <p>Erstellt am: ${new Date().toLocaleString('de-DE')}</p>
      <table>
        <thead>
          <tr>
            ${cols.map(col => `<th>${col.label}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${data.map(item => `
            <tr>
              ${cols.map(col => `<td>${item[col.key] ?? ''}</td>`).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>
      <div style="margin-top: 20px;">
        <button onclick="window.print()" style="padding: 10px 20px; background: #333; color: white; border: none; cursor: pointer;">Drucken</button>
        <button onclick="window.close()" style="padding: 10px 20px; margin-left: 10px; cursor: pointer;">Schließen</button>
      </div>
    </body>
    </html>
  `
  
  printWindow.document.write(html)
  printWindow.document.close()
}

/**
 * Download-Helper für Dateien
 */
function downloadFile(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * Formatiert Datum für Export
 */
export function formatDateForExport(date: string | Date): string {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('de-DE')
}

/**
 * Formatiert Währung für Export
 */
export function formatCurrencyForExport(amount: number, currency = 'EUR'): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency,
  }).format(amount)
}

