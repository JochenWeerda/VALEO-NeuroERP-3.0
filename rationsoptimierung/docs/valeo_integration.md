# VALEO ERP Integration Guide for Rations Optimization Tool

This document provides guidelines for integrating the rations optimization tool as a service within the VALEO ERP Agrarportal.

## Integration Overview

The rations optimization tool is designed as a standalone microservice that can be integrated into the VALEO ERP system. It follows API-first principles and provides clean JSON interfaces for seamless integration.

## VALEO NeuroERP Proxy (Implemented)

The main VALEO backend exposes a proxy at `/api/v1/agrar/rations-optimization/` that forwards requests to the Rationsoptimierung service. Use these paths when calling from the frontend or other VALEO services:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/agrar/rations-optimization/health` | GET | Health check (no auth required) |
| `/api/v1/agrar/rations-optimization/feeds` | GET | List feeds (optional `?group=forage`) |
| `/api/v1/agrar/rations-optimization/feeds/{id}` | GET | Get single feed |
| `/api/v1/agrar/rations-optimization/feeds/validate` | POST | Validate feed list |
| `/api/v1/agrar/rations-optimization/requirements/calculate` | POST | Calculate requirements from cow profile |
| `/api/v1/agrar/rations-optimization/requirements/maintenance` | POST | Maintenance requirements (`?body_weight_kg=650`) |
| `/api/v1/agrar/rations-optimization/optimize` | POST | Full optimization request |
| `/api/v1/agrar/rations-optimization/optimize/demo` | POST | Demo with sample data |
| `/api/v1/agrar/rations-optimization/optimize/from-profile` | POST | Optimize from cow profile only |

**Environment (Docker):** `RATIONS_OPTIMIZATION_URL`, `RATIONS_OPTIMIZATION_API_KEY`

**UI:** Futtermittel → Rationsoptimierung (ERP), Portal → Rationsoptimierung (Landwirte)

### Bedarfsnormen (GfE 2023)

Die Endpunkte `requirements/calculate` und `requirements/maintenance` nutzen im Microservice das Modul `app/nutrition/gfe2023.py`: ME-Erhaltung **0,64 × LM^0,75**, Milchbedarf über **ECM** (Faktor 0,337 + 0,116×Fett% + 0,06×Eiweiß%) und **ME_Milch ≈ ECM × (3,15/0,66)**. sidP, Faser-/Konzentratgrenzen und Minerale sind **Näherungen**; für verbindliche Beratung die Originalpublikation der GfE (AfBN, Sept. 2023, DLG-Verlag) heranziehen. **NEL und ME nicht gleichsetzen**; Futtermitteldaten für das LP müssen **ME** (bzw. aus offizieller ME-Tabelle abgeleitet) sein, nicht NEL-Zahlen 1:1 übernehmen.

**Standard-Futtermittelreferenz (GfE-2023-kompatibel):** Siehe im Microservice `docs/futterwerte_dlg_2025_gfe2023.md` und `data/reference/` (DLG 2025 Konzentrate, LKV Sachsen Getreideernte 2025). Für Produktivdaten `sidp_g_kgdm` und Mineralien aus DLG vollständig oder Labor befüllen.

**POST `/optimize/from-profile`:** Request-Body ist ein Objekt mit `cow_profile` (Pflicht), optional `feeds` (Liste von IDs) und `options`. Wird `feeds` weggelassen, werden alle Futtermittel des Mandanten verwendet – bei schmalem Futtermittelkorb und hohem GfE-ME-Bedarf kann das LP **unlösbar** sein (Mineralien, Stärke-Obergrenzen, Raufutteranteil). Dann entweder Korb erweitern oder im Profil **`target_dmi_kg`** setzen.

## API Versioning

The API uses path-based versioning with `/api/v1/` prefix. Future versions will follow semantic versioning:

- `/api/v1/` - Current stable version
- `/api/v2/` - Future versions with breaking changes
- `/api/v1beta/` - Beta/testing versions

## Authentication and Authorization

For ERP integration, the following authentication methods are recommended:

### 1. API Key Authentication (Simple)
- Include API key in header: `X-API-Key: your-api-key`
- Suitable for internal service-to-service communication
- Easy to implement and rotate

### 2. JWT Bearer Token (Recommended for Production)
- Standard OAuth2/JWT flow
- Token included in Authorization header: `Authorization: Bearer <token>`
- Supports role-based access control (RBAC)
- Can integrate with existing VALEO ERP identity provider

### 3. Mutual TLS (mTLS) (Highest Security)
- Certificate-based authentication
- Both client and server validate certificates
- Recommended for sensitive data exchanges
- Requires certificate management infrastructure

## Data Mapping Guidelines

### From VALEO ERP to Rations Optimization Tool

#### Animal Data (CowProfile)
| VALEO ERP Field | Optimization Tool Field | Mapping Notes |
|-----------------|-------------------------|---------------|
| animal_id | (internal mapping) | ERP maintains internal ID mapping |
| breed | cow_profile.breed | Map ERP breed codes to enum values |
| body_weight | cow_profile.body_weight_kg | Direct mapping |
| daily_milk_yield | cow_profile.milk_kg_day | Direct mapping |
| milk_fat_percent | cow_profile.milk_fat_pct | Direct mapping |
| milk_protein_percent | cow_profile.milk_protein_pct | Direct mapping |
| days_in_lactation | cow_profile.lactation_stage_days | Direct mapping |
| lactation_number | cow_profile.parity | Direct mapping |
| target_dmi | cow_profile.target_dmi_kg | Optional field |

#### Feed Inventory Data
| VALEO ERP Field | Optimization Tool Field | Mapping Notes |
|-----------------|-------------------------|---------------|
| feed_id | feed.id | Direct mapping |
| feed_name | feed.name | Direct mapping |
| feed_group | feed.group | Map ERP feed groups to enum |
| dry_matter_content | feed.dm_frac | Convert percentage to fraction (divide by 100) |
| price_per_ton | feed.price_eur_kgdm | Convert from EUR/ton to EUR/kg (divide by 1000) |
| me_per_kg_dm | feed.me_mj_kgdm | Direct mapping |
| sidp_per_kg_dm | feed.sidp_g_kgdm | Direct mapping |
| andfom_per_kg_dm | feed.andfom_g_kgdm | Direct mapping |
| starch_per_kg_dm | feed.starch_g_kgdm | Direct mapping |
| sugar_per_kg_dm | feed.sugar_g_kgdm | Direct mapping |
| fat_per_kg_dm | feed.fat_g_kgdm | Direct mapping |
| ca_per_kg_dm | feed.ca_g_kgdm | Direct mapping |
| p_per_kg_dm | feed.p_g_kgdm | Direct mapping |
| na_per_kg_dm | feed.na_g_kgdm | Direct mapping |
| min_usage | feed.min_kgdm | Direct mapping |
| max_usage | feed.max_kgdm | Direct mapping |
| is_active | feed.active | Direct mapping |

#### Nutritional Requirements (Optional Pre-calculation)
ERP may choose to calculate requirements internally and pass them directly, or use the tool's requirement calculation service.

| VALEO ERP Field | Optimization Tool Field | Mapping Notes |
|-----------------|-------------------------|---------------|
| dmi_requirement | requirements.dmi_kg | Direct mapping |
| me_requirement | requirements.me_min_mj | Direct mapping |
| sidp_requirement | requirements.sidp_min_g | Direct mapping |
| andfom_min | requirements.andfom_min_g | Direct mapping |
| andfom_max | requirements.andfom_max_g | Direct mapping |
| starch_max | requirements.starch_max_g | Direct mapping |
| sugar_max | requirements.sugar_max_g | Direct mapping |
| fat_max | requirements.fat_max_g | Direct mapping |
| ca_min | requirements.ca_min_g | Direct mapping |
| p_min | requirements.p_min_g | Direct mapping |
| na_min | requirements.na_min_g | Direct mapping |
| forage_share_min | requirements.forage_share_min | Direct mapping |

### From Rations Optimization Tool to VALEO ERP

#### Optimization Results
| Optimization Tool Field | VALEO ERP Field | Usage Notes |
|-------------------------|-----------------|-------------|
| status | optimization_status | Map to ERP status codes |
| total_cost_eur_day | daily_feed_cost | Cost per animal per day |
| ration_items | optimized_ration | List of feed amounts |
| nutrient_supply | actual_nutrient_intake | Verification of requirement fulfillment |
| constraint_report | constraint_fulfillment | Detailed constraint satisfaction |
| warnings | optimization_warnings | Potential issues to review |
| metadata | optimization_metadata | Solver info, timing, iterations |

#### Ration Items Format
Each ration item in the result maps to:
- feed_id → ERP feed identifier
- amount_kg_dm → Daily dry matter allocation
- amount_kg_fm → Daily fresh matter allocation (if needed by ERP)
- cost_per_kg_dm → Unit cost
- daily_cost → Total daily cost for this feed

## Recommended ERP Workflows

### Workflow 1: Real-time Ration Optimization
1. ERP detects need for ration recalculation (feed change, animal group change, price update)
2. ERP gathers current animal profile data
3. ERP retrieves current feed inventory and prices
4. ERP calls `/api/v1/optimize/from-profile` or `/api/v1/optimize`
5. ERP receives optimized ration
6. ERP updates feeding recommendations in animal management module
7. ERP generates feeding instructions for farm personnel

### Workflow 2: Batch Optimization for Herd Groups
1. ERP identifies animal groups with similar characteristics
2. For each group, ERP creates a representative cow profile
3. ERP calls optimization service for each group profile
4. ERP applies results to all animals in the group
5. ERP generates group-level feeding plans

### Workflow 3: What-if Analysis
1. ERP user modifies feed availability or prices in ERP interface
2. ERP calls optimization service to see impact on optimal ration
3. ERP displays comparison between current and optimized rations
4. ERP user approves changes and updates feeding plan

### Workflow 4: Nutritional Auditing
1. ERP periodically pulls current feeding plans from farm management systems
2. ERP compares actual feed usage to optimized recommendations
3. ERP generates reports on nutritional and economic efficiency
4. ERP suggests adjustments for continuous improvement

## Repository Interfaces (Future Implementation)

For tighter ERP integration, the following repository interfaces are recommended:

### FeedRepository
```python
class FeedRepository:
    def get_all_active_feeds() -> List[FeedIngredient]: ...
    def get_feed_by_id(feed_id: str) -> Optional[FeedIngredient]: ...
    def get_feeds_by_group(group: FeedGroup) -> List[FeedIngredient]: ...
    def search_feeds(criteria: Dict[str, Any]) -> List[FeedIngredient]: ...
