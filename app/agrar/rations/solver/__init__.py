"""LP-Solver-Logik (Constraint-Registry, Aggregation, Relaxation, Stage-2)."""

from .feed import Feed
from .mixing import mix_group_order
from .lp_constraints import (
    build_lp_constraint_matrix,
    LPConstraintResult,
)
from .lp_stage2 import (
    POLICY_BAND_SPECS,
    policy_band_coeffs,
    policy_profile_band_evaluate,
    build_policy_band_lp_extension,
    build_policy_profile_evaluation,
)
from .constraint_registry import (
    CONSTR_ANDFOM_GF_GEQ,
    CONSTR_ANDFOM_TOT_GEQ,
    CONSTR_ANDFOM_TOT_LEQ,
    CONSTR_CA_LEQ,
    CONSTR_CP_DENSITY,
    CONSTR_DMI_GEQ,
    CONSTR_DMI_LEQ,
    CONSTR_ME_ABS_LEQ,
    CONSTR_ME_DENSITY,
    CONSTR_ME_GEQ,
    CONSTR_MG_LEQ,
    CONSTR_NA_LEQ,
    CONSTR_P_LEQ,
    CONSTR_PABKH_LEQ,
    CONSTR_RMD_DENSITY,
    CONSTR_SIDP_GEQ,
    CONSTR_XL_DENSITY,
    ConstraintDef,
    ConstraintRegistry,
)

__all__ = [
    "Feed",
    "mix_group_order",
    "build_lp_constraint_matrix",
    "LPConstraintResult",
    "POLICY_BAND_SPECS",
    "policy_band_coeffs",
    "policy_profile_band_evaluate",
    "build_policy_band_lp_extension",
    "build_policy_profile_evaluation",
    "ConstraintDef",
    "ConstraintRegistry",
    "CONSTR_ME_GEQ",
    "CONSTR_SIDP_GEQ",
    "CONSTR_ANDFOM_TOT_GEQ",
    "CONSTR_ANDFOM_GF_GEQ",
    "CONSTR_PABKH_LEQ",
    "CONSTR_XL_DENSITY",
    "CONSTR_CP_DENSITY",
    "CONSTR_RMD_DENSITY",
    "CONSTR_ME_DENSITY",
    "CONSTR_ME_ABS_LEQ",
    "CONSTR_ANDFOM_TOT_LEQ",
    "CONSTR_CA_LEQ",
    "CONSTR_P_LEQ",
    "CONSTR_NA_LEQ",
    "CONSTR_MG_LEQ",
    "CONSTR_DMI_GEQ",
    "CONSTR_DMI_LEQ",
]
