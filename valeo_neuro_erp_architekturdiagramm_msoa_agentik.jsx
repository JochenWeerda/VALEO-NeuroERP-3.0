import React from "react";
import { motion } from "framer-motion";

// VALEO‑NeuroERP – Architekturübersicht (MSOA + Agenten + RAG + Event Bus)
// Hinweis: Dieses Diagramm ist klickbar/skalierbar aufgebaut und dient als lebende Architekturskizze.
// Tech-Marker aus dem Projektkontext: LangGraph/LangChain Agents, MCP, Kafka/NATS, gRPC/REST, Postgres/Mongo/Supabase,
// Keycloak/Auth, Prometheus/Grafana, OpenTelemetry, MinIO/S3, CI/CD, Infrastructure as Code.

const Section = ({ title, children, className = "" }: any) => (
  <div className={`rounded-2xl shadow-lg p-4 bg-white/90 border border-gray-200 ${className}`}>
    <h2 className="text-lg font-semibold mb-2">{title}</h2>
    <div className="space-y-2 text-sm">{children}</div>
  </div>
);

const Pill = ({ label }: { label: string }) => (
  <div className="px-2 py-1 rounded-full border text-xs whitespace-nowrap">{label}</div>
);

const Box = ({ title, items = [] as string[], footer = "", className = "" }) => (
  <div className={`rounded-2xl shadow-md bg-white border border-gray-200 p-3 ${className}`}>
    <div className="text-sm font-semibold mb-1">{title}</div>
    <ul className="text-xs leading-relaxed list-disc list-inside">
      {items.map((t, i) => (
        <li key={i}>{t}</li>
      ))}
    </ul>
    {footer && <div className="text-[10px] text-gray-500 mt-1">{footer}</div>}
  </div>
);

