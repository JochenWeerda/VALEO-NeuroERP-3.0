/**
 * Visual Tour — vollständige Prüfung aller Seiten und Masken
 *
 * Prüft: Overflow, echte 404-Seiten, winzige Schriften, Konsolefehler
 * Viewports: Desktop 1440×900, Tablet 1024×768, Mobile 390×844
 * Screenshots: Desktop (alle Seiten), Tablet + Mobile (nur bei Problemen)
 *
 * Issues werden pro Test in issues-raw/ geschrieben und von
 * visual-tour-teardown.ts zu issues.json aggregiert.
 *
 * Schnellstart (Vite läuft bereits auf :5177):
 *   FRONTEND_BASE_URL=http://127.0.0.1:5177 \
 *   VISUAL_TOUR_WORKERS=4 npx playwright test tests/e2e/visual-tour.spec.ts --project=chromium
 */
import { test, expect } from '@playwright/test'
import type { Page } from '@playwright/test'
import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const PLAYWRIGHT_FRONTEND_PORT = process.env.PLAYWRIGHT_FRONTEND_PORT ?? '5177'
const BASE_URL = process.env.FRONTEND_BASE_URL ?? `http://127.0.0.1:${PLAYWRIGHT_FRONTEND_PORT}`
const SCREENSHOT_DIR = path.join(__dirname, '../../visual-tour-results')
const RAW_DIR = path.join(SCREENSHOT_DIR, 'issues-raw')

const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900,  screenshot: true  },
  { name: 'tablet',  width: 1024, height: 768,  screenshot: false },
  { name: 'mobile',  width: 390,  height: 844,  screenshot: false },
]

