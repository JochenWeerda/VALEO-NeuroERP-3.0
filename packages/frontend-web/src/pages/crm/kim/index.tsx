/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, Suspense, lazy } from 'react';
import { useNavigate } from '@/app/routing/typed-router';
import { Customer, ContactPerson, ContactLog, OpenItem, BusinessDocument } from './types';
import * as kimApi from './kim-api';
import { useToast } from '@/hooks/use-toast';
import { Toaster } from '@/components/ui/toaster';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';

// Bestehende Fachseiten als Tabs einbetten (Wiederverwendung; Konsolidierung folgt).
const LeadsPage = lazy(() => import('../leads'));
const KundenKartePage = lazy(() => import('../kunden-karte'));

// Importing Custom High-Density CRM Modules
import CustomerListSidebar from './components/CustomerListSidebar';
import CustomerHeader from './components/CustomerHeader';
import CustomerActionBar from './components/CustomerActionBar';
import CustomerStatusBanner from './components/CustomerStatusBanner';

import ContactPersonsTable from './components/ContactPersonsTable';
import FinancialOpenItemsPanel from './components/FinancialOpenItemsPanel';
import SalesDocumentsPanel from './components/SalesDocumentsPanel';
import ContractsPanel from './components/ContractsPanel';
import DocumentPanel from './components/DocumentPanel';
import FollowUpTaskPanel from './components/FollowUpTaskPanel';
import NeuroAISidePanel from './components/NeuroAISidePanel';
import ContactHistoryTable from './components/ContactHistoryTable';

import {
  Building2,
  ShieldAlert,
  Settings,
  FileCheck,
  Brain,
  Loader2,
  Gift,
  Phone,
} from 'lucide-react';

type KimTab = 'allgemein' | 'belege' | 'kontrakte' | 'finanzen' | 'audit' | 'tasks' | 'chef' | 'leads' | 'geo';

