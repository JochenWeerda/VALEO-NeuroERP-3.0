"""
Neuro Tool Execution Service - NC-A7
Executes authenticated read/calculation/validation contracts internally.
Legacy writes and external transport remain disabled pending contract approval.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from fastapi import HTTPException
from starlette.requests import Request
from fastapi.testclient import TestClient

from app.core.mcp_tool_contracts import MCPRequestPayloadMode, MCPToolContract, MCPToolKategorie

logger = logging.getLogger(__name__)

_PATH_PARAM_PATTERN = re.compile(r"{([^{}]+)}")


class NeuroToolExecutionService:
    def __init__(
        self,
        client: TestClient | None = None,
        *,
        external_requester: Any | None = None,
    ) -> None:
        self._client = client
        self._external_requester = external_requester

    def execute_contract(
        self,
        contract: MCPToolContract,
        *,
        parameters: dict[str, Any],
        tenant_id: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ctx = context or {}
        method, path_template = self._split_endpoint(contract.api_endpoint or "GET /api/v1/unknown")
        rejection = self._execution_rejection(contract, tenant_id, ctx)
        if rejection is not None:
            return rejection
        try:
            request_spec = self._build_request_spec(
                contract, method=method, path_template=path_template,
                parameters=parameters, tenant_id=tenant_id, context=ctx,
            )
        except HTTPException as exc:
            return {
                "mode": "execution_rejected", "tool_name": contract.tool_name,
                "http_status": exc.status_code, "rejection_reason": ("invalid_contract_payload" if exc.status_code == 422 else "tenant_selector_rejected"),
                "request": {}, "response": None,
            }

        client = self._get_client()
        try:
            response = client.request(
                method=method,
                url=request_spec["path"],
                params=request_spec["query"],
                json=request_spec["json"],
                headers=request_spec["headers"],
            )
        except Exception:  # pragma: no cover - defensive boundary
            logger.warning("Internal tool execution failed for %s", contract.tool_name)
            return self._fallback_result(contract, request_spec, "transport_error")

        if response.status_code >= 400:
            return self._fallback_result(
                contract,
                request_spec,
                f"http_{response.status_code}",
                http_status=response.status_code,
                response_body=self._read_response_body(response),
            )

        return {
            "mode": "openapi_internal",
            "tool_name": contract.tool_name,
            "api_endpoint": contract.api_endpoint,
            "http_status": response.status_code,
            "request": self._public_request_spec(request_spec),
            "response": self._read_response_body(response),
        }

    @staticmethod
    def _execution_rejection(
        contract: MCPToolContract, tenant_id: str, context: dict[str, Any]
    ) -> dict[str, Any] | None:
        # This legacy transport has no target-bound external credentials or
        # approved versioned write-command binding. Caller flags cannot enable it.
        reason, status = None, 403
        token = context.get("auth_token")
        if not isinstance(token, str) or not token.strip() or any(c in token for c in "\r\n"):
            reason, status = "authenticated_token_required", 401
        elif not isinstance(tenant_id, str) or not tenant_id.strip():
            reason = "tenant_required"
        elif context.get("external_base_url"):
            reason = "external_target_not_approved"
        elif contract.tool_name == "valeo_workflow_instance_status":
            # Its REST target lists definitions, not instance/delivery/approval
            # state. Do not let a successful list masquerade as verification.
            reason = "workflow_instance_contract_not_implemented"
        elif contract.kategorie not in {
            MCPToolKategorie.LESEN, MCPToolKategorie.BERECHNEN, MCPToolKategorie.VALIDIEREN
        }:
            reason = "write_capability_not_approved"
        else:
            headers = context.get("execution_headers", {})
            if not isinstance(headers, dict) or any(
                not isinstance(k, str) or k.lower() not in {"x-correlation-id", "x-request-id"}
                or not isinstance(v, str) or any(c in v for c in "\r\n")
                for k, v in headers.items()
            ):
                reason = "execution_headers_not_allowed"
        if reason is None:
            from app.core.security import verified_identity
            from app.core.tenant_binding import check_selector, check_body_selectors
            connection = Request({"type": "http", "method": "GET", "path": "/api/v1/neuro/tool",
                                  "query_string": b"", "headers": []})
            try:
                verified_identity(connection, token.strip())
                check_selector(tenant_id, connection.state.tenant_id)
                check_body_selectors(context.get("policy_context", {}), connection.state.tenant_id)
            except HTTPException as exc:
                reason, status = "identity_or_tenant_rejected", exc.status_code
            else:
                return None
        return {
            "mode": "execution_rejected", "tool_name": contract.tool_name,
            "api_endpoint": contract.api_endpoint, "http_status": status,
            "rejection_reason": reason, "request": {}, "response": None,
        }

    @staticmethod
    def _public_request_spec(request_spec: dict[str, Any]) -> dict[str, Any]:
        # Execution traces must never expose the credential used for transport.
        return {
            **request_spec,
            "headers": {
                k: ("[REDACTED]" if k.lower() == "authorization" else v)
                for k, v in request_spec.get("headers", {}).items()
            },
        }

    @staticmethod
    def _split_endpoint(api_endpoint: str) -> tuple[str, str]:
        parts = api_endpoint.strip().split(" ", 1)
        if len(parts) == 2:
            return parts[0].upper(), parts[1].strip()
        return "GET", api_endpoint.strip()

    def _get_client(self) -> TestClient:
        if self._client is None:
            # Use the same guarded application as the backend container.
            # app.main is the compatibility test surface, not production.
            from main import app as main_app
            self._client = TestClient(main_app, raise_server_exceptions=False)
        return self._client

    def _build_request_spec(
        self,
        contract: MCPToolContract,
        *,
        method: str,
        path_template: str,
        parameters: dict[str, Any],
        tenant_id: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        from app.core.tenant_binding import check_body_selectors
        check_body_selectors(parameters, tenant_id)
        merged = dict(parameters)
        merged.setdefault("tenant_id", tenant_id)
        merged.setdefault("prozess_key", context.get("process_key", "agrar_settlement"))
        merged.setdefault("aktions_typ", parameters.get("action_type", contract.operation.upper()))
        merged.setdefault("betrag_eur", parameters.get("amount"))
        merged.setdefault("ist_wert", parameters.get("amount", 0))
        merged.setdefault("entity_typ", self._normalize_entity_type(parameters.get("entity_type") or context.get("entity_type")))
        merged.setdefault("datensatz", dict(parameters))
        merged.setdefault("kontext", {k: v for k, v in context.items() if k not in {"auth_token", "execution_headers"}})

        path = path_template
        consumed_path_params: set[str] = set()
        for name in _PATH_PARAM_PATTERN.findall(path_template):
            value = merged.get(name)
            if value is None and name == "tenant_id":
                value = tenant_id
            if value is None:
                value = f"missing-{name}"
            path = path.replace(f"{{{name}}}", str(value))
            consumed_path_params.add(name)

        query: dict[str, Any] = {}
        body: dict[str, Any] | None = None

        if method in {"GET", "HEAD"}:
            for param in contract.parameter:
                if param.name in consumed_path_params:
                    continue
                value = merged.get(param.name)
                if value is not None:
                    query[param.name] = value
        else:
            body = self._build_body(contract, merged, parameters, context, tenant_id)

        return {
            "method": method,
            "path": path,
            "query": query,
            "json": body,
            "headers": {
                "Authorization": (
                    f"Bearer {context['auth_token'].strip()}"
                ),
                "X-Tenant-ID": tenant_id,
                "Content-Type": "application/json",
                **dict(context.get("execution_headers", {})),
            },
        }

    def _build_body(
        self,
        contract: MCPToolContract,
        merged: dict[str, Any],
        parameters: dict[str, Any],
        context: dict[str, Any],
        tenant_id: str,
    ) -> dict[str, Any]:
        if contract.tool_name == "valeo_process_data_quality_validate":
            from app.api.v1.schemas.data_quality_input import DataQualityCheckIn
            from pydantic import ValidationError
            try:
                return DataQualityCheckIn.model_validate(parameters).model_dump(mode="json")
            except ValidationError:
                raise HTTPException(422, "Explicit bounded data-quality object required") from None
        if contract.tool_name == "valeo_workflow_migration_check":
            from app.api.v1.schemas.workflow_migration_input import WorkflowMigrationCheckIn
            from pydantic import ValidationError
            try:
                return WorkflowMigrationCheckIn.model_validate(parameters).model_dump(mode="json")
            except ValidationError:
                raise HTTPException(422, "Explicit valid workflow snapshots required") from None
        if contract.request_payload_mode == MCPRequestPayloadMode.DATASET_VALIDATION:
            return {
                "entity_typ": merged.get("entity_typ") or "ARTIKEL",
                "datensatz": dict(parameters),
                "kontext_datensaetze": context.get("comparison_records"),
            }
        if contract.request_payload_mode == MCPRequestPayloadMode.POLICY_CONTEXT:
            return {
                "prozess_key": merged.get("prozess_key", "agrar_settlement"),
                "kontext": {
                    "betrag_eur": merged.get("betrag_eur", 0),
                    "tenant_id": tenant_id,
                    **dict(context.get("policy_context", {})),
                    **dict(parameters),
                },
            }
        if contract.request_payload_mode == MCPRequestPayloadMode.APPROVAL_CONTEXT:
            return {
                "aktions_typ": merged.get("aktions_typ", "NEURO_STEP"),
                "kontext": {
                    "betrag_eur": merged.get("betrag_eur"),
                    "tenant_id": tenant_id,
                    **dict(parameters),
                },
            }
        if contract.tool_name == "valeo_finance_sla_check":
            return {
                "slo_id": merged.get("slo_id", "SLO-API-VERF-01"),
                "ist_wert": merged.get("ist_wert", 0),
            }
        body: dict[str, Any] = {}
        for param in contract.parameter:
            value = merged.get(param.name)
            if value is not None:
                body[param.name] = value
        if body:
            return body
        return dict(parameters)

    @staticmethod
    def _normalize_entity_type(value: Any) -> str | None:
        if not value:
            return None
        text = str(value).strip().upper()
        mapping = {
            "SUPPLIER": "KREDITOR",
            "CUSTOMER": "DEBITOR",
            "ARTICLE": "ARTIKEL",
            "MASTER_DATA": "ARTIKEL",
            "INVOICE": "AP_RECHNUNG",
            "PURCHASE_ORDER": "ARTIKEL",
            "SALES_ORDER": "DEBITOR",
        }
        return mapping.get(text, text)

    @staticmethod
    def _read_response_body(response: Any) -> Any:
        try:
            return response.json()
        except Exception:
            return {"text": response.text}

    @staticmethod
    def _fallback_result(
        contract: MCPToolContract,
        request_spec: dict[str, Any],
        reason: str,
        *,
        http_status: int | None = None,
        response_body: Any = None,
    ) -> dict[str, Any]:
        return {
            "mode": "fallback_contract",
            "tool_name": contract.tool_name,
            "api_endpoint": contract.api_endpoint,
            "fallback_reason": reason,
            "http_status": http_status,
            "request": NeuroToolExecutionService._public_request_spec(request_spec),
            "response": response_body,
        }
