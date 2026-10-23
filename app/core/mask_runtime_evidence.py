"""Conservative static evidence: imports, comments and invisible decoys prove no runtime."""
import re

_HIDDEN = re.compile(r'<(?:div|span)\b[^>]*(?:aria-hidden|sr-only)[^>]*>.*?</(?:div|span)>', re.S)
_COMMENTS = re.compile(r'/\*.*?\*/|^\s*//[^\n]*', re.S | re.M)
_VISIBLE_RUNTIME = re.compile(
    r'<(?:UniversalMaskRenderer|UniversalNative(?:Detail|Create|Cockpit)Page|NativeListPage|'
    r'CaptureScreenHost|MadeByStudio(?:List|Detail|Cockpit)RuntimeWire|'
    r'DocumentControlScopePage|SanktionsScopePage|PartyNativePage|UniversalMaskRolloutPilotPage)\b'
    r'|\b(?:useUniversalMaskRuntime|createStammNative(?:Detail|Create|List)Page)\s*\('
)


def has_visible_runtime(source: str) -> bool:
    code = _COMMENTS.sub('', source)
    if re.search(r'\bcreateLegacyMaskPage\s*\(', code):
        return False
    return bool(_VISIBLE_RUNTIME.search(_HIDDEN.sub('', code)))
