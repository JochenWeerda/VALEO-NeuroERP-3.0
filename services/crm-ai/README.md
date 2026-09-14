# CRM AI

CRM AI API prototype for predictive analytics, lead scoring, and intelligent automation.

**Implementation status (2026-09-14):** The ten business endpoints currently return simulated results. No trained model is loaded, feedback is not persisted, and a training response does not enqueue a real job. Passing the operational checks below establishes startup and HTTP/schema compatibility, not production ML readiness.

## Features

- **Lead Scoring**: ML-powered lead qualification and prioritization
- **Predictive Analytics**: Customer churn prediction, lifetime value forecasting
- **Recommendation Engine**: Next-best-action and product recommendations
- **Natural Language Processing**: Email analysis, sentiment analysis, intent detection
- **Automated Classification**: Intelligent routing and categorization
- **Performance Optimization**: A/B testing and campaign optimization

## API Endpoints

- `POST /api/v1/ai/lead-score` - Calculate lead scores with ML models
- `POST /api/v1/ai/predict/churn` - Predict customer churn probability
- `POST /api/v1/ai/predict/clv` - Calculate customer lifetime value
- `POST /api/v1/ai/recommend/actions` - Get next-best-action recommendations
- `POST /api/v1/ai/analyze/email` - Analyze email content and sentiment
- `POST /api/v1/ai/classify/case` - Auto-classify support cases
- `GET /api/v1/ai/models` - List available ML models and their performance

## Database Tables

- `crm_ai_models` - Trained ML models and metadata
- `crm_ai_predictions` - Prediction results and caching
- `crm_ai_features` - Feature engineering and data preparation
- `crm_ai_experiments` - A/B testing and model experiments
- `crm_ai_feedback` - User feedback for model improvement

## Dependencies

- PostgreSQL for AI data storage
- Redis for model caching and prediction results
- scikit-learn for traditional ML models
- TensorFlow/PyTorch for deep learning models
- spaCy/NLTK for natural language processing
- Integration with CRM services for training data and predictions

## Startup and regression checks

Set `DATABASE_URL` to a PostgreSQL URL using the `postgresql+asyncpg` driver.
The entrypoint applies Alembic migrations and starts Uvicorn on port 6200 only
when migration succeeds. Invalid credentials or a migration failure stop the
container. The database must be reachable when the container starts; deployment
readiness/restart policy supplies retries. No development reload worker is used.

From the repository root:

```sh
docker build -t crm-ai-check services/crm-ai
python scripts/verify_crm_ai_container.py crm-ai-check
docker run --rm --network none --entrypoint python \
  --mount type=bind,src="$PWD/scripts/verify_crm_ai_contracts.py",dst=/verify.py,readonly \
  crm-ai-check /verify.py
```

The startup checker uses its own disposable PostgreSQL container and network,
checks migration reruns, non-root execution, HTTP health and startup refusal on
migration failure, then removes its resources. The HTTP checker exercises all
ten business endpoints and input validation without external traffic. Both
run in `.github/workflows/service-security.yml` against the actual image.

Batch prediction accepts `lead_scoring`, `churn_prediction` and `clv`;
unsupported prediction types return HTTP 400. Batch and training identifiers
are UUIDs as required by their existing response schemas.

Audit all resolved service dependencies with
`python scripts/audit_service_dependencies.py`; reports remain under
`artifacts/service-security/` even when the audit fails. See
[the service security evidence](../../docs/quality-assurance/service-security-gates-2026-09-14.md).
