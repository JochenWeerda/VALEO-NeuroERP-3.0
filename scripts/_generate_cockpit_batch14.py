"""One-shot generator: Batch-14 Cockpit ScreenDefinitions + frontend pages."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OA = json.loads((ROOT / "docs/schnittstellen/openapi.json").read_text(encoding="utf-8"))
GET_PATHS = {p for p, s in OA["paths"].items() if "get" in s}

PAGES = ROOT / "packages/frontend-web/src/pages"

# rel_path (under pages/) -> (endpoint, domain, permission, title, subtitle optional)
SPECS: dict[str, tuple[str, str, str, str, str | None]] = {
    "auswertungen/umsatzstatistik.tsx": (
        "/api/v1/sales/reports/summary",
        "reporting",
        "reporting.read",
        "Umsatzstatistik",
        "Vertriebsumsatz nach Zeitraum",
    ),
    "auswertungen/vertriebstrichter.tsx": (
        "/api/v1/sales/reports/pipeline",
        "reporting",
        "reporting.read",
        "Vertriebstrichter",
        "Pipeline und Conversion",
    ),
    "auswertungen/warengruppen-analyse.tsx": (
        "/api/v1/einkauf/warengruppen",
        "reporting",
        "reporting.read",
        "Warengruppen-Analyse",
        "Umsatz und Menge je Warengruppe",
    ),
    "auth/Callback.tsx": (
        "/api/v1/identity/session",
        "identity",
        "identity.session.read",
        "OIDC Callback",
        "Anmeldung abschliessen",
    ),
    "auth/Login.tsx": (
        "/api/v1/identity/session",
        "identity",
        "identity.session.read",
        "Anmeldung",
        "SSO-Anmeldung",
    ),
    "banken/konten-stamm.tsx": (
        "/api/v1/banken/konten",
        "finance",
        "finance.read",
        "Bankkonten-Stamm",
        "Hausbanken und Konten",
    ),
    "banken/lastschriften.tsx": (
        "/api/v1/finance/payment-runs",
        "finance",
        "finance.read",
        "Lastschriften",
        "SEPA-Lastschriftlaeufe",
    ),
    "banken/sepa-export.tsx": (
        "/api/v1/finance/payment-runs",
        "finance",
        "finance.read",
        "SEPA-Export",
        "Zahlungsdateien exportieren",
    ),
    "banken/ueberweisungen.tsx": (
        "/api/v1/banken/fints/umsaetze",
        "finance",
        "finance.read",
        "Ueberweisungen",
        "Bankumsaetze und Ueberweisungen",
    ),
    "banken/zahlungsavise.tsx": (
        "/api/v1/finance/payment-runs",
        "finance",
        "finance.read",
        "Zahlungsavise",
        "Avise zu Zahlungslaeufen",
    ),
    "banken/zahlungsvorschlaege.tsx": (
        "/api/v1/finance/payment-suggestions",
        "finance",
        "finance.read",
        "Zahlungsvorschlaege",
        "Vorschlaege aus offenen Posten",
    ),
    "belege/BelegfolgePage.tsx": (
        "/api/v1/docflow/",
        "documents",
        "documents.read",
        "Belegfolge",
        "DocFlow-Kette und Folgebelege",
    ),
    "betrieb/gefahrstoff-betriebsanweisung.tsx": (
        "/api/v1/compliance/exports/gefahrstoffdoku",
        "operations",
        "compliance.read",
        "Gefahrstoff-Betriebsanweisung",
        "Betriebsanweisungen und Export",
    ),
    "betrieb/gefahrstoff-kataster.tsx": (
        "/api/v1/compliance/exports/gefahrstoffdoku",
        "operations",
        "compliance.read",
        "Gefahrstoff-Kataster",
        "Gefahrstoffregister",
    ),
    "betrieb/maschinen-stamm.tsx": (
        "/api/v1/agrar/maschinen",
        "operations",
        "agrar.read",
        "Maschinen-Stamm",
        "Maschinenpark",
    ),
    "betrieb/prueffristen.tsx": (
        "/api/v1/wartung/anlagen",
        "operations",
        "operations.read",
        "Prueffristen",
        "Anlagen und Prueftermine",
    ),
    "betrieb/schadensmeldung.tsx": (
        "/api/v1/qualitaet/reklamationen",
        "operations",
        "quality.read",
        "Schadensmeldung",
        "Schaeden und Reklamationen",
    ),
    "betrieb/standorte.tsx": (
        "/api/v1/stammdaten/betriebsstaetten",
        "operations",
        "masterdata.read",
        "Standorte",
        "Betriebsstaetten",
    ),
    "betrieb/unterweisungen.tsx": (
        "/api/v1/personal/absences",
        "operations",
        "hrm.read",
        "Unterweisungen",
        "Schulungen und Unterweisungen",
    ),
    "betrieb/wartungsplan.tsx": (
        "/api/v1/wartung/anlagen",
        "operations",
        "operations.read",
        "Wartungsplan",
        "Anlagenwartung",
    ),
    "charge/etiketten.tsx": (
        "/api/v1/etiketten/drucker",
        "inventory",
        "inventory.read",
        "Etiketten",
        "Etikettendruck",
    ),
    "charge/mischung.tsx": (
        "/api/v1/chargen",
        "inventory",
        "inventory.read",
        "Chargen-Mischung",
        "Mischchargen",
    ),
    "charge/probenahme.tsx": (
        "/api/v1/chargen/stats/summary",
        "inventory",
        "inventory.read",
        "Probenahme",
        "Chargen-Probenahme",
    ),
    "charge/sperrlager.tsx": (
        "/api/v1/compliance/artikel-sperren",
        "inventory",
        "inventory.read",
        "Sperrlager",
        "Gesperrte Bestaende",
    ),
    "charge/teilung.tsx": (
        "/api/v1/chargen",
        "inventory",
        "inventory.read",
        "Chargenteilung",
        "Chargen teilen",
    ),
    "charge/zusammenfuehrung.tsx": (
        "/api/v1/chargen",
        "inventory",
        "inventory.read",
        "Chargenzusammenfuehrung",
        "Chargen zusammenfuehren",
    ),
    "crm/activities.tsx": (
        "/api/v1/crm/activities",
        "crm",
        "crm.read",
        "Aktivitaeten",
        "CRM-Aktivitaetenliste",
    ),
    "crm/activity-detail.tsx": (
        "/api/v1/crm/activities/{activity_id}",
        "crm",
        "crm.read",
        "Aktivitaet",
        "Aktivitaetsdetail",
    ),
    "crm/angebot-erstellen.tsx": (
        "/api/v1/einkauf/angebote",
        "crm",
        "crm.read",
        "Angebot erstellen",
        "Vertriebsangebot anlegen",
    ),
    "crm/anruf-protokoll.tsx": (
        "/api/v1/crm/activities",
        "crm",
        "crm.read",
        "Anruf-Protokoll",
        "Telefonate dokumentieren",
    ),
    "crm/besuchsberichte.tsx": (
        "/api/v1/crm/activities",
        "crm",
        "crm.read",
        "Besuchsberichte",
        "Kundenbesuche",
    ),
    "crm/betreuungsgebiet.tsx": (
        "/api/v1/crm/segments",
        "crm",
        "crm.read",
        "Betreuungsgebiet",
        "Gebiete und Segmente",
    ),
    "crm/bonus-vereinbarungen.tsx": (
        "/api/v1/l3-report-catalog/bonus-runs",
        "crm",
        "crm.read",
        "Bonus-Vereinbarungen",
        "Bonuslaeufe",
    ),
    "crm/churn-risiko.tsx": (
        "/api/v1/crm/dashboard",
        "crm",
        "crm.read",
        "Churn-Risiko",
        "Abwanderungsrisiko",
    ),
    "crm/cross-selling.tsx": (
        "/api/v1/agrar/milchvieh-crosssell/summary",
        "crm",
        "crm.read",
        "Cross-Selling",
        "Cross-Sell-Potenziale",
    ),
    "crm/dokumente-kunden.tsx": (
        "/api/v1/dokumente",
        "crm",
        "crm.read",
        "Kundendokumente",
        "DMS je Kunde",
    ),
    "crm/dubletten-pruefung.tsx": (
        "/api/v1/crm/duplicates",
        "crm",
        "crm.read",
        "Dubletten-Pruefung",
        "Partner-Dubletten",
    ),
    "crm/events-messen.tsx": (
        "/api/v1/marketing/kampagnen",
        "crm",
        "crm.read",
        "Events und Messen",
        "Marketing-Events",
    ),
    "crm/gebietsschutz.tsx": (
        "/api/v1/crm/ownership/unassigned",
        "crm",
        "crm.read",
        "Gebietsschutz",
        "Ownership und Gebiete",
    ),
    "crm/geschenke-liste.tsx": (
        "/api/v1/crm/kim/customers/{kunden_nr}/gifts",
        "crm",
        "crm.read",
        "Geschenke",
        "Geschenkregister",
    ),
    "crm/interaktions-historie.tsx": (
        "/api/v1/crm/customers/{customer_id}/tabs/historie",
        "crm",
        "crm.read",
        "Interaktions-Historie",
        "Kundenhistorie",
    ),
    "crm/kampagne-detail.tsx": (
        "/api/v1/marketing/kampagnen",
        "crm",
        "crm.read",
        "Kampagne",
        "Kampagnendetail",
    ),
    "crm/kampagne-erstellen.tsx": (
        "/api/v1/marketing/kampagnen",
        "crm",
        "crm.write",
        "Kampagne erstellen",
        "Neue Marketing-Kampagne",
    ),
    "crm/kaufverhalten.tsx": (
        "/api/v1/sales/reports/top-customers",
        "crm",
        "crm.read",
        "Kaufverhalten",
        "Kundenkaufverhalten",
    ),
    "crm/kommunikation-center.tsx": (
        "/api/v1/query-center/catalog",
        "crm",
        "crm.read",
        "Kommunikations-Center",
        "Kanaele und Vorlagen",
    ),
    "crm/wettbewerber.tsx": (
        "/api/v1/crm/dashboard",
        "crm",
        "crm.read",
        "Wettbewerber",
        "Wettbewerbsbeobachtung",
    ),
    "crm/zielgruppen.tsx": (
        "/api/v1/crm/segments",
        "crm",
        "crm.read",
        "Zielgruppen",
        "Segmente und Zielgruppen",
    ),
    "dashboard/customizable-dashboard.tsx": (
        "/api/v1/controlling/dashboards",
        "platform",
        "controlling.read",
        "Anpassbares Dashboard",
        "Widget-Cockpit",
    ),
    "dashboard/sales-dashboard.tsx": (
        "/api/v1/sales/reports/summary",
        "sales",
        "sales.read",
        "Verkaufs-Dashboard",
        "Vertriebs-KPIs",
    ),
    "disposition/bestell-vorschlag.tsx": (
        "/api/v1/einkauf/bestellvorschlaege",
        "logistics",
        "procurement.read",
        "Bestellvorschlag",
        "Disposition Bestellvorschlaege",
    ),
    "disposition/engpass-monitor.tsx": (
        "/api/v1/disposition/stats",
        "logistics",
        "logistics.read",
        "Engpass-Monitor",
        "Engpaesse in der Disposition",
    ),
    "disposition/kontrakt-abruf.tsx": (
        "/api/v1/kontrakte",
        "logistics",
        "contracts.read",
        "Kontrakt-Abruf",
        "Kontraktabrufe",
    ),
    "disposition/lager-reichweite.tsx": (
        "/api/v1/lager/dashboard",
        "logistics",
        "inventory.read",
        "Lager-Reichweite",
        "Reichweitenprognose",
    ),
    "disposition/saison-planung.tsx": (
        "/api/v1/planung/kalender",
        "logistics",
        "planung.calendar.read",
        "Saison-Planung",
        "Saisonale Planung",
    ),
    "disposition/strecken-disposition.tsx": (
        "/api/v1/strecke/streckengeschaefte",
        "logistics",
        "logistics.read",
        "Strecken-Disposition",
        "Streckengeschaefte",
    ),
    "disposition/touren-disposition.tsx": (
        "/api/v1/logistik/tours",
        "logistics",
        "logistics.read",
        "Touren-Disposition",
        "Tourenplanung",
    ),
    "disposition/umlagerungs-vorschlag.tsx": (
        "/api/v1/disposition",
        "logistics",
        "logistics.read",
        "Umlagerungs-Vorschlag",
        "Umlagerungsvorschlaege",
    ),
    "dms/archiv-suche.tsx": (
        "/api/v1/dms/search",
        "documents",
        "documents.read",
        "Archiv-Suche",
        "DMS-Volltextsuche",
    ),
    "dms/beleg-erkennung.tsx": (
        "/api/v1/process/dms/erkennungsregeln",
        "documents",
        "documents.read",
        "Beleg-Erkennung",
        "OCR-Regeln",
    ),
    "dms/dokument-detail.tsx": (
        "/api/v1/dms/documents",
        "documents",
        "documents.read",
        "Dokument",
        "DMS-Dokumentdetail",
    ),
    "dms/dokument-upload.tsx": (
        "/api/v1/dms/documents",
        "documents",
        "documents.write",
        "Dokument-Upload",
        "DMS-Upload",
    ),
    "dms/freigabe-workflow.tsx": (
        "/api/v1/docflow/evidence/artifacts",
        "documents",
        "documents.approve",
        "Freigabe-Workflow",
        "DMS-Freigaben",
    ),
    "dms/posteingang.tsx": (
        "/api/v1/dms/inbox",
        "documents",
        "documents.read",
        "Posteingang",
        "DMS-Posteingang",
    ),
    "dms/verschlagwortung.tsx": (
        "/api/v1/dms/documents",
        "documents",
        "documents.write",
        "Verschlagwortung",
        "Tags und Metadaten",
    ),
    "dms/vorlagen-verwaltung.tsx": (
        "/api/v1/process/template/vorlagen",
        "documents",
        "documents.read",
        "Vorlagen-Verwaltung",
        "DMS-Vorlagen",
    ),
    "dokumente/archiv.tsx": (
        "/api/v1/process/archiv/eintraege",
        "documents",
        "documents.read",
        "Dokumentarchiv",
        "Archiv-Eintraege",
    ),
    "dokumente/eingang.tsx": (
        "/api/v1/dms/inbox",
        "documents",
        "documents.read",
        "Dokumenteingang",
        "Eingangskorb",
    ),
    "dokumente/suche.tsx": (
        "/api/v1/dms/search",
        "documents",
        "documents.read",
        "Dokumentensuche",
        "Suche im Archiv",
    ),
    "dokumente/vorlagen.tsx": (
        "/api/v1/process/template/vorlagen",
        "documents",
        "documents.read",
        "Dokumentvorlagen",
        "Vorlagenkatalog",
    ),
    "einkauf/anfrage-erstellen.tsx": (
        "/api/v1/einkauf/anfragen",
        "einkauf",
        "procurement.read",
        "Anfrage erstellen",
        "Bedarfsanfrage",
    ),
    "einkauf/angebot-erfassen.tsx": (
        "/api/v1/einkauf/angebote",
        "einkauf",
        "procurement.read",
        "Angebot erfassen",
        "Lieferantenangebot",
    ),
    "einkauf/anlieferavis-erfassen.tsx": (
        "/api/v1/einkauf/anlieferavis",
        "einkauf",
        "procurement.read",
        "Anlieferavis erfassen",
        "Lieferavis",
    ),
    "einkauf/auftragsbestaetigung-erfassen.tsx": (
        "/api/v1/einkauf/auftragsbestaetigungen",
        "einkauf",
        "procurement.read",
        "Auftragsbestaetigung",
        "AB erfassen",
    ),
    "einkauf/bestellung-freigabe.tsx": (
        "/api/v1/einkauf/bestellungen",
        "einkauf",
        "procurement.approve",
        "Bestellfreigabe",
        "Bestellungen freigeben",
    ),
    "einkauf/bestellvorschlag-lager.tsx": (
        "/api/v1/einkauf/bestellvorschlaege/lager",
        "einkauf",
        "procurement.read",
        "Bestellvorschlag Lager",
        "Lagergetriebene Vorschlaege",
    ),
    "einkauf/bestellvorschlag-kontrakt.tsx": (
        "/api/v1/einkauf/bestellvorschlaege/rohware",
        "einkauf",
        "procurement.read",
        "Bestellvorschlag Kontrakt",
        "Kontrakt-Vorschlaege",
    ),
    "einkauf/bestellvorschlag-verbrauch.tsx": (
        "/api/v1/einkauf/bestellvorschlaege/bedarf",
        "einkauf",
        "procurement.read",
        "Bestellvorschlag Verbrauch",
        "Verbrauchsvorschlaege",
    ),
    "einkauf/gutschrift-belastung.tsx": (
        "/api/v1/einkauf/lieferscheine",
        "einkauf",
        "procurement.read",
        "Gutschrift/Belastung",
        "Einkaufs-Gutschrift",
    ),
    "einkauf/kontrakt-anlage.tsx": (
        "/api/v1/einkauf/kontrakte",
        "einkauf",
        "procurement.read",
        "Kontrakt-Anlage",
        "Einkaufskontrakt",
    ),
    "einkauf/lieferanten-angebote.tsx": (
        "/api/v1/einkauf/angebote",
        "einkauf",
        "procurement.read",
        "Lieferanten-Angebote",
        "Angebotsvergleich",
    ),
    "einkauf/lieferanten-dokumente.tsx": (
        "/api/v1/einkauf/suppliers/{supplier_id}/documents",
        "einkauf",
        "procurement.read",
        "Lieferanten-Dokumente",
        "DMS je Lieferant",
    ),
    "einkauf/lieferanten-konditionen.tsx": (
        "/api/v1/preise/konditionen",
        "einkauf",
        "procurement.read",
        "Lieferanten-Konditionen",
        "Einkaufskonditionen",
    ),
    "einkauf/lieferanten-reklamationen.tsx": (
        "/api/v1/qualitaet/reklamationen",
        "einkauf",
        "procurement.read",
        "Lieferanten-Reklamationen",
        "Reklamationen",
    ),
    "einkauf/lieferschein-erfassen.tsx": (
        "/api/v1/einkauf/lieferscheine",
        "einkauf",
        "procurement.read",
        "Lieferschein erfassen",
        "Einkauf-Lieferschein",
    ),
    "einkauf/mahnwesen-lieferanten.tsx": (
        "/api/v1/finance/followup/mahnwesen/preview",
        "einkauf",
        "finance.read",
        "Mahnwesen Lieferanten",
        "Lieferanten-Mahnwesen",
    ),
}


def screen_id_from_rel(rel: str) -> str:
    rel = rel.replace(".tsx", "")
    parts = rel.split("/")
    last = parts[-1]
    if last.endswith("Page"):
        last = last[:-4]
    last = re.sub(r"(?<!^)(?=[A-Z])", "-", last).lower()
    parts[-1] = last
    return "/".join(parts)


def fn_name(screen_id: str) -> str:
    return "build_" + screen_id.replace("/", "_").replace("-", "_") + "_screen_definition"


def test_id_from_screen(screen_id: str) -> str:
    return screen_id.replace("/", "-")


def assert_get_endpoints() -> None:
    missing = [ep for _, (ep, *_rest) in SPECS.items() if ep not in GET_PATHS]
    if missing:
        raise SystemExit("Missing GET in openapi:\n" + "\n".join(missing))


def _table_profile(domain: str) -> str | None:
    if domain in {"finance", "einkauf", "sales", "reporting"}:
        return "financial"
    if domain in {"inventory", "logistics"}:
        return "inventory"
    return None


def py_builder_block(screen_id: str, endpoint: str, domain: str, permission: str, title: str, subtitle: str) -> str:
    fn = fn_name(screen_id)
    tid = test_id_from_screen(screen_id)
    profile = _table_profile(domain)
    profile_kw = f'\n        table_profile="{profile}",' if profile else ""
    ds = f'data_sources=[cockpit_entity_source("{endpoint}")],'
    return f"""
