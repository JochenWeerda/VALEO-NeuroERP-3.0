const fs = require('fs');
const path = require('path');
const ts = require('typescript');

const registryPath = path.resolve(__dirname, '../packages/frontend-web/src/config/l3-customer-field-registry.ts');
const source = fs.readFileSync(registryPath, 'utf8');
const transpiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2019 },
});
const moduleExports = {};
const moduleWrapper = new Function('exports', 'require', 'module', '__filename', '__dirname', transpiled.outputText);
moduleWrapper(moduleExports, require, { exports: moduleExports }, registryPath, path.dirname(registryPath));
const { CUSTOMER_FIELDS } = moduleExports;

const TAB_LABELS = {
  masterdata: 'Stammdaten',
  address: 'Adresse & Kommunikation',
  finance: 'Finanzen & Konditionen',
  tax: 'Steuern & Rechtliches',
  bank: 'Bank & Zahlung',
  logistics: 'Logistik & Lieferung',
  marketing: 'Marketing & CRM',
  quality_compliance: 'QS & Compliance',
  cooperative: 'Genossenschaft & Gemeinschaften',
  interfaces: 'Schnittstellen',
  output: 'Versand & Ausgabe',
  contacts: 'Ansprechpartner',
  system: 'System & Historie',
};

const SECTION_LABELS = {
  masterdata_basic: 'Basisdaten',
  masterdata_general: 'Allgemein',
  masterdata_classification: 'Klassifizierung',
  masterdata_responsibility: 'Verantwortlichkeiten',
  address_main: 'Hauptanschrift',
  address_additional: 'Weitere Adressen',
  address_communication: 'Kommunikation',
  finance_invoice_account: 'Rechnung & Kontoauszug',
  finance_customer_discounts: 'Kundenrabatte',
  finance_agreed_prices: 'Vereinbarte Kundenpreise',
  finance_pricing_global: 'Preise & Rabatte',
  finance_payment_terms: 'Zahlungsbedingungen',
  finance_accounting: 'Finanzverwaltung',
  tax_flags: 'Steuermerkmale',
  bank_accounts: 'Bankverbindungen',
  logistics_description: 'Lieferparameter',
  marketing_customer_profile: 'Kundenprofil',
  marketing_mailing_lists: 'Mailinglisten',
  quality_farm_ids: 'VVVO / Zertifikate',
  cooperative_shares: 'Genossenschaftsanteile',
  cooperative_farming_groups: 'Betriebsgemeinschaften',
  interfaces_integration: 'Integration & Schnittstellen',
  output_document_delivery: 'Versandinformationen',
  output_delivery_payment_terms: 'Lieferung & Zahlung',
  contacts_primary: 'Primärer Kontakt',
  contacts_list: 'Kontaktliste',
  system_metadata: 'Systemfelder',
  system_blocking: 'Sperren',
  system_misc: 'Sonstige Felder',
  system_selections: 'Selektionen',
  system_notes: 'Notizen',
};

const selectRefs = new Map([
  ['customer.sales_rep', 'salesReps'],
  ['customer.dispatcher', 'dispatchers'],
  ['customer.group', 'customerGroups'],
  ['customer.country', 'countries'],
  ['customer.state', 'states'],
  ['system.branch', 'branches'],
  ['system.cost_center', 'costCenters'],
  ['profile.industry_code', 'industries'],
]);

function humanize(value) {
  return value
    .split(/[_-]/)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

function detectComponent(field) {
  const { key, label } = field;
  const lowerLabel = label.toLowerCase();
  if (/date|datum|erstanlage|gründung|since|eintritt|austritt/.test(lowerLabel) || /(date|_at|_since)$/i.test(key)) {
    return 'DatePicker';
  }
  if (selectRefs.has(key) || /status|art|gruppe|region|tour|segment|opt-in|optout|typ|kategorie/.test(lowerLabel)) {
    return 'Select';
  }
  if (/sperre|flag|enabled|deaktiviert|selbstabrechnung|kontoauszug/.test(lowerLabel)) {
    return 'Checkbox';
  }
  return 'TextField';
}

function buildField(field) {
  const component = detectComponent(field);
  const validators = [];
  const isSystem = field.key.startsWith('system.');
  if (field.priority === 'core' && !isSystem) {
    validators.push('required');
  }
  if (field.key.includes('email')) {
    validators.push('email');
  }
  const base = {
    id: field.key,
    binding: field.key,
    label: field.label,
    component,
    coreField: field.priority === 'core',
    required: field.priority === 'core' && !isSystem,
  };
  if (validators.length) {
    base.validators = Array.from(new Set(validators));
  }
  if (isSystem) {
    base.readonly = true;
  }
  if (component === 'Select') {
    base.optionsRef = selectRefs.get(field.key) || `${field.key.replace(/\./g, '_')}_options`;
  }
  return base;
}

const tabMap = new Map();
for (const field of CUSTOMER_FIELDS) {
  if (!tabMap.has(field.tab)) {
    tabMap.set(field.tab, {
      id: field.tab,
      label: TAB_LABELS[field.tab] || humanize(field.tab),
      sections: new Map(),
    });
  }
  const tab = tabMap.get(field.tab);
  if (!tab.sections.has(field.section)) {
    tab.sections.set(field.section, {
      id: field.section,
      label: SECTION_LABELS[field.section] || humanize(field.section),
      layout: { columns: 2 },
      fields: [],
    });
  }
  tab.sections.get(field.section).fields.push(buildField(field));
}

const tabs = Array.from(tabMap.values()).map((tab) => ({
  id: tab.id,
  label: tab.label,
  sections: Array.from(tab.sections.values()),
}));

const mask = {
  resource: 'customer',
  version: '1.0.0',
  tabs,
  validators: {
    required: { type: 'required', message: 'Dieses Feld ist erforderlich.' },
    email: { type: 'pattern', pattern: '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$', message: 'Bitte eine gültige E-Mail-Adresse eingeben.' },
  },
  api: {
    get: { mode: 'hook', hook: 'useCustomer' },
    create: { mode: 'hook', hook: 'useCreateCustomer' },
    update: { mode: 'hook', hook: 'useUpdateCustomer' },
  },
};

const outputPath = path.resolve(__dirname, '../packages/frontend-web/src/config/mask-builder-customer.json');
fs.writeFileSync(outputPath, JSON.stringify(mask, null, 2) + '\n');
