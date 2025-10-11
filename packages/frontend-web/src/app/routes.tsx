import { type ComponentType, Suspense, lazy } from 'react'
import { type RouteObject, createBrowserRouter } from 'react-router-dom'
import AppLayout from '@/layouts/DashboardLayout'
import { ErrorBoundary } from '@/shared/errors/ErrorBoundary'
import { PageLoader } from '@/app/PageLoader'

const createLazyRoute = (
  factory: () => Promise<{ default: ComponentType<unknown> }>,
): (() => JSX.Element) => {
  const Component = lazy(factory)
  return function LazyRoute(): JSX.Element {
    return (
      <ErrorBoundary>
        <Suspense fallback={<PageLoader />}>
          <Component />
        </Suspense>
      </ErrorBoundary>
    )
  }
}

// Existing routes
const AnalyticsRoute = createLazyRoute(() => import('@/pages/analytics'))
const ContractsRoute = createLazyRoute(() => import('@/pages/contracts'))
const PricingRoute = createLazyRoute(() => import('@/pages/pricing'))
const InventoryRoute = createLazyRoute(() => import('@/pages/inventory'))
const WeighingRoute = createLazyRoute(() => import('@/pages/weighing'))
const SalesRoute = createLazyRoute(() => import('@/pages/sales'))
const DocumentRoute = createLazyRoute(() => import('@/pages/document'))
const PolicyManagerRoute = createLazyRoute(() => import('@/pages/policy-manager'))
const SalesOrderEditorRoute = createLazyRoute(() => import('@/pages/sales/order-editor'))
const SalesDeliveryEditorRoute = createLazyRoute(() => import('@/pages/sales/delivery-editor'))
const SalesInvoiceEditorRoute = createLazyRoute(() => import('@/pages/sales/invoice-editor'))
const SeedListRoute = createLazyRoute(() => import('@/pages/agrar/saatgut/liste'))
const SeedMasterRoute = createLazyRoute(() => import('@/pages/agrar/saatgut/stamm'))
const SeedOrderWizardRoute = createLazyRoute(() => import('@/pages/agrar/saatgut/bestellung'))
const FertilizerListRoute = createLazyRoute(() => import('@/pages/agrar/duenger/liste'))
const FertilizerMasterRoute = createLazyRoute(() => import('@/pages/agrar/duenger/stamm'))

// NEW: 120 Masken-Routes
// Agrar
const PSMListeRoute = createLazyRoute(() => import('@/pages/agrar/psm/liste'))
const PSMStammRoute = createLazyRoute(() => import('@/pages/agrar/psm/stamm'))
const SortenregisterRoute = createLazyRoute(() => import('@/pages/agrar/saatgut/sortenregister'))
const BedarfsrechnerRoute = createLazyRoute(() => import('@/pages/agrar/duenger/bedarfsrechner'))
const FeldSchlagkarteRoute = createLazyRoute(() => import('@/pages/agrar/feldbuch/schlagkartei'))
const FeldMassnahmenRoute = createLazyRoute(() => import('@/pages/agrar/feldbuch/massnahmen'))
const BodenprobenRoute = createLazyRoute(() => import('@/pages/agrar/bodenproben/liste'))
const ErnteListeRoute = createLazyRoute(() => import('@/pages/agrar/ernte/liste'))
const AussaatListeRoute = createLazyRoute(() => import('@/pages/agrar/aussaat/liste'))
const WetterPrognoseRoute = createLazyRoute(() => import('@/pages/agrar/wetter/prognose'))
const WetterwarnungRoute = createLazyRoute(() => import('@/pages/agrar/wetterwarnung'))
const PflanzenschutzApplikationRoute = createLazyRoute(() => import('@/pages/agrar/pflanzenschutz/applikation'))
const DuengungsplanungRoute = createLazyRoute(() => import('@/pages/agrar/duengung/planung'))
const SchlagKarteRoute = createLazyRoute(() => import('@/pages/agrar/schlaege/karte'))
const KulturpflanzenListeRoute = createLazyRoute(() => import('@/pages/agrar/kulturpflanzen/liste'))
const MaschinenauslastungRoute = createLazyRoute(() => import('@/pages/agrar/maschinenauslastung'))

