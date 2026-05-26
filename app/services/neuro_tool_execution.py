"""
Neuro Tool Execution Service - NC-A7
Executes MCP/OpenAPI tool contracts against the internal FastAPI surface and
falls back to contract-only simulation when a route cannot be executed safely.
"""

from __future__ import annotations

import json
import logging
import re
from urllib import parse, request
from typing import Any

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.outbound_security import validate_outbound_http_target
from app.core.mcp_tool_contracts import MCPRequestPayloadMode, MCPToolContract
from app.integrations.services.superglue_secret_resolver import resolve_superglue_auth_token

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
        request_spec = self._build_request_spec(
            contract,
            method=method,
            path_template=path_template,
            parameters=parameters,
            tenant_id=tenant_id,
            context=ctx,
        )

        if ctx.get("external_base_url"):
            return self._execute_external(contract, request_spec, ctx)

        client = self._get_client()
        try:
            response = client.request(
                method=method,
                url=request_spec["path"],
                params=request_spec["query"],
                json=request_spec["json"],
                headers=request_spec["headers"],
            )
        except Exception as exc:  # pragma: no cover - defensive boundary
            logger.warning("Internal tool execution failed for %s: %s", contract.tool_name, exc)
            return self._fallback_result(contract, request_spec, f"transport_error: {exc}")

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
            "request": request_spec,
            "response": self._read_response_body(response),
        }

    def _execute_external(
        self,
        contract: MCPToolContract,
        request_spec: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        path = request_spec["path"]
        try:
            base_url = validate_outbound_http_target(str(context["external_base_url"])).rstrip("/")
            url = f"{base_url}{path}" if path.startswith("/") else f"{base_url}/{path}"
            validate_outbound_http_target(url)
            response = self._request_external(
                method=request_spec["method"],
                url=url,
                params=request_spec["query"],
                json_body=request_spec["json"],
                headers=request_spec["headers"],
            )
        except Exception as exc:  # pragma: no cover - defensive boundary
            logger.warning("External tool execution failed for %s: %s", contract.tool_name, exc)
            return self._fallback_result(
                contract,
                {**request_spec, "url": locals().get("url", f"<blocked>{path}")},
                f"transport_error: {exc}",
            )

        if response["status_code"] >= 400:
            return self._fallback_result(
                contract,
                {**request_spec, "url": url},
                f"http_{response['status_code']}",
                http_status=response["status_code"],
                response_body=response["body"],
            )

        return {
            "mode": "openapi_external",
            "tool_name": contract.tool_name,
            "api_endpoint": contract.api_endpoint,
            "http_status": response["status_code"],
            "request": {**request_spec, "url": url},
            "response": response["body"],
        }

    @staticmethod
    def _split_endpoint(api_endpoint: str) -> tuple[str, str]:
        parts = api_endpoint.strip().split(" ", 1)
        if len(parts) == 2:
            return parts[0].upper(), parts[1].strip()
        return "GET", api_endpoint.strip()

    def _get_client(self) -> TestClient:
        if self._client is None:
            from app.main import app as main_app
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
        merged = dict(parameters)
        merged.setdefault("tenant_id", tenant_id)
        merged.setdefault("prozess_key", context.get("process_key", "agrar_settlement"))
        merged.setdefault("aktions_typ", parameters.get("action_type", contract.operation.upper()))
        merged.setdefault("betrag_eur", parameters.get("amount"))
        merged.setdefault("ist_wert", parameters.get("amount", 0))
        merged.setdefault("entity_typ", self._normalize_entity_type(parameters.get("entity_type") or context.get("entity_type")))
        merged.setdefault("datensatz", dict(parameters))
        merged.setdefault("kontext", dict(context))

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
                    f"Bearer {context.get('auth_token') or (resolve_superglue_auth_token(tenant_id, allow_global_fallback=True) if context.get('provider_key') == 'superglue' else None) or settings.API_DEV_TOKEN or 'neuro-tool-broker'}"
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

    def _request_external(
        self,
        *,
        method: str,
        url: str,
        params: dict[str, Any],
        json_body: dict[str, Any] | None,
        headers: dict[str, Any],
    ) -> dict[str, Any]:
        if self._external_requester is not None:
            return self._external_requester(
                method=method,
                url=url,
                params=params,
                json_body=json_body,
                headers=headers,
            )

        full_url = url
        if params:
            full_url = f"{url}?{parse.urlencode(params, doseq=True)}"

        payload = None
        req_headers = dict(headers)
        if json_body is not None:
            payload = json.dumps(json_body).encode("utf-8")
            req_headers.setdefault("Content-Type", "application/json")

        req = request.Request(full_url, data=payload, headers=req_headers, method=method.upper())
        try:
            with request.urlopen(req, timeout=10) as response:
                body_bytes = response.read()
                body_text = body_bytes.decode("utf-8") if body_bytes else ""
                try:
                    body = json.loads(body_text) if body_text else None
                except Exception:
                    body = {"text": body_text}
                return {"status_code": response.status, "body": body}
        except Exception as exc:
            status = getattr(exc, "code", None)
            body = None
            if hasattr(exc, "read"):
                try:
                    raw = exc.read().decode("utf-8")
                    body = json.loads(raw) if raw else None
                except Exception:
                    body = {"text": raw} if "raw" in locals() else None
            if status is not None:
                return {"status_code": status, "body": body}
            raise

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
            "request": request_spec,
            "response": response_body,
        }
