/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type RefType = 'OFFER' | 'ORDER' | 'CONTRACT' | 'DELIVERY_NOTE' | 'INVOICE' | 'NONE';

export interface Customer {
  id: string;
  name: string;
  debtorNo: string;
  custGroup?: string;
  mainCust?: string;
  coAffiliation?: string;
  street: string;
  zipCode: string;
  city: string;
  postBox?: string;
  phone1: string;
  phone2?: string;
  fax?: string;
  email: string;
  homepage?: string;
  salesRepresentative: string; // VB
  dispatcher: string;         // Disp
  creditLimit: number;        // KV-Limit
  revenueStatus: 'A' | 'B' | 'C'; // Umsatzstatus
  abcStatus: 'A' | 'B' | 'C' | 'D'; // ABC-Status
  profileImage?: string;      // Image placeholder/url
  alertMessages: string[];      // Red banner warnings like "Buhr de Reina -> neu 510200"
  chefAnweisung: string;      // Chef-Anweisung/Alert instruction notes
  profileSummary?: string;    // Brief business summary
}

export interface ContactPerson {
  id: string;
  customerId: string;
  salutation: string; // Anrede
  name: string;
  firstName: string;
  position: string;
  birthdate?: string;
  priority: number;
  phone1: string;
  phone2?: string;
  email?: string;
  fax?: string;
  weeklySchedule: boolean[]; // W1 to W10 status flags for schedule planning
}

export interface ContactLog {
  id: string;
  customerId: string;
  direction: 'INCOMING' | 'OUTGOING'; // Richtung
  date: string;
  completed: boolean; // erl.
  artKurzinfo: string; // Art/Kurzinfo (Anzeige; == betreff)
  art?: string;        // Kontaktart: persoenlich/telefon/email/whatsapp
  betreff?: string;    // Betreffzeile
  kommentar?: string;  // Freitext-Kommentar (blob)
  ccIntern?: string;   // CC: interner Empfaenger (Mitarbeiter/Abteilung) oder E-Mail
  operator: string;    // Bediener
  reSubmissionDate?: string; // Wiedervorlage
  dispatcher?: string; // Disponent
  hasScan?: boolean;   // Dok. Scan
  emailSent?: boolean; // E-Mail Gesendet
  emailDirection?: 'IN' | 'OUT';
  hasAnhang?: boolean; // E-Mail Anhang
  fileLinked?: string; // Datei
  referenceType: RefType; // Verweis Typ
  referenceNo?: string;  // Verweis Nummer
}

export interface OpenItem {
  id: string;
  customerId: string;
  invoiceNo: string;
  date: string;
  dueDate: string;
  amount: number;
  dunningLevel: number; // 0 = none, 1 = first warning, 2 = second, 3 = legal
  status: 'PENDING' | 'OVERDUE' | 'PAID' | 'DISPUTED';
  artKurzinfo: string;
  operator: string;
  isDropShipment: boolean; // Strecken-Geschäft
}

export interface BusinessDocument {
  id: string;
  customerId: string;
  type: 'OFFER' | 'ORDER' | 'DELIVERY_NOTE' | 'PURCHASE_OFFER' | 'PURCHASE_SETTLEMENT' | 'THIRD_PARTY_STOCK'; 
  docNo: string;
  date: string;
  operator: string;
  representative: string; // Vertreter
  plannedDeliveryDate?: string;
  netAmount: number;
  taxAmount: number;
  grossAmount: number;
  completed: boolean;
}