export default function KimCockpitPage() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customersLoaded, setCustomersLoaded] = useState(false);
  // Leer starten, damit fetchCustomers den ERSTEN echten Kunden auto-selektiert
  // (frueherer Mock-Default 'c1' liess den Workspace im Standby haengen).
  const [selectedCustomerId, setSelectedCustomerId] = useState<string>('');

  // High-Density Workstation Tab Selection
  const [activeTab, setActiveTab] = useState<KimTab>('allgemein');

  // Relational client lists synced with database
  const [contacts, setContacts] = useState<ContactPerson[]>([]);
  const [logs, setLogs] = useState<ContactLog[]>([]);
  const [openItems, setOpenItems] = useState<OpenItem[]>([]);
  const [documents, setDocuments] = useState<BusinessDocument[]>([]);

  // NeuroAI summary copiloting state
  const [neuroSummary, setNeuroSummary] = useState<kimApi.NeuroSummary | null>(null);
  const [neuroLoading, setNeuroLoading] = useState(false);

  // Modals / Overlays triggers
  const [showMasterEditModal, setShowMasterEditModal] = useState(false);
  const [savingMaster, setSavingMaster] = useState(false);
  const [showPresentsModal, setShowPresentsModal] = useState(false);
  const [showCallLogModal, setShowCallLogModal] = useState(false);
  const [savingCall, setSavingCall] = useState(false);
  const [showCorporateModal, setShowCorporateModal] = useState(false);
  const [showDocumentsModal, setShowDocumentsModal] = useState(false);
  const [showCustomerInfoModal, setShowCustomerInfoModal] = useState(false);
  const [workspaceResetKey, setWorkspaceResetKey] = useState(0);

  // In-Edit master data fields state
  const [editStreet, setEditStreet] = useState('');
  const [editCity, setEditCity] = useState('');
  const [editLimit, setEditLimit] = useState(0);
  const [editRep, setEditRep] = useState('');
  const [editDisp, setEditDisp] = useState('');
  const [editChefNote, setEditChefNote] = useState('');
  const [editAlertMsg, setEditAlertMsg] = useState('');

  // Immediate New Call Log form state
  const [quickCallDesc, setQuickCallDesc] = useState('');
  const [quickCallDirection, setQuickCallDirection] = useState<'INCOMING' | 'OUTGOING'>('OUTGOING');

  // Fetch all customers on load
  useEffect(() => {
    fetchCustomers();
  }, []);

  // Sync relational lists whenever selected customer changes
  useEffect(() => {
    if (selectedCustomerId) {
      fetchCustomerDataStreams(selectedCustomerId);
      setNeuroSummary(null); // Clear previous AI evaluations
    }
  }, [selectedCustomerId]);

  const fetchCustomers = async () => {
    try {
      const data = await kimApi.fetchCustomers();
      setCustomers(data);
      if (data.length > 0 && !selectedCustomerId) {
        setSelectedCustomerId(data[0].id);
      }
    } catch (err) {
      console.error("Error fetching customers:", err);
      toast({
        title: 'Kundenstamm konnte nicht geladen werden',
        description: 'Bitte Seite neu laden oder Backend-Verbindung prüfen.',
        variant: 'destructive',
      });
    } finally {
      setCustomersLoaded(true);
    }
  };

  const fetchCustomerDataStreams = async (id: string) => {
    try {
      const [contactsData, logsData, financialsData, docsData] = await Promise.all([
        kimApi.fetchContacts(id),
        kimApi.fetchLogs(id),
        kimApi.fetchFinancials(id),
        kimApi.fetchDocuments(id),
      ]);
      setContacts(contactsData || []);
      setLogs(logsData || []);
      setOpenItems(financialsData || []);
      setDocuments(docsData || []);
    } catch (err) {
      console.error("Failed to load customer relational datastreams:", err);
    }
  };

  const activeCustomer = customers.find(c => c.id === selectedCustomerId) || null;

  // Settle outstanding ledgers
  const totalOutstanding = openItems
    .filter(item => item.status !== 'PAID')
    .reduce((sum, item) => sum + item.amount, 0);

  // Initialize editing state when modal opens
  const openMasterEdit = () => {
    if (!activeCustomer) return;
    setEditStreet(activeCustomer.street);
    setEditCity(activeCustomer.city);
    setEditLimit(activeCustomer.creditLimit);
    setEditRep(activeCustomer.salesRepresentative);
    setEditDisp(activeCustomer.dispatcher);
    setEditChefNote(activeCustomer.chefAnweisung);
    setEditAlertMsg(activeCustomer.alertMessages[0] || '');
    setShowMasterEditModal(true);
  };

  const saveMasterEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeCustomer || savingMaster) return;

    const alertMsgs = editAlertMsg.trim() ? [editAlertMsg.trim()] : [];

    setSavingMaster(true);
    try {
      const data = await kimApi.updateCustomer(activeCustomer.id, {
        street: editStreet,
        city: editCity,
        creditLimit: Number(editLimit),
        salesRepresentative: editRep,
        dispatcher: editDisp,
        chefAnweisung: editChefNote,
        alertMessages: alertMsgs,
      });
      if (data.status === "success") {
        await fetchCustomers();
        setShowMasterEditModal(false);
        toast({ title: 'Stammdaten gespeichert', description: activeCustomer.name });
      }
    } catch (err) {
      console.error("Failed to update master record:", err);
      toast({ title: 'Speichern fehlgeschlagen', variant: 'destructive' });
    } finally {
      setSavingMaster(false);
    }
  };

  // Add Contact Person Dispatcher
  const handleAddNewContactPerson = async (newCP: Partial<ContactPerson>) => {
    if (!activeCustomer) return;
    try {
      const data = await kimApi.createContact(activeCustomer.id, newCP);
      if (data.status === "success") {
        await fetchCustomerDataStreams(activeCustomer.id);
      }
    } catch (err) {
      console.error("Failed to add contact person:", err);
    }
  };

  // Add Contact Log Dispatcher
  const handleAddNewContactLog = async (newLog: Partial<ContactLog>) => {
    if (!activeCustomer) return;
    try {
      const data = await kimApi.createLog(activeCustomer.id, newLog);
      if (data.status === "success") {
        await fetchCustomerDataStreams(activeCustomer.id);
      }
    } catch (err) {
      console.error("Failed to submit interaction log:", err);
    }
  };

  // KIM ist für OP/Belege/Kontrakte lesend — die Anlage erfolgt im jeweiligen
  // Fachprozess (Faktura bzw. Verkaufs-/Belegerfassung). Ehrliche Rückmeldung
  // statt einer scheinbar speichernden Maske.
  const infoFachprozess = (was: string, ziel: string) => {
    toast({
      title: `${was} im Fachprozess anlegen`,
      description: `Bitte ${ziel} verwenden. Das Kunden-Cockpit zeigt ${was} lesend an.`,
    });
  };
  const handleAddNewInvoice = async () => infoFachprozess('Offene Posten', 'die Faktura/Finanzbuchhaltung');
  const handleAddNewDocument = async () => infoFachprozess('Belege', 'die Beleg-/Auftragserfassung');

  // Resolve Follow-up Wiedervorlage
  const handleResolveTask = async (logId: string) => {
    if (!activeCustomer) return;
    try {
      const data = await kimApi.completeLog(logId);
      if (data.status === "success") {
        await fetchCustomerDataStreams(activeCustomer.id);
      }
    } catch (err) {
      console.error("Failed to resolve follow-up task:", err);
    }
  };

  // Quick Direct Call-logger popup submission
  const handleSaveQuickCall = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickCallDesc || !activeCustomer || savingCall) return;
    setSavingCall(true);
    try {
      await handleAddNewContactLog({
        direction: quickCallDirection,
        artKurzinfo: `Telefonat: ${quickCallDesc}`,
        completed: true,
        operator: "JW",
        referenceType: "NONE"
      });
      setQuickCallDesc('');
      setShowCallLogModal(false);
    } finally {
      setSavingCall(false);
    }
  };

  // Trigger NeuroAI Cognitive Dossier Compile
  const handleFetchNeuroSummary = async () => {
    if (!activeCustomer) return;
    setNeuroLoading(true);
    try {
      const data = await kimApi.fetchNeuroSummary(activeCustomer.id);
      setNeuroSummary(data);
    } catch (err) {
      console.error("Error communicating with VALEO cognitive systems:", err);
    } finally {
      setNeuroLoading(false);
    }
  };

  // Handle Action click events dispatched from CustomerActionBar
  const handleHeaderAction = (action: string) => {
    switch (action) {
      case 'openMaster':
        openMasterEdit();
        break;
      case 'newContact': {
        // Trigger quick log input inside the bottom ContactHistoryTable
        const formBtn = document.getElementById('btn-trigger-history-form');
        if (formBtn) {
          formBtn.click();
          formBtn.scrollIntoView({ behavior: 'smooth' });
        }
        break;
      }
      case 'infoPopup':
        setShowCustomerInfoModal(true);
        break;
      case 'sendEmail':
        if (activeCustomer?.email) {
          window.location.href = `mailto:${activeCustomer.email}`;
        } else {
          toast({
            title: 'Keine E-Mail-Adresse',
            description: 'Im Kundenstamm ist keine E-Mail-Adresse hinterlegt.',
            variant: 'destructive',
          });
        }
        break;
      case 'neuroIntelligence':
        handleFetchNeuroSummary();
        break;
      case 'presents':
        setShowPresentsModal(true);
        break;
      case 'logCall':
        setShowCallLogModal(true);
        break;
      case 'newOrder':
        if (activeCustomer) {
          const params = new URLSearchParams({
            kunde: activeCustomer.debtorNo,
            kundeName: activeCustomer.name,
            entryMode: 'crm360',
          });
          navigate(`/sales/angebot-erstellen?${params.toString()}`);
        }
        break;
      case 'billingCheck':
        if (activeCustomer) {
          navigate(`/finance/op-debitoren?kunden_nr=${encodeURIComponent(activeCustomer.debtorNo)}`);
        }
        break;
      case 'cleanupFilters':
        setActiveTab('allgemein');
        setWorkspaceResetKey((key) => key + 1);
        toast({
          title: 'Filter zurückgesetzt',
          description: 'Cockpit-Tabellen und Arbeitsbereich wurden auf den Ausgangszustand gesetzt.',
        });
        break;
      default:
        break;
    }
  };

  const openTasksCount = logs.filter(l => l.reSubmissionDate && !l.completed).length;
  const tabs: { key: KimTab; label: string }[] = [
    { key: 'allgemein', label: 'Allgemein / Ansprechpartner' },
    { key: 'belege', label: 'Belegwesen' },
    { key: 'kontrakte', label: 'Silokontrakte' },
    { key: 'finanzen', label: 'Finanzwesen (Offene Posten)' },
    { key: 'audit', label: 'Unterlagen (Dateien)' },
    { key: 'tasks', label: `Wiedervorlage (${openTasksCount})` },
    { key: 'chef', label: 'Chef-Anweisungen' },
    { key: 'leads', label: 'Lead-Management' },
    { key: 'geo', label: 'CRM-Geo / Karte' },
  ];

  return (
    <div className="flex w-full h-full min-h-[calc(100vh-3.5rem)] bg-muted overflow-hidden" id="app-root-frame">

      {/* COLUMN 1: LEFT SIDEBAR kundenliste & alphabetic selectors */}
      <CustomerListSidebar
        customers={customers}
        selectedCustomerId={selectedCustomerId}
        onSelectCustomer={setSelectedCustomerId}
        onOpenEnterprise={() => setShowCorporateModal(true)}
        onOpenGlobalDocs={() => setShowDocumentsModal(true)}
      />

      {/* WORKSPACE AREA */}
      {activeCustomer ? (
        <div className="flex-1 flex flex-col h-full overflow-hidden bg-background" id="crm-main-viewport">

          {/* Top master Header card & action strip */}
          <div className="p-3 bg-card border-b border-border space-y-2">

            {/* Master data board */}
            <CustomerHeader customer={activeCustomer} />

            {/* Direct operations toolbar */}
            <CustomerActionBar
              onActionClick={handleHeaderAction}
              isLoadingAI={neuroLoading}
            />

            {/* Warn banners, credit calculations & Chef Instruction indicators */}
            <CustomerStatusBanner
              customer={activeCustomer}
              totalOutstanding={totalOutstanding}
            />

          </div>

          {/* MAIN HORIZONTAL SPLIT (Mitte Tabs & Belege | Rechts NeuroAI) */}
          <div className="flex-1 flex overflow-hidden" id="central-split-workspace">

            {/* CENTRAL WORKSPACE (Mitte Tabs) */}
            <div className="flex-1 flex flex-col overflow-hidden border-r border-border" id="center-tabbed-pane">

              {/* Tab Navigation Strips */}
              <div className="flex bg-muted/60 border-b border-border text-xs font-medium select-none overflow-x-auto h-10 items-end px-3 gap-1" id="center-pane-tabs">
                {tabs.map(nav => (
                  <button
                    key={nav.key}
                    onClick={() => setActiveTab(nav.key)}
                    data-action-id={`crm360.tab.${nav.key}`}
                    className={`whitespace-nowrap px-3 py-2 rounded-t-md border-t border-x transition-colors ${
                      activeTab === nav.key
                        ? 'bg-background text-foreground border-border font-semibold translate-y-px'
                        : 'bg-transparent text-muted-foreground hover:text-foreground border-transparent hover:bg-muted'
                    }`}
                    id={`sub-workspace-tab-${nav.key}`}
                  >
                    {nav.label}
                  </button>
                ))}
              </div>

              {/* Central contextual render workspace */}
              <div className="flex-1 overflow-y-auto p-4 bg-background" id="center-tab-views">

                {activeTab === 'allgemein' && (
                  <div className="space-y-4">
                    <ContactPersonsTable
                      key={`contacts-${workspaceResetKey}`}
                      contactPersons={contacts}
                      onAddContactPerson={handleAddNewContactPerson}
                    />
                  </div>
                )}

                {activeTab === 'belege' && (
                  <SalesDocumentsPanel
                    key={`documents-${workspaceResetKey}`}
                    customer={activeCustomer}
                    documents={documents}
                    onAddDocument={handleAddNewDocument}
                  />
                )}

                {activeTab === 'kontrakte' && (
                  <ContractsPanel
                    key={`contracts-${workspaceResetKey}`}
                    customer={activeCustomer}
                    documents={documents}
                    onAddContract={handleAddNewDocument}
                  />
                )}

                {activeTab === 'finanzen' && (
                  <FinancialOpenItemsPanel
                    key={`financials-${workspaceResetKey}`}
                    customer={activeCustomer}
                    openItems={openItems}
                    onAddOpenItem={handleAddNewInvoice}
                  />
                )}

                {activeTab === 'audit' && (
                  <DocumentPanel customer={activeCustomer} />
                )}

                {activeTab === 'tasks' && (
                  <FollowUpTaskPanel
                    logs={logs}
                    customer={activeCustomer}
                    onResolveTask={handleResolveTask}
                  />
                )}

                {activeTab === 'chef' && (
                  <div className="space-y-3 text-sm" id="chef-instruction-workstation">
                    <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 flex flex-col gap-2">
                      <div className="flex items-center gap-2 text-destructive font-semibold border-b border-destructive/20 pb-2 mb-1">
                        <ShieldAlert size={16} className="text-destructive" />
                        <span>Verbindliche Chef-Anweisungen &amp; Restriktionen</span>
                      </div>
                      <blockquote className="italic font-medium text-foreground p-3 bg-card rounded-md border border-border">
                        {activeCustomer.chefAnweisung || 'Derzeit keine speziellen Einschränkungen für diesen Debitor hinterlegt.'}
                      </blockquote>
                      <p className="text-xs text-muted-foreground mt-1">
                        Diese Anweisungen werden Mitarbeitern bei der Angebotserstellung, Gutschrift und Mahnungseröffnung prominent eingeblendet, um rechtliche und PR-Risiken auszuschließen.
                      </p>
                    </div>

                    <div className="rounded-lg border border-border bg-card p-4 space-y-2 shadow-sm">
                      <h4 className="font-semibold text-sm text-foreground">Chef-Anweisungsentwurf bearbeiten</h4>
                      <Textarea
                        onBlur={async (e) => {
                          if (!activeCustomer) return;
                          try {
                            const ret = await kimApi.updateCustomer(activeCustomer.id, { chefAnweisung: e.target.value });
                            if (ret.status === "success") {
                              await fetchCustomers();
                            }
                          } catch (err) {
                            console.error(err);
                            toast({ title: 'Anweisung konnte nicht gespeichert werden', variant: 'destructive' });
                          }
                        }}
                        defaultValue={activeCustomer.chefAnweisung}
                        className="h-24"
                        placeholder="Geben Sie hier die verbindlichen Handlungsanweisungen für alle Vertriebsstellen und das Lager ein…"
                      />
                      <div className="flex justify-between items-center text-xs text-muted-foreground">
                        <span>Klicke außerhalb des Feldes zum automatischen Abspeichern.</span>
                        <span>Bediener: JW</span>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'leads' && (
                  <Suspense fallback={<div className="p-6 text-sm text-muted-foreground">Lead-Management wird geladen…</div>}>
                    <LeadsPage />
                  </Suspense>
                )}

                {activeTab === 'geo' && (
                  <Suspense fallback={<div className="p-6 text-sm text-muted-foreground">Karte wird geladen…</div>}>
                    <KundenKartePage />
                  </Suspense>
                )}

              </div>

              {/* BOTTOM CRM HISTORY TIMELINE (Unten Historie/Belege) */}
              <div className="h-72 border-t border-border bg-background flex flex-col overflow-hidden" id="bottom-history-panel">
                <ContactHistoryTable
                  key={`history-${workspaceResetKey}`}
                  logs={logs}
                  customer={activeCustomer}
                  onAddLog={handleAddNewContactLog}
                />
              </div>

            </div>

            {/* COLUMN 3: RIGHT PANEL (rechts NeuroAI/360°-Statuspanel) */}
            <NeuroAISidePanel
              customer={activeCustomer}
              onRefreshSummary={handleFetchNeuroSummary}
              summaryData={neuroSummary}
              loading={neuroLoading}
            />

          </div>

        </div>
      ) : (
        /* Lade- / Leerzustand */
        <div className="flex-1 flex flex-col justify-center items-center text-center bg-background text-muted-foreground gap-3 p-8">
          {!customersLoaded ? (
            <>
              <Loader2 size={40} className="text-primary animate-spin" />
              <h2 className="font-semibold text-foreground">Kundenstamm wird geladen…</h2>
              <p className="text-sm">Einen Moment bitte, das 360°-Cockpit wird aufgebaut.</p>
            </>
          ) : (
            <>
              <Brain size={40} className="text-muted-foreground/50" />
              <h2 className="font-semibold text-foreground">Kein Kunde ausgewählt</h2>
              <p className="text-sm">Bitte links einen Debitor wählen, um das Cockpit zu öffnen.</p>
            </>
          )}
        </div>
      )}

      {/* OVERLAY: Stammdaten Edit */}
      <Dialog open={showMasterEditModal} onOpenChange={(o) => !o && setShowMasterEditModal(false)}>
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Settings size={16} className="text-primary" />
              Stammdaten &amp; Kreditversicherung bearbeiten
            </DialogTitle>
          </DialogHeader>
          {activeCustomer && (
            <form onSubmit={saveMasterEdit} className="space-y-3 text-sm">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label>Straße / Hausnummer</Label>
                  <Input required value={editStreet} onChange={e => setEditStreet(e.target.value)} />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="crm360-edit-city">PLZ &amp; Ort</Label>
                  <Input id="crm360-edit-city" required value={editCity} onChange={e => setEditCity(e.target.value)} />
                </div>
                <div className="space-y-1">
                  <Label>Kreditversicherungsrahmen (EUR-Limit)</Label>
                  <Input type="number" required value={editLimit} onChange={e => setEditLimit(Number(e.target.value))} />
                </div>
                <div className="space-y-1">
                  <Label>Roter Alarmsignal-Bannertext</Label>
                  <Input
                    value={editAlertMsg}
                    onChange={e => setEditAlertMsg(e.target.value)}
                    placeholder="z.B. Blockierung wegen ungedeckter Schecks"
                    className="text-destructive"
                  />
                </div>
                <div className="space-y-1">
                  <Label>Außendienst-Vertreter (Kürzel · VB)</Label>
                  <Input required value={editRep} onChange={e => setEditRep(e.target.value)} className="uppercase" />
                </div>
                <div className="space-y-1">
                  <Label>Silo-Disponent (Kürzel · Disp.)</Label>
                  <Input required value={editDisp} onChange={e => setEditDisp(e.target.value)} className="uppercase" />
                </div>
              </div>

              <div className="space-y-1">
                <Label>Dringliche Chef-Anweisung</Label>
                <Textarea
                  value={editChefNote}
                  onChange={e => setEditChefNote(e.target.value)}
                  className="h-16"
                  placeholder="Einschränkungen bei Getreideanlieferungen…"
                />
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setShowMasterEditModal(false)}>
                  Abbrechen
                </Button>
                <Button type="submit" disabled={savingMaster}>
                  {savingMaster && <Loader2 className="h-4 w-4 animate-spin" />}
                  Sichern
                </Button>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>

      {/* OVERLAY: Kundeninformation */}
      <Dialog open={showCustomerInfoModal} onOpenChange={(o) => !o && setShowCustomerInfoModal(false)}>
        <DialogContent className="max-w-md" data-testid="crm360-customer-info-dialog">
          <DialogHeader>
            <DialogTitle>Kundeninformation</DialogTitle>
            <DialogDescription>{activeCustomer?.name}</DialogDescription>
          </DialogHeader>
          {activeCustomer && (
            <dl className="grid grid-cols-[9rem_1fr] gap-2 text-sm">
              <dt className="font-medium text-muted-foreground">Debitor</dt><dd>{activeCustomer.debtorNo}</dd>
              <dt className="font-medium text-muted-foreground">Adresse</dt><dd>{activeCustomer.street}, {activeCustomer.zipCode} {activeCustomer.city}</dd>
              <dt className="font-medium text-muted-foreground">Telefon</dt><dd>{activeCustomer.phone1}</dd>
              <dt className="font-medium text-muted-foreground">E-Mail</dt><dd>{activeCustomer.email}</dd>
              <dt className="font-medium text-muted-foreground">Vertreter</dt><dd>{activeCustomer.salesRepresentative}</dd>
              <dt className="font-medium text-muted-foreground">Kreditlimit</dt><dd>EUR {activeCustomer.creditLimit.toLocaleString('de-DE')}</dd>
            </dl>
          )}
          <DialogFooter>
            <Button variant="outline" data-action-id="crm360.customer.info.close" onClick={() => setShowCustomerInfoModal(false)}>
              Schließen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* OVERLAY: Präsente */}
      <Dialog open={showPresentsModal} onOpenChange={(o) => !o && setShowPresentsModal(false)}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Gift size={16} className="text-primary" />
              Präsente &amp; Geschenke-PR-Protokoll
            </DialogTitle>
          </DialogHeader>
          {activeCustomer && (
            <div className="space-y-3 text-sm">
              <p className="text-muted-foreground leading-relaxed">
                Im Agrarsektor ist die Geschenke-PR zur Ernteeinbindung von hoher Relevanz. Verteilte Incentives für Mitarbeiter von <strong>{activeCustomer.name}</strong>:
              </p>
              <div className="space-y-2">
                <div className="p-2.5 rounded-md border border-border bg-muted/40 flex justify-between items-center gap-2">
                  <div>
                    <h4 className="font-medium text-foreground">Sondermodell Taschenmesser (L3)</h4>
                    <p className="text-xs text-muted-foreground">Übergabe durch Jochen Weerda am 15.12.2025</p>
                  </div>
                  <Badge variant="info">1 Stk</Badge>
                </div>
                <div className="p-2.5 rounded-md border border-border bg-muted/40 flex justify-between items-center gap-2">
                  <div>
                    <h4 className="font-medium text-foreground">Historischer Wandkalender Folkerts</h4>
                    <p className="text-xs text-muted-foreground">Postalische Aussendung Dezember 2025</p>
                  </div>
                  <Badge variant="secondary">2 Stk</Badge>
                </div>
                <div className="p-2.5 rounded-md border border-border bg-muted/40 flex justify-between items-center gap-2">
                  <div>
                    <h4 className="font-medium text-foreground">Freikarten Landwirtschaftsmesse Aurich</h4>
                    <p className="text-xs text-muted-foreground">Verteilt für Gutsverwalter Eimo de Buhr</p>
                  </div>
                  <Badge variant="success">2 Karten</Badge>
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPresentsModal(false)}>Protokoll schließen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* OVERLAY: Telefon-Logger */}
      <Dialog open={showCallLogModal} onOpenChange={(o) => !o && setShowCallLogModal(false)}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Phone size={16} className="text-primary" />
              Schnelles Telefonat protokollieren
            </DialogTitle>
          </DialogHeader>
          {activeCustomer && (
            <form onSubmit={handleSaveQuickCall} className="space-y-3 text-sm">
              <div className="space-y-1">
                <Label>Gesprächsrichtung</Label>
                <div className="flex gap-2">
                  <label className="flex-1 flex gap-2 items-center justify-center rounded-md border border-border bg-muted/40 p-2 cursor-pointer select-none">
                    <input type="radio" name="quickDir" checked={quickCallDirection === 'INCOMING'} onChange={() => setQuickCallDirection('INCOMING')} />
                    <span>Eingehend</span>
                  </label>
                  <label className="flex-1 flex gap-2 items-center justify-center rounded-md border border-border bg-muted/40 p-2 cursor-pointer select-none">
                    <input type="radio" name="quickDir" checked={quickCallDirection === 'OUTGOING'} onChange={() => setQuickCallDirection('OUTGOING')} />
                    <span>Ausgehend</span>
                  </label>
                </div>
              </div>
              <div className="space-y-1">
                <Label htmlFor="crm360-quick-call-description">Gesprächs-Kurzbericht</Label>
                <Input
                  id="crm360-quick-call-description"
                  required
                  value={quickCallDesc}
                  onChange={e => setQuickCallDesc(e.target.value)}
                  placeholder="z.B. Bestellt 40t Weizensaatgut, Abholung Montag"
                  autoFocus
                />
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setShowCallLogModal(false)}>Abbrechen</Button>
                <Button type="submit" disabled={savingCall}>
                  {savingCall && <Loader2 className="h-4 w-4 animate-spin" />}
                  Loggen
                </Button>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>

      {/* OVERLAY: Unternehmensprofil */}
      <Dialog open={showCorporateModal} onOpenChange={(o) => !o && setShowCorporateModal(false)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-primary">
              <Building2 size={16} />
              Hinrich Folkerts Landhandel GmbH
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-2 text-sm leading-relaxed text-muted-foreground">
            <p>
              Gegründet im Jahre 1922 in Aurich (Ostfriesland) ist die Firma <strong>Hinrich Folkerts Landhandel</strong> Ihre feste Größe im Norden für Getreide, Mais, Saatgut, Raps und Tiernahrung.
            </p>
            <p>
              Mit dem modernisierten <strong>VALEO NeuroERP 3.0</strong> bündeln wir Disposition, Silo-Gewichte, Logistikplanung und offene Rechnungen in einem System.
            </p>
            <div className="rounded-md border border-border bg-muted/40 p-3 space-y-1 text-foreground">
              <div>Hauptniederlassung: Aurich, Ostfriesland</div>
              <div>Geschäftsführung: Jochen Weerda</div>
              <div>Silo-Lager-Gesamtkapazität: 44.000 Tonnen</div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCorporateModal(false)}>Schließen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* OVERLAY: Sammel-Dokumente */}
      <Dialog open={showDocumentsModal} onOpenChange={(o) => !o && setShowDocumentsModal(false)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileCheck size={16} className="text-primary" />
              Sammel-Dokumente &amp; Richtlinien
            </DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Gemeinsames globales Datei-Archiv für Getreidebestimmungen und Handelsklassen:
          </p>
          <div className="space-y-2">
            {[
              { t: 'Qualitätsrichtlinien Sommergerste 2026', m: 'PDF, 2.4 MB – Stand April 2026' },
              { t: 'Agrarhandel Pauschalierungsgesetz § 24', m: 'PDF, 1.1 MB – Steuermandate 2026' },
              { t: 'Handbuch Dispositionsprofil', m: 'PDF, 4.5 MB – VALEO NeuroERP Handbuch' },
            ].map((d) => (
              <div key={d.t} className="p-2.5 rounded-md border border-border bg-muted/40 flex justify-between items-center gap-2">
                <div>
                  <h4 className="font-medium text-foreground">{d.t}</h4>
                  <p className="text-xs text-muted-foreground">{d.m}</p>
                </div>
                <Button variant="link" size="sm" className="h-auto p-0" onClick={(e) => e.preventDefault()}>Öffnen</Button>
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDocumentsModal(false)}>Schließen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Toaster />
    </div>
  );
}
