from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from typing import Optional
import uuid

class TriggerEvent(str, Enum):
    ON_FREIGABE_CLICK = "on_freigabe_click"
    ON_ABLEHNUNG_CLICK = "on_ablehnung_click"
    ON_SPEICHERN_CLICK = "on_speichern_click"
    ON_FINALISIEREN_CLICK = "on_finalisieren_click"
    ON_ZAHLUNGSLAUF_CLICK = "on_zahlungslauf_click"
    ON_LASTSCHRIFT_CLICK = "on_lastschrift_click"

class MaskenCommandBinding(BaseModel):
    """Bindet ein UI-Ereignis einer Maske an einen Process-Kernel-Command."""
    binding_id: str
    masken_id: str                  # z.B. "B001" (aus Wave 3 MaskRegistry)
    masken_name: str
    command_name: str               # z.B. "ApproveAPInvoice" (aus Wave 5 Katalog)
    trigger_event: TriggerEvent
    required_preconditions: list[str]   # Felder die im aggregate_state vorhanden sein muessen
    dispatch_endpoint: str = "/api/v1/commands/dispatch"
    schema_version: int = 1

class MaskenBindingRegistry(BaseModel):
    bindings: list[MaskenCommandBinding] = []
    schema_version: int = 1

    def add(self, binding: MaskenCommandBinding) -> MaskenCommandBinding:
        self.bindings.append(binding)
        return binding

    def by_masken_id(self, masken_id: str) -> list[MaskenCommandBinding]:
        return [b for b in self.bindings if b.masken_id == masken_id]

    def by_command(self, command_name: str) -> list[MaskenCommandBinding]:
        return [b for b in self.bindings if b.command_name == command_name]

    def alle_masken_ids(self) -> list[str]:
        return list({b.masken_id for b in self.bindings})

def build_default_bindings() -> MaskenBindingRegistry:
    """Bindings aller Wave-3-Masken auf Wave-5-Commands."""
    registry = MaskenBindingRegistry()

    # AP-Invoice Masken (Klasse A)
    registry.add(MaskenCommandBinding(
        binding_id=str(uuid.uuid4()),
        masken_id="A001",
        masken_name="AP-Invoice-Genehmigung",
        command_name="ApproveAPInvoice",
        trigger_event=TriggerEvent.ON_FREIGABE_CLICK,
        required_preconditions=["status", "betrag_eur"],
    ))
    registry.add(MaskenCommandBinding(
        binding_id=str(uuid.uuid4()),
        masken_id="A001",
        masken_name="AP-Invoice-Ablehnung",
        command_name="RejectAPInvoice",
        trigger_event=TriggerEvent.ON_ABLEHNUNG_CLICK,
        required_preconditions=["status"],
    ))
    registry.add(MaskenCommandBinding(
        binding_id=str(uuid.uuid4()),
        masken_id="A001",
        masken_name="AP-Invoice-Verbuchung",
        command_name="PostAPInvoice",
        trigger_event=TriggerEvent.ON_FINALISIEREN_CLICK,
        required_preconditions=["status", "freigabe_erteilt"],
    ))

    # Ernte-Annahme Masken (Klasse B)
    registry.add(MaskenCommandBinding(
        binding_id=str(uuid.uuid4()),
        masken_id="B001",
        masken_name="Ernte-Annahme-Finalisierung",
        command_name="FinalizeHarvestAcceptance",
        trigger_event=TriggerEvent.ON_FINALISIEREN_CLICK,
        required_preconditions=["gewicht_netto_kg", "feuchte_pct"],
    ))

    # Qualitaetsprotokoll (Klasse B)
    registry.add(MaskenCommandBinding(
        binding_id=str(uuid.uuid4()),
        masken_id="B002",
        masken_name="Qualitaetsprotokoll-Freigabe",
        command_name="ReleaseQualityProtocol",
        trigger_event=TriggerEvent.ON_FREIGABE_CLICK,
        required_preconditions=["analysen_abgeschlossen"],
    ))

    # Agrar-Settlement (Klasse B)
    registry.add(MaskenCommandBinding(
        binding_id=str(uuid.uuid4()),
        masken_id="B003",
        masken_name="Settlement-Anlage",
        command_name="CreateAgrarSettlement",
        trigger_event=TriggerEvent.ON_SPEICHERN_CLICK,
        required_preconditions=["kontrakt_id", "menge_t"],
    ))
    registry.add(MaskenCommandBinding(
        binding_id=str(uuid.uuid4()),
        masken_id="B003",
        masken_name="Settlement-Finalisierung",
        command_name="FinalizeAgrarSettlement",
        trigger_event=TriggerEvent.ON_FINALISIEREN_CLICK,
        required_preconditions=["positionen_vollstaendig"],
    ))

    # Zahlungslauf (Klasse C)
    registry.add(MaskenCommandBinding(
        binding_id=str(uuid.uuid4()),
        masken_id="C001",
        masken_name="Zahlungslauf-Ausfuehrung",
        command_name="ExecutePaymentRun",
        trigger_event=TriggerEvent.ON_ZAHLUNGSLAUF_CLICK,
        required_preconditions=["freigabe_erteilt", "zahlungsdatum"],
    ))

    # Lastschrift (Klasse C)
    registry.add(MaskenCommandBinding(
        binding_id=str(uuid.uuid4()),
        masken_id="C002",
        masken_name="Lastschrift-Ausfuehrung",
        command_name="ExecuteDirectDebit",
        trigger_event=TriggerEvent.ON_LASTSCHRIFT_CLICK,
        required_preconditions=["mandat_vorhanden", "faelligkeitsdatum"],
    ))

    return registry
