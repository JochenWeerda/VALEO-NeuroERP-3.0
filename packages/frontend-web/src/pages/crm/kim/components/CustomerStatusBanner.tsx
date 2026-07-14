/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { Customer } from '../types';
import { Badge } from '@/components/ui/badge';
import { ShieldAlert, AlertOctagon, HelpCircle } from 'lucide-react';

interface CustomerStatusBannerProps {
  customer: Customer;
  totalOutstanding: number;
}

export default function CustomerStatusBanner({ customer, totalOutstanding }: CustomerStatusBannerProps) {
  const isGesperrt = customer.alertMessages.some(m => m.toLowerCase().includes('gesperrt'));
  const isKreditWarning = totalOutstanding > customer.creditLimit || customer.alertMessages.some(m => m.toLowerCase().includes('limit'));
  const otherAlerts = customer.alertMessages.filter(m => !m.toLowerCase().includes('gesperrt') && !m.toLowerCase().includes('limit'));

  if (customer.alertMessages.length === 0 && !isKreditWarning && !customer.chefAnweisung) {
    return null;
  }

  return (
    <div className="flex flex-col gap-1.5" id="customer-status-banners-container">

      {/* GESPERRT */}
      {isGesperrt && (
        <div className="flex items-center gap-2 rounded-md bg-destructive px-3 py-1.5 text-sm font-medium text-destructive-foreground shadow-sm" id="banner-lock">
          <AlertOctagon size={15} className="shrink-0" />
          <div className="flex-1">
            Debitorenkonto ist gesperrt! Keine Lieferungen, Warenausgänge oder Verträge ohne Freigabe der Geschäftsführung.
          </div>
          <Badge variant="outline" className="border-destructive-foreground/40 text-destructive-foreground">GESPERRT</Badge>
        </div>
      )}

      {/* KREDIT-LIMIT */}
      {isKreditWarning && (
        <div className="flex items-center gap-2 rounded-md border-l-4 border-[hsl(var(--color-semantic-warning-500-hsl))] bg-[hsl(var(--color-semantic-warning-50-hsl))] px-3 py-1.5 text-sm text-[hsl(var(--color-semantic-warning-700-hsl))] shadow-sm dark:bg-[hsl(var(--color-semantic-warning-500-hsl)/0.15)] dark:text-[hsl(var(--color-semantic-warning-50-hsl))]" id="banner-credit-alert">
          <ShieldAlert size={15} className="shrink-0" />
          <div className="flex-1">
            Kreditlinienüberlauf möglich: Offener Saldo <strong>EUR {totalOutstanding.toLocaleString("de-DE", { minimumFractionDigits: 2 })}</strong> bei KV-Limit <strong>EUR {customer.creditLimit.toLocaleString("de-DE")}</strong>.
          </div>
        </div>
      )}

      {/* CHEF-ANWEISUNG */}
      {customer.chefAnweisung && (
        <div className="flex items-start gap-2 rounded-md border-l-4 border-destructive bg-destructive/5 px-3 py-1.5 text-sm text-foreground shadow-sm" id="banner-chef-instructions">
          <ShieldAlert size={15} className="text-destructive shrink-0 mt-0.5" />
          <div className="flex-1">
            <Badge variant="destructive" className="mr-2 align-middle">Chef-Anweisung</Badge>
            <strong>{customer.chefAnweisung}</strong>
          </div>
        </div>
      )}

      {/* OTHER ALERTS */}
      {otherAlerts.length > 0 && (
        <div className="flex items-center gap-2 rounded-md border-l-4 border-[hsl(var(--color-semantic-info-500-hsl))] bg-[hsl(var(--color-semantic-info-50-hsl))] px-3 py-1.5 text-sm text-[hsl(var(--color-semantic-info-700-hsl))] shadow-sm dark:bg-[hsl(var(--color-semantic-info-500-hsl)/0.15)] dark:text-[hsl(var(--color-semantic-info-50-hsl))]" id="banner-other-alerts">
          <HelpCircle size={15} className="shrink-0" />
          <div className="flex-1 flex gap-2 items-center flex-wrap">
            <span>Sondersignal:</span>
            {otherAlerts.map((m, i) => (
              <Badge key={i} variant="info">{m}</Badge>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
