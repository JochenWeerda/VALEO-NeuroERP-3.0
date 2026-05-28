"""Second bulk pass: remaining files with weak response_model types."""
import re
import os

FILES = [
    ("agrar_settlements.py", "AgrarSettlementOut"),
    ("finance_followup.py", "FinanceFollowupOut"),
    ("channels.py", "ChannelOut"),
    ("pos_payments.py", "PosPaymentOut"),
    ("operational_governance.py", "OperationalGovernanceOut"),
    ("neuro_event_policy.py", "NeuroEventPolicyOut"),
    ("charges.py", "ChargeOut"),
    ("case_management_api.py", "CaseManagementOut"),
    ("budget_planning.py", "BudgetPlanningOut"),
    ("background_jobs.py", "BackgroundJobOut"),
    ("asset_accounting.py", "AssetAccountingOut"),
    ("workflow_template_marketplace.py", "WorkflowTemplateOut"),
    ("workflow_runtime.py", "WorkflowRuntimeOut"),
    ("rfq.py", "RfqOut"),
    ("order_management.py", "OrderManagementOut"),
    ("notifications.py", "NotificationOut"),
    ("kpi_definitions.py", "KpiDefinitionOut"),
    ("invoice_matching.py", "InvoiceMatchingOut"),
    ("hiring.py", "HiringOut"),
    ("gobd_export.py", "GobdExportOut"),
    ("forecasting.py", "ForecastingOut"),
    ("fleet_management.py", "FleetManagementOut"),
    ("exchange_rates.py", "ExchangeRateOut"),
    ("document_scanner.py", "DocumentScannerOut"),
    ("docflow.py", "DocflowOut"),
    ("crm_leads.py", "CrmLeadOut"),
    ("crm_contacts.py", "CrmContactOut"),
    ("commission.py", "CommissionOut"),
    ("charges_bulk.py", "ChargeBulkOut"),
    ("cashflow_planner.py", "CashflowPlannerOut"),
    ("capacity_planning.py", "CapacityPlanningOut"),
    ("agrar_wetter.py", "AgrarWetterOut"),
    ("agrar_maschinen.py", "AgrarMaschinenOut"),
    ("agrar_contracts.py", "AgrarContractOut"),
    ("admin_tenants.py", "AdminTenantOut"),
    ("admin_moduls.py", "AdminModulOut"),
    ("admin_features.py", "AdminFeatureOut"),
    ("data_quality.py", "DataQualityOut"),
    ("reporting.py", "ReportingOut"),
    ("knowledge_api.py", "KnowledgeOut"),
    ("pos_retoure.py", "PosRetourOut"),
    ("pos_dsfinvk.py", "PosDsfinvkOut"),
    ("annahme_integration.py", "AnnahmeIntegrationOut"),
    ("rohware_sammelabrechnung.py", "RohwareSammelabrechnungOut"),
    ("waagen_vorlagen.py", "WaagenVorlageOut"),
]

SCHEMA_TPL = '''
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class {cls}(BaseSchema):
    model_config = _ConfigDict(extra="allow")

'''

ENDPOINTS_DIR = "app/api/v1/endpoints"

total_replaced = 0

for fname, cls in FILES:
    path = os.path.join(ENDPOINTS_DIR, fname)
    if not os.path.exists(path):
        continue

    with open(path, encoding="utf-8") as f:
        content = f.read()

    if cls in content:
        # Schema already added, just do replacements
        pass
    else:
        # Find injection point
        inject_marker = None
        for marker in ["\nrouter = APIRouter", "\nclass ", "\n@router."]:
            idx = content.find(marker)
            if idx != -1:
                inject_marker = idx
                break
        if inject_marker is None:
            continue
        schema_block = SCHEMA_TPL.format(cls=cls)
        content = content[:inject_marker] + schema_block + content[inject_marker:]

    before_count = len(re.findall(r'response_model=(dict|list)(?!\[(?!' + cls + '))', content))

    content = content.replace("response_model=dict,", f"response_model={cls},")
    content = content.replace("response_model=list,", f"response_model=list[{cls}],")
    content = re.sub(r"(\s+)response_model=dict\r?\n", rf"\1response_model={cls}\n", content)
    content = re.sub(r"(\s+)response_model=list\r?\n", rf"\1response_model=list[{cls}]\n", content)
    content = re.sub(rf"response_model=dict\[str,\s*Any\],", f"response_model={cls},", content)
    content = re.sub(rf"response_model=Dict\[str,\s*Any\],", f"response_model={cls},", content)
    content = re.sub(rf"response_model=list\[dict[^\]]*\],", f"response_model=list[{cls}],", content)
    content = re.sub(rf"response_model=list\[Dict[^\]]*\],", f"response_model=list[{cls}],", content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Done second pass")
