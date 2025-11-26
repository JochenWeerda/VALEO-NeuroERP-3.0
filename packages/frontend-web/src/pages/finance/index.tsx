/**
 * Finance Module Overview
 * Hauptübersicht für das Finance-Modul
 */

import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  Receipt, 
  FileText, 
  CreditCard, 
  TrendingUp, 
  Banknote,
  Calculator,
  ArrowRight,
  Shield,
  Calendar
} from "lucide-react";

export default function FinanceIndexPage(): JSX.Element {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Finance</h1>
        <p className="text-muted-foreground mt-2">
          Finanzverwaltung und Buchhaltung
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* General Ledger */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Hauptbuch
            </CardTitle>
            <CardDescription>
              Journalbuchungen und Konten
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link 
              to="/finance/bookings/new" 
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              Buchungsjournal <ArrowRight className="h-3 w-3" />
            </Link>
          </CardContent>
        </Card>

        {/* Accounts Receivable */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Receipt className="h-5 w-5" />
              Debitoren
            </CardTitle>
            <CardDescription>
              Rechnungen und Forderungen
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link 
              to="/finance/invoices" 
              className="text-sm text-primary hover:underline flex items-center gap-1 block"
            >
              Rechnungen <ArrowRight className="h-3 w-3" />
            </Link>
            <Link 
              to="/finance/debitoren" 
              className="text-sm text-primary hover:underline flex items-center gap-1 block"
            >
              Debitoren-Liste <ArrowRight className="h-3 w-3" />
            </Link>
          </CardContent>
        </Card>

        {/* Accounts Payable */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              Kreditoren
            </CardTitle>
            <CardDescription>
              Eingangsrechnungen und Verbindlichkeiten
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link 
              to="/finance/ap/invoices" 
              className="text-sm text-primary hover:underline flex items-center gap-1 block"
            >
              Eingangsrechnungen <ArrowRight className="h-3 w-3" />
            </Link>
            <Link 
              to="/finance/kreditoren" 
              className="text-sm text-primary hover:underline flex items-center gap-1 block"
            >
              Kreditoren-Liste <ArrowRight className="h-3 w-3" />
            </Link>
          </CardContent>
        </Card>

        {/* Treasury */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Banknote className="h-5 w-5" />
              Treasury
            </CardTitle>
            <CardDescription>
              Bankkonten und Zahlungen
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link 
              to="/finance/bank" 
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              Bankabgleich <ArrowRight className="h-3 w-3" />
            </Link>
          </CardContent>
        </Card>

        {/* Tax */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              Steuern
            </CardTitle>
            <CardDescription>
              Steuerberechnung und -meldungen
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link 
              to="/export/ustva" 
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              UStVA <ArrowRight className="h-3 w-3" />
            </Link>
          </CardContent>
        </Card>

        {/* Reports */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Berichte
            </CardTitle>
            <CardDescription>
              Finanzberichte und Analysen
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link 
              to="/finance/reports" 
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              Berichte <ArrowRight className="h-3 w-3" />
            </Link>
          </CardContent>
        </Card>

        {/* Compliance / Audit Trail */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              GoBD Audit-Trail
            </CardTitle>
            <CardDescription>
              Vollständige Historie aller Änderungen
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link 
              to="/finance/audit-trail" 
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              Audit-Trail <ArrowRight className="h-3 w-3" />
            </Link>
          </CardContent>
        </Card>

        {/* Period Management */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Periodensteuerung
            </CardTitle>
            <CardDescription>
              Buchungsperioden verwalten
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link 
              to="/finance/periods" 
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              Perioden <ArrowRight className="h-3 w-3" />
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