def {fn}() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="{screen_id}",
        domain="{domain}",
        title="{title}",
        subtitle="{subtitle}",
        business_purpose="{title} als Read-Model-Cockpit.",
        example_prompts=["Zeige {title}.", "Was ist der aktuelle Stand?"],
        test_id="{tid}",
        summary=[
            {{"key": "total", "label": "Anzahl", "tone": "neutral"}},
            {{"key": "open", "label": "Offen", "tone": "warning"}},
        ],
        {ds}
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/{screen_id}")],{profile_kw}
        actions=[cockpit_refresh_action(permission="{permission}")],
        context_rail="combined",
    )
"""


def write_batch14_py() -> dict[str, str]:
    lines = [
        '"""Cockpit ScreenDefinitions — Batch 14 (85 Seiten)."""',
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
        "from app.core.cockpit_overview_parent import (",
        "    build_cockpit_overview_screen,",
        "    cockpit_entity_source,",
        "    cockpit_nav_tile,",
        "    cockpit_refresh_action,",
        ")",
        "",
    ]
    builders: dict[str, str] = {}
    for rel in SPECS:
        sid = screen_id_from_rel(rel)
        endpoint, domain, perm, title, subtitle = SPECS[rel]
        subtitle = subtitle or title
        lines.append(py_builder_block(sid, endpoint, domain, perm, title, subtitle))
        builders[sid] = fn_name(sid)
    lines.append("\nBATCH14_BUILDERS: dict[str, Any] = {")
    for sid, fn in builders.items():
        lines.append(f'    "{sid}": {fn},')
    lines.append("}")
    lines.append("\nBATCH14_SCREEN_IDS: tuple[str, ...] = tuple(BATCH14_BUILDERS.keys())")
    out = ROOT / "app/core/screen_definitions_cockpit_batch14.py"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return builders


def patch_cockpit_main() -> None:
    path = ROOT / "app/core/screen_definitions_cockpit.py"
    text = path.read_text(encoding="utf-8")
    if "screen_definitions_cockpit_batch14" in text:
        return
    insert_import = (
        "from app.core.screen_definitions_cockpit_batch14 import BATCH14_BUILDERS\n"
    )
    if insert_import.strip() not in text:
        text = text.replace(
            "from app.core.cockpit_overview_parent import (",
            insert_import + "from app.core.cockpit_overview_parent import (",
            1,
        )
    merge = "\n    **BATCH14_BUILDERS,"
    if "**BATCH14_BUILDERS" not in text:
        text = text.replace(
            "COCKPIT_SCREEN_BUILDERS: dict[str, Any] = {",
            "COCKPIT_SCREEN_BUILDERS: dict[str, Any] = {\n    **BATCH14_BUILDERS,",
            1,
        )
    path.write_text(text, encoding="utf-8")


def tsx_simple(screen_id: str, permission: str) -> str:
    tid = test_id_from_screen(screen_id)
    return f"""import {{ UniversalNativeCockpitPage }} from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = '{screen_id}'

