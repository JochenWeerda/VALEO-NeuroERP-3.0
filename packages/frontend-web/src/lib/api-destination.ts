/** ERP identity headers belong only to the configured API or the current app origin. */
export function assertTrustedApiDestination(
  requestUrl: string | undefined,
  requestBaseUrl: string | undefined,
  trustedBaseUrl: string,
  pageUrl: string | undefined,
): void {
  try {
    const ambiguous = [requestUrl, requestBaseUrl, trustedBaseUrl].some(value =>
      [...(value ?? '')].some(char => char === '\\' || char.charCodeAt(0) < 32 || char.charCodeAt(0) === 127))
    if (ambiguous) {
      throw new Error('ambiguous URL')
    }
    const page = pageUrl ? new URL(pageUrl) : undefined
    const trusted = new URL(trustedBaseUrl || pageUrl || '', page)
    const base = new URL(requestBaseUrl || trusted.href, page ?? trusted)
    const target = new URL(requestUrl || '', base)
    const allowed = new Set([trusted.origin, ...(page ? [page.origin] : [])])
    if (!['http:', 'https:'].includes(target.protocol) || target.username || target.password
      || !['http:', 'https:'].includes(trusted.protocol) || !allowed.has(target.origin)) {
      throw new Error('untrusted')
    }
  } catch {
    // Never echo a URL: it could itself contain secrets or personal query values.
    throw new Error('API-Ziel ist nicht freigegeben.')
  }
}
