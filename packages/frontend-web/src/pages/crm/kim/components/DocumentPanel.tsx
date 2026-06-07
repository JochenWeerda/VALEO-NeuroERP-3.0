/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef } from 'react';
import { Customer } from '../types';
import { FileCode, Upload, FileText, CheckCircle2, ShieldCheck, Download, Trash2, Eye } from 'lucide-react';

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
    {
      id: "doc_f1",
      fileName: "Anbauerklaerung_Raps_Kampagne2026_buhr.pdf",
      fileSize: "1.2 MB",
      uploadedAt: "2026-05-18",
      category: "CONTRACT",
      securityVerified: true
    },
    {
      id: "doc_f2",
      fileName: "Wiegestation_Aurich_Wiegezettel_LS994412.png",
      fileSize: "340 KB",
      uploadedAt: "2026-05-09",
      category: "SCAN",
      securityVerified: true
    },
    {
      id: "doc_f3",
      fileName: "Bodenanalyse_Zertifikat_Bruchacker_DE.pdf",
      fileSize: "4.8 MB",
      uploadedAt: "2026-03-12",
      category: "AUDIT",
      securityVerified: true
    }
  ]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    if (e.dataTransfer.files?.[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (files: FileList) => {
    setIsUploading(true);
    // Simulate upload delay
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
          securityVerified: true
        });
      }
      setAttachedFiles([...newDocs, ...attachedFiles]);
      setIsUploading(false);
    }, 1200);
  };

  const handleDelete = (id: string) => {
    setAttachedFiles(attachedFiles.filter(f => f.id !== id));
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'AUDIT': return 'Bodenschutz Audit';
      case 'SCAN': return 'Wiegeschein-Scan';
      case 'CONTRACT': return 'Ackererfassungsvertrag';
      case 'SEED_CERTIFICATE': return 'Saatgutzertifikat';
      case 'INSURANCE': return 'Ernteversicherung';
      default: return 'Handelsunterlage';
    }
  };

  return (
    <div className="space-y-4 font-sans select-none" id="documents-panel-component">
      
      {/* Visual File upload Dropzone - Supporting BOTH Click and Drag interface */}
      <div 
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded p-6 text-center transition duration-150 cursor-pointer flex flex-col items-center justify-center gap-2 select-none ${
          dragOver 
            ? 'border-[#006633] bg-emerald-50 text-emerald-950' 
            : 'border-slate-300 bg-slate-50 hover:bg-slate-100 text-slate-600 border-[#94a3b8]'
        }`}
        id="file-upload-dropzone"
      >
        <Upload size={28} className={isUploading ? 'animate-bounce text-[#006633]' : 'text-slate-400'} />
        {isUploading ? (
          <div>
            <strong className="text-xs font-black text-[#006633]">Datei wird ins Silo-Archiv geladen...</strong>
            <p className="text-[10px] text-gray-400 mt-1">L3 Viren-Scans und PDF-Konvertierung aktiv</p>
          </div>
        ) : (
          <div>
            <strong className="text-xs font-bold block text-gray-700">Wiegeschein, Vertrag oder Bodenzertifikat einpflegen</strong>
            <p className="text-[10px] text-gray-500 mt-0.5 font-medium">Dateien per Drag-and-Drop hierhin ziehen oder <span className="text-[#006633] underline">durchsuchen</span></p>
            <p className="text-[9px] text-gray-400 mt-1 italic font-mono uppercase">Erlaubte Formate: PDF, PNG, JPG (Max. 25MB) ● compliance gesichert</p>
          </div>
        )}
        <input 
          type="file" 
          multiple
          ref={fileInputRef} 
          onChange={handleFileSelect} 
          className="hidden" 
          id="hidden-file-input"
        />
      </div>

      {/* Compliance / Regulatory Warning Banner */}
      <div className="bg-emerald-50 border border-emerald-100 p-2.5 rounded flex items-start gap-2 text-xs" id="compliance-banner-file">
        <ShieldCheck className="text-[#006633] mt-0.5 flex-shrink-0" size={15} />
        <div>
          <strong className="text-[#006633] font-bold block">Agrar-Compliance & Pflanzenschutzverordnung gesichert</strong>
          <span className="text-emerald-900 leading-snug">
            Alle hochgeladenen Sortenbescheinigungen werden automatisch indiziert und den Kontrakten (CO-99) zugeordnet. Das Abfall- und EU-Lieferkettengesetz (EUDR) wird lückenlos auditiert.
          </span>
        </div>
      </div>

      {/* Uploaded Documents List */}
      <div className="bg-white border border-[#cbd5e1] rounded-sm overflow-hidden" id="uploaded-files-list">
        <div className="bg-[#e2e8f0] p-2 border-b border-[#cbd5e1] text-gray-800 flex justify-between items-center select-none font-bold">
          <span className="font-mono text-[10px] uppercase tracking-wider flex items-center gap-1.5 ">
            <FileText size={13} className="text-[#006633]" />
            Dossier-Dokumente und Scankopien ({attachedFiles.length})
          </span>
          <span className="text-[9.5px] bg-[#2a3f54] text-white px-1.5 py-0.5 rounded-sm font-mono leading-none">Dokumentenarchiv</span>
        </div>

        <div className="divide-y divide-gray-200 font-sans text-xs">
          {attachedFiles.length === 0 ? (
            <div className="p-8 text-center text-gray-400 font-sans italic">
              Keine gescannten Unterlagen für diesen Kunden vorhanden.
            </div>
          ) : (
            attachedFiles.map(file => (
              <div key={file.id} className="p-2.5 flex items-center justify-between hover:bg-slate-50/70 transition" id={`file-row-${file.id}`}>
                <div className="flex items-center gap-2.5 truncate max-w-[70%]">
                  <div className="p-1.5 bg-slate-100 text-slate-700 rounded-sm border border-slate-200">
                    <FileText size={14} className="text-gray-500" />
                  </div>
                  <div className="truncate leading-tight">
                    <strong className="text-gray-800 font-bold block truncate" title={file.fileName}>{file.fileName}</strong>
                    <div className="flex gap-2 items-center text-[10px] text-gray-400 font-mono mt-0.5">
                      <span>{file.fileSize}</span>
                      <span>•</span>
                      <span>Hochgeladen: {file.uploadedAt}</span>
                      <span>•</span>
                      <span className="bg-[#f0fdf4] text-[#166534] border border-[#bbf7d0] px-1 rounded-sm text-[8px] font-sans font-bold uppercase tracking-wider">{getCategoryLabel(file.category)}</span>
                    </div>
                  </div>
                </div>

                <div className="flex gap-1.5 items-center">
                  <button 
                    onClick={() => alert(`Anzeige der Datei: ${file.fileName}`)}
                    className="p-1 border border-gray-300 rounded hover:bg-gray-100 text-gray-600 transition cursor-pointer"
                    title="Vorschau im Browser"
                  >
                    <Eye size={12} />
                  </button>
                  <button 
                    onClick={() => alert(`Download gestartet: ${file.fileName}`)}
                    className="p-1 border border-gray-300 rounded hover:bg-gray-100 text-gray-600 transition cursor-pointer"
                    title="Originale PDF herunterladen"
                  >
                    <Download size={12} />
                  </button>
                  <button 
                    onClick={() => handleDelete(file.id)}
                    className="p-1 border border-red-200 bg-red-50 text-red-600 rounded hover:bg-red-100 transition cursor-pointer"
                    title="Unterlage dauerhaft im Silo-Archiv löschen"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  );
}