const Arrow = ({ from, to, label = "", curved = false }: any) => {
  // Creates an SVG arrow between two absolutely positioned anchors
  // Anchors are data-attrs on elements: data-anchor="id"
  // We'll compute positions in a simple way once mounted.
  const [path, setPath] = React.useState("");
  const [mid, setMid] = React.useState({ x: 0, y: 0 });
  const svgRef = React.useRef<SVGSVGElement>(null);

  const compute = () => {
    const startEl = document.querySelector(`[data-anchor="${from}"]`) as HTMLElement | null;
    const endEl = document.querySelector(`[data-anchor="${to}"]`) as HTMLElement | null;
    const svgEl = svgRef.current;
    if (!startEl || !endEl || !svgEl) return;
    const s = startEl.getBoundingClientRect();
    const e = endEl.getBoundingClientRect();
    const root = (svgEl.parentElement as HTMLElement).getBoundingClientRect();
    const sx = s.left + s.width / 2 - root.left;
    const sy = s.top + s.height / 2 - root.top + svgEl.parentElement!.scrollTop;
    const ex = e.left + e.width / 2 - root.left;
    const ey = e.top + e.height / 2 - root.top + svgEl.parentElement!.scrollTop;

    if (curved) {
      const cx1 = sx + (ex - sx) * 0.25;
      const cy1 = sy;
      const cx2 = sx + (ex - sx) * 0.75;
      const cy2 = ey;
      setPath(`M ${sx},${sy} C ${cx1},${cy1} ${cx2},${cy2} ${ex},${ey}`);
      setMid({ x: (sx + ex) / 2, y: (sy + ey) / 2 - 10 });
    } else {
      const mx = (sx + ex) / 2;
      const my = (sy + ey) / 2;
      setPath(`M ${sx},${sy} L ${ex},${ey}`);
      setMid({ x: mx, y: my - 8 });
    }
  };

  React.useEffect(() => {
    compute();
    const onResize = () => compute();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  return (
    <svg ref={svgRef} className="absolute inset-0 pointer-events-none">
      <defs>
        <marker id="arrow" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto-start-reverse">
          <path d="M0,0 L8,4 L0,8 Z" />
        </marker>
      </defs>
      <path d={path} fill="none" stroke="currentColor" strokeWidth="1.5" markerEnd="url(#arrow)" />
      {label && (
        <foreignObject x={mid.x - 50} y={mid.y - 10} width="100" height="20">
          <div className="text-[10px] text-center bg-white/80 rounded-full border px-1">
            {label}
          </div>
        </foreignObject>
      )}
    </svg>
  );
};

export default function ArchitectureDiagram() {
  return (
    <div className="w-full min-h-screen p-4 bg-gradient-to-b from-slate-50 to-slate-100 text-slate-900">
      <motion.h1
        initial={{ opacity: 0, y: -6 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-2xl md:text-3xl font-bold mb-4"
      >
        VALEO‑NeuroERP · MSOA + Agentik + Event‑Driven Architektur
      </motion.h1>

      {/* Top Row: Access Layer & Security */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-3 mb-3">
        <Section title="Access Layer / Channels" className="xl:col-span-2" >
          <div className="flex flex-wrap gap-2" data-anchor="access">
            <Pill label="Web‑App (React/Next)" />
            <Pill label="Mobile (PWA)" />
            <Pill label="CLI / Admin" />
            <Pill label="Partner‑Portal" />
            <Pill label="Webhook Endpoints" />
            <Pill label="gRPC/REST SDKs" />
          </div>
        </Section>
        <Section title="API‑Gateway / BFF" className="xl:col-span-1" >
          <div data-anchor="apigw" className="space-y-1">
            <div className="text-sm">Edge‑Routing, Rate‑Limit, Caching, Schema‑Validation</div>
            <div className="text-xs">GraphQL Federation | REST | gRPC</div>
          </div>
        </Section>
        <Section title="Identity & Security" className="xl:col-span-1" >
          <div data-anchor="auth" className="space-y-1">
            <div className="text-sm">Keycloak/OIDC · RBAC/ABAC · SSO</div>
            <div className="text-xs">OAuth2, mTLS, Secrets Mgmt (Vault)</div>
          </div>
        </Section>
      </div>

      {/* Middle: Service Mesh & Event Bus */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 mb-3">
        <Section title="Service Mesh & Event Bus">
          <div className="text-sm mb-2">Istio/Linkerd · Kafka/NATS · Outbox‑Pattern · Saga/Choreography</div>
          <div className="flex flex-wrap gap-2" data-anchor="bus">
            <Pill label="Events: OrderCreated" />
            <Pill label="StockReserved" />
            <Pill label="InvoiceIssued" />
            <Pill label="PaymentCaptured" />
            <Pill label="DeliveryDispatched" />
          </div>
        </Section>
        <Section title="Agenten‑Ebene (LangGraph/MCP)">
          <div className="text-sm">VAN → PLAN → CREATE → IMPLEMENT → REFLECT</div>
          <div className="grid grid-cols-2 gap-2 mt-2" data-anchor="agents">
            <Box title="DeveloperAgent" items={["Code‑Gen/Refactor", "Unit/Contract Tests", "CI Hooks"]} />
            <Box title="AnalystAgent" items={["Spec‑Parsing", "TaskMD/Handover", "Risk Checks"]} />
            <Box title="OpsAgent" items={["Runbooks", "Rollback/Feature Flags", "A/B Canary"]} />
            <Box title="SupportAgent" items={["Chat‑Assist", "Ticket‑Triage", "KB‑Updates"]} />
          </div>
          <div className="text-[10px] text-gray-500 mt-2">MCP‑Connectoren zu GitHub, CI, Grafana, PagerDuty, E‑Mail</div>
        </Section>
        <Section title="RAG / Memory Layer">
          <div className="grid grid-cols-2 gap-2" data-anchor="rag">
            <Box title="VectorStores" items={["pgvector (Postgres)", "Qdrant/Weaviate"]} />
            <Box title="Doc Stores" items={["MongoDB", "Supabase", "MinIO/S3"]} />
            <Box title="Knowledge Packs" items={["ERP‑Schemas", "SOPs/Runbooks", "Produktdaten (ECLASS/ETIM)"]} />
            <Box title="Observability KB" items={["Dashboards", "Alerts", "Playbooks"]} />
          </div>
        </Section>
      </div>

      {/* Domain Microservices */}
      <Section title="Domain‑Microservices (MSOA)" >
        <div className="grid md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3 mt-2" data-anchor="domains">
          <Box title="CRM" items={["Kunden/Leads", "Broadcast/WhatsApp", "Kampagnen"]} footer="Postgres" />
          <Box title="Warenwirtschaft" items={["Artikel/Chargen", "Bestellungen", "Inventur"]} footer="Postgres" />
          <Box title="FIBU" items={["Belege", "Kontenrahmen", "Zahlungen"]} footer="Postgres" />
          <Box title="Disposition/Logistik" items={["Routen/Slots", "Fuhrpark", "Waagen‑Integr."]} footer="Postgres" />
          <Box title="QM/Compliance" items={["PSM/THG", "QS‑Milch/VLOG", "Audit Trails"]} footer="Postgres" />
          <Box title="BI/Reporting" items={["KPIs", "Dashboards", "Exports"]} footer="OLAP/Parquet" />
          <Box title="Produktdaten" items={["ECLASS/ETIM", "TecDoc/EAN", "PIM"]} footer="Mongo/S3" />
          <Box title="Pricing/Offers" items={["Preislogik", "Rabatte", "Kontrakte"]} footer="Postgres" />
          <Box title="Warehouse/SCM" items={["Lagerorte", "Reservierung", "Wareneingang"]} footer="Postgres" />
          <Box title="Auth‑Facade" items={["Mandanten", "Rollen/Policies", "SCIM"]} footer="Keycloak" />
          <Box title="Notifications" items={["E‑Mail/SMS", "Push/Webhooks", "Templates"]} footer="Redis/Queue" />
          <Box title="File/Docs" items={["OCR/PDF", "Versionierung", "Signaturen"]} footer="MinIO/S3" />
        </div>
      </Section>

      {/* Data & Platform Layer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 my-3">
        <Section title="Data Platform">
          <div className="grid grid-cols-2 gap-2" data-anchor="data">
            <Box title="Relational" items={["Postgres + pgBouncer", "Read Replicas", "CDC/Outbox"]} />
            <Box title="Streaming" items={["Kafka Connect", "Debezium", "Schema Registry"]} />
            <Box title="Lakehouse" items={["MinIO/S3", "Delta/Parquet", "DuckDB/Trino"]} />
            <Box title="Cache/Search" items={["Redis", "OpenSearch/Elasticsearch"]} />
          </div>
        </Section>
        <Section title="Observability & SRE">
          <div className="grid grid-cols-2 gap-2" data-anchor="obs">
            <Box title="Metrics/Logs/Traces" items={["Prometheus", "Loki", "Tempo", "OTel"]} />
            <Box title="Dashboards/Alerts" items={["Grafana", "Alertmanager", "SLO/Error Budgets"]} />
            <Box title="QA & Testing" items={["Contract Tests", "e2e/Load", "Chaos"]} />
            <Box title="Security" items={["Vault/KMS", "WAF/mTLS", "SBOM/SCA"]} />
          </div>
        </Section>
        <Section title="Platform & CI/CD">
          <div className="grid grid-cols-2 gap-2" data-anchor="platform">
            <Box title="Kubernetes" items={["Helm/ArgoCD", "HPA/VPA", "Node Pools"]} />
            <Box title="Pipelines" items={["GitHub Actions", "Argo Workflows", "Dagger"]} />
            <Box title="IaC" items={["Terraform", "Crossplane", "Ansible"]} />
            <Box title="Secrets/Keys" items={["Vault/Sealed‑Secrets", "COSIGN/SLSA"]} />
          </div>
        </Section>
      </div>

      {/* Invisible overlay for arrows */}
      <div className="relative w-full h-0">
        {/* Access → API GW → Bus/Agents/Domains */}
        <Arrow from="access" to="apigw" label="BFF / AuthN/AuthZ" />
        <Arrow from="apigw" to="domains" label="REST/gRPC/GraphQL" />
        <Arrow from="domains" to="bus" label="Domain Events" curved />
        <Arrow from="agents" to="domains" label="Orchestrate/Automate" />
        <Arrow from="agents" to="rag" label="Context/RAG" />
        <Arrow from="domains" to="data" label="CDC/ETL" />
        <Arrow from="domains" to="obs" label="Telemetry" />
        <Arrow from="platform" to="domains" label="Deploy/Scale" />
        <Arrow from="auth" to="apigw" label="OIDC/JWT" />
      </div>

      <div className="mt-4 text-xs text-gray-600">
        <p><strong>Legende:</strong> MSOA = Modular Service‑Oriented Architecture. Ereignisgetriebene Kommunikation über Kafka/NATS; synchrone Calls via REST/gRPC. RAG/Memory liefert domänenspezifischen Kontext für Agenten (LangGraph/MCP). Jede Domäne besitzt eigene Datenhaltung (Polyglot Persistence) und veröffentlicht Domain‑Events (Outbox/Saga). Observability und CI/CD sind querliegende Plattform‑Capabilities.</p>
      </div>
    </div>
  );
}
