/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Customer, OpenItem } from '../types';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { NativeSelect } from '@/components/ui/native-select';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Receipt, TrendingDown, AlertOctagon, ShieldAlert, Plus, X, Check } from 'lucide-react';

interface FinancialOpenItemsPanelProps {
  customer: Customer;
  openItems: OpenItem[];
  onAddOpenItem: (vals: Partial<OpenItem>) => void;
}

function KpiCard({ icon, label, value, sub, accent }: { icon: React.ReactNode; label: string; value: string; sub: string; accent?: string }) {
  return (
    <div className="bg-card p-3 rounded-lg border border-border shadow-sm flex items-center justify-between">
      <div>
        <span className="text-xs uppercase font-medium text-muted-foreground">{label}</span>
        <p className={`font-bold text-lg mt-0.5 ${accent || 'text-foreground'}`}>{value}</p>
        <span className="text-xs text-muted-foreground block mt-0.5">{sub}</span>
      </div>
      <div className="p-2 bg-muted rounded-md border border-border text-muted-foreground">{icon}</div>
    </div>
  );
}

export default function FinancialOpenItemsPanel({ customer, openItems, onAddOpenItem }: FinancialOpenItemsPanelProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [invNo, setInvNo] = useState('');
  const [invAmount, setInvAmount] = useState('');
  const [invDate, setInvDate] = useState('');
  const [invDueDate, setInvDueDate] = useState('');
  const [invStatus, setInvStatus] = useState<'PENDING' | 'OVERDUE' | 'PAID' | 'DISPUTED'>('PENDING');
  const [invDunning, setInvDunning] = useState(0);
  const [isDrop, setIsDrop] = useState(false);
  const [invDesc, setInvDesc] = useState('');

  const totalOutstanding = openItems.filter(i => i.status !== 'PAID').reduce((s, i) => s + i.amount, 0);
  const totalOverdue = openItems.filter(i => i.status === 'OVERDUE').reduce((s, i) => s + i.amount, 0);
  const maxDunning = openItems.reduce((max, i) => (i.dunningLevel > max ? i.dunningLevel : max), 0);
  const limitUtilization = customer.creditLimit > 0 ? (totalOutstanding / customer.creditLimit) * 100 : 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!invNo || !invAmount) return;
    onAddOpenItem({
      invoiceNo: invNo, amount: Number(invAmount),
      date: invDate || new Date().toISOString().split('T')[0],
      dueDate: invDueDate || new Date().toISOString().split('T')[0],
      status: invStatus, dunningLevel: Number(invDunning),
      artKurzinfo: invDesc || 'Agrarlieferung', isDropShipment: isDrop,
    });
    setInvNo(''); setInvAmount(''); setInvDate(''); setInvDueDate('');
    setInvStatus('PENDING'); setInvDunning(0); setInvDesc(''); setIsDrop(false); setShowAddForm(false);
  };

  const statusBadge = (status: OpenItem['status']) => {
    switch (status) {
      case 'OVERDUE': return <Badge variant="destructive">Überfällig</Badge>;
      case 'PENDING': return <Badge variant="warning">Ausstehend</Badge>;
      case 'DISPUTED': return <Badge variant="info">Reklamiert</Badge>;
      default: return <Badge variant="success">Bezahlt</Badge>;
    }
  };

  return (
    <div className="space-y-4" id="financial-open-items-panel">

      {/* KPI cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <KpiCard icon={<Receipt size={15} />} label="Offenes Debitoren-Saldo" value={`EUR ${totalOutstanding.toLocaleString("de-DE", { minimumFractionDigits: 2 })}`} sub="Saldo offene Posten" />
        <KpiCard icon={<TrendingDown size={15} />} label="Überfällige Forderungen" value={`EUR ${totalOverdue.toLocaleString("de-DE", { minimumFractionDigits: 2 })}`} sub="Frist überschritten" accent="text-destructive" />
        <KpiCard icon={<AlertOctagon size={15} />} label="Aktivierte Mahnstufe" value={`Stufe ${maxDunning}`} sub={maxDunning === 0 ? 'Zahlungstreu' : `Mahnstufe ${maxDunning} aktiv`} accent={maxDunning > 0 ? 'text-[hsl(var(--color-semantic-warning-700-hsl))]' : 'text-[hsl(var(--color-semantic-success-700-hsl))]'} />

        <div className="bg-card p-3 rounded-lg border border-border shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <div>
              <span className="text-xs uppercase font-medium text-muted-foreground">Kreditrahmen</span>
              <p className="font-bold text-sm text-foreground mt-0.5">{limitUtilization.toFixed(1)}% beansprucht</p>
            </div>
            <Badge variant="info">Limit: {customer.creditLimit / 1000}k</Badge>
          </div>
          <div className="mt-2">
            <Progress value={Math.min(limitUtilization, 100)} className="h-1.5" />
            <div className="flex justify-between items-center text-xs text-muted-foreground mt-1">
              <span>Rest: EUR {(customer.creditLimit - totalOutstanding).toLocaleString("de-DE")}</span>
              <span>100%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Risk + exposure */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="bg-card p-3.5 rounded-lg border border-border shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-1.5 border-b border-border pb-1.5 mb-2">
              <ShieldAlert className="text-destructive" size={14} />
              <h4 className="font-medium text-xs text-muted-foreground uppercase">Debitoren-Risikoprofil</h4>
            </div>
            <p className="text-sm text-muted-foreground mb-3 leading-relaxed">
              Bonitätsbewertung basierend auf Liefertreue (W1–W10), Mahnstufen und Reklamationshistorie.
            </p>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between py-1 border-b border-border text-muted-foreground">
                <span>Zahlungsmoral:</span><span className="font-medium text-foreground">4,5 Tage Verzug</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border text-muted-foreground">
                <span>Skonto-Ausnutzung:</span><span className="font-medium text-[hsl(var(--color-semantic-warning-700-hsl))]">Selten</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border text-muted-foreground">
                <span>Mahnungsanzahl:</span><span className="font-medium text-destructive">{openItems.filter(i => i.dunningLevel > 0).length} Posten</span>
              </div>
            </div>
          </div>
          <div className="bg-muted/40 border border-border p-1.5 text-xs text-center text-muted-foreground rounded-md mt-2.5">
            Zahlungsrisiko: <span className="text-[hsl(var(--color-semantic-success-700-hsl))] font-semibold">Stabil (Low-Risk)</span>
          </div>
        </div>

        <div className="bg-card p-3.5 rounded-lg border border-border shadow-sm md:col-span-2">
          <div className="flex justify-between items-center border-b border-border pb-1.5 mb-2">
            <h4 className="font-medium text-xs text-muted-foreground uppercase">Erwartete Exponierung – Monate (2026)</h4>
            <Badge variant="success">Warenwert</Badge>
          </div>
          <div className="relative h-28 flex items-end justify-around pt-3 pb-1">
            {[
              { m: 'Jan', val: 12500 }, { m: 'Feb', val: 24000 }, { m: 'Mär', val: 18000 },
              { m: 'Apr', val: 28400 }, { m: 'Mai', val: 56000 }, { m: 'Jun', val: totalOutstanding > 0 ? totalOutstanding : 14250 },
            ].map((bar, i) => {
              const pct = (bar.val / 65000) * 100;
              return (
                <div key={i} className="flex flex-col items-center h-full justify-end w-12 group">
                  <span className="text-xs font-medium text-muted-foreground mb-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    {Math.round(bar.val / 100) / 10}k
                  </span>
                  <div className="w-5 rounded-t-md bg-primary transition-all duration-500" style={{ height: `${Math.max(pct, 5)}%` }} />
                  <span className="text-xs text-muted-foreground mt-1">{bar.m}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Ledger */}
      <div className="rounded-lg border border-border bg-card overflow-hidden" id="financial-ledger-table-block">
        <div className="bg-muted/60 px-3 py-2 border-b border-border flex justify-between items-center">
          <div className="flex items-center gap-1.5 text-foreground">
            <Receipt size={15} className="text-primary" />
            <h3 className="font-semibold text-sm">Offene Posten (OP-Warenrechnungen)</h3>
          </div>
          <Button variant="outline" size="sm" onClick={() => setShowAddForm(!showAddForm)} className="gap-1">
            {showAddForm ? <X size={13} /> : <Plus size={13} />}
            {showAddForm ? 'Schließen' : 'Warenrechnung anlegen'}
          </Button>
        </div>

        {showAddForm && (
          <form onSubmit={handleSubmit} className="p-3 bg-muted/30 border-b border-border grid grid-cols-12 gap-2 text-sm" id="inline-op-insert-form">
            <div className="col-span-6 md:col-span-2 space-y-1">
              <Label htmlFor="crm360-open-item-number" className="text-xs">Rechnungsnummer</Label>
              <Input id="crm360-open-item-number" type="text" required value={invNo} onChange={e => setInvNo(e.target.value)} placeholder="RE-260…" />
            </div>
            <div className="col-span-6 md:col-span-2 space-y-1">
              <Label htmlFor="crm360-open-item-net" className="text-xs">Nettobetrag (EUR)</Label>
              <Input id="crm360-open-item-net" type="number" required value={invAmount} onChange={e => setInvAmount(e.target.value)} placeholder="z.B. 14500" />
            </div>
            <div className="col-span-6 md:col-span-2 space-y-1">
              <Label className="text-xs">Rechnungsdatum</Label>
              <Input type="date" value={invDate} onChange={e => setInvDate(e.target.value)} />
            </div>
            <div className="col-span-6 md:col-span-2 space-y-1">
              <Label className="text-xs">Fälligkeit</Label>
              <Input type="date" value={invDueDate} onChange={e => setInvDueDate(e.target.value)} />
            </div>
            <div className="col-span-6 md:col-span-2 space-y-1">
              <Label className="text-xs">Status</Label>
              <NativeSelect value={invStatus} onChange={e => setInvStatus(e.target.value as typeof invStatus)} options={[
                { value: 'PENDING', label: 'Offen / Ausstehend' },
                { value: 'OVERDUE', label: 'Überfällig' },
                { value: 'DISPUTED', label: 'Reklamiert' },
                { value: 'PAID', label: 'Bezahlt' },
              ]} />
            </div>
            <div className="col-span-6 md:col-span-2 space-y-1">
              <Label className="text-xs">Mahnstufe</Label>
              <NativeSelect value={String(invDunning)} onChange={e => setInvDunning(Number(e.target.value))} options={[
                { value: '0', label: 'Stufe 0 – keine' },
                { value: '1', label: 'Stufe 1' },
                { value: '2', label: 'Stufe 2' },
                { value: '3', label: 'Stufe 3 – Inkasso' },
              ]} />
            </div>
            <div className="col-span-12 border-t border-dashed border-border pt-2 flex flex-col md:flex-row items-center gap-4 justify-between">
              <div className="flex items-center gap-4 flex-wrap">
                <Input id="crm360-open-item-description" type="text" required value={invDesc} onChange={e => setInvDesc(e.target.value)} placeholder="Produktinfo (z.B. Weizensaatgut)" className="w-80" />
                <label className="flex items-center gap-1.5 text-sm text-muted-foreground cursor-pointer select-none">
                  <input type="checkbox" checked={isDrop} onChange={e => setIsDrop(e.target.checked)} className="accent-primary" />
                  <span>Direktgeschäft / Streckenbezug?</span>
                </label>
              </div>
              <Button type="submit" size="sm" className="gap-1.5">
                <Check size={13} />
                OP verbuchen
              </Button>
            </div>
          </form>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="bg-muted/60 border-b border-border text-muted-foreground text-xs">
                <th className="p-2 font-medium">Rechnungs-Nr.</th>
                <th className="p-2 font-medium">Datum</th>
                <th className="p-2 font-medium">Fälligkeit</th>
                <th className="p-2 font-medium">Kurzinfo</th>
                <th className="p-2 font-medium text-center">Mahnstufe</th>
                <th className="p-2 font-medium text-center">Strecke?</th>
                <th className="p-2 font-medium text-center">Status</th>
                <th className="p-2 font-medium text-right">Forderung (Netto)</th>
              </tr>
            </thead>
            <tbody>
              {openItems.length === 0 ? (
                <tr>
                  <td colSpan={8} className="p-6 text-center text-muted-foreground italic">
                    Keine registrierten offenen Posten für diesen Kunden vorhanden.
                  </td>
                </tr>
              ) : (
                openItems.map(item => (
                  <tr key={item.id} className="border-b border-border hover:bg-muted/40 transition" id={`item-row-${item.id}`}>
                    <td className="p-2 font-semibold text-foreground">{item.invoiceNo}</td>
                    <td className="p-2 text-muted-foreground">{new Date(item.date).toLocaleDateString("de-DE")}</td>
                    <td className="p-2 text-muted-foreground">{new Date(item.dueDate).toLocaleDateString("de-DE")}</td>
                    <td className="p-2 text-foreground">{item.artKurzinfo}</td>
                    <td className="p-2 text-center">
                      <Badge variant={item.dunningLevel >= 2 ? 'destructive' : item.dunningLevel === 1 ? 'warning' : 'success'}>Stufe {item.dunningLevel}</Badge>
                    </td>
                    <td className="p-2 text-center">
                      <Badge variant={item.isDropShipment ? 'info' : 'muted'}>{item.isDropShipment ? 'Strecke' : 'Silo'}</Badge>
                    </td>
                    <td className="p-2 text-center">{statusBadge(item.status)}</td>
                    <td className="p-2 text-right font-semibold text-foreground">EUR {item.amount.toLocaleString("de-DE", { minimumFractionDigits: 2 })}</td>
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
