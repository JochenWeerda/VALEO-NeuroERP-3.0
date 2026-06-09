/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 *
 * Ansprechpartner-Erweiterung (KIM-S4): Werbe-/Marketingpräferenz-Matrix
 * (je Kategorie: nein / Firma / Privat) + DSGVO-Pseudonymisierung.
 * Backend: /crm/kim/contacts/{id}/marketing-prefs + /pseudonymize.
 */

import React, { useCallback, useEffect, useState } from 'react';
import { Customer, ContactPerson } from '../types';
import * as kimApi from '../kim-api';
import type { MarketingPreference } from '../kim-api';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { NativeSelect } from '@/components/ui/native-select';
import { Badge } from '@/components/ui/badge';
import {
  Dialog, DialogContent, DialogHeader, DialogFooter, DialogTitle, DialogDescription,
} from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { Megaphone, ShieldOff, Loader2 } from 'lucide-react';

interface Props {
  customer: Customer;
  contacts: ContactPerson[];
}

const CATEGORIES: { code: string; label: string }[] = [
  { code: 'NEWSLETTER', label: 'E-Mail-Newsletter' },
  { code: 'POST', label: 'Postwerbung' },
  { code: 'TELEFON', label: 'Telefonwerbung' },
  { code: 'WHATSAPP', label: 'WhatsApp / Messenger' },
  { code: 'MESSEN', label: 'Messen & Events' },
  { code: 'PRODUKTINFO', label: 'Produktinformationen' },
];

const CHOICES: { value: MarketingPreference; label: string }[] = [
  { value: 'none', label: 'nein' },
  { value: 'company', label: 'Firma' },
  { value: 'private', label: 'Privat' },
];

