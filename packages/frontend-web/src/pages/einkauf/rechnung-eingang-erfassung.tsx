import { InvoiceCapturePage } from '@/pages/finance/InvoiceCapturePage'

/** Eingangsrechnung erfassen: dieselbe Studio-Erfassung wie /finance/ap/invoices/new (einkauf/rechnungseingang/neu). */
export default function EinkaufRechnungEingangErfassungPage(): JSX.Element {
  return <InvoiceCapturePage purchase />
}
