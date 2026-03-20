"""
External agent integration catalog.

This module exposes installable provider/use-case profiles for external
agents on top of the productive Process-Kernel contracts.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.agent_command_manifest import build_agent_command_manifest
from app.core.agent_tool_contract_manifest import build_agent_tool_contract_manifest


ProviderKind = Literal[
    "openapi_client",
    "mcp_client",
    "slack_app",
    "microsoft_teams_app",
    "custom_agent_sdk",
    "automation_platform",
]


class ExternalAgentProvider(BaseModel):
    provider_key: str
    provider_name: str
    provider_kind: ProviderKind
    auth_model: str
    supports_openapi: bool = False
    supports_mcp: bool = False
    supports_webhook: bool = False
    requires_manual_install: bool = False
    default_headers: list[str] = Field(default_factory=lambda: ["Authorization", "X-Tenant-ID"])
    install_notes: list[str] = Field(default_factory=list)
    schema_version: int = 1


class ExternalAgentUseCase(BaseModel):
    use_case_id: str
    title: str
    description: str
    domain: str
    status: Literal["active", "beta", "planned"] = "active"
    provider_keys: list[str]
    auth_model: str
    approval_required: bool = False
    approval_triggers: list[str] = Field(default_factory=list)
    entrypoints: list[str] = Field(default_factory=list)
    tool_contracts: list[str] = Field(default_factory=list)
    required_headers: list[str] = Field(default_factory=lambda: ["Authorization", "X-Tenant-ID"])
    install_steps: list[str] = Field(default_factory=list)
    example_prompt: str = ""
    expected_outcome: str = ""
    schema_version: int = 1


class ExternalAgentInstallPack(BaseModel):
    use_case_id: str
    provider_keys: list[str]
    title: str
    install_summary: str
    auth_model: str
    required_headers: list[str]
    entrypoints: list[str]
    install_steps: list[str]
    tool_contracts: list[str]
    command_manifest_url: str = "/api/v1/commands/agent-manifest"
    tool_contract_manifest_url: str = "/api/v1/agent/tool-contracts"
    schema_version: int = 1


class ExternalAgentIntegrationManifest(BaseModel):
    schema_version: int = 1
    generated_at: str
    manifest_kind: str = "EXTERNAL_AGENT_INTEGRATION_CATALOG"
    provider_count: int
    use_case_count: int
    domain_count: int
    domains: list[str] = Field(default_factory=list)
    providers: list[ExternalAgentProvider]
    use_cases: list[ExternalAgentUseCase]
    install_packs_url: str = "/api/v1/agent/integrations/use-cases"
    sources: list[dict[str, Any]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


def _default_providers() -> list[ExternalAgentProvider]:
    return [
        ExternalAgentProvider(
            provider_key="openapi_client",
            provider_name="OpenAPI Client",
            provider_kind="openapi_client",
            auth_model="bearer + tenant header",
            supports_openapi=True,
            install_notes=[
                "Use /api/v1/openapi.json as the canonical schema source.",
                "Best suited for codegen, SDKs and typed clients.",
            ],
        ),
        ExternalAgentProvider(
            provider_key="mcp_client",
            provider_name="MCP Client",
            provider_kind="mcp_client",
            auth_model="bearer + tenant header",
            supports_mcp=True,
            install_notes=[
                "Use /api/v1/agent/tool-contracts/mcp as the tool surface.",
                "Best suited for external agents with tool calling support.",
            ],
        ),
        ExternalAgentProvider(
            provider_key="slack_app",
            provider_name="Slack App",
            provider_kind="slack_app",
            auth_model="Slack signing secret + bot token",
            supports_webhook=True,
            requires_manual_install=True,
            install_notes=[
                "Use the Slack app manifest and incoming events endpoint.",
                "Best suited for human-in-the-loop work in channels and DMs.",
            ],
        ),
        ExternalAgentProvider(
            provider_key="microsoft_teams_app",
            provider_name="Microsoft Teams App",
            provider_kind="microsoft_teams_app",
            auth_model="Teams webhook secret / OAuth",
            supports_webhook=True,
            requires_manual_install=True,
            install_notes=[
                "Use Teams event/webhook ingress with tenant-aware auth.",
            ],
        ),
        ExternalAgentProvider(
            provider_key="custom_agent_sdk",
            provider_name="Custom Agent SDK",
            provider_kind="custom_agent_sdk",
            auth_model="OIDC bearer token + tenant header",
            supports_openapi=True,
            supports_mcp=True,
            install_notes=[
                "Use the manifest + tool contract catalog for SDK bindings.",
                "Best suited for LangGraph, custom bots and agent runtimes.",
            ],
        ),
        ExternalAgentProvider(
            provider_key="automation_platform",
            provider_name="Automation Platform",
            provider_kind="automation_platform",
            auth_model="API key / OAuth2",
            supports_openapi=True,
            supports_webhook=True,
            requires_manual_install=True,
            install_notes=[
                "Best suited for Make, Zapier, Power Automate and similar tools.",
            ],
        ),
    ]


def _default_use_cases() -> list[ExternalAgentUseCase]:
    return [
        ExternalAgentUseCase(
            use_case_id="knowledge_lookup",
            title="Knowledge Lookup",
            description="Get answers from the central knowledge core via chat or API.",
            domain="process",
            provider_keys=["openapi_client", "mcp_client", "slack_app", "microsoft_teams_app", "custom_agent_sdk"],
            auth_model="bearer + tenant header",
            approval_required=False,
            entrypoints=[
                "/api/v1/process/knowledge/retrieve",
                "/api/v1/process/knowledge/context-pack",
                "/api/v1/process/knowledge/onboarding-bundle",
            ],
            tool_contracts=["valeo_process_knowledge_retrieve", "valeo_process_knowledge_context_pack"],
            install_steps=[
                "Connect via OpenAPI or MCP.",
                "Optionally enable Slack/Teams ingress for work-queue access.",
                "Bind tenant headers and knowledge scopes.",
            ],
            example_prompt="What is the approved process for settlement approval?",
            expected_outcome="A structured answer with source references and the relevant knowledge pack.",
        ),
        ExternalAgentUseCase(
            use_case_id="process_action_execution",
            title="Process Action Execution",
            description="Execute business commands with idempotent retries and audit trail.",
            domain="process",
            provider_keys=["openapi_client", "mcp_client", "slack_app", "microsoft_teams_app", "custom_agent_sdk"],
            auth_model="bearer + tenant header",
            approval_required=True,
            approval_triggers=["mutating command", "human confirmation required"],
            entrypoints=["/api/v1/process/actions/execute", "/api/v1/process/actions/idempotency/overview"],
            tool_contracts=["valeo_process_action_execute"],
            install_steps=[
                "Register the tool contracts with the agent runtime.",
                "Use idempotency keys for every command call.",
                "Route approval-required actions through the approval gate.",
            ],
            example_prompt="Create the settlement approval command for tenant X.",
            expected_outcome="A command execution result with replay safety and approval metadata.",
        ),
        ExternalAgentUseCase(
            use_case_id="approval_decision_support",
            title="Approval Decision Support",
            description="Surface approval requirements and decision explanations for human approvers.",
            domain="workflow",
            provider_keys=["slack_app", "microsoft_teams_app", "openapi_client", "custom_agent_sdk"],
            auth_model="bearer + tenant header",
            approval_required=False,
            entrypoints=["/api/v1/process/agent/approval-rules", "/api/v1/process/agent/approval-evaluate"],
            tool_contracts=["valeo_process_agent_approval_evaluate"],
            install_steps=[
                "Bind the workflow approval endpoint to the external agent.",
                "Use human-in-the-loop only for the final decision.",
            ],
            example_prompt="Why is this action blocked and who can approve it?",
            expected_outcome="An explainable approval recommendation with rule and role context.",
        ),
        ExternalAgentUseCase(
            use_case_id="finance_control_read",
            title="Finance Control Read",
            description="Consume safe finance and controlling read models without mutating state.",
            domain="finance",
            provider_keys=["openapi_client", "mcp_client", "custom_agent_sdk", "automation_platform"],
            auth_model="bearer + tenant header",
            approval_required=False,
            entrypoints=[
                "/api/v1/process/actions/idempotency/overview",
                "/api/v1/process-mining/finance/report",
                "/api/v1/benchmark/process-mining/{verbund_id}",
            ],
            tool_contracts=["valeo_finance_payment_run_list", "valeo_process_action_execute"],
            install_steps=[
                "Prefer read-model endpoints for dashboards and external analytics.",
                "Keep the tenant boundary explicit in every request.",
            ],
            example_prompt="Show me the current finance and workflow bottlenecks for this tenant.",
            expected_outcome="A read-only operational view with safe metrics and bottlenecks.",
        ),
        ExternalAgentUseCase(
            use_case_id="bulk_batch_runner",
            title="Bulk Batch Runner",
            description="Run mass operations and batch validation before write paths are activated.",
            domain="process",
            provider_keys=["openapi_client", "mcp_client", "custom_agent_sdk", "automation_platform"],
            auth_model="bearer + tenant header",
            approval_required=True,
            approval_triggers=["batch write", "large import", "high volume mutation"],
            entrypoints=["/api/v1/process/bulk-operations/evaluate", "/api/v1/finance/bulk-journal-import/csv"],
            tool_contracts=["valeo_process_bulk_operations_evaluate"],
            install_steps=[
                "Use batch validation before the first write.",
                "Apply idempotency and DQ checks to every row.",
            ],
            example_prompt="Validate a 500-row import before posting.",
            expected_outcome="Bulk validation output with DQ and limit feedback.",
        ),
        ExternalAgentUseCase(
            use_case_id="document_extraction",
            title="Document Extraction",
            description="Extract structured fields from OCR text and route them to finance/docflow.",
            domain="docflow",
            provider_keys=["openapi_client", "mcp_client", "custom_agent_sdk", "automation_platform"],
            auth_model="bearer + tenant header",
            approval_required=False,
            approval_triggers=["manual review required when OCR confidence is low"],
            entrypoints=["/api/v1/process/dms/extract"],
            tool_contracts=["valeo_process_dms_extract"],
            install_steps=[
                "Send OCR text and document type to the extraction endpoint.",
                "Check the `manuelle_pruefung_erforderlich` flag before auto-posting.",
            ],
            example_prompt="Extract invoice fields from this OCR text.",
            expected_outcome="A structured DMS extraction contract with downstream process hints.",
        ),
        ExternalAgentUseCase(
            use_case_id="supply_chain_eta_monitoring",
            title="Supply Chain ETA Monitoring",
            description="Monitor ETA deviation and trigger alerts when deliveries drift.",
            domain="supply_chain",
            provider_keys=["openapi_client", "mcp_client", "slack_app", "microsoft_teams_app"],
            auth_model="bearer + tenant header",
            approval_required=False,
            entrypoints=["/api/v1/process/supply-chain/eta/alarm"],
            tool_contracts=["valeo_process_supply_chain_eta_alarm"],
            install_steps=[
                "Bind the ETA alarm endpoint to the monitoring agent.",
                "Route alarms to chat channels for operations teams.",
            ],
            example_prompt="Alert me when a delivery is late by more than two hours.",
            expected_outcome="An ETA alarm with deviation and severity metadata.",
        ),
        ExternalAgentUseCase(
            use_case_id="complaint_case_orchestration",
            title="Complaint Case Orchestration",
            description="Create, track and resolve complaint cases with CRM and DMS context.",
            domain="crm",
            provider_keys=["openapi_client", "mcp_client", "custom_agent_sdk"],
            auth_model="bearer + tenant header",
            approval_required=True,
            approval_triggers=["closing a complaint", "accepting a complaint", "changing legal status"],
            entrypoints=[
                "/api/v1/reklamationen",
                "/api/v1/reklamationen/{reklamation_id}",
                "/api/v1/reklamationen/{reklamation_id}/audit",
            ],
            tool_contracts=["valeo_crm_reklamation_create", "valeo_crm_reklamation_transition"],
            install_steps=[
                "Create the complaint record with DMS references.",
                "Keep the CRM/DMS chain explicit for auditability.",
            ],
            example_prompt="Open a complaint and attach the relevant evidence documents.",
            expected_outcome="A complaint case with SLA, DMS and CRM linkage.",
        ),
        ExternalAgentUseCase(
            use_case_id="workflow_sandbox_preview",
            title="Workflow Sandbox Preview",
            description="Preview workflow definitions before they are activated in production.",
            domain="workflow",
            provider_keys=["openapi_client", "mcp_client", "custom_agent_sdk"],
            auth_model="bearer + tenant header",
            approval_required=False,
            entrypoints=["/api/v1/workflow/simulation/scenarios", "/api/v1/workflow/simulation/preview"],
            tool_contracts=["valeo_workflow_simulation_run"],
            install_steps=[
                "Use sandbox preview before promoting workflow changes.",
                "Compare simulation output with the active workflow definition.",
            ],
            example_prompt="Preview the AP approval workflow for next week.",
            expected_outcome="A sandbox preview with warnings and a recommended next action.",
        ),
        ExternalAgentUseCase(
            use_case_id="dashboard_read_model_consumer",
            title="Dashboard Read-Model Consumer",
            description="Consume safe dashboard and process-mining read models for external analytics.",
            domain="analytics",
            provider_keys=["openapi_client", "mcp_client", "automation_platform", "custom_agent_sdk"],
            auth_model="bearer + tenant header",
            approval_required=False,
            entrypoints=[
                "/api/v1/process-mining/finance/report",
                "/api/v1/process-mining/finance/observation",
            ],
            tool_contracts=["valeo_process_mining_finance_report"],
            install_steps=[
                "Prefer read-model endpoints instead of live joins.",
                "Use drilldowns for the top bottlenecks only.",
            ],
            example_prompt="Show me the top 10 process bottlenecks for this tenant.",
            expected_outcome="A stable dashboard read-model with bottleneck drilldown.",
        ),
        ExternalAgentUseCase(
            use_case_id="background_job_orchestration",
            title="Background Job Orchestration",
            description="Queue heavy process work and observe job state without blocking UI flows.",
            domain="process",
            provider_keys=["openapi_client", "mcp_client", "custom_agent_sdk", "automation_platform"],
            auth_model="bearer + tenant header",
            approval_required=False,
            entrypoints=[
                "/api/v1/process/background-jobs/enqueue",
                "/api/v1/process/background-jobs",
                "/api/v1/process/tenant-limits/overview",
            ],
            tool_contracts=["valeo_process_background_jobs"],
            install_steps=[
                "Queue long-running work instead of synchronous mutation paths.",
                "Observe tenant-safe queue and limit state before scaling concurrent runs.",
            ],
            example_prompt="Queue a snapshot rebuild and monitor the tenant-safe background job queue.",
            expected_outcome="A queued background job with stable status and tenant-aware throughput context.",
        ),
    ]


def build_external_agent_integration_catalog(
    domain: str | None = None,
    provider_key: str | None = None,
    use_case_id: str | None = None,
) -> ExternalAgentIntegrationManifest:
    providers = _default_providers()
    use_cases = _default_use_cases()

    if domain:
        use_cases = [use_case for use_case in use_cases if use_case.domain == domain]
    if provider_key:
        use_cases = [use_case for use_case in use_cases if provider_key in use_case.provider_keys]
        providers = [provider for provider in providers if provider.provider_key == provider_key]
    if use_case_id:
        use_cases = [use_case for use_case in use_cases if use_case.use_case_id == use_case_id]

    tool_manifest = build_agent_tool_contract_manifest()
    command_manifest = build_agent_command_manifest()
    domains = sorted({use_case.domain for use_case in use_cases})

    return ExternalAgentIntegrationManifest(
        generated_at=datetime.now(timezone.utc).isoformat(),
        provider_count=len(providers),
        use_case_count=len(use_cases),
        domain_count=len(domains),
        domains=domains,
        providers=providers,
        use_cases=use_cases,
        sources=[
            {
                "rel": "openapi",
                "href": "/api/v1/openapi.json",
                "description": "OpenAPI 3.x source for code generation and typed clients",
            },
            {
                "rel": "mcp-tool-contracts",
                "href": "/api/v1/agent/tool-contracts",
                "description": "Machine-readable tool contract surface for external agents",
            },
            {
                "rel": "agent-command-manifest",
                "href": "/api/v1/commands/agent-manifest",
                "description": "Agent command manifest for idempotent business commands",
            },
            {
                "rel": "tool-contract-summary",
                "href": "/api/v1/agent/tool-contracts/openapi",
                "description": "OpenAPI-linked tool contract view",
            },
        ],
        notes=[
            "Provider catalog and use-case catalog are additive to the Process-Kernel tool manifest.",
            f"Tool contract manifest exposes {tool_manifest.tool_count} productively supported tools.",
            f"Command manifest exposes {len(command_manifest.commands)} command contracts.",
            "Install packs are intentionally opinionated: they show the canonical entry points, headers and approval constraints.",
        ],
    )


def build_external_agent_install_pack(use_case_id: str) -> ExternalAgentInstallPack:
    use_case = next((item for item in _default_use_cases() if item.use_case_id == use_case_id), None)
    if use_case is None:
        raise KeyError(use_case_id)
    provider_labels = ", ".join(use_case.provider_keys)
    return ExternalAgentInstallPack(
        use_case_id=use_case.use_case_id,
        provider_keys=use_case.provider_keys,
        title=use_case.title,
        install_summary=f"Install {use_case.title} for providers: {provider_labels}.",
        auth_model=use_case.auth_model,
        required_headers=use_case.required_headers,
        entrypoints=use_case.entrypoints,
        install_steps=use_case.install_steps,
        tool_contracts=use_case.tool_contracts,
    )