// Futter
const FutterEinzelStammRoute = createLazyRoute(() => import('@/pages/futter/einzel/stamm'))
const FutterEinzelListeRoute = createLazyRoute(() => import('@/pages/futter/einzel/liste'))
const FutterMischStammRoute = createLazyRoute(() => import('@/pages/futter/misch/stamm'))
const FutterMischListeRoute = createLazyRoute(() => import('@/pages/futter/misch/liste'))
const RezepteEditorRoute = createLazyRoute(() => import('@/pages/rezepte/editor'))
const MischfutterProduktionRoute = createLazyRoute(() => import('@/pages/produktion/mischfutter-produktion'))

// Verkauf & Kunden
const KundenStammRoute = createLazyRoute(() => import('@/pages/verkauf/kunden-stamm'))
const KundenListeRoute = createLazyRoute(() => import('@/pages/verkauf/kunden-liste'))

// Einkauf & Lieferanten
const LieferantenStammRoute = createLazyRoute(() => import('@/pages/einkauf/lieferanten-stamm'))
const LieferantenListeRoute = createLazyRoute(() => import('@/pages/einkauf/lieferanten-liste'))
const BestellvorschlaegeRoute = createLazyRoute(() => import('@/pages/einkauf/bestellvorschlaege'))
const WarengruppenRoute = createLazyRoute(() => import('@/pages/einkauf/warengruppen'))

// Artikel
const ArtikelStammRoute = createLazyRoute(() => import('@/pages/artikel/stamm'))
const ArtikelListeRoute = createLazyRoute(() => import('@/pages/artikel/liste'))

// Charge
const ChargeStammRoute = createLazyRoute(() => import('@/pages/charge/stamm'))
const ChargeListeRoute = createLazyRoute(() => import('@/pages/charge/liste'))
const ChargeRueckverfolgungRoute = createLazyRoute(() => import('@/pages/charge/rueckverfolgung'))
const ChargeWareneingangRoute = createLazyRoute(() => import('@/pages/charge/wareneingang'))

// Lager
const BestandsuebersichtRoute = createLazyRoute(() => import('@/pages/lager/bestandsuebersicht'))
const EinlagerungRoute = createLazyRoute(() => import('@/pages/lager/einlagerung'))
const AuslagerungRoute = createLazyRoute(() => import('@/pages/lager/auslagerung'))
const InventurRoute = createLazyRoute(() => import('@/pages/lager/inventur'))
const BewegungenStatistikRoute = createLazyRoute(() => import('@/pages/statistik/bewegungen'))
const SiloKapazitaetenRoute = createLazyRoute(() => import('@/pages/silo/kapazitaeten'))

// Logistik & Transporte
const TourenplanungRoute = createLazyRoute(() => import('@/pages/logistik/tourenplanung'))
const LKWBeladungRoute = createLazyRoute(() => import('@/pages/verladung/lkw-beladung'))
const VerladungListeRoute = createLazyRoute(() => import('@/pages/verladung/liste'))
const FahrerListeRoute = createLazyRoute(() => import('@/pages/transporte/fahrer-liste'))

// Annahme
const WarteschlangeRoute = createLazyRoute(() => import('@/pages/annahme/warteschlange'))
const LKWRegistrierungRoute = createLazyRoute(() => import('@/pages/annahme/lkw-registrierung'))
const QualitaetsCheckRoute = createLazyRoute(() => import('@/pages/annahme/qualitaets-check'))

// Waage
const WaageListeRoute = createLazyRoute(() => import('@/pages/waage/liste'))
const WiegungenRoute = createLazyRoute(() => import('@/pages/waage/wiegungen'))
const TankstelleZapfungenRoute = createLazyRoute(() => import('@/pages/tankstelle/zapfungen'))

