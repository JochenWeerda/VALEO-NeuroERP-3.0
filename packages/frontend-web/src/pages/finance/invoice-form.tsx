/**
 * Finance Invoice Form
 * Formular zum Erstellen/Bearbeiten von Rechnungen im Finance-Modul
 * 
 * Basierend auf sales/invoice-editor.tsx, aber für Finance-Modul angepasst
 * M18: Echte Kunden-Suche über CRM Customers API
 */

import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Plus, Trash2, Save, X, Check, ChevronsUpDown } from "lucide-react";
import { ModuleToolbar } from "@/components/navigation/ModuleToolbar";
import { useToast } from "@/hooks/use-toast";
import { apiClient } from "@/lib/api-client";
import { cn } from "@/lib/utils";

const CUSTOMER_SEARCH_DEBOUNCE_MS = 300;
const MIN_SEARCH_LENGTH = 2;

type CustomerOption = { id: string; company_name: string; customer_number?: string; email?: string };

interface InvoiceLine {
  article: string;
  description: string;
  qty: number;
  price: number;
  vatRate: number;
  netAmount: number;
  taxAmount: number;
  grossAmount: number;
}

export default function FinanceInvoiceFormPage(): JSX.Element {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [invoiceNumber, setInvoiceNumber] = useState("");
  const [invoiceDate, setInvoiceDate] = useState(new Date().toISOString().split("T")[0]);
  const [customerId, setCustomerId] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [paymentTerms, setPaymentTerms] = useState("net30");
  const [notes, setNotes] = useState("");
  const [lines, setLines] = useState<InvoiceLine[]>([]);
  const [subtotalNet, setSubtotalNet] = useState(0);
  const [totalTax, setTotalTax] = useState(0);
  const [totalGross, setTotalGross] = useState(0);
  const [loading, setLoading] = useState(false);
  const [customerPopoverOpen, setCustomerPopoverOpen] = useState(false);
  const [customerSearchQuery, setCustomerSearchQuery] = useState("");
  const [customerSearchResults, setCustomerSearchResults] = useState<CustomerOption[]>([]);
  const [customerSearchLoading, setCustomerSearchLoading] = useState(false);
  const [customerSearchDebounce, setCustomerSearchDebounce] = useState("");

  useEffect(() => {
    const t = setTimeout(() => setCustomerSearchDebounce(customerSearchQuery), CUSTOMER_SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(t);
  }, [customerSearchQuery]);

  const fetchCustomers = useCallback(async (search: string) => {
    if (search.trim().length < MIN_SEARCH_LENGTH) {
      setCustomerSearchResults([]);
      return;
    }
    setCustomerSearchLoading(true);
    try {
      const res = await apiClient.get<{ items?: CustomerOption[] }>(
        `/api/v1/crm/customers?search=${encodeURIComponent(search.trim())}&limit=20`
      );
      const body = res.data ?? (res as unknown as { data?: { items?: CustomerOption[] } }).data;
      const items = body?.items ?? [];
      setCustomerSearchResults(Array.isArray(items) ? items : []);
    } catch {
      setCustomerSearchResults([]);
    } finally {
      setCustomerSearchLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCustomers(customerSearchDebounce);
  }, [customerSearchDebounce, fetchCustomers]);

  const selectCustomer = (c: CustomerOption) => {
    setCustomerId(c.id);
    setCustomerName(c.company_name || c.customer_number || c.id);
    setCustomerPopoverOpen(false);
    setCustomerSearchQuery("");
    setCustomerSearchResults([]);
  };

  // Berechne Beträge bei Änderungen
  useEffect(() => {
    const net = lines.reduce((sum, line) => sum + line.netAmount, 0);
    const tax = lines.reduce((sum, line) => sum + line.taxAmount, 0);
    const gross = lines.reduce((sum, line) => sum + line.grossAmount, 0);
    
    setSubtotalNet(net);
    setTotalTax(tax);
    setTotalGross(gross);
  }, [lines]);

  const addLine = () => {
    setLines([
      ...lines,
      {
        article: "",
        description: "",
        qty: 1,
        price: 0,
        vatRate: 19,
        netAmount: 0,
        taxAmount: 0,
        grossAmount: 0,
      },
    ]);
  };

  const removeLine = (index: number) => {
    setLines(lines.filter((_, i) => i !== index));
  };

  const updateLine = (index: number, field: keyof InvoiceLine, value: string | number) => {
    const updated = [...lines];
    updated[index] = { ...updated[index], [field]: value };
    
    // Berechne Beträge für diese Zeile
    const qty = updated[index].qty;
    const price = updated[index].price;
    const vatRate = updated[index].vatRate;
    
    const netAmount = qty * price;
    const taxAmount = netAmount * (vatRate / 100);
    const grossAmount = netAmount + taxAmount;
    
    updated[index].netAmount = netAmount;
    updated[index].taxAmount = taxAmount;
    updated[index].grossAmount = grossAmount;
    
    setLines(updated);
  };

  const handleSave = async () => {
    if (!customerId) {
      toast({
        title: "Fehler",
        description: "Bitte wählen Sie einen Kunden aus",
        variant: "destructive",
      });
      return;
    }

    if (lines.length === 0) {
      toast({
        title: "Fehler",
        description: "Bitte fügen Sie mindestens eine Position hinzu",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      // Generiere Rechnungsnummer falls nicht vorhanden
      let number = invoiceNumber;
      if (!number) {
        const year = new Date().getFullYear();
        const random = Math.floor(Math.random() * 10000).toString().padStart(5, "0");
        number = `INV-${year}-${random}`;
      }

      // Berechne Fälligkeitsdatum
      const date = new Date(invoiceDate);
      const days = paymentTerms === "net30" ? 30 : paymentTerms === "net14" ? 14 : 7;
      const dueDate = new Date(date);
      dueDate.setDate(dueDate.getDate() + days);

      const invoiceData = {
        number,
        date: invoiceDate,
        customerId,
        paymentTerms,
        dueDate: dueDate.toISOString().split("T")[0],
        status: "ENTWURF",
        notes,
        lines: lines.map(line => ({
          article: line.article,
          qty: line.qty,
          price: line.price,
          vatRate: line.vatRate,
        })),
        subtotalNet,
        totalTax,
        totalGross,
      };

      const response = await fetch("/api/v1/finance/invoices", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(invoiceData),
      });

      if (!response.ok) {
        throw new Error("Fehler beim Speichern der Rechnung");
      }

      toast({
        title: "Erfolg",
        description: "Rechnung wurde erfolgreich gespeichert",
      });

      navigate("/finance/invoices");
    } catch (error) {
      toast({
        title: "Fehler",
        description: error instanceof Error ? error.message : "Fehler beim Speichern",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <ModuleToolbar backTarget="/finance/invoices" closeTarget="/finance/invoices" title="Rechnung erstellen" />
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Rechnung erstellen</h1>
        <p className="text-muted-foreground mt-2">
          Neue Rechnung im Finance-Modul anlegen
        </p>
      </div>

      <div className="space-y-6">
        {/* Grundinformationen */}
        <Card>
          <CardHeader>
            <CardTitle>Grundinformationen</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="invoiceNumber">Rechnungsnummer</Label>
                <Input
                  id="invoiceNumber"
                  value={invoiceNumber}
                  onChange={(e) => setInvoiceNumber(e.target.value)}
                  placeholder="Wird automatisch generiert"
                />
              </div>
              <div>
                <Label htmlFor="invoiceDate">Rechnungsdatum</Label>
                <Input
                  id="invoiceDate"
                  type="date"
                  value={invoiceDate}
                  onChange={(e) => setInvoiceDate(e.target.value)}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="customer">Kunde *</Label>
                <Popover open={customerPopoverOpen} onOpenChange={setCustomerPopoverOpen}>
                  <PopoverTrigger asChild>
                    <Button
                      id="customer"
                      variant="outline"
                      role="combobox"
                      aria-expanded={customerPopoverOpen}
                      className="w-full justify-between font-normal"
                    >
                      {customerName || "Kunde suchen..."}
                      <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0" align="start">
                    <Command shouldFilter={false}>
                      <CommandInput
                        placeholder="Name, Nr. oder E-Mail eingeben..."
                        value={customerSearchQuery}
                        onValueChange={setCustomerSearchQuery}
                      />
                      <CommandList>
                        <CommandEmpty>
                          {customerSearchLoading ? "Suche..." : customerSearchQuery.length < MIN_SEARCH_LENGTH ? "Mind. 2 Zeichen eingeben" : "Keine Kunden gefunden"}
                        </CommandEmpty>
                        <CommandGroup>
                          {customerSearchResults.map((c) => (
                            <CommandItem
                              key={c.id}
                              value={c.id}
                              onSelect={() => selectCustomer(c)}
                            >
                              <Check className={cn("mr-2 h-4 w-4", customerId === c.id ? "opacity-100" : "opacity-0")} />
                              {c.company_name}
                              {c.customer_number ? ` (${c.customer_number})` : ""}
                            </CommandItem>
                          ))}
                        </CommandGroup>
                      </CommandList>
                    </Command>
                  </PopoverContent>
                </Popover>
              </div>
              <div>
                <Label htmlFor="paymentTerms">Zahlungsbedingungen</Label>
                <Select value={paymentTerms} onValueChange={setPaymentTerms}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="net7">7 Tage netto</SelectItem>
                    <SelectItem value="net14">14 Tage netto</SelectItem>
                    <SelectItem value="net30">30 Tage netto</SelectItem>
                    <SelectItem value="net60">60 Tage netto</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label htmlFor="notes">Notizen</Label>
              <Textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        {/* Positionen */}
        <Card>
          <CardHeader>
            <CardTitle>Positionen</CardTitle>
            <CardDescription>
              Artikel und Leistungen für diese Rechnung
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4">
              {lines.map((line, index) => (
                <div key={index} className="grid grid-cols-12 gap-2 items-end p-4 border rounded-lg">
                  <div className="col-span-3">
                    <Label>Artikel</Label>
                    <Input
                      value={line.article}
                      onChange={(e) => updateLine(index, "article", e.target.value)}
                      placeholder="Artikel-Nr."
                    />
                  </div>
                  <div className="col-span-4">
                    <Label>Beschreibung</Label>
                    <Input
                      value={line.description}
                      onChange={(e) => updateLine(index, "description", e.target.value)}
                      placeholder="Beschreibung"
                    />
                  </div>
                  <div className="col-span-1">
                    <Label>Menge</Label>
                    <Input
                      type="number"
                      value={line.qty}
                      onChange={(e) => updateLine(index, "qty", parseFloat(e.target.value) || 0)}
                      min="0"
                      step="0.01"
                    />
                  </div>
                  <div className="col-span-2">
                    <Label>Preis</Label>
                    <Input
                      type="number"
                      value={line.price}
                      onChange={(e) => updateLine(index, "price", parseFloat(e.target.value) || 0)}
                      min="0"
                      step="0.01"
                    />
                  </div>
                  <div className="col-span-1">
                    <Label>MwSt %</Label>
                    <Input
                      type="number"
                      value={line.vatRate}
                      onChange={(e) => updateLine(index, "vatRate", parseFloat(e.target.value) || 0)}
                      min="0"
                      max="100"
                    />
                  </div>
                  <div className="col-span-1 flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeLine(index)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            <Button variant="outline" onClick={addLine}>
              <Plus className="h-4 w-4 mr-2" />
              Position hinzufügen
            </Button>
          </CardContent>
        </Card>

        {/* Zusammenfassung */}
        <Card>
          <CardHeader>
            <CardTitle>Zusammenfassung</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Summe Netto:</span>
                <span className="font-semibold">{subtotalNet.toFixed(2)} €</span>
              </div>
              <div className="flex justify-between">
                <span>Summe MwSt:</span>
                <span className="font-semibold">{totalTax.toFixed(2)} €</span>
              </div>
              <div className="flex justify-between text-lg font-bold border-t pt-2">
                <span>Summe Brutto:</span>
                <span>{totalGross.toFixed(2)} €</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Aktionen */}
        <div className="flex justify-end gap-4">
          <Button variant="outline" onClick={() => navigate("/finance/invoices")}>
            <X className="h-4 w-4 mr-2" />
            Abbrechen
          </Button>
          <Button onClick={handleSave} disabled={loading}>
            <Save className="h-4 w-4 mr-2" />
            {loading ? "Speichern..." : "Speichern"}
          </Button>
        </div>
      </div>
    </div>
  );
}

