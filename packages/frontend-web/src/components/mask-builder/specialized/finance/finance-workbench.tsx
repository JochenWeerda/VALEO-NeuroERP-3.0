import type { SpecializedComponentProps } from '../types'
import { DomainContractBoundary } from '../intake/domain-runtime'
import BankSurface from './bank-surface'
import DunningSurface from './dunning-surface'

const BANK_FIELDS = ['kontoId', 'camtFile', 'statementId', 'startSaldo', 'endSaldo', 'gebuchteUmsaetze', 'zugeordnet', 'nichtZugeordnet', 'abgleichsDifferenz', 'accountingBalance', 'zuordnungData', 'importErrors', 'differences', 'comparisonState']
const DUNNING_FIELDS = ['op_id', 'rechnungsnr', 'partner', 'tage_ueberfaellig', 'offen', 'aktuelle_stufe', 'naechste_stufe', 'dunning_fee', 'interest', 'total_amount', 'id', 'stufe', 'gesamt', 'frist', 'datum', 'status', 'versand_art', 'empfaenger', 'auswahl']

export function FinanceWorkbench({ contract, plan }: SpecializedComponentProps): JSX.Element {
  if (!plan || plan.specialized?.id !== contract.id || plan.specialized.type !== 'finance_workbench'
    || (plan.screenId !== contract.id && !plan.screenId.startsWith('tenant/'))) return <p role="alert">Finanzvertrag ist nicht verfügbar.</p>
  if (contract.id === 'finance/bank-abgleich') return <DomainContractBoundary plan={plan} fields={BANK_FIELDS}><BankSurface plan={plan} /></DomainContractBoundary>
  if (contract.id === 'mahnwesen/mahnlauf') return <DomainContractBoundary plan={plan} fields={DUNNING_FIELDS}><DunningSurface plan={plan} /></DomainContractBoundary>
  return <p role="alert">Unbekannter Finanzvertrag.</p>
}
