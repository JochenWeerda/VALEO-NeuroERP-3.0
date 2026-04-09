export type NawaroCommunicationArtifact = {
  fileName: string
  content: string
}

export function openHtmlPreview(title: string, sections: Array<{ label: string; value: string }>): void {
  const html = `<!doctype html>
  <html lang="de">
    <head>
      <meta charset="utf-8" />
      <title>${title}</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 32px; color: #1f2937; }
        h1 { margin-bottom: 24px; }
        table { width: 100%; border-collapse: collapse; }
        td { padding: 10px 12px; border-bottom: 1px solid #d1d5db; vertical-align: top; }
        td:first-child { width: 32%; color: #6b7280; font-weight: 600; }
      </style>
    </head>
    <body>
      <h1>${title}</h1>
      <table>
        ${sections.map((section) => `<tr><td>${section.label}</td><td>${section.value}</td></tr>`).join('')}
      </table>
    </body>
  </html>`
  const previewWindow = window.open('', '_blank', 'noopener,noreferrer,width=980,height=720')
  if (!previewWindow) return
  previewWindow.document.write(html)
  previewWindow.document.close()
}

export function downloadArtifact(artifact: NawaroCommunicationArtifact, mimeType = 'text/plain;charset=utf-8'): void {
  const blob = new Blob([artifact.content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = artifact.fileName
  anchor.click()
  URL.revokeObjectURL(url)
}

export function buildCsvArtifact(fileName: string, headers: string[], rows: Array<Array<string | number | null | undefined>>): NawaroCommunicationArtifact {
  const escapeCell = (value: string | number | null | undefined): string => `"${String(value ?? '').replace(/"/g, '""')}"`
  const body = rows.map((row) => row.map(escapeCell).join(';')).join('\n')
  return { fileName, content: `${headers.join(';')}\n${body}` }
}