// ---------------------------------------------------------------------------
// Route-Liste — statische Routen, keine :id-Parameter, keine Auth/Error-Seiten
// ---------------------------------------------------------------------------
const ROUTES: Array<{ path: string; label: string; group: string }> = [
  // Haupt-Dashboard
  { path: '/',                                    label: 'Dashboard',                           group: 'core' },
  { path: '/dashboard/customizable',              label: 'Dashboard Customizable',              group: 'core' },
  { path: '/dashboard/einkauf',                   label: 'Dashboard Einkauf',                   group: 'core' },
  { path: '/dashboard/sales',                     label: 'Dashboard Sales',                     group: 'core' },
  { path: '/management/executive-dashboard',      label: 'Executive Dashboard',                 group: 'core' },
  { path: '/copilot',                             label: 'AI Copilot',                          group: 'core' },
  { path: '/inbox',                               label: 'Inbox',                               group: 'core' },
  { path: '/benachrichtigungen',                  label: 'Benachrichtigungen',                  group: 'core' },

  // Agrar
  { path: '/agrar/ernte',                         label: 'Agrar Ernte',                         group: 'agrar' },
  { path: '/agrar/ernte-annahme-erfassung',       label: 'Ernte-Annahme Erfassung',             group: 'agrar' },
  { path: '/agrar/erntefenster-konfig',           label: 'Erntefenster Konfiguration',          group: 'agrar' },
  { path: '/agrar/maschinenauslastung',           label: 'Maschinenauslastung',                 group: 'agrar' },
  { path: '/agrar/bodenproben',                   label: 'Bodenproben',                         group: 'agrar' },
  { path: '/agrar/biostimulanzien',               label: 'Biostimulanzien',                     group: 'agrar' },
  { path: '/agrar/wetter/prognose',               label: 'Wetterprognose',                      group: 'agrar' },
  { path: '/agrar/wetterwarnung',                 label: 'Wetterwarnungen',                     group: 'agrar' },
  { path: '/agrar/saatgut',                       label: 'Saatgut Übersicht',                   group: 'agrar' },
  { path: '/agrar/saatgut/liste',                 label: 'Saatgut Liste',                       group: 'agrar' },
  { path: '/agrar/saatgut/sortenregister',        label: 'Sortenregister',                      group: 'agrar' },
  { path: '/agrar/saatgut/stamm',                 label: 'Saatgut Stamm',                       group: 'agrar' },
  { path: '/agrar/saatgut/bestellung',            label: 'Saatgut Bestellung',                  group: 'agrar' },
  { path: '/agrar/saatzucht',                     label: 'Saatzucht',                           group: 'agrar' },
  { path: '/agrar/duenger',                       label: 'Dünger',                              group: 'agrar' },
  { path: '/agrar/duenger-liste',                 label: 'Dünger Liste',                        group: 'agrar' },
  { path: '/agrar/duenger/bedarfsrechner',        label: 'Dünger Bedarfsrechner',               group: 'agrar' },
  { path: '/agrar/duenger/mischungen',            label: 'Dünger Mischungen',                   group: 'agrar' },
  { path: '/agrar/psm',                           label: 'PSM Übersicht',                       group: 'agrar' },
  { path: '/agrar/psm/abgabedokumentation',       label: 'PSM Abgabedokumentation',             group: 'agrar' },
  { path: '/agrar/psm/auflagen-manager',          label: 'PSM Auflagen-Manager',                group: 'agrar' },
  { path: '/agrar/psm/beratung',                  label: 'PSM Beratung',                        group: 'agrar' },
  { path: '/agrar/psm/resistenz',                 label: 'PSM Resistenz',                       group: 'agrar' },
  { path: '/agrar/psm/sachkunde-register',        label: 'PSM Sachkunde',                       group: 'agrar' },
  { path: '/agrar/psm/wasserschutz',              label: 'PSM Wasserschutz',                    group: 'agrar' },
  { path: '/agrar/pflanzenschutz/applikation',    label: 'PSM Applikation',                     group: 'agrar' },
  { path: '/agrar/feldbuch/schlagkartei',         label: 'Feldbuch Schlagkartei',               group: 'agrar' },
  { path: '/agrar/feldbuch/massnahmen',           label: 'Feldbuch Maßnahmen',                  group: 'agrar' },
  { path: '/agrar/feldbuch/schlag/neu',           label: 'Feldbuch Schlag Neu',                 group: 'agrar' },
  { path: '/agrar/schlaege/karte',                label: 'Schläge Karte',                       group: 'agrar' },

  // Annahme
  { path: '/annahme/rohware',                     label: 'Annahme Rohware',                     group: 'annahme' },
  { path: '/annahme/warteschlange',               label: 'Annahme Warteschlange',               group: 'annahme' },
  { path: '/annahme/qualitaets-check',            label: 'Annahme Qualitätscheck',              group: 'annahme' },
  { path: '/annahme/lkw-registrierung',           label: 'LKW Registrierung',                   group: 'annahme' },
  { path: '/annahme/abrechnung',                  label: 'Annahme Abrechnung',                  group: 'annahme' },
  { path: '/silo/kapazitaeten',                   label: 'Silo Kapazitäten',                    group: 'annahme' },

  // Einkauf
  { path: '/einkauf/bestellungen',                label: 'Einkauf Bestellungen',                group: 'einkauf' },
  { path: '/einkauf/bestellungen/neu',            label: 'Einkauf Bestellung Neu',              group: 'einkauf' },
  { path: '/einkauf/bestellvorschlaege',          label: 'Bestellvorschläge',                   group: 'einkauf' },
  { path: '/einkauf/bestellvorschlag-lager',      label: 'Bestellvorschlag Lager',              group: 'einkauf' },
  { path: '/einkauf/bestellvorschlag-rohware',    label: 'Bestellvorschlag Rohware',            group: 'einkauf' },
  { path: '/einkauf/bestellvorschlag-verkauf',    label: 'Bestellvorschlag Verkauf',            group: 'einkauf' },
  { path: '/einkauf/anfragen',                    label: 'Einkauf Anfragen',                    group: 'einkauf' },
  { path: '/einkauf/anfrage',                     label: 'Einkauf Anfrage',                     group: 'einkauf' },
  { path: '/einkauf/anfrage-erfassung',           label: 'Anfrage Erfassung',                   group: 'einkauf' },
  { path: '/einkauf/angebote',                    label: 'Einkauf Angebote',                    group: 'einkauf' },
  { path: '/einkauf/angebote-liste',              label: 'Einkauf Angebote Liste',              group: 'einkauf' },
  { path: '/einkauf/auftragsbestaetigungen',      label: 'Auftragsbestätigungen',               group: 'einkauf' },
  { path: '/einkauf/rechnungseingang',            label: 'Rechnungseingang',                    group: 'einkauf' },
  { path: '/einkauf/rechnungseingaenge',          label: 'Rechnungseingänge',                   group: 'einkauf' },
  { path: '/einkauf/rechnung-eingang-erfassung',  label: 'Rechnung Eingang Erfassung',          group: 'einkauf' },
  { path: '/einkauf/rechnung-abgleich',           label: 'Rechnung Abgleich',                   group: 'einkauf' },
  { path: '/einkauf/wareneingang',                label: 'Einkauf Wareneingang',                group: 'einkauf' },
  { path: '/einkauf/lieferschein-erfassung',      label: 'Lieferschein Erfassung',              group: 'einkauf' },
  { path: '/einkauf/lieferschein-frachtauftrag',  label: 'Lieferschein Frachtauftrag',          group: 'einkauf' },
  { path: '/einkauf/anlieferavis',                label: 'Anlieferavis',                        group: 'einkauf' },
  { path: '/einkauf/anlieferavis-liste',          label: 'Anlieferavis Liste',                  group: 'einkauf' },
  { path: '/einkauf/anlieferavis/neu',            label: 'Anlieferavis Neu',                    group: 'einkauf' },
  { path: '/einkauf/lieferanten',                 label: 'Einkauf Lieferanten',                 group: 'einkauf' },
  { path: '/einkauf/lieferantenbewertung',        label: 'Lieferantenbewertung',                group: 'einkauf' },
  { path: '/einkauf/lieferanten-dokumente',       label: 'Lieferanten Dokumente',               group: 'einkauf' },
  { path: '/einkauf/warengruppen',                label: 'Warengruppen',                        group: 'einkauf' },
  { path: '/einkauf/edi-portal',                  label: 'EDI Portal',                          group: 'einkauf' },
  { path: '/einkauf/rfq-bids',                    label: 'RFQ Bids',                            group: 'einkauf' },
  { path: '/einkauf/service-entry-sheets',        label: 'Service Entry Sheets',                group: 'einkauf' },
  { path: '/einkauf/gutschriften-belastungen',    label: 'Gutschriften Belastungen',            group: 'einkauf' },
  { path: '/einkauf/retouren',                    label: 'Einkauf Retouren',                    group: 'einkauf' },
  { path: '/einkauf/reports',                     label: 'Einkauf Reports',                     group: 'einkauf' },
  { path: '/einkauf/audit-drilldown',             label: 'Einkauf Audit Drilldown',             group: 'einkauf' },

  // Verkauf / Sales
  { path: '/verkauf/auftraege',                   label: 'Verkauf Aufträge',                    group: 'verkauf' },
  { path: '/verkauf/betriebs-auftraege',          label: 'Betriebs-Aufträge',                   group: 'verkauf' },
  { path: '/verkauf/kommissions-auftraege',       label: 'Kommissions-Aufträge',                group: 'verkauf' },
  { path: '/verkauf/kunden-liste',                label: 'Verkauf Kunden',                      group: 'verkauf' },
  { path: '/verkauf/lieferschein-erfassung',      label: 'Verkauf Lieferschein',                group: 'verkauf' },
  { path: '/verkauf/unerledigte-auftrags-positionen', label: 'Unerledigte Auftragspositionen',  group: 'verkauf' },
  { path: '/sales/auftraege',                     label: 'Sales Aufträge',                      group: 'verkauf' },
  { path: '/sales/orders-modern',                 label: 'Sales Orders Modern',                 group: 'verkauf' },
  { path: '/sales/orders/new',                    label: 'Sales Order Neu',                     group: 'verkauf' },
  { path: '/sales/angebote',                      label: 'Sales Angebote',                      group: 'verkauf' },
  { path: '/sales/angebot/neu',                   label: 'Sales Angebot Neu',                   group: 'verkauf' },
  { path: '/sales/lieferungen',                   label: 'Sales Lieferungen',                   group: 'verkauf' },
  { path: '/sales/deliveries/new',                label: 'Sales Lieferung Neu',                 group: 'verkauf' },
  { path: '/sales/rechnungen',                    label: 'Sales Rechnungen',                    group: 'verkauf' },
  { path: '/sales/invoices/new',                  label: 'Sales Rechnung Neu',                  group: 'verkauf' },
  { path: '/sales/credit-note-editor',            label: 'Sales Gutschrift Editor',             group: 'verkauf' },
  { path: '/vertrieb/kundenumsatz',               label: 'Kundenumsatz',                        group: 'verkauf' },
  { path: '/kontrakte',                           label: 'Kontrakte',                           group: 'verkauf' },
  { path: '/kontrakte/neu',                       label: 'Kontrakt Neu',                        group: 'verkauf' },
  { path: '/kontrakte/kontraktklassen',           label: 'Kontraktklassen',                     group: 'verkauf' },
  { path: '/contracts',                           label: 'Contracts',                           group: 'verkauf' },
  { path: '/pricing',                             label: 'Pricing',                             group: 'verkauf' },
  { path: '/preise/kalkulation',                  label: 'Preiskalkulation',                    group: 'verkauf' },
  { path: '/preise/konditionen',                  label: 'Preiskonditionen',                    group: 'verkauf' },
  { path: '/preise/historie',                     label: 'Preishistorie',                       group: 'verkauf' },

  // Lager / Inventory
  { path: '/lager',                               label: 'Lager Übersicht',                     group: 'lager' },
  { path: '/lager/bestandsuebersicht',            label: 'Bestandsübersicht',                   group: 'lager' },
  { path: '/lager/bestandskorrektur',             label: 'Bestandskorrektur',                   group: 'lager' },
  { path: '/lager/einlagerung',                   label: 'Einlagerung',                         group: 'lager' },
  { path: '/lager/auslagerung',                   label: 'Auslagerung',                         group: 'lager' },
  { path: '/lager/lagerbewegungen',               label: 'Lagerbewegungen',                     group: 'lager' },
  { path: '/lager/lagerplaetze',                  label: 'Lagerplätze',                         group: 'lager' },
  { path: '/lager/inventur',                      label: 'Inventur',                            group: 'lager' },
  { path: '/inventory/adjust',                    label: 'Inventory Adjust',                    group: 'lager' },
  { path: '/inventory/epcis',                     label: 'Inventory EPCIS',                     group: 'lager' },
  { path: '/inventory-dashboard',                 label: 'Inventory Dashboard',                 group: 'lager' },
  { path: '/inventory-reports',                   label: 'Inventory Reports',                   group: 'lager' },
  { path: '/stock-management',                    label: 'Stock Management',                    group: 'lager' },

  // Finance / FIBU
  { path: '/finance',                             label: 'Finance Übersicht',                   group: 'finance' },
  { path: '/finance/buchungserfassung',           label: 'Buchungserfassung',                   group: 'finance' },
  { path: '/finance/bookings/new',                label: 'Buchung Neu',                         group: 'finance' },
  { path: '/finance/chart-of-accounts',           label: 'Kontenplan Finance',                  group: 'finance' },
  { path: '/finance/kontenplan',                  label: 'Finance Kontenplan',                  group: 'finance' },
  { path: '/finance/invoices',                    label: 'Finance Rechnungen',                  group: 'finance' },
  { path: '/finance/invoices/new',                label: 'Finance Rechnung Neu',                group: 'finance' },
  { path: '/finance/payments',                    label: 'Finance Zahlungen',                   group: 'finance' },
  { path: '/finance/debitoren',                   label: 'Finance Debitoren',                   group: 'finance' },
  { path: '/finance/debitoren-liste',             label: 'Finance Debitoren Liste',             group: 'finance' },
  { path: '/finance/kreditoren',                  label: 'Finance Kreditoren',                  group: 'finance' },
  { path: '/finance/mahnwesen',                   label: 'Finance Mahnwesen',                   group: 'finance' },
  { path: '/finance/dunning-editor',              label: 'Finance Dunning Editor',              group: 'finance' },
  { path: '/finance/op-debitoren',               label: 'Finance OP Debitoren',                group: 'finance' },
  { path: '/finance/op-kreditoren',              label: 'Finance OP Kreditoren',               group: 'finance' },
  { path: '/finance/steuerschluessel',            label: 'Finance Steuerschlüssel',             group: 'finance' },
  { path: '/finance/skonto-optimizer',            label: 'Finance Skonto',                      group: 'finance' },
  { path: '/finance/ustva',                       label: 'Finance UStVA',                       group: 'finance' },
  { path: '/finance/abschluss',                   label: 'Finance Abschluss',                   group: 'finance' },
  { path: '/finance/periods',                     label: 'Finance Perioden',                    group: 'finance' },
  { path: '/finance/bank-abgleich',               label: 'Bank Abgleich',                       group: 'finance' },
  { path: '/finance/bank-stamm',                  label: 'Bank Stamm',                          group: 'finance' },
  { path: '/finance/bankkonten',                  label: 'Bankkonten',                          group: 'finance' },
  { path: '/finance/lastschriften-debitoren',     label: 'Lastschriften Debitoren',             group: 'finance' },
  { path: '/finance/zahlungslauf-kreditoren',     label: 'Zahlungslauf Kreditoren',             group: 'finance' },
  { path: '/finance/nebenbuch-abstimmung',        label: 'Nebenbuch Abstimmung',                group: 'finance' },
  { path: '/finance/kasse',                       label: 'Finance Kasse',                       group: 'finance' },
  { path: '/finance/ap/invoices',                 label: 'AP Rechnungen',                       group: 'finance' },
  { path: '/finance/ap/invoices/new',             label: 'AP Rechnung Neu',                     group: 'finance' },
  { path: '/fibu/bilanz',                         label: 'FIBU Bilanz',                         group: 'fibu' },
  { path: '/fibu/guv',                            label: 'FIBU GuV',                            group: 'fibu' },
  { path: '/fibu/bwa',                            label: 'FIBU BWA',                            group: 'fibu' },
  { path: '/fibu/hauptbuch',                      label: 'FIBU Hauptbuch',                      group: 'fibu' },
  { path: '/fibu/buchungsjournal',                label: 'FIBU Buchungsjournal',                group: 'fibu' },
  { path: '/fibu/kontenplan',                     label: 'FIBU Kontenplan',                     group: 'fibu' },
  { path: '/fibu/debitoren',                      label: 'FIBU Debitoren',                      group: 'fibu' },
  { path: '/fibu/kreditoren',                     label: 'FIBU Kreditoren',                     group: 'fibu' },
  { path: '/fibu/offene-posten',                  label: 'FIBU Offene Posten',                  group: 'fibu' },
  { path: '/fibu/op-verwaltung',                  label: 'FIBU OP Verwaltung',                  group: 'fibu' },
  { path: '/fibu/verbindlichkeiten',              label: 'FIBU Verbindlichkeiten',              group: 'fibu' },
  { path: '/fibu/zahlungseingaenge',              label: 'FIBU Zahlungseingänge',               group: 'fibu' },
  { path: '/fibu/zahlungslaeufe',                 label: 'FIBU Zahlungsläufe',                  group: 'fibu' },
  { path: '/fibu/zahlungsvorschlaege',            label: 'FIBU Zahlungsvorschläge',             group: 'fibu' },
  { path: '/fibu/anlagen',                        label: 'FIBU Anlagen',                        group: 'fibu' },
  { path: '/fibu/anlagen-suite',                  label: 'FIBU Anlagen Suite',                  group: 'fibu' },
  { path: '/fibu/abschluss-cockpit',              label: 'FIBU Abschluss-Cockpit',              group: 'fibu' },
  { path: '/fibu/kostenstellenrechnung',          label: 'FIBU Kostenstellenrechnung',          group: 'fibu' },
  { path: '/fibu/kreditlinien',                   label: 'FIBU Kreditlinien',                   group: 'fibu' },
  { path: '/fibu/sicherheiten',                   label: 'FIBU Sicherheiten',                   group: 'fibu' },
  { path: '/fibu/debitoren-api',                  label: 'FIBU Debitoren API',                  group: 'fibu' },
  { path: '/fibu/lohn-connector',                 label: 'FIBU Lohn-Connector',                 group: 'fibu' },
  { path: '/fibu/elster-online',                  label: 'FIBU Elster Online',                  group: 'fibu' },
  { path: '/fibu/atlas',                          label: 'FIBU Atlas',                          group: 'fibu' },
  { path: '/fibu/schnittstelle-fibu',             label: 'FIBU Schnittstelle',                  group: 'fibu' },
  { path: '/fibu/schnittstellen-center',          label: 'FIBU Schnittstellen Center',          group: 'fibu' },
  { path: '/fibu/buchungsuebernahme-connectors',  label: 'FIBU Buchungsübernahme',              group: 'fibu' },
  { path: '/fibu/quadriga-connector',             label: 'FIBU Quadriga Connector',             group: 'fibu' },
  { path: '/export/ustva',                        label: 'Export UStVA',                        group: 'fibu' },
  { path: '/finanzplanung/liquiditaet',           label: 'Liquiditätsplanung',                  group: 'fibu' },
  { path: '/banken/konten',                       label: 'Banken Konten',                       group: 'fibu' },
  { path: '/mahnwesen/mahnlauf',                  label: 'Mahnlauf',                            group: 'fibu' },

  // CRM
  { path: '/crm/kunden',                          label: 'CRM Kunden',                          group: 'crm' },
  { path: '/crm/kunden-stamm-modern',             label: 'CRM Kunden Stamm Modern',             group: 'crm' },
  { path: '/crm/kontakte',                        label: 'CRM Kontakte',                        group: 'crm' },
  { path: '/crm/kontakt-management',              label: 'CRM Kontakt-Management',              group: 'crm' },
  { path: '/crm/lieferanten',                     label: 'CRM Lieferanten',                     group: 'crm' },
  { path: '/crm/betriebsprofile',                 label: 'CRM Betriebsprofile',                 group: 'crm' },
  { path: '/crm/leads',                           label: 'CRM Leads',                           group: 'crm' },
  { path: '/crm/opportunities',                   label: 'CRM Opportunities',                   group: 'crm' },
  { path: '/crm/opportunities-forecast',          label: 'CRM Opportunities Forecast',          group: 'crm' },
  { path: '/crm/opportunities-kanban',            label: 'CRM Opportunities Kanban',            group: 'crm' },
  { path: '/crm/opportunity/new',                 label: 'CRM Opportunity Neu',                 group: 'crm' },
  { path: '/crm/aktivitaeten',                    label: 'CRM Aktivitäten',                     group: 'crm' },
  { path: '/crm/campaigns',                       label: 'CRM Kampagnen',                       group: 'crm' },
  { path: '/crm/campaign/new',                    label: 'CRM Kampagne Neu',                    group: 'crm' },
  { path: '/crm/campaign-builder',                label: 'CRM Campaign Builder',                group: 'crm' },
  { path: '/crm/campaign-performance',            label: 'CRM Campaign Performance',            group: 'crm' },
  { path: '/crm/campaign-templates',              label: 'CRM Campaign Templates',              group: 'crm' },
  { path: '/crm/campaign-template/new',           label: 'CRM Campaign Template Neu',           group: 'crm' },
  { path: '/crm/segments',                        label: 'CRM Segmente',                        group: 'crm' },
  { path: '/crm/segment/new',                     label: 'CRM Segment Neu',                     group: 'crm' },
  { path: '/crm/consents',                        label: 'CRM Einwilligungen',                  group: 'crm' },
  { path: '/crm/consent/new',                     label: 'CRM Einwilligung Neu',                group: 'crm' },
  { path: '/crm/gdpr-requests',                   label: 'CRM DSGVO Anfragen',                  group: 'crm' },
  { path: '/crm/gdpr-request/new',                label: 'CRM DSGVO Anfrage Neu',               group: 'crm' },
  { path: '/crm/crm-dashboard',                   label: 'CRM Dashboard',                       group: 'crm' },
  { path: '/prospecting/leads',                   label: 'Prospecting Leads',                   group: 'crm' },
  { path: '/marketing/kampagnen',                 label: 'Marketing Kampagnen',                 group: 'crm' },

  // Controlling
  { path: '/controlling/plan-ist',                label: 'Controlling Plan-Ist',                group: 'controlling' },
  { path: '/controlling/benchmark-cockpit',       label: 'Benchmark Cockpit',                   group: 'controlling' },
  { path: '/controlling/kpi-verwaltung',          label: 'KPI Verwaltung',                      group: 'controlling' },
  { path: '/controlling/massnahmen',              label: 'Controlling Maßnahmen',               group: 'controlling' },
  { path: '/controlling/timeseries-erfassung',    label: 'Timeseries Erfassung',                group: 'controlling' },
  { path: '/controlling/dashboard-verwaltung',    label: 'Dashboard Verwaltung',                group: 'controlling' },
  { path: '/controlling/widget-verwaltung',       label: 'Widget Verwaltung',                   group: 'controlling' },
  { path: '/reports',                             label: 'Reports',                             group: 'controlling' },
  { path: '/reports/umsatz',                      label: 'Report Umsatz',                       group: 'controlling' },
  { path: '/reports/deckungsbeitrag',             label: 'Report Deckungsbeitrag',              group: 'controlling' },
  { path: '/reports/lagerbestand',                label: 'Report Lagerbestand',                 group: 'controlling' },

  // Compliance
  { path: '/compliance/bvl-umsatzmeldung',        label: 'BVL Umsatzmeldung',                   group: 'compliance' },
  { path: '/compliance/cross-compliance',         label: 'Cross-Compliance',                    group: 'compliance' },
  { path: '/compliance/enni-meldungen',           label: 'ENNI Meldungen',                      group: 'compliance' },
  { path: '/compliance/export-pruefprotokoll',    label: 'Export Prüfprotokoll',                group: 'compliance' },
  { path: '/compliance/gelangensbestaetigung',    label: 'Gelangensbestätigung',                group: 'compliance' },
  { path: '/compliance/intrastat',                label: 'Intrastat',                           group: 'compliance' },
  { path: '/compliance/lksg',                     label: 'LkSG',                                group: 'compliance' },
  { path: '/compliance/meldewesen-konsole',       label: 'Meldewesen Konsole',                  group: 'compliance' },
  { path: '/compliance/pcn-ufi',                  label: 'PCN UFI',                             group: 'compliance' },
  { path: '/compliance/qs-checkliste',            label: 'QS Checkliste',                       group: 'compliance' },
  { path: '/compliance/saatgut-nachbau',          label: 'Saatgut Nachbau',                     group: 'compliance' },
  { path: '/compliance/sachkunde-register',       label: 'Sachkunde Register',                  group: 'compliance' },
  { path: '/compliance/sanktionspruefung',        label: 'Sanktionsprüfung',                    group: 'compliance' },
  { path: '/compliance/vvvo-register',            label: 'VVVO Register',                       group: 'compliance' },
  { path: '/compliance/zulassungen-register',     label: 'Zulassungen Register',                group: 'compliance' },

  // Nachhaltigkeit
  { path: '/nachhaltigkeit/co2-bilanz',           label: 'CO2 Bilanz',                          group: 'nachhaltigkeit' },
  { path: '/nachhaltigkeit/eudr-compliance',      label: 'EUDR Compliance',                     group: 'nachhaltigkeit' },
  { path: '/nachhaltigkeit/biodiversitaet',       label: 'Biodiversität',                       group: 'nachhaltigkeit' },
  { path: '/nachhaltigkeit/esg-report',           label: 'ESG Report',                          group: 'nachhaltigkeit' },
  { path: '/subventionen/dashboard',              label: 'Subventionen Dashboard',              group: 'nachhaltigkeit' },
  { path: '/foerderung',                          label: 'Förderung',                           group: 'nachhaltigkeit' },
  { path: '/foerderung/antrag',                   label: 'Förderantrag',                        group: 'nachhaltigkeit' },
  { path: '/nawaro/anbauflaechen',                label: 'Nawaro Anbauflächen',                 group: 'nachhaltigkeit' },
  { path: '/nawaro/raps-profil',                  label: 'Nawaro Raps-Profil',                  group: 'nachhaltigkeit' },
  { path: '/nawaro/vertraege',                    label: 'Nawaro Verträge',                     group: 'nachhaltigkeit' },

  // Qualität / Labor
  { path: '/qualitaet/labor',                     label: 'Qualität Labor',                      group: 'qualitaet' },
  { path: '/qualitaet/labor-auftrag',             label: 'Labor Auftrag',                       group: 'qualitaet' },
  { path: '/qualitaet/labor-liste',               label: 'Labor Liste',                         group: 'qualitaet' },
  { path: '/qualitaet/reklamationen',             label: 'Reklamationen',                       group: 'qualitaet' },
  { path: '/qualitaet/ausnahmen',                 label: 'Qualität Ausnahmen',                  group: 'qualitaet' },
  { path: '/labor/proben',                        label: 'Labor Proben',                        group: 'qualitaet' },
  { path: '/charge/liste',                        label: 'Charge Liste',                        group: 'qualitaet' },
  { path: '/charge/stamm',                        label: 'Charge Stamm',                        group: 'qualitaet' },
  { path: '/charge/wareneingang',                 label: 'Charge Wareneingang',                 group: 'qualitaet' },
  { path: '/charge/rueckverfolgung',              label: 'Charge Rückverfolgung',               group: 'qualitaet' },

  // Logistik / Fuhrpark
  { path: '/logistik/frachtbriefe',               label: 'Frachtbriefe',                        group: 'logistik' },
  { path: '/logistik/tour-fracht-arbeitsraum',    label: 'Tour & Fracht Dispo',                 group: 'logistik' },
  { path: '/logistik/tourenplanung',              label: 'Tourenplanung',                       group: 'logistik' },
  { path: '/strecke/streckengeschaeft',           label: 'Streckengeschäft',                    group: 'logistik' },
  { path: '/strecke/vorlaeufige-streckengeschaefte', label: 'Vorläufige Streckengeschäfte',     group: 'logistik' },
  { path: '/strecke/nawaro-lieferungen',          label: 'Nawaro Lieferungen',                  group: 'logistik' },
  { path: '/strecke/nawaro-uebersicht',           label: 'Nawaro Übersicht',                    group: 'logistik' },
  { path: '/strecke/nawaro-vertraege-pruefen',    label: 'Nawaro Verträge Prüfen',              group: 'logistik' },
  { path: '/strecke/qualitaets-abweichung',       label: 'Qualitätsabweichung',                 group: 'logistik' },
  { path: '/strecke/speditionen-fracht-preise',   label: 'Speditionen Frachtpreise',            group: 'logistik' },
  { path: '/strecke/menu',                        label: 'Strecke Menü',                        group: 'logistik' },
  { path: '/strecke/disposition',                 label: 'Strecke Disposition',                 group: 'logistik' },
  { path: '/strecke/dokumente-drucken',           label: 'Strecke Dokumente',                   group: 'logistik' },
  { path: '/verladung',                           label: 'Verladung',                           group: 'logistik' },
  { path: '/verladung/lkw-beladung',              label: 'LKW Beladung',                        group: 'logistik' },
  { path: '/versand/frachtdokumente',             label: 'Frachtdokumente',                     group: 'logistik' },
  { path: '/versand/paket-etikett',               label: 'Paketetikett',                        group: 'logistik' },
  { path: '/versand/versand-avis',                label: 'Versand-Avis',                        group: 'logistik' },
  { path: '/transporte/fahrer',                   label: 'Transporte Fahrer',                   group: 'logistik' },
  { path: '/fuhrpark/fahrzeuge',                  label: 'Fuhrpark Fahrzeuge',                  group: 'logistik' },
  { path: '/fuhrpark/fahrzeug/neu',               label: 'Fuhrpark Fahrzeug Neu',               group: 'logistik' },
  { path: '/fuhrpark/uebersicht',                 label: 'Fuhrpark Übersicht',                  group: 'logistik' },
  { path: '/fuhrpark/fuhrpark-rechnungen',        label: 'Fuhrpark Rechnungen',                 group: 'logistik' },
  { path: '/fuhrpark/fuhrpark-stammdaten',        label: 'Fuhrpark Stammdaten',                 group: 'logistik' },
  { path: '/fuhrpark/fuhrpark-auswertung-kosten-pro-fahrzeug', label: 'Fuhrpark Kostenauswertung', group: 'logistik' },

  // Personal / HRM
  { path: '/personal/mitarbeiter',                label: 'Mitarbeiter Liste',                   group: 'personal' },
  { path: '/personal/mitarbeiter/neu',            label: 'Mitarbeiter Neu',                     group: 'personal' },
  { path: '/personal/zeiterfassung',              label: 'Zeiterfassung',                       group: 'personal' },
  { path: '/personal/stundenzettel',              label: 'Stundenzettel',                       group: 'personal' },
  { path: '/personal/abwesenheiten',              label: 'Abwesenheiten',                       group: 'personal' },
  { path: '/personal/schulungen',                 label: 'Schulungen',                          group: 'personal' },
  { path: '/personal/schulung-neu',               label: 'Schulung Neu',                        group: 'personal' },
  { path: '/personal/qualifikationen',            label: 'Qualifikationen',                     group: 'personal' },
  { path: '/personal/bewerbungen',                label: 'Bewerbungen',                         group: 'personal' },
  { path: '/personal/onboarding',                 label: 'Onboarding',                          group: 'personal' },
  { path: '/personal/organigramm',                label: 'Organigramm',                         group: 'personal' },
  { path: '/personal/hrm-operations-gates',       label: 'HRM Operations Gates',               group: 'personal' },
  { path: '/schichtplan',                         label: 'Schichtplan',                         group: 'personal' },
  { path: '/termine/kalender',                    label: 'Kalender',                            group: 'personal' },

  // Artikel / Stammdaten
  { path: '/artikel',                             label: 'Artikel Liste',                       group: 'stammdaten' },
  { path: '/artikel/neu',                         label: 'Artikel Neu',                         group: 'stammdaten' },
  { path: '/genossenschaft/mitglieder',           label: 'Genossenschaft Mitglieder',           group: 'stammdaten' },
  { path: '/agribusiness/farmers',                label: 'Agribusiness Farmers',                group: 'stammdaten' },
  { path: '/agribusiness/field-service-tasks',    label: 'Field Service Tasks',                 group: 'stammdaten' },
  { path: '/agribusiness/field-service-tasks/neu', label: 'Field Service Task Neu',             group: 'stammdaten' },

  // Futtermittel / Rationen
  { path: '/futtermittel/einzelfuttermittel-liste', label: 'Einzelfuttermittel',               group: 'futtermittel' },
  { path: '/futtermittel/mischfuttermittel-liste', label: 'Mischfuttermittel',                 group: 'futtermittel' },
  { path: '/futtermittel/grundfutteranalysen',    label: 'Grundfutteranalysen',                 group: 'futtermittel' },
  { path: '/futtermittel/rationsoptimierung',     label: 'Rationsoptimierung',                  group: 'futtermittel' },
  { path: '/futtermittel/rations-zugang',         label: 'Rationen Zugang',                     group: 'futtermittel' },
  { path: '/futtermittel/futtermittel-bestellung', label: 'Futtermittel Bestellung',            group: 'futtermittel' },
  { path: '/futtermittel/futtermittel-wareneingang', label: 'Futtermittel Wareneingang',        group: 'futtermittel' },
  { path: '/futtermittel/futtermittel-qualitaetskontrolle', label: 'Futtermittel Qualität',    group: 'futtermittel' },
  { path: '/futtermittel/futtermittel-statistik', label: 'Futtermittel Statistik',              group: 'futtermittel' },
  { path: '/futtermittel/charge-verfolgung',      label: 'Futtermittel Chargen',                group: 'futtermittel' },
  { path: '/futter/einzel',                       label: 'Futter Einzelmittel',                 group: 'futtermittel' },
  { path: '/futter/misch',                        label: 'Futter Mischfutter',                  group: 'futtermittel' },
  { path: '/produktion/mischfutter',              label: 'Produktion Mischfutter',              group: 'futtermittel' },
  { path: '/rezepte/editor',                      label: 'Rezepte Editor',                      group: 'futtermittel' },

  // POS / Kasse
  { path: '/pos/terminal',                        label: 'POS Terminal',                        group: 'pos' },
  { path: '/pos/tagesabschluss',                  label: 'POS Tagesabschluss',                  group: 'pos' },
  { path: '/pos/tagesabschluss-enhanced',         label: 'POS Tagesabschluss Enhanced',         group: 'pos' },
  { path: '/pos/retoure',                         label: 'POS Retoure',                         group: 'pos' },
  { path: '/pos/rabatte',                         label: 'POS Rabatte',                         group: 'pos' },
  { path: '/pos/promotionen',                     label: 'POS Promotionen',                     group: 'pos' },
  { path: '/pos/gift-cards',                      label: 'POS Geschenkkarten',                  group: 'pos' },
  { path: '/pos/suspended-sales',                 label: 'POS Suspended Sales',                 group: 'pos' },
  { path: '/kasse/tagesabschluss',                label: 'Kasse Tagesabschluss',                group: 'pos' },

  // Waage
  { path: '/waage',                               label: 'Waage',                               group: 'waage' },
  { path: '/waage/hofliste',                      label: 'Waage Hofliste',                      group: 'waage' },
  { path: '/waage/liste',                         label: 'Waage Liste',                         group: 'waage' },
  { path: '/waage/vorlagen',                      label: 'Waage Vorlagen',                      group: 'waage' },
  { path: '/waage/wiegungen',                     label: 'Wiegungen',                           group: 'waage' },
  { path: '/weighing',                            label: 'Weighing',                            group: 'waage' },
  { path: '/tankstelle/zapfungen',                label: 'Tankstelle Zapfungen',                group: 'waage' },

  // Workflow / Process
  { path: '/workflow/flow-spine-studio',          label: 'Flow Spine Studio',                   group: 'workflow' },
  { path: '/workflow/flow-spine-order-to-cash',   label: 'Flow Order-to-Cash',                  group: 'workflow' },
  { path: '/workflow/flow-spine-procure-to-pay',  label: 'Flow Procure-to-Pay',                 group: 'workflow' },
  { path: '/workflow/flow-spine-harvest-to-settlement', label: 'Flow Harvest-to-Settlement',    group: 'workflow' },
  { path: '/workflow/flow-spine-contract-to-settlement', label: 'Flow Contract-to-Settlement',  group: 'workflow' },
  { path: '/workflow/flow-spine-finance-to-close', label: 'Flow Finance-to-Close',              group: 'workflow' },
  { path: '/workflow/flow-spine-inventory-to-settlement', label: 'Flow Inventory-to-Settlement', group: 'workflow' },
  { path: '/workflow/flow-spine-complaint-to-resolution', label: 'Flow Complaint-to-Resolution', group: 'workflow' },
  { path: '/workflow/flow-spine-compliance-to-report', label: 'Flow Compliance-to-Report',      group: 'workflow' },
  { path: '/workflow/flow-spine-service-to-customer', label: 'Flow Service-to-Customer',        group: 'workflow' },
  { path: '/workflow/process-mining-analytics',   label: 'Process Mining Analytics',            group: 'workflow' },
  { path: '/workflow/workflow-monitoring',        label: 'Workflow Monitoring',                 group: 'workflow' },
  { path: '/workflow/workflow-regeln',            label: 'Workflow Regeln',                     group: 'workflow' },
  { path: '/workflows/approval',                  label: 'Workflows Approval',                  group: 'workflow' },
  { path: '/workflows/supervisor',                label: 'Workflows Supervisor',                group: 'workflow' },
  { path: '/workflows/trigger',                   label: 'Workflows Trigger',                   group: 'workflow' },
  { path: '/policies',                            label: 'Policies',                            group: 'workflow' },
  { path: '/projekte',                            label: 'Projekte',                            group: 'workflow' },
  { path: '/schaeden',                            label: 'Schäden',                             group: 'workflow' },
  { path: '/schaeden/meldung',                    label: 'Schäden Meldung',                     group: 'workflow' },
  { path: '/versicherungen',                      label: 'Versicherungen',                      group: 'workflow' },

  // Service / Support
  { path: '/service/anfragen',                    label: 'Service Anfragen',                    group: 'service' },
  { path: '/service/anfrage/neu',                 label: 'Service Anfrage Neu',                 group: 'service' },
  { path: '/service/rueckmeldung',                label: 'Service Rückmeldung',                 group: 'service' },
  { path: '/service/abschluss',                   label: 'Service Abschluss',                   group: 'service' },
  { path: '/wissen/wissensbasis',                 label: 'Wissensbasis',                        group: 'service' },

  // Admin / System
  { path: '/einstellungen/system',                label: 'Einstellungen System',                group: 'admin' },
  { path: '/setup/firma',                         label: 'Setup Firma',                         group: 'admin' },
  { path: '/admin/benutzer',                      label: 'Admin Benutzer',                      group: 'admin' },
  { path: '/admin/compliance',                    label: 'Admin Compliance',                    group: 'admin' },
  { path: '/admin/audit-log',                     label: 'Admin Audit Log',                     group: 'admin' },
  { path: '/admin/nummernkreise',                 label: 'Admin Nummernkreise',                 group: 'admin' },
  { path: '/admin/webhooks',                      label: 'Admin Webhooks',                      group: 'admin' },
  { path: '/admin/integrationen-quarantaene',     label: 'Integrationen Quarantäne',            group: 'admin' },
  { path: '/admin/ai-approvals',                  label: 'Admin AI Approvals',                  group: 'admin' },
  { path: '/admin/agenten-integration',           label: 'Agenten Integration',                 group: 'admin' },
  { path: '/admin/command-monitor',               label: 'Command Monitor',                     group: 'admin' },
  { path: '/admin/control-center',                label: 'Control Center',                      group: 'admin' },
  { path: '/admin/control-center/agent-ops',      label: 'Agent Ops',                           group: 'admin' },
  { path: '/admin/control-center/superglue',      label: 'Superglue',                           group: 'admin' },
  { path: '/admin/data-quality',                  label: 'Data Quality',                        group: 'admin' },
  { path: '/admin/gap-pipeline',                  label: 'Gap Pipeline',                        group: 'admin' },
  { path: '/admin/report-berechtigungen',         label: 'Report Berechtigungen',               group: 'admin' },
  { path: '/admin/setup',                         label: 'Admin Setup',                         group: 'admin' },
  { path: '/admin/setup/dms-integration',         label: 'DMS Integration',                     group: 'admin' },
  { path: '/admin/voice-channel',                 label: 'Voice Channel',                       group: 'admin' },
  { path: '/admin/webshop',                       label: 'Admin Webshop',                       group: 'admin' },
  { path: '/system/live-monitor',                 label: 'System Live Monitor',                 group: 'admin' },
  { path: '/monitoring/alerts',                   label: 'Monitoring Alerts',                   group: 'admin' },
  { path: '/monitoring/regeln',                   label: 'Monitoring Regeln',                   group: 'admin' },

  // Portal
  { path: '/portal',                              label: 'Portal',                              group: 'portal' },
  { path: '/portal/anfragen',                     label: 'Portal Anfragen',                     group: 'portal' },
  { path: '/portal/bestellungen',                 label: 'Portal Bestellungen',                 group: 'portal' },
  { path: '/portal/dokumente',                    label: 'Portal Dokumente',                    group: 'portal' },
  { path: '/portal/feldbuch',                     label: 'Portal Feldbuch',                     group: 'portal' },
  { path: '/portal/naehrstoffbilanzen',           label: 'Portal Nährstoffbilanzen',            group: 'portal' },
  { path: '/portal/rechnungen',                   label: 'Portal Rechnungen',                   group: 'portal' },
  { path: '/portal/vertraege',                    label: 'Portal Verträge',                     group: 'portal' },
  { path: '/portal/zertifikate',                  label: 'Portal Zertifikate',                  group: 'portal' },

  // Sonstiges
  { path: '/energie/verbrauch',                   label: 'Energie Verbrauch',                   group: 'sonstiges' },
  { path: '/dokumente/ablage',                    label: 'Dokumentenablage',                    group: 'sonstiges' },
  { path: '/zertifikate',                         label: 'Zertifikate',                         group: 'sonstiges' },
  { path: '/zertifikate/liste',                   label: 'Zertifikate Liste',                   group: 'sonstiges' },
  { path: '/wartung/anlagen',                     label: 'Wartung Anlagen',                     group: 'sonstiges' },
  { path: '/statistik/bewegungen',                label: 'Statistik Bewegungen',                group: 'sonstiges' },
]

