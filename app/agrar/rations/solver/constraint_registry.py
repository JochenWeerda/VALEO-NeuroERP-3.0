"""Constraint-Registry für den Stage-1-LP (Refactor Schritt 3, 2026-04-23).

Ersetzt die bisherige Index-Magie (``_IDX_XL = 5``, ``_IDX_ANDFOM_GF = 3``,
``_IDX_RMD = 7``, ``_IDX_ME_ABS = 9``) durch benannte Handles.

Das ist bewusst ein **minimaler** erster Schritt: der bisherige LP-Aufbau
in ``_run_lp`` bleibt unverändert (erst Schritt 4 zerlegt die LP-Phasen
deklarativ); die Registry führt nur die Zuordnung ``name -> row-index``
und liefert die vier Index-Konstanten, die an den Relaxations-Schritten
verwendet werden. Damit verschwindet die Gefahr, dass eine neue
Nebenbedingung zwischen zwei anderen die hart verdrahteten Indizes
verschiebt.

Motivation (User-Feedback 2026-04-23):
- "Sehr viel ist aktuell „hart im Code verdrahtet“ (``_IDX_XL = 5``)."
- "Das ist gefährlich, weil jede neue Nebenbedingung die Indizes
  verschiebt. Besser mit Namen statt Index arbeiten."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class ConstraintDef:
    """Benannte Nebenbedingung im Stage-1-LP.

    Die Registry zählt beim Anlegen einen internen Index hoch und gibt
    ihn über ``index`` zurück.
    """

    name: str
    index: int
    description: str = ""
    relaxable: bool = False


@dataclass(slots=True)
class ConstraintRegistry:
    """Registry für Stage-1-LP-Rows.

    Verwendung:

    .. code-block:: python

        reg = ConstraintRegistry()
        A_ub, b_ub = [], []
        reg.add("me_geq", description="ME >= Bedarf")
        A_ub.append(...); b_ub.append(...)
        reg.add("xl_density", description="XL-Dichte <= 40", relaxable=True)
        ...
        idx_xl = reg.index_of("xl_density")
        A_ub[idx_xl] = ...  # Relaxation
    """

    defs: List[ConstraintDef] = field(default_factory=list)
    _by_name: Dict[str, int] = field(default_factory=dict)

    def add(
        self,
        name: str,
        *,
        description: str = "",
        relaxable: bool = False,
    ) -> int:
        """Registriert eine neue Row und liefert den vergebenen Index."""
        if name in self._by_name:
            raise ValueError(f"Constraint '{name}' bereits registriert")
        idx = len(self.defs)
        self.defs.append(
            ConstraintDef(name=name, index=idx, description=description, relaxable=relaxable)
        )
        self._by_name[name] = idx
        return idx

    def index_of(self, name: str) -> int:
        try:
            return self._by_name[name]
        except KeyError as exc:
            raise KeyError(
                f"Unbekannter Constraint-Name '{name}'. "
                f"Registrierte: {list(self._by_name)}"
            ) from exc

    def names(self) -> List[str]:
        return [cd.name for cd in self.defs]


# Symbolische Namen der historisch relaxierbaren Constraints.
# Die konkreten Indizes werden in ``_run_lp`` per ``reg.add(...)`` vergeben
# und dann über ``reg.index_of(CONSTR_XL_DENSITY)`` symbolisch abgerufen.
CONSTR_ME_GEQ = "me_geq"
CONSTR_SIDP_GEQ = "sidp_geq"
CONSTR_ANDFOM_TOT_GEQ = "andfom_total_geq"
CONSTR_ANDFOM_GF_GEQ = "andfom_gf_geq"        # idx 3 (historisch)
CONSTR_PABKH_LEQ = "pabkh_density_leq"
CONSTR_XL_DENSITY = "xl_density_leq"            # idx 5 (historisch)
CONSTR_CP_DENSITY = "cp_density_leq"
CONSTR_RMD_DENSITY = "rmd_density_leq"          # idx 7 (historisch)
CONSTR_ME_DENSITY = "me_density_leq"
CONSTR_ME_ABS_LEQ = "me_absolute_leq"           # idx 9 (historisch)
CONSTR_ANDFOM_TOT_LEQ = "andfom_total_leq"
CONSTR_CA_LEQ = "ca_density_leq"
CONSTR_P_LEQ = "p_density_leq"
CONSTR_NA_LEQ = "na_density_leq"
CONSTR_MG_LEQ = "mg_density_leq"
CONSTR_DMI_GEQ = "dmi_geq"
CONSTR_DMI_LEQ = "dmi_leq"


__all__ = [
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
