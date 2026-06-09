/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState } from 'react';
import { Customer, BusinessDocument } from '../types';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Plus, Calendar, FileCheck, FolderOpen } from 'lucide-react';

export type DocCategory =
  | 'ALL'
  | 'OFFER'
  | 'ORDER'
  | 'DELIVERY_NOTE'
  | 'INQUIRY'
  | 'PURCHASE_ORDER'
  | 'PURCHASE_OFFER'
  | 'PURCHASE_SETTLEMENT'
  | 'THIRD_PARTY_STOCK';

interface SalesDocumentsPanelProps {
  customer: Customer;
  documents: BusinessDocument[];
  onOpenDocument: (document: BusinessDocument) => void;
  onCreateDocument: (category: DocCategory) => void;
  activeCategory: DocCategory;
  onCategoryChange: (category: DocCategory) => void;
}

const categories: Array<{ key: DocCategory; label: string; desc: string }> = [
  { key: 'ALL', label: 'Übersicht', desc: 'Alle kundenbezogenen Belege' },
  { key: 'OFFER', label: 'Angebote', desc: 'Vertriebs-Angebote' },
  { key: 'ORDER', label: 'Aufträge', desc: 'Silo-Abnahmen & feste Verkäufe' },
  { key: 'DELIVERY_NOTE', label: 'Lieferscheine', desc: 'Fracht- und Wiegezettel' },
  { key: 'INQUIRY', label: 'Anfragen', desc: 'Kundenbezogene Anfragen' },
  { key: 'PURCHASE_ORDER', label: 'Bestellungen', desc: 'Kundenbezogene Bestellungen' },
  { key: 'PURCHASE_OFFER', label: 'Kaufangebote', desc: 'Preisanfrage Erzeugnisse (KA)' },
  { key: 'PURCHASE_SETTLEMENT', label: 'Kaufabrechnungen', desc: 'Gutschriften Erzeuger (KB)' },
  { key: 'THIRD_PARTY_STOCK', label: 'Fremdbestände', desc: 'Silo-Einkellerungen Partner' },
];

export default function SalesDocumentsPanel({
  customer,
  documents,
  onOpenDocument,
  onCreateDocument,
  activeCategory,
  onCategoryChange,
}: SalesDocumentsPanelProps) {
  const [selectedDocumentId, setSelectedDocumentId] = useState('');
  const filteredDocs = activeCategory === 'ALL'
    ? documents
    : documents.filter((doc) => doc.type === activeCategory);
  const selectedDocument = filteredDocs.find((doc) => doc.id === selectedDocumentId) ?? null;

  return (
    <div className="space-y-4" id="sales-documents-panel-component" data-customer-id={customer.id}>
      <div className="flex flex-wrap items-end border-b border-border gap-1">
        {categories.map((category) => (
          <button
            key={category.key}
            onClick={() => {
              onCategoryChange(category.key);
              setSelectedDocumentId('');
            }}
            className={`px-3 py-1.5 text-xs font-medium transition rounded-t-md border-b-2 ${
              activeCategory === category.key
                ? 'border-primary text-primary bg-primary/5 font-semibold'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
            title={category.desc}
            id={`tab-doc-sel-${category.key}`}
          >
            {category.label}
          </button>
        ))}
        <Button
          variant="outline"
          size="sm"
          disabled={!selectedDocument}
          onClick={() => selectedDocument && onOpenDocument(selectedDocument)}
          className="ml-auto gap-1 mb-1"
          data-action-id="crm360.document.open"
        >
          <FolderOpen size={13} /> Öffnen
        </Button>
        <Button
          size="sm"
          disabled={activeCategory === 'ALL'}
          onClick={() => onCreateDocument(activeCategory)}
          className="gap-1 mb-1"
          data-action-id="crm360.document.create"
        >
          <Plus size={13} /> Neu
        </Button>
      </div>

      <div className="rounded-lg border border-border bg-card overflow-hidden" id="documents-grid-control">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="bg-muted/60 border-b border-border text-muted-foreground text-xs">
                <th className="p-2 font-medium">Beleg-Nr.</th>
                <th className="p-2 font-medium">Ausstelldatum</th>
                <th className="p-2 font-medium text-center">Betriebsleiter</th>
                <th className="p-2 font-medium text-center">Vertrieb VB</th>
                <th className="p-2 font-medium text-center">Gepl. Lieferdatum</th>
                <th className="p-2 font-medium text-right">Netto</th>
                <th className="p-2 font-medium text-right">MwSt</th>
                <th className="p-2 font-medium text-right">Brutto</th>
                <th className="p-2 font-medium text-center">Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredDocs.length === 0 ? (
                <tr>
                  <td colSpan={9} className="p-6 text-center text-muted-foreground italic">
                    {activeCategory === 'ALL'
                      ? 'Keine Belege für diesen Kunden registriert.'
                      : `Keine ${categories.find((category) => category.key === activeCategory)?.label} für diesen Kunden registriert.`}
                  </td>
                </tr>
              ) : (
                filteredDocs.map((document) => (
                  <tr
                    key={document.id}
                    className={`border-b border-border transition cursor-pointer ${
                      selectedDocumentId === document.id ? 'bg-primary/10' : 'hover:bg-muted/40'
                    }`}
                    id={`doc-row-entry-${document.id}`}
                    data-action-id="crm360.document.select"
                    aria-selected={selectedDocumentId === document.id}
                    onClick={() => setSelectedDocumentId(document.id)}
                    onDoubleClick={() => onOpenDocument(document)}
                  >
                    <td className="p-2 font-semibold text-foreground">
                      <span className="flex items-center gap-1">
                        <FileCheck className="text-muted-foreground" size={12} />
                        {document.docNo}
                      </span>
                    </td>
                    <td className="p-2 text-muted-foreground">
                      {new Date(document.date).toLocaleDateString('de-DE')}
                    </td>
                    <td className="p-2 text-center text-muted-foreground">{document.operator}</td>
                    <td className="p-2 text-center font-medium text-primary">{document.representative}</td>
                    <td className="p-2 text-center text-muted-foreground">
                      {document.plannedDeliveryDate ? (
                        <span className="flex items-center justify-center gap-1 text-xs">
                          <Calendar size={11} className="text-[hsl(var(--color-semantic-warning-500-hsl))]" />
                          {new Date(document.plannedDeliveryDate).toLocaleDateString('de-DE')}
                        </span>
                      ) : '—'}
                    </td>
                    <td className="p-2 text-right font-medium text-foreground">
                      EUR {document.netAmount.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="p-2 text-right text-muted-foreground">
                      +EUR {document.taxAmount.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="p-2 text-right font-semibold text-foreground">
                      EUR {document.grossAmount.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="p-2 text-center">
                      <Badge variant={document.completed ? 'success' : 'warning'}>
                        {document.completed ? 'Erledigt' : 'Ausstehend'}
                      </Badge>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
