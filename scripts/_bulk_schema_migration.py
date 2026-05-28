"""Bulk migration: add domain Out schema + replace weak response_model in many files."""
import re
import os

# (filename, schema_class_name, inject_after_line_pattern)
FILES = [
    ("external_agent_integrations.py", "AgentIntegrationOut"),
    ("compliance.py", "ComplianceOut"),
    ("kontrakte.py", "KontraktOut"),
    ("gap.py", "GapOut"),
    ("crm_campaigns.py", "CrmCampaignOut"),
    ("agents.py", "AgentOut"),
    ("training.py", "TrainingOut"),
    ("waage.py", "WaageOut"),
    ("fuhrpark.py", "FuhrparkOut"),
    ("agrar_feldbuch.py", "AgrarFeldbuchOut"),
    ("flow_spines.py", "FlowSpineOut"),
    ("warehouse_wms.py", "WarehouseWmsOut"),
    ("rations_optimization.py", "RationsOptimizationOut"),
    ("neuro_state_graph_api.py", "NeuroStateOut"),
    ("controlling.py", "ControllingOut"),
    ("personal.py", "PersonalOut"),
    ("logistics_tours.py", "LogisticsTourOut"),
    ("banken.py", "BankenOut"),
    ("channel_work_surfaces.py", "ChannelWorkSurfaceOut"),
    ("sustainability.py", "SustainabilityOut"),
    ("silo.py", "SiloOut"),
    ("reklamation_api.py", "ReklamationOut"),
    ("portal_feldbuch.py", "PortalFeldbuchOut"),
    ("rohware_schema.py", "RohwareOut"),
    ("futtermittel_rezepte.py", "FuttermittelRezeptOut"),
]

SCHEMA_TPL = '''
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class {cls}(BaseSchema):
    """Typed response schema for {cls} endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")

'''

ENDPOINTS_DIR = "app/api/v1/endpoints"

total_replaced = 0

for fname, cls in FILES:
    path = os.path.join(ENDPOINTS_DIR, fname)
    if not os.path.exists(path):
        print(f"SKIP (not found): {fname}")
        continue

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Skip if already migrated
    if cls in content:
        print(f"SKIP (already has {cls}): {fname}")
        continue

    # Find a good injection point: after last import block before first class/router
    # Strategy: inject before first @router. or before first class definition
    inject_marker = None
    for marker in ["\nrouter = APIRouter", "\nclass ", "\n@router."]:
        idx = content.find(marker)
        if idx != -1:
            inject_marker = idx
            break

    if inject_marker is None:
        print(f"SKIP (no injection point): {fname}")
        continue

    schema_block = SCHEMA_TPL.format(cls=cls)
    content = content[:inject_marker] + schema_block + content[inject_marker:]

    # Replace response_model=dict, and response_model=dict\n
    before = content.count("response_model=dict")
    content = content.replace("response_model=dict,", f"response_model={cls},")
    # Multi-line (standalone on its own line, possibly with trailing \r)
    content = re.sub(r"(\s+)response_model=dict\r?\n", rf"\1response_model={cls}\n", content)

    # Replace response_model=list, and standalone response_model=list\n
    content = content.replace("response_model=list,", f"response_model=list[{cls}],")
    content = re.sub(r"(\s+)response_model=list\r?\n", rf"\1response_model=list[{cls}]\n", content)

    after = content.count("response_model=dict") + content.count("response_model=list,") + \
            len(re.findall(r"response_model=list\b(?!\[)", content))

    replaced = before - after
    total_replaced += replaced

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  {fname:55s} {replaced:3d} replaced")

print(f"\nTotal replaced: {total_replaced}")