```

### RequirementRepository
```python
class RequirementRepository:
    def calculate_requirements(cow_profile: CowProfile) -> NutrientRequirements: ...
    def get_maintenance_requirements(body_weight_kg: float) -> NutrientRequirements: ...
    # Future: Implement actual GfE-2023 formulas here
```

### OptimizationAuditRepository
```python
class OptimizationAuditRepository:
    def save_optimization_result(
        cow_profile: CowProfile,
        requirements: NutrientRequirements,
        result: OptimizationResult
    ) -> str: ...  # Returns audit ID
    
    def get_optimization_history(
        animal_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[OptimizationAuditRecord]: ...
    
    def get_cost_savings_report(
        period_start: datetime,
        period_end: datetime
    ) -> CostSavingsReport: ...
```

## Error Handling and Resilience

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (validation errors, invalid input)
- `401` - Unauthorized (missing or invalid authentication)
- `403` - Forbidden (authenticated but insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `422` - Unprocessable Entity (semantic errors)
- `429` - Too Many Requests (rate limiting)
- `500` - Internal Server Error (unexpected failures)
- `503` - Service Unavailable (temporary overload, maintenance)

### Error Response Format
All error responses follow this format:
```json
{
  "success": false,
  "timestamp": "2026-03-18T05:00:00Z",
  "message": "Human-readable error description",
  "error_code": "ERROR_CODE_IDENTIFIER",
  "details": {
    "field": "specific_field_that_failed",
    "issue": "description_of_the_problem",
    "rejected_value": "value_that_caused_the_error"
  }
}
```

### Retry Logic Recommendations
- Implement exponential backoff for 5xx errors
- Do not retry 4xx errors (client errors)
- Maximum 3 retry attempts for transient failures
- Circuit breaker pattern for extended service outages

## Performance and Scalability

### Response Times
- Health check: < 50ms
- Feed listing: < 100ms
- Requirement calculation: < 50ms
- Single optimization: Typically < 2s (depends on problem complexity)
- Demo optimization: < 1s

### Concurrency
- Service designed to handle multiple concurrent requests
- Each optimization request is independent
- Horizontal scaling possible by running multiple instances

### Resource Usage
- Memory: Typically < 100MB per instance
- CPU: Optimization is CPU-intensive during solve phase
- Disk: Minimal persistent storage needed (mainly for logs)

## Monitoring and Logging

### Health Endpoints
- `GET /health` - Basic liveness check
- Consider adding `/health/detailed` for dependency checks

### Metrics to Collect
- Request rates and response times per endpoint
- Optimization success/failure rates
- Average solve time
- Constraint violation frequencies
- Feed usage statistics

### Logging
- Structured JSON logging recommended
- Log levels: DEBUG, INFO, WARN, ERROR
- Correlation IDs for request tracing
- Audit logs for optimization results (if required)

## Security Considerations

### Data Protection
- All data in transit should be encrypted (HTTPS)
- Consider encrypting sensitive data at rest if stored
- Regular security updates for dependencies

### Input Validation
- Strict validation of all inputs (already implemented in service)
- Protection against common injection attacks
- Size limits on request payloads

### Rate Limiting
- Implement rate limiting at API gateway level
- Different limits for different endpoint types
- Consider burst allowances for interactive use

## Deployment Recommendations

### Container Orchestration
- Kubernetes preferred for production deployments
- Helm charts available for easy installation
- Resource requests/limits:
  - Requests: 100m CPU, 128Mi Memory
  - Limits: 500m CPU, 512Mi Memory

### Configuration Management
- Environment-specific configuration via environment variables
- ConfigMaps for non-sensitive configuration
- Secrets for API keys, certificates, etc.

### Backup and Disaster Recovery
- No persistent state stored in optimization service
- Configuration and sample data should be backed up
- Consider backing up optimization audit logs if implemented

## Testing in ERP Context

### Contract Testing
- Ensure ERP requests match service expectations
- Validate service responses match ERP handling capabilities
- Use tools like Pact for consumer-driven contract testing

### Integration Testing
- Test end-to-end workflows from ERP UI to service and back
- Validate error handling and recovery scenarios
- Performance testing under expected load

### User Acceptance Testing
- Verify optimization results make nutritional sense
- Check that cost savings are realistic
- Ensure user interface presents results clearly

## Change Management

### Version Compatibility
- Maintain backward compatibility within major versions
- Provide deprecation notices for removed features
- Use semantic versioning for API changes

### Migration Strategies
- Parallel run: old and new systems side-by-side
- Feature flags for gradual rollout
- Rollback procedures for problematic releases

## Example Integration Code Snippets

### Python ERP Integration Example
```python
import requests
from typing import Dict, Any, Optional

class RationsOptimizationClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Content-Type': 'application/json',
        }
        if api_key:
            self.headers['X-API-Key'] = api_key
    
    def optimize_ration_from_profile(
        self, 
        cow_profile: Dict[str, Any],
        feed_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Optimize ration starting from cow profile"""
        endpoint = f"{self.base_url}/api/v1/optimize/from-profile"
        
        payload = {
            "cow_profile": cow_profile
        }
        if feed_ids:
            payload["feeds"] = feed_ids
            
        response = requests.post(
            endpoint,
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def validate_feeds(self, feeds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate feed ingredients"""
        endpoint = f"{self.base_url}/api/v1/feeds/validate"
        
        response = requests.post(
            endpoint,
            json=feeds,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
```

### Health Check Monitoring Example
```python
def check_rations_service_health(service_url: str) -> bool:
    """Check if the rations optimization service is healthy"""
    try:
        response = requests.get(f"{service_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("success", False) and data.get("status") == "healthy"
        return False
    except requests.RequestException:
        return False
```

## Conclusion

This integration guide provides a comprehensive approach to incorporating the rations optimization tool into the VALEO ERP Agrarportal. By following these guidelines, the integration will be:

1. **Reliable** - Proper error handling and validation
2. **Secure** - Appropriate authentication and authorization
3. **Maintainable** - Clear separation of concerns and versioning
4. **Performant** - Efficient resource usage and response times
5. **Observable** - Comprehensive logging and monitoring capabilities
6. **Extensible** - Designed for future enhancements and changing requirements

The tool's modular architecture and API-first design ensure that it can evolve alongside the VALEO ERP system while maintaining a clean integration boundary.