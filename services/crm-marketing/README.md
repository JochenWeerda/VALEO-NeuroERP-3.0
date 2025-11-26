# CRM Marketing Service

Marketing automation service for segments, campaigns, and target groups.

## Responsibilities

- Manage marketing segments (dynamic and static)
- Segment rule engine
- Segment performance tracking
- Campaign management (future)
- Target group management

## API Endpoints

- `POST /api/v1/segments` - Create segment
- `GET /api/v1/segments` - List segments with filters
- `GET /api/v1/segments/{id}` - Get segment details
- `PUT /api/v1/segments/{id}` - Update segment
- `DELETE /api/v1/segments/{id}` - Delete segment
- `POST /api/v1/segments/{id}/rules` - Add rule
- `PUT /api/v1/segments/{id}/rules/{rule_id}` - Update rule
- `DELETE /api/v1/segments/{id}/rules/{rule_id}` - Delete rule
- `POST /api/v1/segments/{id}/members` - Add member manually
- `DELETE /api/v1/segments/{id}/members/{member_id}` - Remove member
- `POST /api/v1/segments/{id}/calculate` - Recalculate segment
- `GET /api/v1/segments/{id}/members` - List members
- `GET /api/v1/segments/{id}/performance` - Get performance data
- `GET /api/v1/segments/{id}/export` - Export segment

## Events

- `crm.segment.created`
- `crm.segment.updated`
- `crm.segment.member_added`
- `crm.segment.member_removed`
- `crm.segment.calculated`
