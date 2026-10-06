# CRM Multi-Channel Integration

Service handling multi-channel customer interactions including social media, web forms, external systems, and omnichannel communication.

## Implementation status

The service defines channel, conversation, message, form and integration schemas
and exposes their HTTP contracts. Platform-specific connectors are not implemented:
several endpoints return example data or placeholder acknowledgements. The webhook
signature check is a TODO; no verified platform delivery or synchronization is
provided by these handlers.

Facebook, Twitter, LinkedIn, Slack, Stripe, Shopify and WooCommerce SDKs are not
imported or dynamically loaded by the service. Their unused requirements have been
removed, including the transitive OAuth dependency reported by the service audit.
Platform names in schemas and example responses remain descriptive data. A future
connector must implement authentication, signature verification, delivery and tests
before adding the SDK it actually consumes.

## API Endpoints

- `POST /api/v1/multichannel/webhooks/{platform}` - Receive social media webhooks
- `GET /api/v1/multichannel/conversations` - List omnichannel conversations
- `POST /api/v1/multichannel/messages/send` - Send messages across channels
- `GET /api/v1/multichannel/forms` - List available web forms
- `POST /api/v1/multichannel/forms/{id}/submit` - Handle form submissions
- `GET /api/v1/multichannel/integrations` - List external system integrations
- `POST /api/v1/multichannel/sync` - Trigger data synchronization

## Database Tables

- `crm_multichannel_channels` - Social media and external channel configurations
- `crm_multichannel_conversations` - Unified conversation threads across channels
- `crm_multichannel_messages` - Individual messages from all channels
- `crm_multichannel_webforms` - Dynamic web form definitions
- `crm_multichannel_submissions` - Form submission data
- `crm_multichannel_integrations` - External system connection configurations

## Dependencies

- PostgreSQL for multi-channel data storage
- Redis for webhook queuing and real-time messaging
- FastAPI, SQLAlchemy and the pinned HTTP/runtime dependencies in `requirements.txt`

External platform APIs are future integration targets; the current service does not
require their SDKs.
