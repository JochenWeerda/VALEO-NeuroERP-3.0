# CRM Sync / Legacy Adapter Service

Responsibilities:
- Consume events/APIs from legacy ERP modules and map them to CRM canonical events (`CustomerReference`, `InteractionEvent`).
- Publish new events on the central bus when legacy systems lack them.
- Provide pull APIs for transitional read models (order history, invoice ledger).
