import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RefreshCw, CheckCircle2, AlertTriangle, XCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";

interface GateStatus {
  system_id: string;
  label: string;
  description: string;
  kategorie: string;
  status: "ok" | "warning" | "faellig" | "fehler" | "unbekannt";
  hinweis: string | null;
  abgerufen_am: string;
  simulated?: boolean;
  [key: string]: unknown;
}

interface GatesOverview {
  tenant_id: string;
  gesamt: number;
  status_zusammenfassung: Record<string, number>;
  abgerufen_am: string;
  gates: GateStatus[];
}

const STATUS_CONFIG = {
  ok: {
    label: "OK",
    variant: "default" as const,
    icon: CheckCircle2,
    className: "text-status-success",
  },
  warning: {
    label: "Warnung",
    variant: "secondary" as const,
    icon: AlertTriangle,
    className: "text-status-warning",
  },
  faellig: {
    label: "Fällig",
    variant: "destructive" as const,
    icon: Clock,
    className: "text-status-warning",
  },
  fehler: {
    label: "Fehler",
    variant: "destructive" as const,
    icon: XCircle,
    className: "text-status-error",
  },
  unbekannt: {
    label: "Unbekannt",
    variant: "outline" as const,
    icon: AlertTriangle,
    className: "text-gray-400",
  },
} as const;

function StatusIcon({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status as keyof typeof STATUS_CONFIG] ?? STATUS_CONFIG.unbekannt;
  const Icon = cfg.icon;
  return <Icon className={`h-5 w-5 ${cfg.className}`} />;
}

function GateCard({ gate }: { gate: GateStatus }) {
  const cfg = STATUS_CONFIG[gate.status as keyof typeof STATUS_CONFIG] ?? STATUS_CONFIG.unbekannt;

  const detailKeys = Object.entries(gate).filter(
    ([k]) =>
      !["system_id", "label", "description", "kategorie", "status", "hinweis",
        "abgerufen_am", "simulated", "tenant_id"].includes(k)
  );

  return (
    <Card className="relative">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <StatusIcon status={gate.status} />
            <CardTitle className="text-base">{gate.label}</CardTitle>
          </div>
          <Badge variant={cfg.variant}>{cfg.label}</Badge>
        </div>
        <p className="text-sm text-muted-foreground">{gate.description}</p>
      </CardHeader>
      <CardContent className="space-y-2">
        {gate.hinweis && (
          <div className="rounded-md bg-yellow-50 border border-yellow-200 px-3 py-2 text-sm text-yellow-800">
            {gate.hinweis}
          </div>
        )}
        <dl className="grid grid-cols-1 gap-1 text-xs text-muted-foreground">
          {detailKeys.map(([k, v]) => (
            <div key={k} className="flex justify-between gap-2">
              <dt className="font-medium">{k.replace(/_/g, " ")}</dt>
              <dd className="truncate text-right">{String(v)}</dd>
            </div>
          ))}
        </dl>
        {gate.simulated && (
          <p className="text-xs text-muted-foreground italic">Simulierter Status</p>
        )}
      </CardContent>
    </Card>
  );
}

export default function ExterneGatesPage() {
  const { data, isLoading, error, refetch, isFetching } = useQuery<GatesOverview>({
    queryKey: ["external-gates"],
    queryFn: async () => {
      const res = await apiClient.get<GatesOverview>("/api/v1/external-gates/");
      return res.data;
    },
    refetchInterval: 60_000,
  });

  const summary = data?.status_zusammenfassung ?? {};
  const problemCount = (summary["faellig"] ?? 0) + (summary["fehler"] ?? 0) + (summary["warning"] ?? 0);

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Externe Gates</h1>
          <p className="text-muted-foreground text-sm">
            Integrationsstatus: DATEV · ELSTER · TSE · DMS · Bank/SEPA
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isFetching}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isFetching ? "animate-spin" : ""}`} />
          Aktualisieren
        </Button>
      </div>

      {/* Zusammenfassung */}
      {data && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Card className="text-center p-4">
            <div className="text-2xl font-bold">{data.gesamt}</div>
            <div className="text-xs text-muted-foreground">Systeme gesamt</div>
          </Card>
          <Card className="text-center p-4">
            <div className="text-2xl font-bold text-status-success">{summary["ok"] ?? 0}</div>
            <div className="text-xs text-muted-foreground">OK</div>
          </Card>
          <Card className="text-center p-4">
            <div className={`text-2xl font-bold ${problemCount > 0 ? "text-status-warning" : "text-muted-foreground"}`}>
              {problemCount}
            </div>
            <div className="text-xs text-muted-foreground">Handlungsbedarf</div>
          </Card>
          <Card className="text-center p-4">
            <div className="text-2xl font-bold text-muted-foreground">
              {data.abgerufen_am ? new Date(data.abgerufen_am).toLocaleTimeString("de-DE") : "—"}
            </div>
            <div className="text-xs text-muted-foreground">Stand</div>
          </Card>
        </div>
      )}

      {isLoading && (
        <div className="text-center py-12 text-muted-foreground">Lade Gate-Status…</div>
      )}

      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 px-4 py-3 text-red-800 text-sm">
          Fehler beim Laden: {String(error)}
        </div>
      )}

      {data && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {data.gates
            .sort((a, b) => {
              const order = { fehler: 0, faellig: 1, warning: 2, ok: 3, unbekannt: 4 };
              return (order[a.status as keyof typeof order] ?? 4) -
                (order[b.status as keyof typeof order] ?? 4);
            })
            .map((gate) => (
              <GateCard key={gate.system_id} gate={gate} />
            ))}
        </div>
      )}
    </div>
  );
}
