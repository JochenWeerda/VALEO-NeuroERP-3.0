/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { Customer } from '../types';
import { Badge } from '@/components/ui/badge';
import {
  Building,
  MapPin,
  Phone,
  Printer,
  Mail,
} from 'lucide-react';

interface CustomerHeaderProps {
  customer: Customer;
}

function FieldGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="md:col-span-4 space-y-1.5 rounded-md border border-border bg-card p-2.5">
      <div className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground border-b border-border pb-1 mb-1">
        {title}
      </div>
      {children}
    </div>
  );
}

export default function CustomerHeader({ customer }: CustomerHeaderProps) {
  return (
    <div className="rounded-lg border border-border bg-muted/40 p-3 text-sm shadow-sm" id="customer-identity-header-board">

      {/* Name and Debtor no title block */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-border pb-2 mb-3 gap-2">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-md bg-primary text-primary-foreground flex items-center justify-center font-bold text-xs shadow-sm">
            {customer.name.slice(0, 1).toUpperCase()}
          </div>
          <h2 className="font-bold text-base text-foreground leading-tight" id="master-cust-name-header">
            {customer.name}
          </h2>
          <Badge variant="secondary">Konto-Nr: {customer.debtorNo}</Badge>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>Sprache: DE</span>
          <span className="h-1.5 w-1.5 rounded-full bg-[hsl(var(--color-semantic-success-500-hsl))]" />
          <span>Währung: EUR</span>
        </div>
      </div>

      {/* Master Grid columns */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-3" id="master-header-grid-layout">

        {/* Address */}
        <FieldGroup title="Standort / Anschrift">
          <div className="flex items-start gap-1.5">
            <MapPin size={13} className="text-muted-foreground mt-0.5 flex-shrink-0" />
            <div className="leading-tight">
              <span className="font-medium text-foreground block">{customer.street || '—'}</span>
              <span className="font-semibold text-foreground block">{customer.zipCode} {customer.city}</span>
            </div>
          </div>
          {customer.coAffiliation && (
            <div className="pt-1 mt-1 border-t border-dashed border-border flex items-center gap-1 text-xs text-primary font-medium">
              <Building size={12} />
              <span>Verbund: {customer.coAffiliation}</span>
            </div>
          )}
        </FieldGroup>

        {/* Telecom */}
        <FieldGroup title="Telekommunikation">
          <div className="flex items-center gap-1.5">
            <Phone size={12} className="text-muted-foreground flex-shrink-0" />
            <span className="text-foreground truncate">Tel 1: <strong>{customer.phone1 || '—'}</strong></span>
          </div>
          <div className="flex items-center gap-1.5">
            {customer.fax ? (
              <>
                <Printer size={12} className="text-muted-foreground flex-shrink-0" />
                <span className="text-foreground truncate">Fax: <strong>{customer.fax}</strong></span>
              </>
            ) : (
              <>
                <Phone size={12} className="text-muted-foreground/50 flex-shrink-0" />
                <span className="text-muted-foreground italic">Tel 2: Keine Angabe</span>
              </>
            )}
          </div>
          <div className="flex items-center gap-1.5">
            <Mail size={12} className="text-primary flex-shrink-0" />
            {customer.email ? (
              <a href={`mailto:${customer.email}`} className="text-primary hover:underline font-medium truncate max-w-[190px]" title={customer.email}>
                {customer.email}
              </a>
            ) : (
              <span className="text-muted-foreground italic">Keine E-Mail</span>
            )}
          </div>
        </FieldGroup>

        {/* Responsibility / Finance */}
        <FieldGroup title="Verantwortung / Finanzen">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <span className="block text-[10px] uppercase font-semibold text-muted-foreground">Vertreter VB</span>
              <span className="block font-semibold text-primary mt-0.5">{customer.salesRepresentative || 'JW'}</span>
            </div>
            <div>
              <span className="block text-[10px] uppercase font-semibold text-muted-foreground">Disponent</span>
              <span className="block font-semibold text-foreground mt-0.5">{customer.dispatcher || 'Disp. 1'}</span>
            </div>
          </div>
          <div className="pt-1 mt-1 border-t border-dashed border-border flex items-center justify-between text-xs">
            <div className="flex items-center gap-1">
              <span className="text-[10px] uppercase font-semibold text-muted-foreground">KV-Limit</span>
              <strong className="text-foreground">EUR {customer.creditLimit.toLocaleString("de-DE")}</strong>
            </div>
            <div className="flex gap-1">
              <Badge variant={customer.revenueStatus === 'A' ? 'success' : 'warning'}>U: {customer.revenueStatus}</Badge>
              <Badge variant="secondary">ABC: {customer.abcStatus}</Badge>
            </div>
          </div>
        </FieldGroup>

      </div>

    </div>
  );
}
