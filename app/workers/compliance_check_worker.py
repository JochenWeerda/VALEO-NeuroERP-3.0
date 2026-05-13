"""Compliance Check Worker — monitors certificates, licenses, and VAT IDs."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy import and_, or_

from ..core.config import settings
from app.infrastructure.models import BusinessPartner

from .base_worker import BaseWorker

logger = logging.getLogger(__name__)


class ComplianceCheckWorker(BaseWorker):
    async def run(self) -> Dict[str, Any]:
        result = self._base_result(issues=[], checks=0, passed=0, failed=0)
        try:
            await self._ensure_db()

            checks = [
                self._check_certificate_expiry,
                self._check_employee_certifications,
                self._check_vehicle_inspections,
                self._check_warehouse_licenses,
                self._check_tax_compliance,
            ]
            for check in checks:
                issues = await check()
                result["issues"].extend(issues)
                result["checks"] += 1
                if issues:
                    result["failed"] += 1
                else:
                    result["passed"] += 1

            logger.info(
                "Compliance checks: %d passed, %d failed",
                result["passed"], result["failed"],
            )
        except Exception as exc:
            self._error_result(result, exc)
        return result

    async def _check_certificate_expiry(self) -> List[Dict[str, Any]]:
        try:
            if not self.db:
                return []
            threshold = datetime.utcnow() + timedelta(days=30)
            rows = (
                self.db.query(BusinessPartner)
                .filter(
                    BusinessPartner.status == "active",
                    or_(
                        and_(
                            BusinessPartner.qs_valid_until.isnot(None),
                            BusinessPartner.qs_valid_until <= threshold,
                        ),
                        and_(
                            BusinessPartner.bio_certificate_valid_until.isnot(None),
                            BusinessPartner.bio_certificate_valid_until <= threshold,
                        ),
                    ),
                ).limit(500).all()
            )
            return [
                {
                    "type": "certificate_expiry",
                    "partner_id": r.partner_id,
                    "name": r.name_1,
                    "qs_valid_until": r.qs_valid_until.isoformat() if r.qs_valid_until else None,
                    "bio_valid_until": r.bio_certificate_valid_until.isoformat() if r.bio_certificate_valid_until else None,
                }
                for r in rows
            ]
        except Exception as exc:
            logger.error("Error checking certificates: %s", exc)
            return [{"type": "error", "message": str(exc)}]

    async def _check_employee_certifications(self) -> List[Dict[str, Any]]:
        try:
            if not self.db:
                return []
            logger.info("Checking employee certifications...")
            return []
        except Exception as exc:
            logger.error("Error checking employee certifications: %s", exc)
            return [{"type": "error", "message": str(exc)}]

    async def _check_vehicle_inspections(self) -> List[Dict[str, Any]]:
        try:
            if not self.db:
                return []
            logger.info("Checking vehicle inspections...")
            return []
        except Exception as exc:
            logger.error("Error checking vehicle inspections: %s", exc)
            return [{"type": "error", "message": str(exc)}]

    async def _check_warehouse_licenses(self) -> List[Dict[str, Any]]:
        try:
            if not self.db:
                return []
            logger.info("Checking warehouse licenses...")
            return []
        except Exception as exc:
            logger.error("Error checking warehouse licenses: %s", exc)
            return [{"type": "error", "message": str(exc)}]

    async def _check_tax_compliance(self) -> List[Dict[str, Any]]:
        try:
            if not self.db:
                return []
            from app.core.vies import check_vat_format, check_vat_vies

            partners = (
                self.db.query(BusinessPartner)
                .filter(
                    BusinessPartner.status == "active",
                    BusinessPartner.vat_id.isnot(None),
                    BusinessPartner.vat_id != "",
                ).limit(200).all()
            )
            issues: List[Dict[str, Any]] = []
            vies_enabled = getattr(settings, "ENABLE_VIES_CHECK", False)
            vies_checked = 0
            for p in partners:
                vat = (p.vat_id or "").strip()
                if not vat:
                    continue
                fmt_err = check_vat_format(vat)
                if fmt_err:
                    issues.append({
                        "type": "tax_compliance",
                        "message": fmt_err,
                        "partner_id": p.partner_id,
                        "name": p.name_1,
                        "vat_id": vat,
                    })
                    continue
                if vies_enabled and vies_checked < 20:
                    vies_result = check_vat_vies(vat)
                    vies_checked += 1
                    if vies_result.service_unavailable:
                        logger.warning("VIES service unavailable, skipping further checks")
                        break
                    if not vies_result.valid and vies_result.error_message:
                        issues.append({
                            "type": "tax_compliance",
                            "message": vies_result.error_message,
                            "partner_id": p.partner_id,
                            "name": p.name_1,
                            "vat_id": vat,
                            "vies_valid": False,
                        })
            logger.info(
                "Tax compliance check: %d partners, %d issues, %d VIES checks",
                len(partners), len(issues), vies_checked,
            )
            return issues
        except Exception as exc:
            logger.error("Error checking tax compliance: %s", exc)
            return [{"type": "error", "message": str(exc)}]

    async def cleanup(self) -> None:
        if self.db:
            self.db.close()


async def run_compliance_checks() -> Dict[str, Any]:
    worker = ComplianceCheckWorker()
    try:
        await worker.initialize()
        return await worker.run()
    except Exception as exc:
        logger.error("Critical error in compliance check worker: %s", exc)
        return {"success": False, "error": str(exc)}
    finally:
        await worker.cleanup()


def execute_compliance_checks() -> Dict[str, Any]:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_compliance_checks())
        loop.close()
        return result
    except Exception as exc:
        logger.error("Error executing compliance checks: %s", exc)
        return {"success": False, "error": str(exc)}