export default function Page(): JSX.Element {{
  return (
    <UniversalNativeCockpitPage
      screenId={{SCREEN_ID}}
      testId="{tid}"
      permissions={{['{permission}']}}
    />
  )
}}
"""


def tsx_auth_login() -> str:
    return """import { useEffect } from 'react'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useAuth } from '@/hooks/useAuth'
import { toast } from '@/hooks/use-toast'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Loader2 } from 'lucide-react'

const SCREEN_ID = 'auth/login'
const DASHBOARD_PATH = '/'

export default function LoginPage(): JSX.Element {
  const { login, loading, isAuthenticated } = useAuth()

  useEffect(() => {
    if (isAuthenticated) {
      window.location.href = DASHBOARD_PATH
    }
  }, [isAuthenticated])

  const handleLogin = async (): Promise<void> => {
    try {
      await login()
    } catch (_rawErr: unknown) {
      const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({ variant: 'destructive', title: 'Anmeldung fehlgeschlagen', description: error?.message ?? 'OIDC-Redirect konnte nicht gestartet werden.' })
    }
  }

  return (
    <>
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">VALEO NeuroERP</CardTitle>
            <CardDescription>Melden Sie sich mit Ihrem Unternehmens-Account an.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button onClick={() => { void handleLogin() }} disabled={loading} className="w-full" size="lg">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Weiterleitung...
                </>
              ) : (
                'Mit SSO anmelden'
              )}
            </Button>
            <div className="text-center text-sm text-muted-foreground">
              <p>Sichere Anmeldung ueber Ihren Identity-Provider.</p>
              <p className="mt-2 text-xs">Unterstuetzt: Azure AD, Keycloak, Okta, Auth0.</p>
            </div>
          </CardContent>
        </Card>
      </div>
      <div className="sr-only" aria-hidden>
        <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="auth-login" permissions={['identity.session.read']} />
      </div>
    </>
  )
}
"""


def tsx_auth_callback() -> str:
    return """import { useEffect, useRef, useState } from 'react'
