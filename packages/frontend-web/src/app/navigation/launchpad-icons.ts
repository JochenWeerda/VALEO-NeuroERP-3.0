/** Semantic symbols for canonical launcher identities; never an authorization decision. */
import {
  ArrowDownToLine, ArrowLeftRight, ArrowUpFromLine, BadgePercent, Barcode, Beef,
  Blend, BookOpen, Boxes, BriefcaseBusiness, Calculator, CalendarCheck2,
  CalendarDays, ChartNoAxesCombined, CircleDollarSign, ClipboardCheck, ClipboardList,
  ContactRound, CreditCard, Cylinder, Factory, FileCheck2, FilePlus2, FlaskConical,
  Handshake, Headset, Landmark, LayoutGrid, ListChecks, ListOrdered, MapPin,
  MessageSquareWarning, MonitorCheck, PackageCheck, ReceiptText, Route, Scale,
  Send, ShieldCheck, ShoppingCart, SlidersHorizontal, Sprout, Tags,
  TestTubeDiagonal, Tractor, Truck, Users, Warehouse, Wheat,
} from 'lucide-react'
import type { NavItem } from './types'

type AppIcon = NavItem['icon']
const ICONS: Record<string, AppIcon> = {
  kunden: Users, kundenakte: ContactRound, 'kunden-karte': MapPin,
  aktivitaeten: CalendarDays, vertreterstamm: BriefcaseBusiness, betriebsprofile: Tractor,
  angebot: BadgePercent, 'ausgehend-angebot': FilePlus2,
  auftrag: ClipboardList, 'ausgehend-auftrag': ClipboardCheck,
  lieferung: Truck, rechnung: ReceiptText, 'ausgehende-belege': Send,
  bestellungen: ShoppingCart, wareneingang: PackageCheck,
  'eingehende-belege': ArrowDownToLine, rechnungseingaenge: ReceiptText,
  'kontrakt-uebersicht': Handshake, 'kontrakt-erfuellung': ListChecks,
  'kontrakt-settlement': CircleDollarSign,
  'preis-kalkulation': Calculator, 'preis-konditionen': Tags, konditionssystem: SlidersHorizontal,
  'pos-terminal': MonitorCheck, tagesabschluss: CalendarCheck2,
  warteschlange: ListOrdered, wiegungen: Scale, hofliste: Truck,
  ernte: Wheat, 'ernte-annahme': ArrowDownToLine,
  'labor-auftraege': FlaskConical, 'qm-dokumente': FileCheck2,
  reklamationen: MessageSquareWarning, bodenproben: TestTubeDiagonal,
  'annahme-qualitaets-check': ShieldCheck,
  sammelabrechnung: ReceiptText, 'annahme-abrechnung': Calculator,
  'silo-uebersicht': Cylinder, fremdware: Boxes, lagerplaetze: Warehouse,
  bestandsuebersicht: Boxes, lagerbewegungen: ArrowLeftRight,
  'tour-fracht-arbeitsraum': Route, tourenplanung: Route, fuhrpark: Truck, frachtbriefe: FileCheck2,
  'versand-avis': Send, 'versand-frachtdokumente': FileCheck2,
  einlagerung: ArrowDownToLine, auslagerung: ArrowUpFromLine,
  inventur: ClipboardCheck, 'permanente-inventur': ListChecks,
  'duenger-liste': Sprout, 'duenger-bedarfsrechner': Calculator, 'duenger-mischungen': Blend,
  'psm-liste': ShieldCheck, 'psm-applikation': Sprout, 'psm-auflagen-manager': FileCheck2,
  'saatgut-liste': Wheat, 'saatgut-sortenregister': BookOpen, 'saatgut-bestellung': ShoppingCart,
  einzelfuttermittel: Beef, mischfuttermittel: Blend, rationsoptimierung: Calculator,
  produktionsleitstand: Factory, rezepturgruppen: Blend,
  partiestamm: Barcode, 'chargen-bearbeiten': Barcode,
  'op-verwaltung': BookOpen, mahnlauf: MessageSquareWarning,
  'op-kreditoren-finance': BookOpen, 'fibu-verbindlichkeiten': Landmark,
  zahlungslaeufe: CreditCard, zahlungseingang: CircleDollarSign,
  'beleg-kontrolle': FileCheck2, 'auftrags-kontrolle': ClipboardCheck,
  'lieferschein-kontrolle': PackageCheck, kostenstellenrechnung: Calculator,
  'plan-ist': ChartNoAxesCombined, deckungsbeitrag: Calculator, liquiditaet: Landmark,
  periodenabschluss: CalendarCheck2, 'datev-export': ArrowUpFromLine,
  freigaben: ShieldCheck, 'meine-aufgaben': ListChecks, 'kim-cockpit': Headset,
}

export function launchpadIcon(id: string, navigationIcon?: AppIcon): AppIcon {
  return ICONS[id] ?? navigationIcon ?? LayoutGrid
}
