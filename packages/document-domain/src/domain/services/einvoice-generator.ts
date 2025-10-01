import pino from 'pino';

const logger = pino({ name: 'einvoice-generator' });

export interface InvoiceData {
  invoiceNumber: string;
  invoiceDate: string;
  dueDate: string;
  seller: {
    name: string;
    vatId: string;
    address: string;
    city: string;
    postalCode: string;
    country: string;
  };
  buyer: {
    name: string;
    vatId?: string;
    address: string;
    city: string;
    postalCode: string;
    country: string;
  };
  items: Array<{
    description: string;
    quantity: number;
    unitPrice: number;
    vatRate: number;
    netAmount: number;
  }>;
  totalNet: number;
  totalVat: number;
  totalGross: number;
  currency: string;
}

export async function generateXRechnung(data: InvoiceData): Promise<string> {
  logger.info({ invoiceNumber: data.invoiceNumber }, 'Generating XRechnung XML');

  // Simplified XRechnung XML (UBL format)
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:CustomizationID>urn:cen.eu:en16931:2017***REMOVED***compliant***REMOVED***urn:xeinkauf.de:kosit:xrechnung_3.0</cbc:CustomizationID>
  <cbc:ID>${escapeXml(data.invoiceNumber)}</cbc:ID>
  <cbc:IssueDate>${data.invoiceDate}</cbc:IssueDate>
  <cbc:DueDate>${data.dueDate}</cbc:DueDate>
  <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode>${data.currency}</cbc:DocumentCurrencyCode>
  
  <cac:AccountingSupplierParty>
    <cac:Party>
      <cac:PartyName>
        <cbc:Name>${escapeXml(data.seller.name)}</cbc:Name>
      </cac:PartyName>
      <cac:PostalAddress>
        <cbc:StreetName>${escapeXml(data.seller.address)}</cbc:StreetName>
        <cbc:CityName>${escapeXml(data.seller.city)}</cbc:CityName>
        <cbc:PostalZone>${data.seller.postalCode}</cbc:PostalZone>
        <cac:Country>
          <cbc:IdentificationCode>${data.seller.country}</cbc:IdentificationCode>
        </cac:Country>
      </cac:PostalAddress>
      <cac:PartyTaxScheme>
        <cbc:CompanyID>${data.seller.vatId}</cbc:CompanyID>
        <cac:TaxScheme>
          <cbc:ID>VAT</cbc:ID>
        </cac:TaxScheme>
      </cac:PartyTaxScheme>
    </cac:Party>
  </cac:AccountingSupplierParty>
  
  <cac:AccountingCustomerParty>
    <cac:Party>
      <cac:PartyName>
        <cbc:Name>${escapeXml(data.buyer.name)}</cbc:Name>
      </cac:PartyName>
      <cac:PostalAddress>
        <cbc:StreetName>${escapeXml(data.buyer.address)}</cbc:StreetName>
        <cbc:CityName>${escapeXml(data.buyer.city)}</cbc:CityName>
        <cbc:PostalZone>${data.buyer.postalCode}</cbc:PostalZone>
        <cac:Country>
          <cbc:IdentificationCode>${data.buyer.country}</cbc:IdentificationCode>
        </cac:Country>
      </cac:PostalAddress>
    </cac:Party>
  </cac:AccountingCustomerParty>
  
  ${data.items
    .map(
      (item, idx) => `
  <cac:InvoiceLine>
    <cbc:ID>${idx + 1}</cbc:ID>
    <cbc:InvoicedQuantity unitCode="C62">${item.quantity}</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount currencyID="${data.currency}">${item.netAmount.toFixed(2)}</cbc:LineExtensionAmount>
    <cac:Item>
      <cbc:Description>${escapeXml(item.description)}</cbc:Description>
    </cac:Item>
    <cac:Price>
      <cbc:PriceAmount currencyID="${data.currency}">${item.unitPrice.toFixed(2)}</cbc:PriceAmount>
    </cac:Price>
  </cac:InvoiceLine>`
    )
    .join('')}
  
  <cac:TaxTotal>
    <cbc:TaxAmount currencyID="${data.currency}">${data.totalVat.toFixed(2)}</cbc:TaxAmount>
  </cac:TaxTotal>
  
  <cac:LegalMonetaryTotal>
    <cbc:LineExtensionAmount currencyID="${data.currency}">${data.totalNet.toFixed(2)}</cbc:LineExtensionAmount>
    <cbc:TaxExclusiveAmount currencyID="${data.currency}">${data.totalNet.toFixed(2)}</cbc:TaxExclusiveAmount>
    <cbc:TaxInclusiveAmount currencyID="${data.currency}">${data.totalGross.toFixed(2)}</cbc:TaxInclusiveAmount>
    <cbc:PayableAmount currencyID="${data.currency}">${data.totalGross.toFixed(2)}</cbc:PayableAmount>
  </cac:LegalMonetaryTotal>
</Invoice>`;

  return xml;
}

function escapeXml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

export async function generateZUGFeRD(data: InvoiceData, pdfBuffer: Buffer): Promise<Buffer> {
  logger.info({ invoiceNumber: data.invoiceNumber }, 'Generating ZUGFeRD (PDF/A-3)');

  // In production: Embed XML in PDF using pdf-lib or similar
  // For now, return PDF as-is (mock implementation)
  logger.warn('ZUGFeRD embedding not yet implemented, returning plain PDF');

  return pdfBuffer;
}
