// VALEO Mask Builder Formatting Utilities

export function formatCurrency(value: number, currency = 'EUR'): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency,
  }).format(value)
}

export function formatNumber(value: number, decimals = 2): string {
  return new Intl.NumberFormat('de-DE', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

export function formatPercentage(value: number): string {
  return `${formatNumber(value)}%`
}

export function formatDate(value: string | Date): string {
  const date = typeof value === 'string' ? new Date(value) : value
  return date.toLocaleDateString('de-DE')
}

export function formatDateTime(value: string | Date): string {
  const date = typeof value === 'string' ? new Date(value) : value
  return date.toLocaleString('de-DE')
}

export function formatFileSize(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${formatNumber(size, 1)} ${units[unitIndex]}`
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return `${text.substring(0, maxLength)}...`
}

export function capitalizeFirst(text: string): string {
  return `${text.charAt(0).toUpperCase()}${text.slice(1).toLowerCase()}`
}

export function formatList(items: string[], maxItems = 3): string {
  if (items.length <= maxItems) {
    return items.join(', ')
  }

  const visibleItems = items.slice(0, maxItems)
  const remainingCount = items.length - maxItems

  return `${visibleItems.join(', ')} (+${remainingCount} weitere)`
}