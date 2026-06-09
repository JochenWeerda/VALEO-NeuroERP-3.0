/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Customer, BusinessDocument } from '../types';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { NativeSelect } from '@/components/ui/native-select';
import { Label } from '@/components/ui/label';
import { Plus, X, Check, Calendar, FileCheck } from 'lucide-react';

interface SalesDocumentsPanelProps {
  customer: Customer;
  documents: BusinessDocument[];
  onAddDocument: (vals: Partial<BusinessDocument>) => void;
}

type DocCategory = 'OFFER' | 'ORDER' | 'DELIVERY_NOTE' | 'PURCHASE_OFFER' | 'PURCHASE_SETTLEMENT' | 'THIRD_PARTY_STOCK';

export default function SalesDocumentsPanel({ customer, documents, onAddDocument }: SalesDocumentsPanelProps) {
  const [activeCategory, setActiveCategory] = useState<DocCategory>('ORDER');
  const [showAddForm, setShowAddForm] = useState(false);

  const [docType, setDocType] = useState<DocCategory>('ORDER');
  const [docNo, setDocNo] = useState('');
  const [docDate, setDocDate] = useState(new Date().toISOString().split('T')[0]);
  const [docOp, setDocOp] = useState('JW');
  const [docRep, setDocRep] = useState('JW');
  const [docDelivery, setDocDelivery] = useState('');
  const [docNet, setDocNet] = useState('');
  const [docTaxPct, setDocTaxPct] = useState('7');
  const [docIsCompleted, setDocIsCompleted] = useState(false);

  const filteredDocs = documents.filter(doc => doc.type === activeCategory);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!docNo || !docNet) return;
    const net = Number(docNet);
    const tax = net * (Number(docTaxPct) / 100);
    onAddDocument({
      type: docType, docNo, date: docDate, operator: docOp, representative: docRep,
      plannedDeliveryDate: docDelivery || undefined, netAmount: net, taxAmount: tax,
      grossAmount: net + tax, completed: docIsCompleted,
    });
    setDocNo(''); setDocDate(new Date().toISOString().split('T')[0]); setDocDelivery('');
    setDocNet(''); setDocIsCompleted(false); setShowAddForm(false);
  };

  const categories: { key: DocCategory; label: string; desc: string }[] = [
    { key: 'OFFER', label: 'Angebote', desc: 'Vertriebs-Angebote' },
    { key: 'ORDER', label: 'Aufträge', desc: 'Silo-Abnahmen & feste Verkäufe' },
    { key: 'DELIVERY_NOTE', label: 'Lieferscheine', desc: 'Fracht- und Wiegezettel' },
    { key: 'PURCHASE_OFFER', label: 'Kaufangebote', desc: 'Preisanfrage Erzeugnisse (KA)' },
    { key: 'PURCHASE_SETTLEMENT', label: 'Kaufabrechnungen', desc: 'Gutschriften Erzeuger (KB)' },
    { key: 'THIRD_PARTY_STOCK', label: 'Fremdbestände', desc: 'Silo-Einkellerungen Partner' },
  ];

  return (
    <div className="space-y-4" id="sales-documents-panel-component">

      {/* Category tabs */}
      <div className="flex flex-wrap items-end border-b border-border gap-1">
        {categories.map((cat) => (
          <button
            key={cat.key}
            onClick={() => { setActiveCategory(cat.key); setDocType(cat.key); }}
            className={`px-3 py-1.5 text-xs font-medium transition rounded-t-md border-b-2 ${
              activeCategory === cat.key ? 'border-primary text-primary bg-primary/5 font-semibold' : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
            title={cat.desc}
            id={`tab-doc-sel-${cat.key}`}
          >
            {cat.label}
          </button>
        ))}
        <Button size="sm" onClick={() => setShowAddForm(!showAddForm)} className="ml-auto gap-1 mb-1" id="btn-trigger-add-doc">
          {showAddForm ? <X size={13} /> : <Plus size={13} />}
          {showAddForm ? 'Schließen' : 'Warenbeleg erfassen'}
        </Button>
      </div>

      {/* Add form */}
      {showAddForm && (
        <form onSubmit={handleSubmit} className="p-3 bg-muted/30 border border-border rounded-lg text-sm grid grid-cols-12 gap-2" id="add-beleg-transaction-form">
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Vorgangstyp</Label>
            <NativeSelect value={docType} onChange={e => setDocType(e.target.value as DocCategory)} options={categories.map(c => ({ value: c.key, label: c.label }))} />
          </div>
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label htmlFor="crm360-document-number" className="text-xs">Belegnummer</Label>
            <Input id="crm360-document-number" type="text" required value={docNo} onChange={e => setDocNo(e.target.value)} placeholder="z.B. AU-2610… / CO-881…" />
          </div>
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Belegdatum</Label>
            <Input type="date" required value={docDate} onChange={e => setDocDate(e.target.value)} />
          </div>
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label htmlFor="crm360-document-net" className="text-xs">Warenwert Netto (EUR)</Label>
            <Input id="crm360-document-net" type="number" required value={docNet} onChange={e => setDocNet(e.target.value)} placeholder="EUR-Wert" />
          </div>
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">USt-Satz</Label>
            <NativeSelect value={docTaxPct} onChange={e => setDocTaxPct(e.target.value)} options={[
              { value: '7', label: '7% (Saatgut / Futter)' },
              { value: '9', label: '9% (Pauschalierte LW)' },
              { value: '19', label: '19% (Gewerblich)' },
              { value: '0', label: '0% (Ausfuhr)' },
            ]} />
          </div>
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Lieferzeitraum</Label>
            <Input type="date" value={docDelivery} onChange={e => setDocDelivery(e.target.value)} />
          </div>

          <div className="col-span-12 border-t border-dashed border-border pt-2 flex flex-col md:flex-row items-center gap-4 justify-between">
            <div className="flex flex-wrap gap-4 items-center text-sm text-muted-foreground">
              <label className="flex items-center gap-1.5">Bediener:
                <Input required value={docOp} onChange={e => setDocOp(e.target.value)} className="w-16 h-8 text-center" />
              </label>
              <label className="flex items-center gap-1.5">Vertreter (VB):
                <Input required value={docRep} onChange={e => setDocRep(e.target.value)} className="w-16 h-8 text-center" />
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer select-none">
                <input type="checkbox" checked={docIsCompleted} onChange={e => setDocIsCompleted(e.target.checked)} className="accent-primary" />
                <span>Beleg vollständig ausgeführt &amp; archiviert</span>
              </label>
            </div>
            <Button type="submit" size="sm" className="gap-1.5" id="btn-save-doc-recept">
              <Check size={13} />
              Beleg anlegen
            </Button>
          </div>
        </form>
      )}

      {/* Table */}
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
                    Keine {categories.find(c => c.key === activeCategory)?.label} für diesen Mandanten registriert.
                  </td>
                </tr>
              ) : (
                filteredDocs.map((doc) => (
                  <tr key={doc.id} className="border-b border-border hover:bg-muted/40 transition" id={`doc-row-entry-${doc.id}`}>
                    <td className="p-2 font-semibold text-foreground">
                      <span className="flex items-center gap-1"><FileCheck className="text-muted-foreground" size={12} />{doc.docNo}</span>
                    </td>
                    <td className="p-2 text-muted-foreground">{new Date(doc.date).toLocaleDateString("de-DE")}</td>
                    <td className="p-2 text-center text-muted-foreground">{doc.operator}</td>
                    <td className="p-2 text-center font-medium text-primary">{doc.representative}</td>
                    <td className="p-2 text-center text-muted-foreground">
                      {doc.plannedDeliveryDate ? (
                        <span className="flex items-center justify-center gap-1 text-xs">
                          <Calendar size={11} className="text-[hsl(var(--color-semantic-warning-500-hsl))]" />
                          {new Date(doc.plannedDeliveryDate).toLocaleDateString("de-DE")}
                        </span>
                      ) : '—'}
                    </td>
                    <td className="p-2 text-right font-medium text-foreground">EUR {doc.netAmount.toLocaleString("de-DE", { minimumFractionDigits: 2 })}</td>
                    <td className="p-2 text-right text-muted-foreground">+EUR {doc.taxAmount.toLocaleString("de-DE", { minimumFractionDigits: 2 })}</td>
                    <td className="p-2 text-right font-semibold text-foreground">EUR {doc.grossAmount.toLocaleString("de-DE", { minimumFractionDigits: 2 })}</td>
                    <td className="p-2 text-center">
                      <Badge variant={doc.completed ? 'success' : 'warning'}>{doc.completed ? 'Erledigt' : 'Ausstehend'}</Badge>
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
