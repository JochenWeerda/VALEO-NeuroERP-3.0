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
import { Check, Plus, X, Landmark, Compass, Award } from 'lucide-react';

interface ContractsPanelProps {
  customer: Customer;
  documents: BusinessDocument[];
  onAddContract: (vals: Partial<BusinessDocument>) => void;
}

interface CropContract {
  id: string;
  cropNo: string;
  cropType: string;
  quantityTotal: number;
  quantityDelivered: number;
  fixedPricePerDt: number;
  validUntil: string;
  qualitySpecs: string;
  status: 'ACTIVE' | 'PARTIALLY_FULFILLED' | 'CLOSED' | 'EXPIRED';
}

function SummaryCard({ icon, label, value, sub }: { icon: React.ReactNode; label: string; value: string; sub: string }) {
  return (
    <div className="bg-card p-3 border border-border rounded-lg shadow-sm flex items-center justify-between">
      <div>
        <span className="text-xs uppercase font-medium text-muted-foreground">{label}</span>
        <p className="font-bold text-foreground text-lg">{value}</p>
        <span className="text-xs text-muted-foreground block">{sub}</span>
      </div>
      <div className="p-2.5 bg-primary/10 text-primary rounded-md border border-primary/20">{icon}</div>
    </div>
  );
}

export default function ContractsPanel({ customer, documents, onAddContract }: ContractsPanelProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [cNo, setCNo] = useState('');
  const [cType, setCType] = useState('Weichweizen (Futter)');
  const [cQty, setCQty] = useState('150');
  const [cPrice, setCPrice] = useState('22.50');
  const [cDate, setCDate] = useState(new Date().toISOString().split('T')[0]);
  const [cSpecs, setCSpecs] = useState('Feuchte <14.5%, Besatz <2%');

  const [customContracts, setCustomContracts] = useState<CropContract[]>([
    { id: "cc1", cropNo: "CO-998822", cropType: "Proteingetreide (A-Weizen)", quantityTotal: 300, quantityDelivered: 120, fixedPricePerDt: 24.80, validUntil: "2026-09-30", qualitySpecs: "Protein >13.5%, Hektolitergewicht >76kg", status: "PARTIALLY_FULFILLED" },
    { id: "cc2", cropNo: "CO-881203", cropType: "Rapsernte (Sonderkampagne)", quantityTotal: 150, quantityDelivered: 150, fixedPricePerDt: 46.50, validUntil: "2026-08-31", qualitySpecs: "Ölgehalt >40%, Beimischung <1.5%", status: "CLOSED" },
    { id: "cc3", cropNo: "CO-262299", cropType: "Silomais (Frischsubstrat)", quantityTotal: 1200, quantityDelivered: 0, fixedPricePerDt: 4.80, validUntil: "2026-11-15", qualitySpecs: "Trockensubstanz (TS) 32-35%", status: "ACTIVE" },
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cNo || !cQty || !cPrice) return;

    const newRow: CropContract = {
      id: `cc_${Date.now()}`, cropNo: cNo, cropType: cType, quantityTotal: Number(cQty),
      quantityDelivered: 0, fixedPricePerDt: Number(cPrice), validUntil: cDate, qualitySpecs: cSpecs, status: 'ACTIVE',
    };
    setCustomContracts(prev => [newRow, ...prev]);

    const net = Number(cQty) * Number(cPrice) * 10;
    const tax = net * 0.07;
    onAddContract({
      type: 'ORDER', docNo: cNo, date: new Date().toISOString().split('T')[0], operator: 'JW',
      representative: 'JW', plannedDeliveryDate: cDate, netAmount: net, taxAmount: tax, grossAmount: net + tax, completed: false,
    });

    setCNo(''); setCQty('150'); setCPrice('22.50'); setCSpecs('Feuchte <14.5%, Besatz <2%'); setShowAddForm(false);
  };

  const openSaldo = customContracts.filter(c => c.status !== 'CLOSED').reduce((sum, c) => sum + (c.quantityTotal - c.quantityDelivered), 0);
  const fulfilQuote = (customContracts.reduce((s, c) => s + c.quantityDelivered, 0) / customContracts.reduce((s, c) => s + c.quantityTotal, 0)) * 100;

  return (
    <div className="space-y-4" id="agrarian-contracts-widget">

      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <SummaryCard icon={<Landmark size={15} />} label="Offener Kontraktsaldo" value={`${openSaldo} t`} sub="Silo-Lieferungsansprüche" />
        <SummaryCard icon={<Compass size={15} />} label="Ø Kontraktwert" value="EUR 24,50 / dt" sub="Absicherung MATIF" />
        <SummaryCard icon={<Award size={15} />} label="Abarbeitungsquote" value={`${fulfilQuote.toFixed(1)}%`} sub="Abschlüsse ernteschonend erfasst" />
      </div>

      {/* Header */}
      <div className="flex justify-between items-center rounded-t-lg border border-border bg-muted/60 px-3 py-2">
        <div className="flex items-center gap-1.5 text-foreground">
          <Landmark size={15} className="text-primary" />
          <h3 className="font-semibold text-sm">Getreidekontrakte &amp; Silo-Abnahmeverträge</h3>
        </div>
        <Button variant="outline" size="sm" onClick={() => setShowAddForm(!showAddForm)} className="gap-1">
          {showAddForm ? <X size={13} /> : <Plus size={13} />}
          {showAddForm ? 'Schließen' : 'Silokontrakt registrieren'}
        </Button>
      </div>

      {/* Add form */}
      {showAddForm && (
        <form onSubmit={handleSubmit} className="p-3 bg-muted/30 border border-border rounded-lg grid grid-cols-12 gap-2 text-sm" id="add-grain-contract-form">
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Kontrakt-Nr.</Label>
            <Input required value={cNo} onChange={e => setCNo(e.target.value)} placeholder="CO-2026…" />
          </div>
          <div className="col-span-6 md:col-span-3 space-y-1">
            <Label className="text-xs">Getreide-Kategorie</Label>
            <NativeSelect value={cType} onChange={e => setCType(e.target.value)} options={[
              { value: 'A-Weizen (Backweizen)', label: 'A-Weizen (Backweizen)' },
              { value: 'B-Weizen (Mahlweizen)', label: 'B-Weizen (Mahlweizen)' },
              { value: 'Weichweizen (Futter)', label: 'Weichweizen (Futter)' },
              { value: 'Raps (Ölmühle)', label: 'Raps (Ölmühle)' },
              { value: 'Braugerste', label: 'Braugerste (Sommergerste)' },
              { value: 'Silomais (Frischsubstrat)', label: 'Silomais (Frischsubstrat)' },
            ]} />
          </div>
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Liefermenge (t)</Label>
            <Input type="number" required value={cQty} onChange={e => setCQty(e.target.value)} placeholder="in t" />
          </div>
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Festpreis pro dt (EUR)</Label>
            <Input required value={cPrice} onChange={e => setCPrice(e.target.value)} placeholder="€/dt" />
          </div>
          <div className="col-span-6 md:col-span-3 space-y-1">
            <Label className="text-xs">Liefer-Deadline</Label>
            <Input type="date" required value={cDate} onChange={e => setCDate(e.target.value)} />
          </div>
          <div className="col-span-12 border-t border-dashed border-border pt-2 flex items-center gap-3 justify-between">
            <Input className="w-2/3" value={cSpecs} onChange={e => setCSpecs(e.target.value)} placeholder="Qualitätsspezifikationen (z.B. Fallzahl >220s)" />
            <Button type="submit" size="sm" className="gap-1.5">
              <Check size={13} />
              Silo-Abschluss sichern
            </Button>
          </div>
        </form>
      )}

      {/* Table */}
      <div className="rounded-lg border border-border bg-card overflow-hidden" id="contracts-table-grid">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="bg-muted/60 border-b border-border text-muted-foreground text-xs">
                <th className="p-2 font-medium">Kontrakt-Nr.</th>
                <th className="p-2 font-medium">Getreidetyp / Sorte</th>
                <th className="p-2 font-medium text-right">Gesamt (t)</th>
                <th className="p-2 font-medium text-right">Geliefert (t)</th>
                <th className="p-2 font-medium text-right">Rest (t)</th>
                <th className="p-2 font-medium text-right">Festpreis/dt</th>
                <th className="p-2 font-medium">Ziel-Erntezeitraum</th>
                <th className="p-2 font-medium">Qualitätszertifikate</th>
                <th className="p-2 font-medium text-center">Status</th>
              </tr>
            </thead>
            <tbody>
              {customContracts.map((cnt) => {
                const rest = cnt.quantityTotal - cnt.quantityDelivered;
                const pct = (cnt.quantityDelivered / cnt.quantityTotal) * 100;
                return (
                  <tr key={cnt.id} className="border-b border-border hover:bg-muted/40 transition" id={`cnt-row-entry-${cnt.id}`}>
                    <td className="p-2 font-semibold text-foreground">{cnt.cropNo}</td>
                    <td className="p-2 font-medium text-foreground">{cnt.cropType}</td>
                    <td className="p-2 text-right text-foreground">{cnt.quantityTotal} t</td>
                    <td className="p-2 text-right text-muted-foreground">{cnt.quantityDelivered} t</td>
                    <td className={`p-2 text-right font-semibold ${rest > 0 ? 'text-primary' : 'text-muted-foreground'}`}>{rest} t</td>
                    <td className="p-2 text-right font-semibold text-primary">EUR {cnt.fixedPricePerDt.toLocaleString("de-DE", { minimumFractionDigits: 2 })}</td>
                    <td className="p-2 text-muted-foreground">{new Date(cnt.validUntil).toLocaleDateString("de-DE")}</td>
                    <td className="p-2 text-muted-foreground truncate max-w-[200px]" title={cnt.qualitySpecs}>{cnt.qualitySpecs}</td>
                    <td className="p-2 text-center">
                      <Badge variant={cnt.status === 'CLOSED' ? 'success' : cnt.status === 'PARTIALLY_FULFILLED' ? 'warning' : 'info'}>
                        {cnt.status === 'CLOSED' ? 'Erledigt' : cnt.status === 'PARTIALLY_FULFILLED' ? `${pct.toFixed(0)}%` : 'Aktiv'}
                      </Badge>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
