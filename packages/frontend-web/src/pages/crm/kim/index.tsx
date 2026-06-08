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
  MapPin, 
  ShieldAlert, 
  Sparkles, 
  Settings, 
  FileCheck, 
  X, 
  Check, 
  Brain,
  MessageSquareWarning,
  Plus
} from 'lucide-react';

type KimTab = 'allgemein' | 'belege' | 'kontrakte' | 'finanzen' | 'audit' | 'tasks' | 'chef' | 'leads' | 'geo';

export default function KimCockpitPage() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [customers, setCustomers] = useState<Customer[]>([]);
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
  const [showPresentsModal, setShowPresentsModal] = useState(false);
  const [showCallLogModal, setShowCallLogModal] = useState(false);
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
    if (!activeCustomer) return;

    const alertMsgs = editAlertMsg.trim() ? [editAlertMsg.trim()] : [];

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
      }
    } catch (err) {
      console.error("Failed to update master record:", err);
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
    if (!quickCallDesc || !activeCustomer) return;
    await handleAddNewContactLog({
      direction: quickCallDirection,
      artKurzinfo: `Telefonat: ${quickCallDesc}`,
      completed: true,
      operator: "JW", 
      referenceType: "NONE"
    });
    setQuickCallDesc('');
    setShowCallLogModal(false);
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

  return (
    <div className="flex w-full h-full min-h-[calc(100vh-3.5rem)] bg-[#e2e8f0] overflow-hidden select-none" id="app-root-frame">
      
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
        <div className="flex-1 flex flex-col h-full overflow-hidden bg-white" id="crm-main-viewport">
          
          {/* Top master Header card & action strip */}
          <div className="p-2 bg-slate-50 border-b border-[#cbd5e1] space-y-1 select-none">
            
            {/* L3 master data board */}
            <CustomerHeader customer={activeCustomer} />

            {/* Direct operations bar with keyboard shortcuts indicators */}
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
            <div className="flex-1 flex flex-col overflow-hidden border-r border-[#cbd5e1]" id="center-tabbed-pane">
              
              {/* Tab Navigation Strips */}
              <div className="flex bg-[#cbd5e1]/40 border-b border-[#cbd5e1] text-[11px] font-sans font-bold select-none overflow-x-auto leading-none h-[2.375rem] items-end px-3 gap-0.5" id="center-pane-tabs">
                {[
                  { key: 'allgemein', label: 'Allgemein / Ansprechpartner' },
                  { key: 'belege', label: 'Belegwesen' },
                  { key: 'kontrakte', label: 'Silokontrakte' },
                  { key: 'finanzen', label: 'Finanzwesen (Offene Posten)' },
                  { key: 'audit', label: 'Unterlagen (Dateien)' },
                  { key: 'tasks', label: `Wiedervorlage (${logs.filter(l=>l.reSubmissionDate && !l.completed).length})` },
                  { key: 'chef', label: 'Chef-Anweisungen' },
                  { key: 'leads', label: 'Lead-Management' },
                  { key: 'geo', label: 'CRM-Geo / Karte' }
                ].map(nav => (
                  <button
                    key={nav.key}
                    onClick={() => setActiveTab(nav.key as KimTab)}
                    data-action-id={`crm360.tab.${nav.key}`}
                    className={`px-3 py-2 uppercase transition-all duration-150 rounded-t-sm border-t border-x cursor-pointer ${
                      activeTab === nav.key 
                        ? 'bg-white text-[#111827] border-[#cbd5e1] font-black translate-y-[1px] z-10' 
                        : 'bg-transparent text-gray-500 hover:text-gray-800 border-transparent hover:bg-[#cbd5e1]/20'
                    }`}
                    id={`sub-workspace-tab-${nav.key}`}
                  >
                    {nav.label}
                  </button>
                ))}
              </div>

              {/* Central contextual render workspace */}
              <div className="flex-1 overflow-y-auto p-3 bg-white" id="center-tab-views">
                
                {activeTab === 'allgemein' && (
                  <div className="space-y-4 font-sans text-xs">
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
                  <div className="space-y-3 font-sans text-xs" id="chef-instruction-workstation">
                    <div className="bg-red-50 border border-red-200 p-4 rounded flex flex-col gap-2">
                      <div className="flex items-center gap-1.5 text-red-950 font-bold uppercase leading-none border-b border-red-100 pb-1.5 mb-1 text-[11px]">
                        <ShieldAlert size={14} className="text-red-700 font-extrabold animate-pulse" />
                        <span>Verbindliche Chef-Anweisungen & Restriktionen</span>
                      </div>
                      <blockquote className="italic font-bold font-sans text-sm text-red-900 p-2.5 bg-white rounded border border-red-100 shadow-inner">
                        {activeCustomer.chefAnweisung || '"Derzeit keine speziellen Einschränkungen für diesen Debitor hinterlegt."'}
                      </blockquote>
                      <p className="text-[10px] text-gray-500 mt-1">
                        *Diese Anweisungen werden Mandanten-Mitarbeitern (Bedienern wie AO, CHM, JW) bei der Angebotserstellung, Gutschrift und Mahnungseröffnung prominent eingeblendet, um rechtliche und PR-Risiken auszuschließen.
                      </p>
                    </div>

                    <div className="bg-white border border-gray-200 p-3 rounded shadow-sm space-y-1.5">
                      <h4 className="font-bold text-[10px] uppercase text-gray-400 tracking-wider font-mono">Chef-Anweisungsentwurf bearbeiten</h4>
                      <textarea
                        onBlur={async (e) => {
                          if (!activeCustomer) return;
                          try {
                            const ret = await kimApi.updateCustomer(activeCustomer.id, { chefAnweisung: e.target.value });
                            if (ret.status === "success") {
                              await fetchCustomers();
                            }
                          } catch (err) {
                            console.error(err);
                          }
                        }}
                        defaultValue={activeCustomer.chefAnweisung}
                        className="w-full h-24 p-2 border border-gray-300 rounded font-sans text-xs outline-none focus:ring-1 focus:ring-[#006633]"
                        placeholder="Geben Sie hier die verbindlichen Handlungsanweisungen für alle Vertriebsstellen und das Lager ein..."
                      />
                      <div className="flex justify-between items-center text-[9px] text-gray-400 font-mono">
                        <span>*Klicke außerhalb des Feldes zum automatischen Abspeichern.</span>
                        <span>Bediener: JW</span>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'leads' && (
                  <Suspense fallback={<div className="p-6 text-xs text-gray-400 font-sans">Lead-Management wird geladen…</div>}>
                    <LeadsPage />
                  </Suspense>
                )}

                {activeTab === 'geo' && (
                  <Suspense fallback={<div className="p-6 text-xs text-gray-400 font-sans">Karte wird geladen…</div>}>
                    <KundenKartePage />
                  </Suspense>
                )}

              </div>

              {/* BOTTOM CRM HISTORY TIMELINE (Unten Historie/Belege) */}
              <div className="h-68 border-t border-[#cbd5e1] bg-white flex flex-col overflow-hidden" id="bottom-history-panel">
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
        /* Standby initialization loader view */
        <div className="flex-1 flex flex-col justify-center items-center text-center bg-[#f1f5f9] text-gray-400 font-sans text-sm gap-2">
          <Brain size={48} className="text-slate-300 animate-pulse" />
          <h2 className="font-extrabold text-slate-700">VALEO NeuroERP Cockpit wird gestartet...</h2>
          <p className="text-gray-400 text-xs font-mono uppercase">L3 Schnittstellenbaugruppe initialisiert</p>
        </div>
      )}

      {/* ======================================= */}
      {/* OVERLAY MODAL 1: Stammdaten Edit */}
      {/* ======================================= */}
      {showMasterEditModal && activeCustomer && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-labelledby="crm360-master-title">
          <form onSubmit={saveMasterEdit} className="bg-white rounded border border-[#cbd5e1] shadow-2xl max-w-xl w-full p-4 space-y-3 font-sans text-xs">
            <div className="flex justify-between items-center border-b border-gray-100 pb-2">
              <div className="flex items-center gap-1.5 text-gray-900 font-bold">
                <Settings size={14} className="text-[#006633]" />
                <span id="crm360-master-title" className="text-xs font-extrabold uppercase font-mono">Stammdaten & Kreditversicherung bearbeiten</span>
              </div>
              <button 
                type="button" 
                onClick={() => setShowMasterEditModal(false)}
                className="text-gray-400 hover:text-gray-600 transition"
              >
                <X size={15} />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="block text-gray-500 font-bold uppercase mb-0.5">Strasse / Hausnummer</label>
                <input
                  type="text"
                  required
                  value={editStreet}
                  onChange={e => setEditStreet(e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded px-2.5 py-1 outline-none font-medium text-xs focus:ring-1 focus:ring-[#006633]"
                />
              </div>
              <div>
                <label htmlFor="crm360-edit-city" className="block text-gray-500 font-bold uppercase mb-0.5">PLZ & Ort</label>
                <input
                  id="crm360-edit-city"
                  type="text"
                  required
                  value={editCity}
                  onChange={e => setEditCity(e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded px-2.5 py-1 outline-none font-medium text-xs focus:ring-1 focus:ring-[#006633]"
                />
              </div>
              <div>
                <label className="block text-gray-500 font-bold uppercase mb-0.5">Kreditversicherungsverband Rahmen (EUR-Limit)</label>
                <input
                  type="number"
                  required
                  value={editLimit}
                  onChange={e => setEditLimit(Number(e.target.value))}
                  className="w-full bg-white border border-gray-300 rounded px-2.5 py-1 outline-none font-medium text-xs focus:ring-1 focus:ring-[#006633]"
                />
              </div>
              <div>
                <label className="block text-gray-500 font-bold uppercase mb-0.5">Roter Alarmsignal-Bannertext</label>
                <input
                  type="text"
                  value={editAlertMsg}
                  onChange={e => setEditAlertMsg(e.target.value)}
                  placeholder="z.B. Blockierung wegen ungedeckter Schecks"
                  className="w-full bg-white border border-gray-300 rounded px-2.5 py-1 outline-none font-medium text-xs focus:ring-1 focus:ring-red-500 text-red-700 font-bold"
                />
              </div>
              <div>
                <label className="block text-gray-500 font-bold uppercase mb-0.5">Außendienst Vertreter (Kürzel - VB)</label>
                <input
                  type="text"
                  required
                  value={editRep}
                  onChange={e => setEditRep(e.target.value)}
                  className="w-full bg-slate-50 border border-gray-300 rounded px-2.5 py-1 outline-none font-extrabold text-xs text-[#006633] text-center uppercase"
                />
              </div>
              <div>
                <label className="block text-gray-500 font-bold uppercase mb-0.5">Silo-Disponent (Kürzel - Disp.)</label>
                <input
                  type="text"
                  required
                  value={editDisp}
                  onChange={e => setEditDisp(e.target.value)}
                  className="w-full bg-slate-50 border border-gray-300 rounded px-2.5 py-1 outline-none font-extrabold text-xs text-gray-800 text-center uppercase"
                />
              </div>
            </div>

            <div>
              <label className="block text-gray-500 font-bold uppercase mb-0.5">Dringliche Chef-Anweisung</label>
              <textarea
                value={editChefNote}
                onChange={e => setEditChefNote(e.target.value)}
                className="w-full h-16 p-1.5 border border-gray-300 rounded outline-none w-full text-xs"
                placeholder="Einschränkungen bei Getreideanlieferungen..."
              />
            </div>

            <div className="flex gap-2 justify-end border-t border-gray-100 pt-2.5">
              <button
                type="button"
                onClick={() => setShowMasterEditModal(false)}
                className="px-3 py-1 border border-gray-300 rounded text-gray-600 bg-white hover:bg-gray-50 font-bold cursor-pointer"
              >
                Abbrechen
              </button>
              <button
                type="submit"
                className="px-4 py-1 bg-[#006633] text-white rounded font-bold hover:bg-emerald-800 transition cursor-pointer"
              >
                Sichern
              </button>
            </div>
          </form>
        </div>
      )}

      {showCustomerInfoModal && activeCustomer && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="crm360-customer-info-title"
          data-testid="crm360-customer-info-dialog"
        >
          <div className="bg-white rounded border border-[#cbd5e1] shadow-2xl max-w-md w-full p-5 space-y-3 font-sans text-xs">
            <div className="flex justify-between items-center border-b border-gray-100 pb-2">
              <div>
                <h2 id="crm360-customer-info-title" className="font-black uppercase font-mono">Kundeninformation</h2>
                <p className="text-gray-500">{activeCustomer.name}</p>
              </div>
              <button
                type="button"
                onClick={() => setShowCustomerInfoModal(false)}
                data-action-id="crm360.customer.info.close"
                aria-label="Kundeninformation schließen"
                className="text-gray-400 hover:text-gray-600 transition"
              >
                <X size={15} />
              </button>
            </div>
            <dl className="grid grid-cols-[9rem_1fr] gap-2">
              <dt className="font-bold text-gray-500">Debitor</dt><dd>{activeCustomer.debtorNo}</dd>
              <dt className="font-bold text-gray-500">Adresse</dt><dd>{activeCustomer.street}, {activeCustomer.zipCode} {activeCustomer.city}</dd>
              <dt className="font-bold text-gray-500">Telefon</dt><dd>{activeCustomer.phone1}</dd>
              <dt className="font-bold text-gray-500">E-Mail</dt><dd>{activeCustomer.email}</dd>
              <dt className="font-bold text-gray-500">Vertreter</dt><dd>{activeCustomer.salesRepresentative}</dd>
              <dt className="font-bold text-gray-500">Kreditlimit</dt><dd>EUR {activeCustomer.creditLimit.toLocaleString('de-DE')}</dd>
            </dl>
          </div>
        </div>
      )}

      {/* ======================================= */}
      {/* OVERLAY MODAL 2: PRÄSENTE */}
      {/* ======================================= */}
      {showPresentsModal && activeCustomer && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded border border-[#cbd5e1] shadow-2xl max-w-sm w-full p-4 space-y-3 font-sans text-xs">
            <div className="flex justify-between items-center border-b border-gray-100 pb-2">
              <span className="font-extrabold text-xs text-gray-900 uppercase font-mono flex items-center gap-1.5">
                🎁 Präsente & Geschenke-PR Protokoll
              </span>
              <button onClick={() => setShowPresentsModal(false)} className="text-gray-400 hover:text-gray-600 transition">
                <X size={15} />
              </button>
            </div>

            <p className="text-gray-600 leading-relaxed font-medium">
              Im Agrarsektor ist die Geschenke-PR zur Ernteeinbindung von hoher Relevanz. Hier sehen Sie die verteilten Incentives für Mitarbeiter von <strong>{activeCustomer.name}</strong>:
            </p>

            <div className="space-y-1.5 font-sans">
              <div className="p-2 bg-[#f0f9ff] border-l-4 border-blue-500 rounded flex justify-between items-center">
                <div>
                  <h4 className="font-bold text-gray-800">Sondermodell Taschenmesser (L3)</h4>
                  <p className="text-[9px] text-gray-400">Übergabe durch Jochen Weerda am 15.12.2025</p>
                </div>
                <span className="bg-blue-100 text-blue-700 font-mono text-[9px] px-1 rounded font-bold">1 Stk</span>
              </div>
              <div className="p-2 bg-rose-50 border-l-4 border-rose-500 rounded flex justify-between items-center">
                <div>
                  <h4 className="font-bold text-gray-800">Historischer Wandkalender Folkerts</h4>
                  <p className="text-[9px] text-gray-400">Postalische Aussendung Dezember 2025</p>
                </div>
                <span className="bg-rose-100 text-rose-700 font-mono text-[9px] px-1 rounded font-bold">2 Stk</span>
              </div>
              <div className="p-2 bg-emerald-50 border-l-4 border-emerald-500 rounded flex justify-between items-center">
                <div>
                  <h4 className="font-bold text-gray-800">Freikarten Landwirtschaftsmesse Aurich</h4>
                  <p className="text-[9px] text-gray-400">Verteilt für Gutsverwalter Eimo de Buhr</p>
                </div>
                <span className="bg-emerald-100 text-emerald-700 font-mono text-[9px] px-1 rounded font-bold">2 Karten</span>
              </div>
            </div>

            <button
              onClick={() => setShowPresentsModal(false)}
              className="w-full py-1.5 bg-[#006633] text-white rounded font-mono font-bold text-center hover:bg-emerald-800 cursor-pointer text-[10px] uppercase tracking-wide leading-none"
            >
              Protokoll schließen
            </button>
          </div>
        </div>
      )}

      {/* ======================================= */}
      {/* OVERLAY MODAL 3: TELEFON-LOGGER */}
      {/* ======================================= */}
      {showCallLogModal && activeCustomer && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <form onSubmit={handleSaveQuickCall} className="bg-white rounded border border-gray-300 shadow-2xl max-w-sm w-full p-4 space-y-3 font-sans text-xs">
            <div className="flex justify-between items-center border-b border-gray-200 pb-2">
              <span className="font-extrabold text-xs text-gray-900 uppercase font-mono">📞 Schnelles Telefonat protokollieren</span>
              <button type="button" onClick={() => setShowCallLogModal(false)} className="text-gray-400 hover:text-gray-600 transition">
                <X size={15} />
              </button>
            </div>

            <div className="space-y-2">
              <div>
                <label className="block text-[9px] text-gray-400 uppercase font-bold mb-0.5">Gesprächsrichtung</label>
                <div className="flex gap-1.5 font-sans text-[10.5px] font-bold">
                  <label className="flex-1 flex gap-1.5 items-center bg-gray-50 p-1 rounded border border-gray-200 cursor-pointer justify-center select-none">
                    <input
                      type="radio"
                      name="quickDir"
                      checked={quickCallDirection === 'INCOMING'}
                      onChange={() => setQuickCallDirection('INCOMING')}
                    />
                    <span>Eingehend</span>
                  </label>
                  <label className="flex-1 flex gap-1.5 items-center bg-gray-50 p-1 rounded border border-gray-200 cursor-pointer justify-center select-none">
                    <input
                      type="radio"
                      name="quickDir"
                      checked={quickCallDirection === 'OUTGOING'}
                      onChange={() => setQuickCallDirection('OUTGOING')}
                    />
                    <span>Ausgehend</span>
                  </label>
                </div>
              </div>

              <div>
                <label htmlFor="crm360-quick-call-description" className="block text-[9px] text-gray-400 uppercase font-bold mb-0.5">Gesprächs-Kurzbericht</label>
                <input
                  id="crm360-quick-call-description"
                  type="text"
                  required
                  value={quickCallDesc}
                  onChange={e => setQuickCallDesc(e.target.value)}
                  placeholder="z.B. Bestellt 40t Weizensaatgut, Abholung Montag"
                  className="w-full bg-white border border-gray-300 rounded p-2 text-xs outline-none focus:ring-1 focus:ring-[#006633]"
                  autoFocus
                />
              </div>
            </div>

            <div className="flex gap-2 justify-end pt-2 border-t border-gray-100">
              <button
                type="button"
                onClick={() => setShowCallLogModal(false)}
                className="px-3 py-1 border border-gray-300 rounded text-gray-600 hover:bg-gray-50 font-bold cursor-pointer"
              >
                Abbrechen
              </button>
              <button
                type="submit"
                className="px-4 py-1 bg-[#006633] text-white rounded font-extrabold hover:bg-emerald-800 cursor-pointer"
              >
                Loggen
              </button>
            </div>
          </form>
        </div>
      )}

      {/* ======================================= */}
      {/* OVERLAY MODAL 4: HINRIC FOLKERTS BRAND */}
      {/* ======================================= */}
      {showCorporateModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded border border-[#cbd5e1] shadow-2xl max-w-md w-full p-5 space-y-3 font-sans text-xs">
            <div className="flex justify-between items-center border-b border-gray-100 pb-2">
              <div className="flex items-center gap-1.5 font-bold text-[#006633]">
                <Building2 size={15} />
                <span className="text-xs font-black uppercase font-mono">Hinrich Folkerts Landhandel GmbH</span>
              </div>
              <button onClick={() => setShowCorporateModal(false)} className="text-gray-400 hover:text-gray-600 transition">
                <X size={15} />
              </button>
            </div>

            <div className="space-y-2 leading-relaxed text-gray-600">
              <p>
                Gegründet im Jahre 1922 in Aurich (Ostfriesland) ist die Firma <strong>Hinrich Folkerts Landhandel</strong> Ihre feste Größe im Norden für Getreide, Mais, Saatgut, Raps und Tiernahrung.
              </p>
              <p>
                Mit unserem modernisierten <strong>VALEO NeuroERP 3.0 Module L3</strong> bündeln wir Disposition, Silo-Gewichte, Logistikplanung und offene Rechnungen in einem System.
              </p>
              
              <div className="p-2.5 bg-gray-50 border border-gray-200 rounded text-[9.5px] font-mono space-y-1 text-slate-700">
                <div>Hauptniederlassung: Aurich, Ostfriesland</div>
                <div>Geschäftsführung: Jochen Weerda</div>
                <div>Silo-Lager-Gesamtkapazität: 44.000 Tonnen</div>
                <div>Schnittstelletyp: L3 System-ERP Desktop Interconnect</div>
              </div>
            </div>

            <button
              onClick={() => setShowCorporateModal(false)}
              className="w-full py-1.5 bg-slate-800 text-white rounded font-bold text-center hover:bg-slate-900 cursor-pointer"
            >
              Schließen
            </button>
          </div>
        </div>
      )}

      {/* ======================================= */}
      {/* OVERLAY MODAL 5: SAMMEL-DOKUMENTE */}
      {/* ======================================= */}
      {showDocumentsModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded border border-[#cbd5e1] shadow-2xl max-w-md w-full p-5 space-y-3 font-sans text-xs">
            <div className="flex justify-between items-center border-b border-gray-100 pb-2">
              <div className="flex items-center gap-1.5 font-bold text-gray-900">
                <FileCheck size={15} className="text-indigo-700 font-extrabold" />
                <span className="text-xs font-black uppercase font-mono">Sammel-Dokumente & Richtlinien</span>
              </div>
              <button onClick={() => setShowDocumentsModal(false)} className="text-gray-400 hover:text-gray-600 transition">
                <X size={15} />
              </button>
            </div>

            <p className="text-gray-600">
              Gemeinsames globales Datei-Archiv von VALEO NeuroERP für Getreidebestimmungen und Handelsklassen:
            </p>

            <div className="space-y-1.5">
              <div className="p-2 bg-slate-50 border border-gray-200 rounded flex justify-between items-center">
                <div>
                  <h4 className="font-bold text-slate-800">Qualitätsrichtlinien Sommergerste 2026</h4>
                  <p className="text-[9px] text-gray-400">PDF, 2.4 MB - Stand April 2026</p>
                </div>
                <a href="#" className="text-[10px] text-blue-700 font-bold hover:underline" onClick={(e)=>e.preventDefault()}>Öffnen</a>
              </div>
              <div className="p-2 bg-slate-50 border border-gray-200 rounded flex justify-between items-center">
                <div>
                  <h4 className="font-bold text-slate-800">Agrarhandel Pauschalierungsgesetz § 24</h4>
                  <p className="text-[9px] text-gray-400">PDF, 1.1 MB - Steuermandate 2026</p>
                </div>
                <a href="#" className="text-[10px] text-blue-700 font-bold hover:underline" onClick={(e)=>e.preventDefault()}>Öffnen</a>
              </div>
              <div className="p-2 bg-slate-50 border border-gray-200 rounded flex justify-between items-center">
                <div>
                  <h4 className="font-bold text-slate-800">Handbuch L3 Dispositionsprofil</h4>
                  <p className="text-[9px] text-gray-400">PDF, 4.5 MB - VALEO NeuroERP Handbuch</p>
                </div>
                <a href="#" className="text-[10px] text-blue-700 font-bold hover:underline" onClick={(e)=>e.preventDefault()}>Öffnen</a>
              </div>
            </div>

            <button
              onClick={() => setShowDocumentsModal(false)}
              className="w-full py-1.5 bg-slate-800 text-white rounded font-bold text-center hover:bg-slate-900 cursor-pointer"
            >
              Schließen
            </button>
          </div>
        </div>
      )}

      <Toaster />
    </div>
  );
}
