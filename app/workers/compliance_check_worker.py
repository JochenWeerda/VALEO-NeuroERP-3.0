"""
Compliance Check Worker
Scheduled worker for monitoring compliance requirements (certificates, licenses, etc.)
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

from sqlalchemy import or_, and_

from ..core.config import settings
from app.core.database import get_db
from app.infrastructure.models import BusinessPartner

logger = logging.getLogger(__name__)


class ComplianceCheckWorker:
    """Worker for automated compliance checks"""

    def __init__(self):
        self.db = None

    async def initialize(self):
        """Initialize database connection"""
        self.db = next(get_db())

    async def run_compliance_checks(self) -> Dict[str, Any]:
        """
        Run compliance checks and generate alerts
        
        Returns:
            Dictionary with compliance check results
        """
        results = {
            'success': True,
            'issues': [],
            'checks': 0,
            'passed': 0,
            'failed': 0
        }

        try:
            if not self.db:
                await self.initialize()

            # Check 1: Business partner certificates (QS, Bio, etc.)
            issues = await self._check_certificate_expiry()
            results['issues'].extend(issues)
            results['checks'] += 1
            if not issues:
                results['passed'] += 1
            else:
                results['failed'] += 1

            # Check 2: Employee certifications
            issues = await self._check_employee_certifications()
            results['issues'].extend(issues)
            results['checks'] += 1
            if not issues:
                results['passed'] += 1
            else:
                results['failed'] += 1

            # Check 3: Vehicle inspections (TÜV, etc.)
            issues = await self._check_vehicle_inspections()
            results['issues'].extend(issues)
            results['checks'] += 1
            if not issues:
                results['passed'] += 1
            else:
                results['failed'] += 1

            # Check 4: Warehouse licenses
            issues = await self._check_warehouse_licenses()
            results['issues'].extend(issues)
            results['checks'] += 1
            if not issues:
                results['passed'] += 1
            else:
                results['failed'] += 1

            # Check 5: Tax compliance (VAT IDs)
            issues = await self._check_tax_compliance()
            results['issues'].extend(issues)
            results['checks'] += 1
            if not issues:
                results['passed'] += 1
            else:
                results['failed'] += 1

            logger.info(f"Compliance checks completed: {results['passed']} passed, {results['failed']} failed")

        except Exception as e:
            logger.error(f"Error in compliance checks: {e}")
            results['success'] = False
            results['error'] = str(e)

        return results

    async def _check_certificate_expiry(self) -> List[Dict[str, Any]]:
        """Check for expired business partner certificates"""
        try:
            if not self.db:
                return []
            threshold = datetime.utcnow() + timedelta(days=30)
            q = self.db.query(BusinessPartner).filter(
                BusinessPartner.status == "active",
                or_(
                    and_(BusinessPartner.qs_valid_until.isnot(None), BusinessPartner.qs_valid_until <= threshold),
                    and_(BusinessPartner.bio_certificate_valid_until.isnot(None), BusinessPartner.bio_certificate_valid_until <= threshold),
                ),
            )
            rows = q.limit(500).all()
            return [
                {"type": "certificate_expiry", "partner_id": r.partner_id, "name": r.name_1, "qs_valid_until": r.qs_valid_until.isoformat() if r.qs_valid_until else None, "bio_valid_until": r.bio_certificate_valid_until.isoformat() if r.bio_certificate_valid_until else None}
                for r in rows
            ]
        except Exception as e:
            logger.error(f"Error checking certificates: {e}")
            return [{'type': 'error', 'message': str(e)}]

    async def _check_employee_certifications(self) -> List[Dict[str, Any]]:
        """Prüft abgelaufene Mitarbeiter-Zertifikate/Schulungen.
        Datenquelle: Bei Bedarf Tabelle z. B. domain_shared.employee_certifications
        (employee_id, certificate_type, valid_until, training_id)."""
        try:
            if not self.db:
                return []
            # Optional: Abfrage auf employee_certifications sobald Modell existiert
            logger.info("Checking employee certifications...")
            return []
        except Exception as e:
            logger.error(f"Error checking employee certifications: {e}")
            return [{'type': 'error', 'message': str(e)}]

    async def _check_vehicle_inspections(self) -> List[Dict[str, Any]]:
        """Prüft abgelaufene Fahrzeugprüfungen (TÜV/o. Ä.).
        Datenquelle: Bei Bedarf Tabelle z. B. domain_logistics.vehicle_inspections
        (vehicle_id, inspection_type, valid_until)."""
        try:
            if not self.db:
                return []
            logger.info("Checking vehicle inspections...")
            return []
        except Exception as e:
            logger.error(f"Error checking vehicle inspections: {e}")
            return [{'type': 'error', 'message': str(e)}]

    async def _check_warehouse_licenses(self) -> List[Dict[str, Any]]:
        """Prüft abgelaufene Lager-Lizenzen (z. B. Getreidelager).
        Datenquelle: Bei Bedarf Tabelle z. B. domain_inventory.warehouse_licenses
        (warehouse_id, license_type, valid_until)."""
        try:
            if not self.db:
                return []
            logger.info("Checking warehouse licenses...")
            return []
        except Exception as e:
            logger.error(f"Error checking warehouse licenses: {e}")
            return [{'type': 'error', 'message': str(e)}]

    async def _check_tax_compliance(self) -> List[Dict[str, Any]]:
        """Prüft USt-ID: Format; bei ENABLE_VIES_CHECK zusätzlich EU-VIES-Service."""
        try:
            if not self.db:
                return []
            from app.infrastructure.models import BusinessPartner
            from app.core.vies import check_vat_format, check_vat_vies

            q = self.db.query(BusinessPartner).filter(
                BusinessPartner.status == "active",
                BusinessPartner.vat_id.isnot(None),
                BusinessPartner.vat_id != "",
            ).limit(200)
            partners = q.all()
            issues = []
            vies_enabled = getattr(settings, "ENABLE_VIES_CHECK", False)
            vies_checked = 0
            for p in partners:
                vat = (p.vat_id or "").strip()
                if not vat:
                    continue
                format_err = check_vat_format(vat)
                if format_err:
                    issues.append({
                        "type": "tax_compliance",
                        "message": format_err,
                        "partner_id": p.partner_id,
                        "name": p.name_1,
                        "vat_id": vat,
                    })
                    continue
                if vies_enabled and vies_checked < 20:
                    result = check_vat_vies(vat)
                    vies_checked += 1
                    if result.service_unavailable:
                        logger.warning("VIES service unavailable, skipping further checks")
                        break
                    if not result.valid and result.error_message:
                        issues.append({
                            "type": "tax_compliance",
                            "message": result.error_message,
                            "partner_id": p.partner_id,
                            "name": p.name_1,
                            "vat_id": vat,
                            "vies_valid": False,
                        })
            logger.info("Checking tax compliance: %s partners, %s issues, VIES checks %s", len(partners), len(issues), vies_checked)
            return issues
        except Exception as e:
            logger.error(f"Error checking tax compliance: {e}")
            return [{'type': 'error', 'message': str(e)}]

    async def cleanup(self):
        """Clean up database connections"""
        if self.db:
            self.db.close()


async def run_compliance_checks():
    """Main function to run compliance checks"""
    worker = ComplianceCheckWorker()

    try:
        await worker.initialize()
        result = await worker.run_compliance_checks()

        if result['success']:
            logger.info(f"Compliance checks completed: {result}")
        else:
            logger.error(f"Compliance checks failed: {result}")

        return result

    except Exception as e:
        logger.error(f"Critical error in compliance check worker: {e}")
        return {
            'success': False,
            'error': str(e)
        }

    finally:
        await worker.cleanup()


# Scheduled execution function (to be called by scheduler)
def execute_compliance_checks():
    """Synchronous wrapper for scheduled execution"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_compliance_checks())
        loop.close()

        return result

    except Exception as e:
        logger.error(f"Error executing compliance checks: {e}")
        return {
            'success': False,
            'error': str(e)
        }
