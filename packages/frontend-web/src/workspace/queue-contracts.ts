/** The existing document Inbox queue endpoint, shared by the widget and live signals. */
export const INBOX_SLOT = {
  kind: 'inbox' as const,
  queueEndpoint: '/api/mcp/documents/inbox/queue',
  label: 'Beleg-Inbox',
}
