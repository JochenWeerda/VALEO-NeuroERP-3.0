/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 *
 * Kunden-Präsente (KIM-S3) — kundenbezogene Geschenke-PR mit Jahr-/AP-Filter,
 * Tabelle und Erfassungs-/Bearbeitungsformular. Backend: /crm/kim/.../gifts.
 */

import React, { useCallback, useEffect, useState } from 'react';
import { Customer, ContactPerson } from '../types';
import * as kimApi from '../kim-api';
import type { CustomerGift } from '../kim-api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { NativeSelect } from '@/components/ui/native-select';
import { useToast } from '@/hooks/use-toast';
import { Gift, Plus, X, Check, Pencil, Trash2, Loader2 } from 'lucide-react';

interface CustomerGiftsTabProps {
  customer: Customer;
  contacts: ContactPerson[];
  initialContactId?: string | null;
}

const CURRENT_YEAR = new Date().getFullYear();
const emptyForm = () => ({
  id: '' as string,
  date: new Date().toISOString().split('T')[0],
  sequenceNumber: '' as string,
  occasion: '',
  contactId: '',
  giftName: '',
  quantity: '1',
  operatorId: 'JW',
  salesRepId: 'JW',
});

export default function CustomerGiftsTab({ customer, contacts, initialContactId }: CustomerGiftsTabProps) {
  const { toast } = useToast();
  const [year, setYear] = useState<number>(CURRENT_YEAR);
  const [contactFilter, setContactFilter] = useState<string>(initialContactId || '');
  const [gifts, setGifts] = useState<CustomerGift[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<string>('');
  const [form, setForm] = useState(emptyForm());

  const contactName = useCallback((id?: string | null) => {
    if (!id) return '—';
    const c = contacts.find(c => c.id === id);
    return c ? `${c.firstName} ${c.name}`.trim() : id;
  }, [contacts]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setGifts(await kimApi.fetchGifts(customer.id, year, contactFilter || undefined));
    } catch (err) {
      console.error('Präsente konnten nicht geladen werden:', err);
      toast({ title: 'Präsente konnten nicht geladen werden', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  }, [customer.id, year, contactFilter, toast]);

  useEffect(() => { void load(); }, [load]);

  const openNew = () => { setForm(emptyForm()); setShowForm(true); };
  const openEdit = (g: CustomerGift) => {
    setForm({
      id: g.id,
      date: g.gift_date || new Date().toISOString().split('T')[0],
      sequenceNumber: g.sequence_number != null ? String(g.sequence_number) : '',
      occasion: g.occasion || '',
      contactId: g.contact_id || '',
      giftName: g.gift_name || '',
      quantity: String(g.quantity ?? 1),
      operatorId: g.operator || 'JW',
      salesRepId: g.sales_rep || 'JW',
    });
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (saving || !form.giftName) return;
    setSaving(true);
    const payload = {
      year,
      date: form.date || undefined,
      occasion: form.occasion || undefined,
      contactId: form.contactId || undefined,
      giftName: form.giftName,
      quantity: Number(form.quantity) || 1,
      operatorId: form.operatorId || undefined,
      salesRepId: form.salesRepId || undefined,
      sequenceNumber: form.sequenceNumber ? Number(form.sequenceNumber) : undefined,
    };
    try {
      if (form.id) await kimApi.updateGift(form.id, payload);
      else await kimApi.createGift(customer.id, payload);
      toast({ title: form.id ? 'Präsent aktualisiert' : 'Präsent angelegt', description: form.giftName });
      setShowForm(false);
      await load();
    } catch (err) {
      console.error('Präsent konnte nicht gespeichert werden:', err);
      toast({ title: 'Speichern fehlgeschlagen', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (pendingDelete) return;
    setPendingDelete(id);
    try {
      await kimApi.deleteGift(id);
      toast({ title: 'Präsent gelöscht' });
      await load();
    } catch (err) {
      console.error('Präsent konnte nicht gelöscht werden:', err);
      toast({ title: 'Löschen fehlgeschlagen', variant: 'destructive' });
    } finally {
      setPendingDelete('');
    }
  };

  const years = Array.from({ length: 6 }, (_, i) => CURRENT_YEAR - i);

  return (
    <div className="space-y-4" id="customer-gifts-tab">

      {/* Filter + Aktionen */}
      <div className="flex flex-wrap items-end justify-between gap-3 rounded-lg border border-border bg-muted/40 p-3">
        <div className="flex flex-wrap items-end gap-3">
          <div className="space-y-1">
            <Label className="text-xs">Jahr</Label>
            <NativeSelect
              value={String(year)}
              onChange={e => setYear(Number(e.target.value))}
              options={years.map(y => ({ value: String(y), label: String(y) }))}
            />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Ansprechpartner</Label>
            <NativeSelect
              value={contactFilter}
              onChange={e => setContactFilter(e.target.value)}
              options={[{ value: '', label: 'Alle' }, ...contacts.map(c => ({ value: c.id, label: `${c.firstName} ${c.name}`.trim() }))]}
            />
          </div>
        </div>
        <Button size="sm" onClick={openNew} className="gap-1" id="btn-gift-new">
          <Plus size={14} /> Präsent erfassen
        </Button>
      </div>

      {/* Erfassungs-/Bearbeitungsformular */}
      {showForm && (
        <form onSubmit={handleSubmit} className="grid grid-cols-12 gap-2 rounded-lg border border-border bg-card p-3 text-sm" id="gift-form">
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Datum</Label>
            <Input type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))} />
          </div>
          <div className="col-span-6 md:col-span-1 space-y-1">
            <Label className="text-xs">lfd. Nr.</Label>
            <Input value={form.sequenceNumber} onChange={e => setForm(f => ({ ...f, sequenceNumber: e.target.value }))} />
          </div>
          <div className="col-span-12 md:col-span-3 space-y-1">
            <Label className="text-xs">Anlass</Label>
            <Input value={form.occasion} onChange={e => setForm(f => ({ ...f, occasion: e.target.value }))} placeholder="z.B. Weihnachten" />
          </div>
          <div className="col-span-12 md:col-span-3 space-y-1">
            <Label className="text-xs">Präsent <span className="text-destructive">*</span></Label>
            <Input required value={form.giftName} onChange={e => setForm(f => ({ ...f, giftName: e.target.value }))} placeholder="z.B. Taschenmesser" />
          </div>
          <div className="col-span-6 md:col-span-1 space-y-1">
            <Label className="text-xs">Anzahl</Label>
            <Input type="number" min={1} value={form.quantity} onChange={e => setForm(f => ({ ...f, quantity: e.target.value }))} />
          </div>
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Ansprechpartner</Label>
            <NativeSelect
              value={form.contactId}
              onChange={e => setForm(f => ({ ...f, contactId: e.target.value }))}
              options={[{ value: '', label: '—' }, ...contacts.map(c => ({ value: c.id, label: `${c.firstName} ${c.name}`.trim() }))]}
            />
          </div>
          <div className="col-span-6 md:col-span-1 space-y-1">
            <Label className="text-xs">Bediener</Label>
            <Input value={form.operatorId} onChange={e => setForm(f => ({ ...f, operatorId: e.target.value }))} className="text-center" />
          </div>
          <div className="col-span-6 md:col-span-1 space-y-1">
            <Label className="text-xs">VB</Label>
            <Input value={form.salesRepId} onChange={e => setForm(f => ({ ...f, salesRepId: e.target.value }))} className="text-center" />
          </div>
          <div className="col-span-12 flex justify-end gap-2 border-t border-dashed border-border pt-2">
            <Button type="button" variant="outline" size="sm" onClick={() => setShowForm(false)}><X size={13} /> Abbrechen</Button>
            <Button type="submit" size="sm" disabled={saving} className="gap-1" id="btn-gift-save">
              {saving ? <Loader2 size={13} className="animate-spin" /> : <Check size={13} />} Zeile OK
            </Button>
          </div>
        </form>
      )}

      {/* Tabelle */}
      <div className="rounded-lg border border-border bg-card overflow-hidden">
        <div className="bg-muted/60 px-3 py-2 border-b border-border flex items-center gap-1.5">
          <Gift size={15} className="text-primary" />
          <span className="text-sm font-semibold text-foreground">Kunden-Präsente {year} ({gifts.length})</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="bg-muted/40 border-b border-border text-muted-foreground text-xs">
                <th className="p-2 font-medium">Datum</th>
                <th className="p-2 font-medium">Ansprechpartner</th>
                <th className="p-2 font-medium">Anlass</th>
                <th className="p-2 font-medium text-center">lfd. Nr.</th>
                <th className="p-2 font-medium">Präsent</th>
                <th className="p-2 font-medium text-center">Anzahl</th>
                <th className="p-2 font-medium text-center">VB</th>
                <th className="p-2 font-medium text-center">Bediener</th>
                <th className="p-2 font-medium text-right">Aktion</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={9} className="p-8 text-center text-muted-foreground"><Loader2 size={16} className="animate-spin inline" /> Lädt…</td></tr>
              ) : gifts.length === 0 ? (
                <tr><td colSpan={9} className="p-8 text-center text-muted-foreground italic">Keine Präsente für {year} erfasst.</td></tr>
              ) : (
                gifts.map(g => (
                  <tr key={g.id} className="border-b border-border hover:bg-muted/40 transition" id={`gift-row-${g.id}`}>
                    <td className="p-2 text-muted-foreground">{g.gift_date ? new Date(g.gift_date).toLocaleDateString('de-DE') : '—'}</td>
                    <td className="p-2 text-foreground">{contactName(g.contact_id)}</td>
                    <td className="p-2 text-muted-foreground">{g.occasion || '—'}</td>
                    <td className="p-2 text-center text-muted-foreground">{g.sequence_number ?? '—'}</td>
                    <td className="p-2 font-medium text-foreground">{g.gift_name || '—'}</td>
                    <td className="p-2 text-center">{g.quantity}</td>
                    <td className="p-2 text-center text-primary font-medium">{g.sales_rep || '—'}</td>
                    <td className="p-2 text-center text-muted-foreground">{g.operator || '—'}</td>
                    <td className="p-2">
                      <div className="flex justify-end gap-1">
                        <Button variant="outline" size="icon" className="h-7 w-7" onClick={() => openEdit(g)} title="Bearbeiten"><Pencil size={13} /></Button>
                        <Button variant="outline" size="icon" className="h-7 w-7 text-destructive hover:text-destructive" disabled={pendingDelete === g.id} onClick={() => handleDelete(g.id)} title="Löschen">
                          {pendingDelete === g.id ? <Loader2 size={13} className="animate-spin" /> : <Trash2 size={13} />}
                        </Button>
                      </div>
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
