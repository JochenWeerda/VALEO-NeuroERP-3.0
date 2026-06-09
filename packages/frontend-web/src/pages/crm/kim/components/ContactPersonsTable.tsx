/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { ContactPerson } from '../types';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { NativeSelect } from '@/components/ui/native-select';
import { Label } from '@/components/ui/label';
import { Phone, Calendar, UserCheck, Plus, X, Check, FolderOpen, Mail, Gift, Search } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

interface ContactPersonsTableProps {
  contactPersons: ContactPerson[];
  onAddContactPerson: (vals: Partial<ContactPerson>) => void;
  onEmailContact: (contact: ContactPerson) => void;
  onOpenPresents: (contact: ContactPerson) => void;
}

export default function ContactPersonsTable({
  contactPersons,
  onAddContactPerson,
  onEmailContact,
  onOpenPresents,
}: ContactPersonsTableProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedContactId, setSelectedContactId] = useState('');
  const [filter, setFilter] = useState('');
  const [showDetails, setShowDetails] = useState(false);
  const [salutation, setSalutation] = useState('Herr');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [position, setPosition] = useState('');
  const [phone1, setPhone1] = useState('');
  const [phone2, setPhone2] = useState('');
  const [fax, setFax] = useState('');
  const [priority, setPriority] = useState(2);
  const [birthdate, setBirthdate] = useState('');
  const [schedule, setSchedule] = useState<boolean[]>(Array(10).fill(false));
  const selectedContact = contactPersons.find((person) => person.id === selectedContactId) ?? null;
  const normalizedFilter = filter.trim().toLocaleLowerCase('de-DE');
  const filteredContacts = normalizedFilter
    ? contactPersons.filter((person) =>
        [person.name, person.firstName, person.position, person.phone1, person.phone2]
          .some((value) => value?.toLocaleLowerCase('de-DE').includes(normalizedFilter)),
      )
    : contactPersons;

  const handleToggleSchedule = (idx: number) => {
    setSchedule(prev => prev.map((v, i) => (i === idx ? !v : v)));
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!lastName) return;

    onAddContactPerson({
      salutation, name: lastName, firstName, position, phone1,
      phone2: phone2 || undefined, fax: fax || undefined, priority,
      birthdate: birthdate || undefined, weeklySchedule: schedule,
    });

    setFirstName(''); setLastName(''); setPosition(''); setPhone1(''); setPhone2('');
    setFax(''); setPriority(2); setBirthdate(''); setSchedule(Array(10).fill(false));
    setShowAddForm(false);
  };

  return (
    <div className="rounded-lg border border-border bg-card shadow-sm overflow-hidden" id="contact-persons-table-component">

      {/* Title bar */}
      <div className="bg-muted/60 border-b border-border px-3 py-2 flex justify-between items-center">
        <div className="flex items-center gap-1.5 font-semibold text-foreground text-sm">
          <UserCheck size={15} className="text-primary" />
          <span>Ansprechpartner / Anbauleitung ({contactPersons.length})</span>
        </div>
        <Button variant="outline" size="sm" onClick={() => setShowAddForm(!showAddForm)} className="gap-1">
          {showAddForm ? <X size={13} /> : <Plus size={13} />}
          {showAddForm ? 'Schließen' : 'Neuer Kontakt'}
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-2 border-b border-border bg-card px-3 py-2">
        <div className="relative min-w-56 flex-1">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
            placeholder="Ansprechpartner filtern"
            className="pl-8"
            data-action-id="crm360.contact.filter"
          />
        </div>
        <Button
          variant="outline"
          size="sm"
          disabled={!selectedContact}
          onClick={() => setShowDetails(true)}
          data-action-id="crm360.contact.open"
          className="gap-1"
        >
          <FolderOpen size={13} /> Öffnen
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={!selectedContact?.phone1}
          onClick={() => {
            if (selectedContact?.phone1) window.location.href = `tel:${selectedContact.phone1}`;
          }}
          data-action-id="crm360.contact.call"
          className="gap-1"
        >
          <Phone size={13} /> Telefon
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={!selectedContact}
          onClick={() => selectedContact && onEmailContact(selectedContact)}
          data-action-id="crm360.contact.email"
          className="gap-1"
        >
          <Mail size={13} /> E-Mail
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={!selectedContact}
          onClick={() => selectedContact && onOpenPresents(selectedContact)}
          data-action-id="crm360.contact.presents"
          className="gap-1"
        >
          <Gift size={13} /> Präsente
        </Button>
      </div>

      {/* Insert form */}
      {showAddForm && (
        <form onSubmit={handleFormSubmit} className="p-3 bg-muted/30 border-b border-border grid grid-cols-12 gap-2 text-sm" id="inline-cp-insert-form">
          <div className="col-span-6 md:col-span-1 space-y-1">
            <Label className="text-xs">Anrede</Label>
            <NativeSelect
              value={salutation}
              onChange={e => setSalutation(e.target.value)}
              options={[{ value: 'Herr', label: 'Herr' }, { value: 'Frau', label: 'Frau' }, { value: 'Firma', label: 'Firma' }]}
            />
          </div>
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Vorname</Label>
            <Input value={firstName} onChange={e => setFirstName(e.target.value)} placeholder="z.B. Eimo" />
          </div>
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Nachname / Name</Label>
            <Input required value={lastName} onChange={e => setLastName(e.target.value)} placeholder="z.B. de Buhr" />
          </div>
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Position / Verantwortung</Label>
            <Input value={position} onChange={e => setPosition(e.target.value)} placeholder="z.B. Gutsverwalter" />
          </div>
          <div className="col-span-6 md:col-span-2 space-y-1">
            <Label className="text-xs">Telefon 1</Label>
            <Input required value={phone1} onChange={e => setPhone1(e.target.value)} placeholder="Durchwahl" />
          </div>
          <div className="col-span-6 md:col-span-1 space-y-1">
            <Label className="text-xs">Prio</Label>
            <Input type="number" min={1} max={9999} value={priority} onChange={e => setPriority(Number(e.target.value))} />
          </div>
          <div className="col-span-12 md:col-span-2 space-y-1">
            <Label className="text-xs">Geburtsdatum</Label>
            <Input type="date" value={birthdate} onChange={e => setBirthdate(e.target.value)} />
          </div>

          <div className="col-span-12 flex flex-col md:flex-row items-center gap-4 pt-3 border-t border-dashed border-border justify-between">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">Wochenplanung (Erreichbarkeit W1–W10):</span>
              <div className="flex gap-0.5">
                {Array(10).fill(0).map((_, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => handleToggleSchedule(i)}
                    className={`w-6 h-6 text-xs rounded-md border transition ${schedule[i] ? 'bg-primary text-primary-foreground border-transparent' : 'bg-card border-border text-muted-foreground hover:bg-muted'}`}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>
            </div>
            <Button type="submit" size="sm" className="gap-1 self-end">
              <Check size={13} />
              Sichern
            </Button>
          </div>
        </form>
      )}

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm border-collapse">
          <thead>
            <tr className="bg-muted/60 border-b border-border text-muted-foreground text-xs">
              <th className="p-2 font-medium">Anrede</th>
              <th className="p-2 font-medium">Name</th>
              <th className="p-2 font-medium">Vorname</th>
              <th className="p-2 font-medium">Position</th>
              <th className="p-2 font-medium text-center">Prio</th>
              <th className="p-2 font-medium text-center">Geburtsdatum</th>
              <th className="p-2 font-medium">Telefon 1</th>
              <th className="p-2 font-medium">Telefon 2 / Mobil</th>
              <th className="p-2 font-medium text-center">Entscheid</th>
              <th className="p-2 font-medium text-center border-l border-border" colSpan={10}>Lieferplan-Rotation (W1–W10)</th>
            </tr>
          </thead>
          <tbody>
            {filteredContacts.length === 0 ? (
              <tr>
                <td colSpan={19} className="p-6 text-center text-muted-foreground italic">
                  Keine zugeordneten Kontakt-Partner im System hinterlegt.
                </td>
              </tr>
            ) : (
              filteredContacts.map((person) => (
                <tr
                  key={person.id}
                  className={`border-b border-border transition cursor-pointer ${
                    selectedContactId === person.id ? 'bg-primary/10' : 'hover:bg-muted/40'
                  }`}
                  id={`cp-row-${person.id}`}
                  data-action-id="crm360.contact.select"
                  aria-selected={selectedContactId === person.id}
                  onClick={() => setSelectedContactId(person.id)}
                  onDoubleClick={() => {
                    setSelectedContactId(person.id);
                    setShowDetails(true);
                  }}
                >
                  <td className="p-2 text-muted-foreground">{person.salutation}</td>
                  <td className="p-2 font-semibold text-foreground">{person.name}</td>
                  <td className="p-2 text-foreground">{person.firstName}</td>
                  <td className="p-2"><Badge variant="secondary">{person.position || 'Anbauleitung'}</Badge></td>
                  <td className="p-2 text-center">
                    <Badge variant={person.priority === 1 ? 'destructive' : 'muted'}>{person.priority}</Badge>
                  </td>
                  <td className="p-2 text-center text-muted-foreground whitespace-nowrap">
                    {person.birthdate ? (
                      <span className="flex items-center justify-center gap-1 text-xs">
                        <Calendar size={11} className="text-muted-foreground" />
                        {new Date(person.birthdate).toLocaleDateString("de-DE")}
                      </span>
                    ) : '—'}
                  </td>
                  <td className="p-2">
                    {person.phone1 ? (
                      <a href={`tel:${person.phone1}`} className="text-primary hover:underline font-medium flex items-center gap-1">
                        <Phone size={10} /> {person.phone1}
                      </a>
                    ) : '—'}
                  </td>
                  <td className="p-2">
                    {person.phone2 ? (
                      <a href={`tel:${person.phone2}`} className="text-primary hover:underline font-medium flex items-center gap-1">
                        <Phone size={10} /> {person.phone2}
                      </a>
                    ) : <span className="text-muted-foreground">—</span>}
                  </td>
                  <td className="p-2 text-center"><Badge variant="success">EN</Badge></td>

                  {Array(10).fill(0).map((_, idx) => {
                    const isWeekActive = person.weeklySchedule?.[idx];
                    return (
                      <td key={idx} className={`p-1 text-center ${idx === 0 ? 'border-l border-border' : ''}`}>
                        <span
                          className={`w-4 h-4 rounded text-[9px] font-semibold inline-flex items-center justify-center border ${isWeekActive ? 'bg-primary text-primary-foreground border-transparent' : 'bg-muted border-border text-muted-foreground/40'}`}
                          title={`Lieferzeitfenster Woche ${idx + 1}`}
                        >
                          {idx + 1}
                        </span>
                      </td>
                    );
                  })}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent className="max-w-md" data-testid="crm360-contact-details-dialog">
          <DialogHeader>
            <DialogTitle>Ansprechpartner</DialogTitle>
          </DialogHeader>
          {selectedContact && (
            <dl className="grid grid-cols-[8rem_1fr] gap-2 text-sm">
              <dt className="text-muted-foreground">Name</dt>
              <dd>{selectedContact.salutation} {selectedContact.firstName} {selectedContact.name}</dd>
              <dt className="text-muted-foreground">Position</dt>
              <dd>{selectedContact.position || 'Nicht hinterlegt'}</dd>
              <dt className="text-muted-foreground">Telefon</dt>
              <dd>{selectedContact.phone1 || 'Nicht hinterlegt'}</dd>
              <dt className="text-muted-foreground">Mobil</dt>
              <dd>{selectedContact.phone2 || 'Nicht hinterlegt'}</dd>
              <dt className="text-muted-foreground">Priorität</dt>
              <dd>{selectedContact.priority}</dd>
            </dl>
          )}
        </DialogContent>
      </Dialog>

    </div>
  );
}