// ---------------------------------------------------------------------------
// Hilfsfunktionen
// ---------------------------------------------------------------------------
type Issue = { route: string; viewport: string; type: string; detail: string }

function ensureDir(dir: string): void {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
}

function writeTestIssues(safeLabel: string, vpName: string, testIssues: Issue[]): void {
  if (testIssues.length === 0) return
  ensureDir(RAW_DIR)
  const file = path.join(RAW_DIR, `${safeLabel}__${vpName}.json`)
  fs.writeFileSync(file, JSON.stringify(testIssues))
}

async function collectIssues(page: Page, route: string, viewportName: string): Promise<Issue[]> {
  const found: Issue[] = []

  // Overflow — Elemente die sichtbar über den Viewport hinausgehen
  const overflowElements = await page.evaluate(() => {
    const vw = window.innerWidth
    const results: string[] = []
    document.querySelectorAll('*').forEach((el) => {
      const style = window.getComputedStyle(el)
      if (['fixed', 'absolute', 'sticky'].includes(style.position)) return
      if (style.overflow === 'hidden' || style.overflowX === 'hidden') return
      // Elemente in scrollbarem Container sind kein visueller Bug
      let ancestor = el.parentElement
      while (ancestor && ancestor !== document.body) {
        const as = window.getComputedStyle(ancestor)
        if (as.overflowX === 'auto' || as.overflowX === 'scroll') return
        ancestor = ancestor.parentElement
      }
      const rect = el.getBoundingClientRect()
      // Vollständig außerhalb (hidden panel / drawer)
      if (rect.left >= vw - 5 || rect.right <= 5) return
      if (rect.right > vw + 5 || rect.left < -5) {
        const tag = el.tagName.toLowerCase()
        const id = el.id ? `#${el.id}` : ''
        const cls = Array.from(el.classList).slice(0, 2).join('.')
        results.push(`${tag}${id}.${cls} (right:${Math.round(rect.right)}, vw:${vw})`)
      }
    })
    return results.slice(0, 5)
  })

  // 404-Seite — nur echte Fehler-Überschriften
  const is404 = await page.evaluate(() => {
    const headings = Array.from(document.querySelectorAll('h1, h2, [role="heading"]'))
    return headings.some((h) => {
      const t = (h as HTMLElement).innerText ?? ''
      return /^\s*(404|Seite nicht gefunden|Not Found|Page Not Found)\s*$/.test(t)
    })
  })

  // Winzige Texte (< 10 px)
  const tinyText = await page.evaluate(() => {
    const tiny: string[] = []
    document.querySelectorAll('p, span, td, th, label, button, a').forEach((el) => {
      const style = window.getComputedStyle(el)
      const size = parseFloat(style.fontSize)
      if (size > 0 && size < 10 && (el as HTMLElement).innerText?.trim().length > 0) {
        tiny.push(`${el.tagName.toLowerCase()}: "${(el as HTMLElement).innerText.substring(0, 30)}" (${size}px)`)
      }
    })
    return tiny.slice(0, 3)
  })

  // Konsolefehler (gesammelt vor dem Aufruf via page.on)
  // (wird durch Closure in aufrufender Funktion befüllt)

  if (is404) found.push({ route, viewport: viewportName, type: '404', detail: 'Seite leer oder 404' })
  overflowElements.forEach((el) => found.push({ route, viewport: viewportName, type: 'overflow', detail: el }))
  tinyText.forEach((t) => found.push({ route, viewport: viewportName, type: 'tiny-text', detail: t }))
  return found
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
// issues-raw leeren vor Lauf (nur Worker 0 macht das, idempotent)
test.beforeAll(async ({}, testInfo) => {
  if (testInfo.workerIndex === 0 && fs.existsSync(RAW_DIR)) {
    fs.readdirSync(RAW_DIR).forEach((f) => fs.unlinkSync(path.join(RAW_DIR, f)))
  }
})

for (const vp of VIEWPORTS) {
  test.describe(`[${vp.name}] ${vp.width}×${vp.height}`, () => {
    test.use({ viewport: { width: vp.width, height: vp.height } })

    for (const route of ROUTES) {
      const safeLabel = route.label.replace(/[^a-zA-Z0-9äöüÄÖÜß]/g, '-')

      test(`${route.group} / ${route.label}`, async ({ page }) => {
        const consoleErrors: string[] = []
        page.on('console', (msg) => {
          if (msg.type() !== 'error') return
          const t = msg.text()
          // Rausfiltern: Netz-/Infrastruktur-Rauschen das kein Code-Bug ist
          if (t.includes('Warning')) return
          if (t.includes('axe')) return
          if (t.includes('ERR_NAME_NOT_RESOLVED')) return   // externe Fonts/APIs offline
          if (t.includes('ERR_NETWORK_IO_SUSPENDED')) return // Netz kurz unterbrochen
          if (t.includes('ERR_NETWORK_CHANGED')) return      // Netz-Wechsel im Test
          if (t.includes('ERR_FAILED') && t.includes('Failed to load resource')) return
          if (t.includes('Failed to load resource: the server responded with a status of 500')) return // Backend/API offline im Visual-Audit
          if (t.includes('Failed to load resource: the server responded with a status of 503')) return // Backend/API bewusst nicht Teil der Visual-Tour
          if (t.includes('WebSocket connection to')) return  // Copilot-WS ohne Backend erwartet
          if (t.includes('fonts.gstatic.com') || t.includes('fonts.googleapis.com')) return
          if (t.includes('Access to font')) return
          consoleErrors.push(t.substring(0, 120))
        })

        await page.setExtraHTTPHeaders({ 'Authorization': 'Bearer dev-token' })
        await page.goto(BASE_URL + route.path, { waitUntil: 'domcontentloaded', timeout: 30_000 })
        await page.waitForTimeout(600)

        // Screenshot nur auf Desktop
        if (vp.screenshot) {
          ensureDir(path.join(SCREENSHOT_DIR, 'screenshots', vp.name, route.group))
          const screenshotPath = path.join(
            SCREENSHOT_DIR, 'screenshots', vp.name, route.group,
            `${safeLabel}.png`,
          )
          await page.screenshot({ path: screenshotPath, fullPage: false })
        }

        const issues = await collectIssues(page, route.path, vp.name)
        consoleErrors.forEach((e) =>
          issues.push({ route: route.path, viewport: vp.name, type: 'console-error', detail: e }),
        )
        writeTestIssues(safeLabel, vp.name, issues)

        // Grundbedingung: Seite nicht vollständig leer (soft — Timeout zählt als Issue, nicht als Testfehler)
        const mainContent = page.locator('main, [role="main"], #root > *')
        try {
          await expect(mainContent.first()).toBeVisible({ timeout: 8000 })
        } catch {
          writeTestIssues(safeLabel, vp.name, [{
            route: route.path, viewport: vp.name, type: 'empty-page',
            detail: 'Hauptinhalt nach 8s nicht sichtbar (Render-Timeout)',
          }])
        }
      })
    }
  })
}