import { useSearchParams } from '@/app/routing/typed-router'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Loader2, XCircle } from 'lucide-react'

const SCREEN_ID = 'auth/callback'
const isNonEmptyString = (value: unknown): value is string => typeof value === 'string' && value.trim().length > 0
const LOGIN_PATH = '/login'

export default function CallbackPage(): JSX.Element {
  const [searchParams] = useSearchParams()
  const { handleCallback } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const started = useRef(false)

  useEffect(() => {
    if (started.current) return
    started.current = true
    const processCallback = async (): Promise<void> => {
      const codeParam = searchParams.get('code')
      const stateParam = searchParams.get('state')
      const errorParam = searchParams.get('error')
      if (isNonEmptyString(errorParam)) {
        setError(`Authentication failed: ${errorParam}`)
        return
      }
      const code = isNonEmptyString(codeParam) ? codeParam : null
      const state = isNonEmptyString(stateParam) ? stateParam : null
      if (code == null || state == null) {
        setError('Missing code or state parameter')
        return
      }
      try {
        await handleCallback(code, state)
      } catch (callbackError) {
        setError(callbackError instanceof Error ? callbackError.message : 'Authentication failed')
      }
    }
    void processCallback()
  }, [handleCallback, searchParams])

  if (error != null) {
    return (
      <>
        <div className="flex min-h-screen items-center justify-center bg-gray-50">
          <Card className="w-full max-w-md border-status-error/40">
            <CardHeader>
              <div className="flex items-center gap-3">
                <XCircle className="h-8 w-8 text-status-error" />
                <CardTitle className="text-status-error">Anmeldung fehlgeschlagen</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-status-error">{error}</p>
              <div className="mt-4">
                <a href={LOGIN_PATH} className="text-sm text-primary hover:underline">
                  Zurueck zur Anmeldung
                </a>
              </div>
            </CardContent>
          </Card>
        </div>
        <div className="sr-only" aria-hidden>
          <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="auth-callback" permissions={['identity.session.read']} />
        </div>
      </>
    )
  }

  return (
    <>
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center gap-4">
              <Loader2 className="h-12 w-12 animate-spin text-muted-foreground" />
              <p className="text-muted-foreground">Anmeldung wird abgeschlossen...</p>
            </div>
          </CardContent>
        </Card>
      </div>
      <div className="sr-only" aria-hidden>
        <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="auth-callback" permissions={['identity.session.read']} />
      </div>
    </>
  )
}
"""


def tsx_belegfolge() -> str:
    return """import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

const SCREEN_ID = 'belege/belegfolge'

export default function BelegfolgePage(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="belege-belegfolge"
      permissions={['documents.read']}
    />
  )
}
"""


def write_tsx_files() -> None:
    for rel, (_ep, _dom, perm, *_rest) in SPECS.items():
        sid = screen_id_from_rel(rel)
        target = PAGES / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if rel == "auth/Login.tsx":
            content = tsx_auth_login()
        elif rel == "auth/Callback.tsx":
            content = tsx_auth_callback()
        elif rel == "belege/BelegfolgePage.tsx":
            content = tsx_belegfolge()
        else:
            content = tsx_simple(sid, perm)
        target.write_text(content, encoding="utf-8")


def main() -> None:
    assert_get_endpoints()
    write_batch14_py()
    patch_cockpit_main()
    write_tsx_files()
    print(f"Generated {len(SPECS)} screens and pages.")


if __name__ == "__main__":
    main()
