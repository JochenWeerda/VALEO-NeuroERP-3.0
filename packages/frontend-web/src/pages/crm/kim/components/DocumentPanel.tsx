/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef } from 'react';
import { Customer } from '../types';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Upload, FileText, ShieldCheck, Download, Trash2, Eye } from 'lucide-react';

interface DocumentPanelProps {
  customer: Customer;
}

interface AttachedFile {
  id: string;
  fileName: string;
  fileSize: string;
  uploadedAt: string;
  category: 'AUDIT' | 'SCAN' | 'CONTRACT' | 'SEED_CERTIFICATE' | 'INSURANCE';
  securityVerified: boolean;
}

export default function DocumentPanel({ customer }: DocumentPanelProps) {
  const [dragOver, setDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([
    { id: "doc_f1", fileName: "Anbauerklaerung_Raps_Kampagne2026_buhr.pdf", fileSize: "1.2 MB", uploadedAt: "2026-05-18", category: "CONTRACT", securityVerified: true },
    { id: "doc_f2", fileName: "Wiegestation_Aurich_Wiegezettel_LS994412.png", fileSize: "340 KB", uploadedAt: "2026-05-09", category: "SCAN", securityVerified: true },
    { id: "doc_f3", fileName: "Bodenanalyse_Zertifikat_Bruchacker_DE.pdf", fileSize: "4.8 MB", uploadedAt: "2026-03-12", category: "AUDIT", securityVerified: true },
  ]);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files?.[0]) handleFiles(e.dataTransfer.files);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) handleFiles(e.target.files);
  };

  const handleFiles = (files: FileList) => {
    setIsUploading(true);
    setTimeout(() => {
      const newDocs: AttachedFile[] = [];
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const sizeKb = Math.round(file.size / 1024);
        const sizeStr = sizeKb > 1024 ? `${(sizeKb / 1024).toFixed(1)} MB` : `${sizeKb} KB`;
        newDocs.push({
          id: `f_${Date.now()}_${i}`,
          fileName: file.name,
          fileSize: sizeStr,
          uploadedAt: new Date().toISOString().split('T')[0],
          category: file.name.toLowerCase().includes('zertifikat') ? 'SEED_CERTIFICATE' : 'SCAN',
          securityVerified: true,
        });
      }
      setAttachedFiles(prev => [...newDocs, ...prev]);
      setIsUploading(false);
    }, 1200);
  };

  const handleDelete = (id: string) => setAttachedFiles(prev => prev.filter(f => f.id !== id));

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'AUDIT': return 'Bodenschutz-Audit';
      case 'SCAN': return 'Wiegeschein-Scan';
      case 'CONTRACT': return 'Ackererfassungsvertrag';
      case 'SEED_CERTIFICATE': return 'Saatgutzertifikat';
      case 'INSURANCE': return 'Ernteversicherung';
      default: return 'Handelsunterlage';
    }
  };

  return (
    <div className="space-y-4" id="documents-panel-component">

      {/* Dropzone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-6 text-center transition cursor-pointer flex flex-col items-center justify-center gap-2 ${
          dragOver ? 'border-primary bg-primary/5 text-foreground' : 'border-border bg-muted/30 hover:bg-muted/60 text-muted-foreground'
        }`}
        id="file-upload-dropzone"
      >
        <Upload size={28} className={isUploading ? 'animate-bounce text-primary' : 'text-muted-foreground'} />
        {isUploading ? (
          <div>
            <strong className="text-sm text-primary">Datei wird ins Archiv geladen…</strong>
            <p className="text-xs text-muted-foreground mt-1">Viren-Scan und PDF-Konvertierung aktiv</p>
          </div>
        ) : (
          <div>
            <strong className="text-sm block text-foreground">Wiegeschein, Vertrag oder Bodenzertifikat einpflegen</strong>
            <p className="text-xs text-muted-foreground mt-0.5">Dateien per Drag-and-Drop hierhin ziehen oder <span className="text-primary underline">durchsuchen</span></p>
            <p className="text-xs text-muted-foreground/80 mt-1">Erlaubte Formate: PDF, PNG, JPG (max. 25 MB) · compliance-gesichert</p>
          </div>
        )}
        <input type="file" multiple ref={fileInputRef} onChange={handleFileSelect} className="hidden" id="hidden-file-input" />
      </div>

      {/* Compliance banner */}
      <div className="rounded-md border border-[hsl(var(--color-semantic-success-500-hsl)/0.25)] bg-[hsl(var(--color-semantic-success-50-hsl))] p-2.5 flex items-start gap-2 text-sm dark:bg-[hsl(var(--color-semantic-success-500-hsl)/0.12)]" id="compliance-banner-file">
        <ShieldCheck className="text-[hsl(var(--color-semantic-success-700-hsl))] mt-0.5 flex-shrink-0 dark:text-[hsl(var(--color-semantic-success-50-hsl))]" size={16} />
        <div className="text-[hsl(var(--color-semantic-success-700-hsl))] dark:text-[hsl(var(--color-semantic-success-50-hsl))]">
          <strong className="block">Agrar-Compliance &amp; Pflanzenschutzverordnung gesichert</strong>
          <span className="leading-snug">
            Hochgeladene Sortenbescheinigungen werden automatisch indiziert und den Kontrakten zugeordnet. EUDR-Lieferkettengesetz wird lückenlos auditiert.
          </span>
        </div>
      </div>

      {/* Uploaded files */}
      <div className="rounded-lg border border-border bg-card overflow-hidden" id="uploaded-files-list">
        <div className="bg-muted/60 px-3 py-2 border-b border-border flex justify-between items-center">
          <span className="text-sm font-semibold flex items-center gap-1.5 text-foreground">
            <FileText size={15} className="text-primary" />
            Dossier-Dokumente und Scankopien ({attachedFiles.length})
          </span>
          <Badge variant="secondary">Dokumentenarchiv</Badge>
        </div>

        <div className="divide-y divide-border text-sm">
          {attachedFiles.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground italic">
              Keine gescannten Unterlagen für diesen Kunden vorhanden.
            </div>
          ) : (
            attachedFiles.map(file => (
              <div key={file.id} className="p-2.5 flex items-center justify-between gap-2 hover:bg-muted/50 transition" id={`file-row-${file.id}`}>
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="p-1.5 bg-muted rounded-md border border-border flex-shrink-0">
                    <FileText size={14} className="text-muted-foreground" />
                  </div>
                  <div className="min-w-0">
                    <strong className="text-foreground block truncate" title={file.fileName}>{file.fileName}</strong>
                    <div className="flex gap-2 items-center text-xs text-muted-foreground mt-0.5 flex-wrap">
                      <span>{file.fileSize}</span>
                      <span>•</span>
                      <span>{file.uploadedAt}</span>
                      <Badge variant="success">{getCategoryLabel(file.category)}</Badge>
                    </div>
                  </div>
                </div>

                <div className="flex gap-1 items-center flex-shrink-0">
                  <Button variant="outline" size="icon" className="h-8 w-8" onClick={() => alert(`Anzeige der Datei: ${file.fileName}`)} title="Vorschau">
                    <Eye size={14} />
                  </Button>
                  <Button variant="outline" size="icon" className="h-8 w-8" onClick={() => alert(`Download gestartet: ${file.fileName}`)} title="Herunterladen">
                    <Download size={14} />
                  </Button>
                  <Button variant="outline" size="icon" className="h-8 w-8 text-destructive hover:text-destructive" onClick={() => handleDelete(file.id)} title="Löschen">
                    <Trash2 size={14} />
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  );
}
