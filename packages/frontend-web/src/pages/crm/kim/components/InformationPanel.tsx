/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 *
 * Information-Subtabs der Kundenakte (L3 „Information"-Menü). Module mit echter
 * Datenquelle (Profil, Kreditsicherheit, Konzern) zeigen Kundenwerte; noch nicht
 * fachlich hinterlegte Module zeigen einen stabilen Platzhalter mit Titel,
 * Beschreibung und leerem Tabellenlayout — niemals 404.
 */

import React from 'react';
import { Customer } from '../types';
import { Badge } from '@/components/ui/badge';
import { Info } from 'lucide-react';

export type InfoSection =
  | 'selektion' | 'profil' | 'mitbewerber' | 'kreditsicherheit'
  | 'kunden-artikel' | 'lieferanten-artikel' | 'preisvereinbarung'
  | 'konzern' | 'zusatzfelder';

interface InformationPanelProps {
  customer: Customer;
  section: InfoSection;
}

const META: Record<InfoSection, { title: string; desc: string }> = {
  'selektion': { title: 'Selektion', desc: 'Selektionskriterien und Zielgruppen-Zuordnung des Kunden.' },
  'profil': { title: 'Profil', desc: 'Geschäftsprofil und Kurzbeschreibung.' },
  'mitbewerber': { title: 'Mitbewerber', desc: 'Wettbewerbssituation und konkurrierende Lieferanten beim Kunden.' },
  'kreditsicherheit': { title: 'Kreditsicherheit', desc: 'Kreditversicherung, KV-Limit und Bonitätseinstufung.' },
  'kunden-artikel': { title: 'Kunden-Artikel', desc: 'Kundenspezifische Artikelzuordnungen und Artikelnummern.' },
  'lieferanten-artikel': { title: 'Lieferanten-Artikel', desc: 'Lieferantenartikel mit Bezug zu diesem Kunden.' },
  'preisvereinbarung': { title: 'Kunden-Preisvereinbarung', desc: 'Vereinbarte Preise, Rabatte und Konditionen.' },
  'konzern': { title: 'Konzernzugehörigkeit', desc: 'Konzern-/Verbundstruktur und Hauptkunde.' },
  'zusatzfelder': { title: 'Zusätzliche Felder/Angaben', desc: 'Erweiterte, mandantenspezifische Zusatzangaben.' },
};

function Placeholder({ section }: { section: InfoSection }) {
  const m = META[section];
  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      <div className="bg-muted/60 px-3 py-2 border-b border-border flex items-center gap-1.5">
        <Info size={15} className="text-primary" />
        <span className="text-sm font-semibold text-foreground">{m.title}</span>
        <Badge variant="muted" className="ml-2">in Vorbereitung</Badge>
      </div>
      <p className="px-3 py-2 text-sm text-muted-foreground border-b border-border">{m.desc}</p>
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="bg-muted/40 border-b border-border text-muted-foreground text-xs">
            <th className="p-2 font-medium">Eintrag</th>
            <th className="p-2 font-medium">Wert</th>
            <th className="p-2 font-medium">Stand</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td colSpan={3} className="p-8 text-center text-muted-foreground italic">
              Noch keine Einträge für diesen Bereich hinterlegt.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

function DataCard({ title, rows }: { title: string; rows: [string, React.ReactNode][] }) {
  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      <div className="bg-muted/60 px-3 py-2 border-b border-border flex items-center gap-1.5">
        <Info size={15} className="text-primary" />
        <span className="text-sm font-semibold text-foreground">{title}</span>
      </div>
      <dl className="grid grid-cols-[12rem_1fr] gap-x-3 gap-y-2 p-3 text-sm">
        {rows.map(([k, v]) => (
          <React.Fragment key={k}>
            <dt className="font-medium text-muted-foreground">{k}</dt>
            <dd className="text-foreground">{v ?? '—'}</dd>
          </React.Fragment>
        ))}
      </dl>
    </div>
  );
}

export default function InformationPanel({ customer, section }: InformationPanelProps) {
  if (section === 'profil') {
    return (
      <DataCard title="Profil" rows={[
        ['Name', customer.name],
        ['Kundengruppe', customer.custGroup || '—'],
        ['Umsatzstatus', <Badge key="u" variant={customer.revenueStatus === 'A' ? 'success' : 'warning'}>{customer.revenueStatus}</Badge>],
        ['ABC-Status', <Badge key="abc" variant="secondary">{customer.abcStatus}</Badge>],
        ['Profil-Zusammenfassung', customer.profileSummary || 'Keine Zusammenfassung hinterlegt.'],
      ]} />
    );
  }
  if (section === 'kreditsicherheit') {
    return (
      <DataCard title="Kreditsicherheit" rows={[
        ['KV-Limit', `EUR ${customer.creditLimit.toLocaleString('de-DE')}`],
        ['Umsatzstatus', customer.revenueStatus],
        ['ABC-Einstufung', customer.abcStatus],
        ['Warnhinweise', customer.alertMessages.length ? customer.alertMessages.join(' · ') : 'Keine'],
      ]} />
    );
  }
  if (section === 'konzern') {
    return (
      <DataCard title="Konzernzugehörigkeit" rows={[
        ['Hauptkunde', customer.mainCust || '—'],
        ['Konzern/Verbund', customer.coAffiliation || 'Kein Verbund hinterlegt.'],
        ['Debitor-Nr.', customer.debtorNo],
      ]} />
    );
  }
  return <Placeholder section={section} />;
}