// Qualität & Labor
const LaborAuftragRoute = createLazyRoute(() => import('@/pages/qualitaet/labor-auftrag'))
const LaborListeRoute = createLazyRoute(() => import('@/pages/qualitaet/labor-liste'))
const LaborProbenListeRoute = createLazyRoute(() => import('@/pages/labor/proben-liste'))
const ReklamationenRoute = createLazyRoute(() => import('@/pages/qualitaet/reklamationen'))

// Compliance
const ZulassungenRegisterRoute = createLazyRoute(() => import('@/pages/compliance/zulassungen-register'))
const EUDRComplianceRoute = createLazyRoute(() => import('@/pages/nachhaltigkeit/eudr-compliance'))
const CO2BilanzRoute = createLazyRoute(() => import('@/pages/nachhaltigkeit/co2-bilanz'))
const BiodiversitaetRoute = createLazyRoute(() => import('@/pages/nachhaltigkeit/biodiversitaet'))
const CrossComplianceRoute = createLazyRoute(() => import('@/pages/compliance/cross-compliance'))
const QSChecklisteRoute = createLazyRoute(() => import('@/pages/compliance/qs-checkliste'))
const ZertifikateListeRoute = createLazyRoute(() => import('@/pages/zertifikate/liste'))

// CRM
const KontakteListeRoute = createLazyRoute(() => import('@/pages/crm/kontakte-liste'))
const BetriebsprofileRoute = createLazyRoute(() => import('@/pages/crm/betriebsprofile'))
const LeadsRoute = createLazyRoute(() => import('@/pages/crm/leads'))

// Marketing
const KampagnenRoute = createLazyRoute(() => import('@/pages/marketing/kampagnen'))

// Finanzen
const HauptbuchRoute = createLazyRoute(() => import('@/pages/fibu/hauptbuch'))
const KostenstellenrechnungRoute = createLazyRoute(() => import('@/pages/fibu/kostenstellenrechnung'))
const ZahlungseingaengeRoute = createLazyRoute(() => import('@/pages/fibu/zahlungseingaenge'))
const ZahlungsvorschlaegeRoute = createLazyRoute(() => import('@/pages/fibu/zahlungsvorschlaege'))
const ZahlungslaeufeRoute = createLazyRoute(() => import('@/pages/fibu/zahlungslaeufe'))
const LiquiditaetRoute = createLazyRoute(() => import('@/pages/finanzplanung/liquiditaet'))
const BankkontenRoute = createLazyRoute(() => import('@/pages/banken/konten'))
const UStVARoute = createLazyRoute(() => import('@/pages/export/umsatzsteuervoranmeldung'))
const DebitorenRoute = createLazyRoute(() => import('@/pages/fibu/debitoren'))
const KreditorenRoute = createLazyRoute(() => import('@/pages/fibu/kreditoren'))
const BuchungsjournalRoute = createLazyRoute(() => import('@/pages/fibu/buchungsjournal'))
const KontenplanRoute = createLazyRoute(() => import('@/pages/fibu/kontenplan'))
const BilanzRoute = createLazyRoute(() => import('@/pages/fibu/bilanz'))
const GuvRoute = createLazyRoute(() => import('@/pages/fibu/guv'))
const BwaRoute = createLazyRoute(() => import('@/pages/fibu/bwa'))
const AnlagenRoute = createLazyRoute(() => import('@/pages/fibu/anlagen'))
const SachkontoRoute = createLazyRoute(() => import('@/pages/fibu/sachkonto'))
const OPVerwaltungRoute = createLazyRoute(() => import('@/pages/fibu/op-verwaltung'))

// Controlling
const PlanIstRoute = createLazyRoute(() => import('@/pages/controlling/plan-ist'))

// Reports
const UmsatzReportRoute = createLazyRoute(() => import('@/pages/reports/umsatz'))
const DeckungsbeitragRoute = createLazyRoute(() => import('@/pages/reports/deckungsbeitrag'))
const LagerbestandReportRoute = createLazyRoute(() => import('@/pages/reports/lagerbestand'))
const PreisHistorieRoute = createLazyRoute(() => import('@/pages/preise/historie'))
const PreisKonditionenRoute = createLazyRoute(() => import('@/pages/preise/konditionen'))

