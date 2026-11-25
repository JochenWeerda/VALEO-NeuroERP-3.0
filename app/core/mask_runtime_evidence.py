"""Conservative static evidence: imports, comments and invisible decoys prove no runtime."""
import re
from pathlib import Path

_HIDDEN = re.compile(r'<(?:div|span)\b[^>]*(?:aria-hidden|sr-only)[^>]*>.*?</(?:div|span)>', re.S)
_COMMENTS = re.compile(r'/\*.*?\*/|^\s*//[^\n]*', re.S | re.M)
_VISIBLE_RUNTIME = re.compile(
    r'<(?:UniversalMaskRenderer|UniversalNative(?:Detail|Create|Cockpit)Page|NativeListPage|NativeAuditListPage|'
    r'CaptureScreenHost|MadeByStudio(?:List|Detail|Cockpit)RuntimeWire|'
    r'DocumentControlScopePage|SanktionsScopePage|PartyNativePage|UniversalMaskRolloutPilotPage)\b'
    # belegSeite → UniversalNativeDetailPage (BELEG-052 DocFlow); createStamm* → Native Create/Detail.
    r'|\b(?:useUniversalMaskRuntime|createStammNative(?:Detail|Create|List)Page|belegSeite)\s*\('
)


def has_visible_runtime(source: str) -> bool:
    code = _COMMENTS.sub('', source)
    if re.search(r'\bcreateLegacyMaskPage\s*\(', code):
        return False
    return bool(_VISIBLE_RUNTIME.search(_HIDDEN.sub('', code)))


def is_navigate_only_redirect(source: str, *, filename: str = '') -> bool:
    """Reine Umleitungsseiten sind keine Altmasken (technische Redirects).

    Dececkt ``<Navigate … replace />`` und programmatische ``navigate(…, { replace: true })``
    ohne Runtime-Host und ohne Legacy-ObjectPage/ListReport/Wizard.
    """
    if filename in ('NotFound.tsx', 'Login.tsx', 'Callback.tsx'):
        return False
    code = _HIDDEN.sub('', _COMMENTS.sub('', source))
    has_jsx_navigate = bool(re.search(r'\bNavigate\b', code))
    has_prog_navigate = bool(
        re.search(r'\bnavigate\s*\([^)]*\{\s*replace\s*:\s*true\s*\}', code)
    )
    if not has_jsx_navigate and not has_prog_navigate:
        return False
    # Kein Runtime-Host und keine Legacy-ObjectPage — nur Umleitung.
    if has_visible_runtime(code) or re.search(r'\bObjectPage\b|\bListReport\b|\bWizard\b', code):
        return False
    return not re.search(r'\bcreateLegacyMaskPage\s*\(', code)


def bound_domain_runtime_ids(source: str, *, root: Path | None = None) -> frozenset[str]:
    """Evidence for the fixed specialist host, including its actual runtime chain.

    A wrapper name alone is insufficient: require the exact imported host,
    visible literal identity, canonical specialist declaration and registered
    domain renderer. This remains structural evidence, not a live acceptance.
    """
    root = root or Path(__file__).resolve().parents[2]
    code = _HIDDEN.sub('', _COMMENTS.sub('', source))
    if not re.search(r"import\s*\{\s*IntakeWeighingPage\s*\}\s*from\s*['\"]@/components/mask-builder/specialized/intake/domain-runtime['\"]", code):
        return frozenset()
    host_root = root / 'packages/frontend-web/src/components/mask-builder'
    try:
        host = (host_root / 'specialized/intake/domain-runtime.tsx').read_text(encoding='utf-8')
        registry = (host_root / 'specialized/registry.ts').read_text(encoding='utf-8')
        renderer = (host_root / 'UniversalMaskRenderer.tsx').read_text(encoding='utf-8')
    except OSError:
        return frozenset()
    if (not has_visible_runtime(host) or not re.search(r'<SpecializedComponentHost\s+specialized=\{plan.specialized\}\s+plan=\{plan\}', renderer)):
        return frozenset()
    from app.core.screen_definitions import get_screen_definition
    from app.core.stamm_object_page_parent import ensure_stamm_screen_registry
    ensure_stamm_screen_registry()
    from app.services.studio_runtime_surface_contracts import SPECIALIZED_SCREENS, validate_runtime_surface
    found = set()
    for screen_id in re.findall(r'<IntakeWeighingPage\s+screenId=[\'"]([^\'"]+)[\'"]\s*/>', code):
        definition = get_screen_definition(screen_id)
        specialized = definition.get('specialized') if definition else None
        if not isinstance(specialized, dict) or validate_runtime_surface(definition):
            continue
        kind = specialized.get('type')
        if not isinstance(kind, str) or screen_id not in SPECIALIZED_SCREENS.get(kind, ()):
            continue
        modules = {'intake': ('Intake', 'intake/intake.tsx'),
                   'weighing': ('Weighing', 'weighing/weighing.tsx'),
                   'finance_workbench': ('FinanceWorkbench', 'finance/finance-workbench.tsx'),
                   # Seit 23.11.2026: Control-Center und Webhooks laufen ueber denselben Fach-Host; ohne diesen
                   # Eintrag stand das Control-Center im Inventar als "handgebaut".
                   'admin_workbench': ('AdminWorkbench', 'admin/admin-workbench.tsx')}
        if kind not in modules:
            continue
        symbol, module = modules[kind]
        if not re.search(r'\b' + kind + r'\s*:\s*' + symbol + r'\b', registry):
            continue
        try:
            domain = (host_root / 'specialized' / module).read_text(encoding='utf-8')
        except OSError:
            continue
        if (f"'{screen_id}'" in domain and 'plan={plan}' in domain
                and 'contract.id' in domain and 'plan.specialized' in domain):
            found.add(screen_id)
    return frozenset(found)
