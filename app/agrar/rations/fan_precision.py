"""FAN precision formulas from DLG Information 01|2025, chapters 4.3 and 6.2."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import exp
from typing import Literal

PassageClass = Literal["roughage", "concentrate", "mixed_juice"]

# DLG 01|2025 table 6. Values are %/h. The mixed/juice row is evaluated by
# its stated linear relation and table endpoints (2.9 at FAN1, 5.8 at FAN4),
# avoiding the obvious non-monotonic extraction artefact at FAN2.
_PASSAGE_ENDPOINTS: dict[PassageClass, tuple[float, float]] = {
    "roughage": (2.6, 5.3),
    "concentrate": (3.5, 7.2),
    "mixed_juice": (2.9, 5.8),
}

@dataclass(frozen=True)
class FanPrecision:
    fani: float
    passage_class: PassageClass
    passage_rate_pct_h: float
    omd_fan1_pct: float | None
    omd_fani_pct: float | None
    me_fan1_mj_kgdm: float
    me_fani_mj_kgdm: float
    edg_fan1_pct: float | None
    edg_fani_pct: float | None
    udp_fani_pct: float | None
    sidp_fan1_g_kgdm: float
    sidp_fani_g_kgdm: float
    method: str = "DLG-01|2025-ch4.3-ch6.2"

    def to_dict(self) -> dict[str, float | str | None]:
        return asdict(self)


def _clamp_fani(fani: float) -> float:
    return max(1.0, min(float(fani), 5.0))


def passage_rate_pct_h(fani: float, passage_class: PassageClass) -> float:
    """Linear table-6 passage rate, extrapolated only to the supported FAN1..5 range."""
    fan = _clamp_fani(fani)
    at_one, at_four = _PASSAGE_ENDPOINTS[passage_class]
    return round(at_one + (at_four - at_one) / 3.0 * (fan - 1.0), 3)


def omd_at_fani(omd_fan1_pct: float, fani: float) -> float:
    """OMD_FANi = OMD_FAN1 - (1.5 + .05*(OMD_FAN1-65))*(FANi-1)."""
    fan = _clamp_fani(fani)
    omd = float(omd_fan1_pct)
    return round(max(0.0, min(100.0, omd - (1.5 + 0.05 * (omd - 65.0)) * (fan - 1.0))), 4)


def me_at_fani(*, me_fan1: float, ge_mj_kgdm: float | None, ash_g_kgdm: float | None,
               cp_g_kgdm: float | None, omd_fan1_pct: float | None, fani: float) -> tuple[float, float | None]:
    """DLG energy chain anchored to the catalogued ME_FAN1 value.

    Anchoring preserves laboratory/table calibration while applying the exact DLG FAN delta.
    """
    if None in (ge_mj_kgdm, ash_g_kgdm, cp_g_kgdm, omd_fan1_pct):
        return round(float(me_fan1), 4), None
    fan = _clamp_fani(fani)
    om_fraction = max(0.001, 1.0 - float(ash_g_kgdm) / 1000.0)
    ge_om = float(ge_mj_kgdm) / om_fraction
    cp_om = float(cp_g_kgdm) / om_fraction
    omd1 = float(omd_fan1_pct)
    omdi = omd_at_fani(omd1, fan)

    def calculated_me(omd: float, current_fan: float) -> float:
        de = ge_om * (omd - 3.3) / 100.0
        ch4_fan1 = 0.7 + 0.014 * omd1
        ch4 = ch4_fan1 if current_fan == 1.0 else (ch4_fan1 + 0.9 * (current_fan - 1.0)) / current_fan
        urine = 0.0037 * cp_om
        return (de - ch4 - urine) * om_fraction

    corrected = float(me_fan1) + calculated_me(omdi, fan) - calculated_me(omd1, 1.0)
    return round(max(0.0, corrected), 4), omdi


def effective_degradation_pct(*, a_pct: float | None, b_pct: float | None, c_pct_h: float | None,
                              lag_h: float | None, passage_rate_pct: float) -> float | None:
    """EDG = a + b*c/(c+k)*exp(-k*lag), using decimal hourly rates."""
    if None in (a_pct, b_pct, c_pct_h):
        return None
    a, b = float(a_pct), float(b_pct)
    c = float(c_pct_h) / 100.0
    k = float(passage_rate_pct) / 100.0
    lag = float(lag_h or 0.0)
    if c + k <= 0:
        return round(a, 4)
    return round(max(0.0, min(100.0, a + b * c / (c + k) * exp(-k * lag))), 4)


def microbial_yield_g_per_kg_dom(fani: float) -> float:
    fan = _clamp_fani(fani)
    return 150.0 if fan <= 3.4 else min(180.0, -11.0 + 47.1 * fan)


def precision_for_feed(*, fani: float, passage_class: PassageClass, me_fan1: float,
                       sidp_fan1: float, ge_mj_kgdm: float | None = None,
                       ash_g_kgdm: float | None = None, cp_g_kgdm: float | None = None,
                       omd_fan1_pct: float | None = None, a_pct: float | None = None,
                       b_pct: float | None = None, c_pct_h: float | None = None,
                       lag_h: float | None = None, sidudp_pct: float | None = None) -> FanPrecision:
    fan = _clamp_fani(fani)
    passage = passage_rate_pct_h(fan, passage_class)
    me, omdi = me_at_fani(me_fan1=me_fan1, ge_mj_kgdm=ge_mj_kgdm, ash_g_kgdm=ash_g_kgdm,
                          cp_g_kgdm=cp_g_kgdm, omd_fan1_pct=omd_fan1_pct, fani=fan)
    passage1 = passage_rate_pct_h(1.0, passage_class)
    edg1 = effective_degradation_pct(a_pct=a_pct, b_pct=b_pct, c_pct_h=c_pct_h, lag_h=lag_h, passage_rate_pct=passage1)
    edgi = effective_degradation_pct(a_pct=a_pct, b_pct=b_pct, c_pct_h=c_pct_h, lag_h=lag_h, passage_rate_pct=passage)
    sidp = float(sidp_fan1)
    if None not in (edg1, edgi, cp_g_kgdm, omd_fan1_pct, omdi):
        om = max(0.0, 1000.0 - float(ash_g_kgdm or 0.0))
        digestibility = float(sidudp_pct or 85.0) / 100.0
        def calculated_sidp(edg: float, omd: float, current_fan: float) -> float:
            dom_kg = om * omd / 100.0 / 1000.0
            sidp_mcp = dom_kg * microbial_yield_g_per_kg_dom(current_fan) * 0.85 * 0.78
            sidp_udp = float(cp_g_kgdm) * (100.0 - edg) / 100.0 * digestibility
            return sidp_mcp + sidp_udp
        sidp = max(0.0, sidp + calculated_sidp(float(edgi), float(omdi), fan) - calculated_sidp(float(edg1), float(omd_fan1_pct), 1.0))
    return FanPrecision(fan, passage_class, passage, omd_fan1_pct, omdi, float(me_fan1), me,
                        edg1, edgi, None if edgi is None else round(100.0-edgi, 4),
                        float(sidp_fan1), round(sidp, 4))