export default function CustomerContactMarketing({ customer, contacts }: Props) {
  const { toast } = useToast();
  const [contactId, setContactId] = useState<string>('');
  const [prefs, setPrefs] = useState<Record<string, MarketingPreference>>({});
  const [loading, setLoading] = useState(false);
  const [savingKey, setSavingKey] = useState<string>('');
  const [confirmPseudo, setConfirmPseudo] = useState(false);
  const [pseudonymizing, setPseudonymizing] = useState(false);

  useEffect(() => {
    if (!contactId && contacts.length > 0) setContactId(contacts[0].id);
  }, [contacts, contactId]);

  const load = useCallback(async () => {
    if (!contactId) { setPrefs({}); return; }
    setLoading(true);
    try {
      const rows = await kimApi.fetchMarketingPrefs(contactId);
      const map: Record<string, MarketingPreference> = {};
      rows.forEach(r => { map[r.category_code] = r.preference; });
      setPrefs(map);
    } catch (err) {
      console.error('Werbepräferenzen konnten nicht geladen werden:', err);
      toast({ title: 'Werbepräferenzen konnten nicht geladen werden', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  }, [contactId, toast]);

  useEffect(() => { void load(); }, [load]);

  const setPref = async (code: string, label: string, value: MarketingPreference) => {
    if (!contactId || savingKey) return;
    setSavingKey(code);
    const prev = prefs[code];
    setPrefs(p => ({ ...p, [code]: value })); // optimistisch
    try {
      await kimApi.setMarketingPref(contactId, code, value, label, customer.debtorNo);
    } catch (err) {
      console.error('Werbepräferenz konnte nicht gespeichert werden:', err);
      setPrefs(p => ({ ...p, [code]: prev ?? 'none' })); // rollback
      toast({ title: 'Speichern fehlgeschlagen', variant: 'destructive' });
    } finally {
      setSavingKey('');
    }
  };

  const doPseudonymize = async () => {
    if (!contactId || pseudonymizing) return;
    setPseudonymizing(true);
    try {
      await kimApi.pseudonymizeContact(contactId);
      toast({ title: 'Ansprechpartner pseudonymisiert', description: 'Personenbezogene Daten wurden DSGVO-konform neutralisiert.' });
      setConfirmPseudo(false);
    } catch (err) {
      console.error('Pseudonymisierung fehlgeschlagen:', err);
      toast({ title: 'Pseudonymisierung fehlgeschlagen', variant: 'destructive' });
    } finally {
      setPseudonymizing(false);
    }
  };

  const selectedContact = contacts.find(c => c.id === contactId);

  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden" id="contact-marketing-panel">
      <div className="bg-muted/60 px-3 py-2 border-b border-border flex flex-wrap items-center justify-between gap-2">
        <span className="text-sm font-semibold text-foreground flex items-center gap-1.5">
          <Megaphone size={15} className="text-primary" />
          Werbe-/Marketingpräferenzen &amp; Datenschutz
        </span>
        <div className="flex items-center gap-2">
          <Label className="text-xs">Ansprechpartner</Label>
          <NativeSelect
            value={contactId}
            onChange={e => setContactId(e.target.value)}
            options={contacts.length
              ? contacts.map(c => ({ value: c.id, label: `${c.firstName} ${c.name}`.trim() || c.id }))
              : [{ value: '', label: '— kein Ansprechpartner —' }]}
          />
        </div>
      </div>

      {!contactId ? (
        <p className="p-6 text-center text-sm text-muted-foreground italic">Kein Ansprechpartner vorhanden.</p>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="bg-muted/40 border-b border-border text-muted-foreground text-xs">
                  <th className="p-2 font-medium">Werbekanal</th>
                  {CHOICES.map(ch => <th key={ch.value} className="p-2 font-medium text-center w-20">{ch.label}</th>)}
                </tr>
              </thead>
              <tbody>
                {CATEGORIES.map(cat => {
                  const cur = prefs[cat.code] ?? 'none';
                  return (
                    <tr key={cat.code} className="border-b border-border hover:bg-muted/40" id={`mkt-row-${cat.code}`}>
                      <td className="p-2 text-foreground">{cat.label}</td>
                      {CHOICES.map(ch => (
                        <td key={ch.value} className="p-2 text-center">
                          <input
                            type="radio"
                            name={`mkt-${cat.code}`}
                            className="accent-primary"
                            disabled={loading || savingKey === cat.code}
                            checked={cur === ch.value}
                            onChange={() => setPref(cat.code, cat.label, ch.value)}
                            aria-label={`${cat.label}: ${ch.label}`}
                          />
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between gap-2 border-t border-border p-2.5">
            <span className="text-xs text-muted-foreground">
              Einwilligungen je Kanal — „Firma" = geschäftlich, „Privat" = privat, „nein" = keine Werbung.
            </span>
            <Button
              variant="outline"
              size="sm"
              className="gap-1 text-destructive hover:text-destructive"
              onClick={() => setConfirmPseudo(true)}
              id="btn-contact-pseudonymize"
            >
              <ShieldOff size={14} /> Pseudonymisieren
            </Button>
          </div>
        </>
      )}

      <Dialog open={confirmPseudo} onOpenChange={(o) => !o && setConfirmPseudo(false)}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><ShieldOff size={16} className="text-destructive" /> Pseudonymisieren</DialogTitle>
            <DialogDescription>
              {selectedContact ? `${selectedContact.firstName} ${selectedContact.name}`.trim() : ''} — personenbezogene Daten
              werden DSGVO-konform durch neutrale Werte ersetzt. Das kann nicht rückgängig gemacht werden.
            </DialogDescription>
          </DialogHeader>
          <div className="text-sm text-muted-foreground">
            <Badge variant="destructive" className="mb-2">Unwiderruflich</Badge>
            <p>Name, Vorname, Telefonnummern und Geburtsdatum werden entfernt; ein Pseudonymisierungs-Marker wird gesetzt.</p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmPseudo(false)}>Abbrechen</Button>
            <Button variant="destructive" onClick={doPseudonymize} disabled={pseudonymizing} className="gap-1">
              {pseudonymizing && <Loader2 size={14} className="animate-spin" />} Pseudonymisieren
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