// Dashboards
const SalesDashboardRoute = createLazyRoute(() => import('@/pages/dashboard/sales-dashboard'))
const EinkaufDashboardRoute = createLazyRoute(() => import('@/pages/dashboard/einkauf-dashboard'))
const GeschaeftsfuehrungRoute = createLazyRoute(() => import('@/pages/dashboards/geschaeftsfuehrung'))
const SubventionenDashboardRoute = createLazyRoute(() => import('@/pages/subventionen/dashboard'))

// Administration
const BenutzerListeRoute = createLazyRoute(() => import('@/pages/admin/benutzer-liste'))
const RollenVerwaltungRoute = createLazyRoute(() => import('@/pages/admin/rollen-verwaltung'))
const AuditLogRoute = createLazyRoute(() => import('@/pages/admin/audit-log'))
const SystemEinstellungenRoute = createLazyRoute(() => import('@/pages/einstellungen/system'))
const MonitoringAlertsRoute = createLazyRoute(() => import('@/pages/monitoring/alerts'))

// Personal
const MitarbeiterListeRoute = createLazyRoute(() => import('@/pages/personal/mitarbeiter-liste'))
const ZeiterfassungRoute = createLazyRoute(() => import('@/pages/personal/zeiterfassung'))
const SchichtplanRoute = createLazyRoute(() => import('@/pages/schichtplan/liste'))

// Fuhrpark
const FahrzeugeRoute = createLazyRoute(() => import('@/pages/fuhrpark/fahrzeuge'))
const EnergieverbrauchRoute = createLazyRoute(() => import('@/pages/energie/verbrauch'))

// Verträge & Versicherungen
const RahmenvertraegeRoute = createLazyRoute(() => import('@/pages/vertrag/rahmenvertraege'))
const VersicherungenListeRoute = createLazyRoute(() => import('@/pages/versicherungen/liste'))
const SchadenMeldungRoute = createLazyRoute(() => import('@/pages/schaeden/meldung'))
const SchaedenListeRoute = createLazyRoute(() => import('@/pages/schaeden/liste'))
const FoerderantragRoute = createLazyRoute(() => import('@/pages/foerderung/antrag'))
const FoerderantraegeListeRoute = createLazyRoute(() => import('@/pages/foerderung/liste'))

// Wartung & Service
const WartungAnlagenRoute = createLazyRoute(() => import('@/pages/wartung/anlagen-liste'))
const ServiceAnfragenRoute = createLazyRoute(() => import('@/pages/service/anfragen'))

// Dokumente & Sonstiges
const DokumenteAblageRoute = createLazyRoute(() => import('@/pages/dokumente/ablage'))
const ProjekteListeRoute = createLazyRoute(() => import('@/pages/projekte/liste'))
const TermineKalenderRoute = createLazyRoute(() => import('@/pages/termine/kalender'))
const BenachrichtigungenRoute = createLazyRoute(() => import('@/pages/benachrichtigungen/liste'))
const DispositionRoute = createLazyRoute(() => import('@/pages/disposition/liste'))
const MahnwesenRoute = createLazyRoute(() => import('@/pages/mahnwesen/mahnlauf'))
const KasseTagesabschlussRoute = createLazyRoute(() => import('@/pages/kasse/tagesabschluss'))
const EtikettenDruckenRoute = createLazyRoute(() => import('@/pages/etiketten/drucken'))
const MobileScannerRoute = createLazyRoute(() => import('@/pages/mobile/scanner'))

