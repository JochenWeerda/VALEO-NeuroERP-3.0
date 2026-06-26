import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  RefreshCw,
  XCircle,
} from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DOCS_BASE_URL } from "@/lib/docs-help";

interface DimensionResult {
  dimension: string;
  status: string;
  detail: string;
}

interface QualityEvidenceSummary {
  generated_at: string;
  overall_status: string;
  dimensions: DimensionResult[];
  summary: Record<string, number>;
  source: string;
}

const DIMENSION_LABELS: Record<string, string> = {
  drift: "Doku-Drift",
  openapi: "OpenAPI-Sync",
  inventories: "Code-Inventare",
  coverage: "Coverage-Ratchet",
  slice_harness: "Slice-Harness",
  external: "Externe Prüfer",
};

const STATUS_CONFIG = {
  pass: {
    label: "OK",
    variant: "default" as const,
    icon: CheckCircle2,
    className: "text-green-600",
  },
  warn: {
    label: "Warnung",
    variant: "secondary" as const,
    icon: AlertTriangle,
    className: "text-yellow-600",
  },
  fail: {
    label: "Fehler",
    variant: "destructive" as const,
    icon: XCircle,
    className: "text-red-600",
  },
} as const;

function overallConfig(status: string) {
  return STATUS_CONFIG[status as keyof typeof STATUS_CONFIG] ?? {
    label: status,
    variant: "outline" as const,
    icon: Activity,
    className: "text-muted-foreground",
  };
}

function DimensionCard({ dim }: { dim: DimensionResult }) {
  const cfg = overallConfig(dim.status);
  const Icon = cfg.icon;
  const label = DIMENSION_LABELS[dim.dimension] ?? dim.dimension;

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <Icon className={`h-5 w-5 ${cfg.className}`} />
            <CardTitle className="text-base">{label}</CardTitle>
          </div>
          <Badge variant={cfg.variant}>{cfg.label}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{dim.detail}</p>
      </CardContent>
    </Card>
  );
}

export default function QualitaetsCockpitPage() {
  const { data, isLoading, error, refetch, isFetching } = useQuery<QualityEvidenceSummary>({
    queryKey: ["quality-evidence"],
    queryFn: async () => {
      const res = await apiClient.get<QualityEvidenceSummary>("/api/v1/admin/quality-evidence/");
      return res.data;
    },
    refetchInterval: 60_000,
  });

  const overall = data ? overallConfig(data.overall_status) : null;
  const OverallIcon = overall?.icon ?? Activity;
  const summary = data?.summary ?? {};

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Qualitäts-Cockpit</h1>
          <p className="text-muted-foreground text-sm">
            Release-Evidenz: Drift · OpenAPI · Inventare · Coverage · Harness · Externe Gates
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link to="/admin/externe-gates">Externe Gates</Link>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <a
              href={`${DOCS_BASE_URL}/entwickler/drift-dashboard/`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <ExternalLink className="h-4 w-4 mr-2 inline" />
              Drift-Dashboard
            </a>
          </Button>
          <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isFetching}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isFetching ? "animate-spin" : ""}`} />
            Aktualisieren
          </Button>
        </div>
      </div>

      {data && overall && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Card className="text-center p-4 col-span-2 sm:col-span-1">
            <div className="flex items-center justify-center gap-2 mb-1">
              <OverallIcon className={`h-6 w-6 ${overall.className}`} />
              <span className="text-lg font-semibold">{overall.label}</span>
            </div>
            <div className="text-xs text-muted-foreground">Gesamtstatus</div>
          </Card>
          <Card className="text-center p-4">
            <div className="text-2xl font-bold text-green-600">{summary.pass ?? 0}</div>
            <div className="text-xs text-muted-foreground">OK</div>
          </Card>
          <Card className="text-center p-4">
            <div className="text-2xl font-bold text-yellow-600">{summary.warn ?? 0}</div>
            <div className="text-xs text-muted-foreground">Warnungen</div>
          </Card>
          <Card className="text-center p-4">
            <div className="text-2xl font-bold text-red-600">{summary.fail ?? 0}</div>
            <div className="text-xs text-muted-foreground">Fehler</div>
          </Card>
        </div>
      )}

      {isLoading && (
        <div className="text-center py-12 text-muted-foreground">Lade Qualitätsnachweise…</div>
      )}

      {error && (
        <div className="rounded-md bg-amber-50 border border-amber-200 px-4 py-3 text-amber-900 text-sm space-y-2">
          <p>
            <strong>Keine Release-Evidenz verfügbar.</strong>{" "}
            {error instanceof Error ? error.message : String(error)}
          </p>
          <p className="text-xs">
            Lokal:{" "}
            <code className="bg-amber-100 px-1 rounded">
              python scripts/release_evidence_report.py
            </code>{" "}
            ausführen, oder CI-Artefakt abwarten.
          </p>
        </div>
      )}

      {data && (
        <>
          <p className="text-xs text-muted-foreground">
            Quelle: {data.source} · Stand:{" "}
            {data.generated_at
              ? new Date(data.generated_at).toLocaleString("de-DE")
              : "—"}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {[...data.dimensions]
              .sort((a, b) => {
                const order = { fail: 0, warn: 1, pass: 2 };
                return (
                  (order[a.status as keyof typeof order] ?? 3) -
                  (order[b.status as keyof typeof order] ?? 3)
                );
              })
              .map((dim) => (
                <DimensionCard key={dim.dimension} dim={dim} />
              ))}
          </div>
        </>
      )}
    </div>
  );
}
