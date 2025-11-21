# CRM AI

Advanced AI and machine learning service for CRM predictive analytics, lead scoring, and intelligent automation.

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