const routeConfig: RouteObject[] = [
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <AnalyticsRoute /> },
      { path: 'analytics', element: <AnalyticsRoute /> },
      { path: 'contracts', element: <ContractsRoute /> },
      { path: 'pricing', element: <PricingRoute /> },
      { path: 'inventory', element: <InventoryRoute /> },
      { path: 'weighing', element: <WeighingRoute /> },
      { path: 'sales', element: <SalesRoute /> },
      { path: 'document', element: <DocumentRoute /> },
      { path: 'policies', element: <PolicyManagerRoute /> },
      { path: 'sales/order', element: <SalesOrderEditorRoute /> },
      { path: 'sales/delivery', element: <SalesDeliveryEditorRoute /> },
      { path: 'sales/invoice', element: <SalesInvoiceEditorRoute /> },
      
      // Agrar
      { path: 'agrar/psm', element: <PSMListeRoute /> },
      { path: 'agrar/psm/stamm', element: <PSMStammRoute /> },
      { path: 'agrar/saatgut', element: <SeedListRoute /> },
      { path: 'agrar/saatgut/stamm', element: <SeedMasterRoute /> },
      { path: 'agrar/saatgut/bestellung', element: <SeedOrderWizardRoute /> },
      { path: 'agrar/saatgut/sortenregister', element: <SortenregisterRoute /> },
      { path: 'agrar/duenger', element: <FertilizerListRoute /> },
      { path: 'agrar/duenger/stamm', element: <FertilizerMasterRoute /> },
      { path: 'agrar/duenger/bedarfsrechner', element: <BedarfsrechnerRoute /> },
      { path: 'agrar/feldbuch/schlagkartei', element: <FeldSchlagkarteRoute /> },
      { path: 'agrar/feldbuch/massnahmen', element: <FeldMassnahmenRoute /> },
      { path: 'agrar/bodenproben', element: <BodenprobenRoute /> },
      { path: 'agrar/ernte', element: <ErnteListeRoute /> },
      { path: 'agrar/aussaat', element: <AussaatListeRoute /> },
      { path: 'agrar/wetter/prognose', element: <WetterPrognoseRoute /> },
      { path: 'agrar/wetterwarnung', element: <WetterwarnungRoute /> },
      { path: 'agrar/pflanzenschutz/applikation', element: <PflanzenschutzApplikationRoute /> },
      { path: 'agrar/duengung/planung', element: <DuengungsplanungRoute /> },
      { path: 'agrar/schlaege/karte', element: <SchlagKarteRoute /> },
      { path: 'agrar/kulturpflanzen', element: <KulturpflanzenListeRoute /> },
      { path: 'agrar/maschinenauslastung', element: <MaschinenauslastungRoute /> },
      
      // Futter
      { path: 'futter/einzel/stamm', element: <FutterEinzelStammRoute /> },
      { path: 'futter/einzel/liste', element: <FutterEinzelListeRoute /> },
      { path: 'futter/misch/stamm', element: <FutterMischStammRoute /> },
      { path: 'futter/misch/liste', element: <FutterMischListeRoute /> },
      { path: 'rezepte/editor', element: <RezepteEditorRoute /> },
      { path: 'produktion/mischfutter', element: <MischfutterProduktionRoute /> },
      
      // Verkauf & Kunden
      { path: 'verkauf/kunden-stamm', element: <KundenStammRoute /> },
      { path: 'verkauf/kunden-liste', element: <KundenListeRoute /> },
      
      // Einkauf
      { path: 'einkauf/lieferanten-stamm', element: <LieferantenStammRoute /> },
      { path: 'einkauf/lieferanten-liste', element: <LieferantenListeRoute /> },
      { path: 'einkauf/bestellvorschlaege', element: <BestellvorschlaegeRoute /> },
      { path: 'einkauf/warengruppen', element: <WarengruppenRoute /> },
      
      // Artikel
      { path: 'artikel/stamm', element: <ArtikelStammRoute /> },
      { path: 'artikel/liste', element: <ArtikelListeRoute /> },
      
      // Charge
      { path: 'charge/stamm', element: <ChargeStammRoute /> },
      { path: 'charge/liste', element: <ChargeListeRoute /> },
      { path: 'charge/rueckverfolgung', element: <ChargeRueckverfolgungRoute /> },
      { path: 'charge/wareneingang', element: <ChargeWareneingangRoute /> },
      
      // Lager
      { path: 'lager/bestandsuebersicht', element: <BestandsuebersichtRoute /> },
      { path: 'lager/einlagerung', element: <EinlagerungRoute /> },
      { path: 'lager/auslagerung', element: <AuslagerungRoute /> },
      { path: 'lager/inventur', element: <InventurRoute /> },
      { path: 'statistik/bewegungen', element: <BewegungenStatistikRoute /> },
      { path: 'silo/kapazitaeten', element: <SiloKapazitaetenRoute /> },
      
      // Logistik
      { path: 'logistik/tourenplanung', element: <TourenplanungRoute /> },
      { path: 'verladung/lkw-beladung', element: <LKWBeladungRoute /> },
      { path: 'verladung/liste', element: <VerladungListeRoute /> },
      { path: 'transporte/fahrer-liste', element: <FahrerListeRoute /> },
      
      // Annahme & Waage
      { path: 'annahme/warteschlange', element: <WarteschlangeRoute /> },
      { path: 'annahme/lkw-registrierung', element: <LKWRegistrierungRoute /> },
      { path: 'annahme/qualitaets-check', element: <QualitaetsCheckRoute /> },
      { path: 'waage/liste', element: <WaageListeRoute /> },
      { path: 'waage/wiegungen', element: <WiegungenRoute /> },
      { path: 'tankstelle/zapfungen', element: <TankstelleZapfungenRoute /> },
      
      // Qualität & Labor
      { path: 'qualitaet/labor-auftrag', element: <LaborAuftragRoute /> },
      { path: 'qualitaet/labor-liste', element: <LaborListeRoute /> },
      { path: 'labor/proben-liste', element: <LaborProbenListeRoute /> },
      { path: 'qualitaet/reklamationen', element: <ReklamationenRoute /> },
      
      // Compliance
      { path: 'compliance/zulassungen-register', element: <ZulassungenRegisterRoute /> },
      { path: 'nachhaltigkeit/eudr-compliance', element: <EUDRComplianceRoute /> },
      { path: 'nachhaltigkeit/co2-bilanz', element: <CO2BilanzRoute /> },
      { path: 'nachhaltigkeit/biodiversitaet', element: <BiodiversitaetRoute /> },
      { path: 'compliance/cross-compliance', element: <CrossComplianceRoute /> },
      { path: 'compliance/qs-checkliste', element: <QSChecklisteRoute /> },
      { path: 'zertifikate/liste', element: <ZertifikateListeRoute /> },
      
      // CRM & Marketing
      { path: 'crm/kontakte-liste', element: <KontakteListeRoute /> },
      { path: 'crm/betriebsprofile', element: <BetriebsprofileRoute /> },
      { path: 'crm/leads', element: <LeadsRoute /> },
      { path: 'marketing/kampagnen', element: <KampagnenRoute /> },
      
      // Finanzen
      { path: 'fibu/hauptbuch', element: <HauptbuchRoute /> },
      { path: 'fibu/debitoren', element: <DebitorenRoute /> },
      { path: 'fibu/kreditoren', element: <KreditorenRoute /> },
      { path: 'fibu/buchungsjournal', element: <BuchungsjournalRoute /> },
      { path: 'fibu/kontenplan', element: <KontenplanRoute /> },
      { path: 'fibu/bilanz', element: <BilanzRoute /> },
      { path: 'fibu/guv', element: <GuvRoute /> },
      { path: 'fibu/bwa', element: <BwaRoute /> },
      { path: 'fibu/anlagen', element: <AnlagenRoute /> },
      { path: 'fibu/sachkonto', element: <SachkontoRoute /> },
      { path: 'fibu/op-verwaltung', element: <OPVerwaltungRoute /> },
      { path: 'fibu/kostenstellenrechnung', element: <KostenstellenrechnungRoute /> },
      { path: 'fibu/zahlungseingaenge', element: <ZahlungseingaengeRoute /> },
      { path: 'fibu/zahlungsvorschlaege', element: <ZahlungsvorschlaegeRoute /> },
      { path: 'fibu/zahlungslaeufe', element: <ZahlungslaeufeRoute /> },
      { path: 'finanzplanung/liquiditaet', element: <LiquiditaetRoute /> },
      { path: 'banken/konten', element: <BankkontenRoute /> },
      { path: 'export/ustva', element: <UStVARoute /> },
      
      // Controlling & Reports
      { path: 'controlling/plan-ist', element: <PlanIstRoute /> },
      { path: 'reports/umsatz', element: <UmsatzReportRoute /> },
      { path: 'reports/deckungsbeitrag', element: <DeckungsbeitragRoute /> },
      { path: 'reports/lagerbestand', element: <LagerbestandReportRoute /> },
      { path: 'preise/historie', element: <PreisHistorieRoute /> },
      { path: 'preise/konditionen', element: <PreisKonditionenRoute /> },
      
      // Dashboards
      { path: 'dashboard/sales', element: <SalesDashboardRoute /> },
      { path: 'dashboard/einkauf', element: <EinkaufDashboardRoute /> },
      { path: 'dashboards/geschaeftsfuehrung', element: <GeschaeftsfuehrungRoute /> },
      { path: 'subventionen/dashboard', element: <SubventionenDashboardRoute /> },
      
      // Administration
      { path: 'admin/benutzer-liste', element: <BenutzerListeRoute /> },
      { path: 'admin/rollen-verwaltung', element: <RollenVerwaltungRoute /> },
      { path: 'admin/audit-log', element: <AuditLogRoute /> },
      { path: 'einstellungen/system', element: <SystemEinstellungenRoute /> },
      { path: 'monitoring/alerts', element: <MonitoringAlertsRoute /> },
      
      // Personal
      { path: 'personal/mitarbeiter-liste', element: <MitarbeiterListeRoute /> },
      { path: 'personal/zeiterfassung', element: <ZeiterfassungRoute /> },
      { path: 'schichtplan/liste', element: <SchichtplanRoute /> },
      
      // Fuhrpark
      { path: 'fuhrpark/fahrzeuge', element: <FahrzeugeRoute /> },
      { path: 'energie/verbrauch', element: <EnergieverbrauchRoute /> },
      
      // Verträge & Versicherungen
      { path: 'vertrag/rahmenvertraege', element: <RahmenvertraegeRoute /> },
      { path: 'versicherungen/liste', element: <VersicherungenListeRoute /> },
      { path: 'schaeden/meldung', element: <SchadenMeldungRoute /> },
      { path: 'schaeden/liste', element: <SchaedenListeRoute /> },
      { path: 'foerderung/antrag', element: <FoerderantragRoute /> },
      { path: 'foerderung/liste', element: <FoerderantraegeListeRoute /> },
      
      // Wartung & Service
      { path: 'wartung/anlagen-liste', element: <WartungAnlagenRoute /> },
      { path: 'service/anfragen', element: <ServiceAnfragenRoute /> },
      
      // Dokumente & Sonstiges
      { path: 'dokumente/ablage', element: <DokumenteAblageRoute /> },
      { path: 'projekte/liste', element: <ProjekteListeRoute /> },
      { path: 'termine/kalender', element: <TermineKalenderRoute /> },
      { path: 'benachrichtigungen/liste', element: <BenachrichtigungenRoute /> },
      { path: 'disposition/liste', element: <DispositionRoute /> },
      { path: 'mahnwesen/mahnlauf', element: <MahnwesenRoute /> },
      { path: 'kasse/tagesabschluss', element: <KasseTagesabschlussRoute /> },
      { path: 'etiketten/drucken', element: <EtikettenDruckenRoute /> },
      { path: 'mobile/scanner', element: <MobileScannerRoute /> },
    ],
  },
]

export const router = createBrowserRouter(routeConfig)

export const routes = routeConfig
